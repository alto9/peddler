from datetime import datetime
from time import sleep
from typing import cast, Any, Dict, List, Optional, Type

import click

from .. import config as peddler_config
from .. import env as peddler_env
from .. import exceptions
from .. import fmt
from .. import interactive as interactive_config
from .. import jobs
from .. import serialize
from .. import utils
from .context import Context


class K8sClients:
    _instance = None

    def __init__(self) -> None:
        # Loading the kubernetes module here to avoid import overhead
        from kubernetes import client, config  # pylint: disable=import-outside-toplevel

        config.load_kube_config()
        self._batch_api = None
        self._core_api = None
        self._client = client

    @classmethod
    def instance(cls: Type["K8sClients"]) -> "K8sClients":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def batch_api(self):  # type: ignore
        if self._batch_api is None:
            self._batch_api = self._client.BatchV1Api()
        return self._batch_api

    @property
    def core_api(self):  # type: ignore
        if self._core_api is None:
            self._core_api = self._client.CoreV1Api()
        return self._core_api


class K8sJobRunner(jobs.BaseJobRunner):
    def load_job(self, name: str) -> Any:
        all_jobs = self.render("k8s", "jobs.yml")
        for job in serialize.load_all(all_jobs):
            job_name = cast(str, job["metadata"]["name"])
            if job_name == name:
                return job
        raise ValueError("Could not find job '{}'".format(name))

    def active_job_names(self) -> List[str]:
        """
        Return a list of active job names
        Docs:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#list-job-v1-batch
        """
        api = K8sClients.instance().batch_api
        return [
            job.metadata.name
            for job in api.list_namespaced_job(self.config["K8S_NAMESPACE"]).items
            if job.status.active
        ]

    def run_cmd(self, service: str, command: str) -> int:
        utils.kubectl(
            "exec",
            "-it",
            "deploy/{}".format(service),
            "-n",
            self.config["K8S_NAMESPACE"],
            "--",
            "bash",
            "-c",
            command,
        )

        return 0

    def run_job(self, service: str, command: str) -> int:
        job_name = "{}-job".format(service)
        try:
            job = self.load_job(job_name)
        except ValueError:
            message = (
                "The '{job_name}' kubernetes job does not exist in the list of job "
                "runners. This might be caused by an older plugin. Peddler switched to a"
                " job runner model for running one-time commands, such as database"
                " initialisation. For the record, this is the command that we are "
                "running:\n"
                "\n"
                "    {command}\n"
                "\n"
                "Old-style job running will be deprecated soon. Please inform "
                "your plugin maintainer!"
            ).format(
                job_name=job_name,
                command=command.replace("\n", "\n    "),
            )
            fmt.echo_alert(message)
            wait_for_pod_ready(self.config, service)
            return kubectl_exec(self.config, service, command)
        # Create a unique job name to make it deduplicate jobs and make it easier to
        # find later. Logs of older jobs will remain available for some time.
        job_name += "-" + datetime.now().strftime("%Y%m%d%H%M%S")

        # Wait until all other jobs are completed
        while True:
            active_jobs = self.active_job_names()
            if not active_jobs:
                break
            fmt.echo_info(
                "Waiting for active jobs to terminate: {}".format(" ".join(active_jobs))
            )
            sleep(5)

        # Configure job
        job["metadata"]["name"] = job_name
        job["metadata"].setdefault("labels", {})
        job["metadata"]["labels"]["app.kubernetes.io/name"] = job_name
        # Define k8s entrypoint/args
        shell_command = ["sh", "-e", "-c"]
        if job["spec"]["template"]["spec"]["containers"][0].get("command") == []:
            # Empty "command" (aka: entrypoint) might not be taken into account by jobs, so we need to manually
            # override the entrypoint. We do not do this for every job, because some entrypoints are actually useful.
            job["spec"]["template"]["spec"]["containers"][0]["command"] = shell_command
            container_args = [command]
        else:
            container_args = shell_command + [command]
        job["spec"]["template"]["spec"]["containers"][0]["args"] = container_args
        job["spec"]["backoffLimit"] = 1
        job["spec"]["ttlSecondsAfterFinished"] = 3600
        # Save patched job to "jobs.yml" file
        with open(peddler_env.pathjoin(self.root, "k8s", "jobs.yml"), "w") as job_file:
            serialize.dump(job, job_file)
        # We cannot use the k8s API to create the job: configMap and volume names need
        # to be found with the right suffixes.
        utils.kubectl(
            "apply",
            "--kustomize",
            peddler_env.pathjoin(self.root),
            "--selector",
            "app.kubernetes.io/name={}".format(job_name),
        )

        message = (
            "Job {job_name} is running. To view the logs from this job, run:\n\n"
            """    kubectl logs --namespace={namespace} --follow $(kubectl get --namespace={namespace} pods """
            """--selector=job-name={job_name} -o=jsonpath="{{.items[0].metadata.name}}")\n\n"""
            "Waiting for job completion..."
        ).format(job_name=job_name, namespace=self.config["K8S_NAMESPACE"])
        fmt.echo_info(message)

        # Wait for completion
        field_selector = "metadata.name={}".format(job_name)
        while True:
            namespaced_jobs = K8sClients.instance().batch_api.list_namespaced_job(
                self.config["K8S_NAMESPACE"], field_selector=field_selector
            )
            if not namespaced_jobs.items:
                continue
            job = namespaced_jobs.items[0]
            if not job.status.active:
                if job.status.succeeded:
                    fmt.echo_info("Job {} successful.".format(job_name))
                    break
                if job.status.failed:
                    raise exceptions.PeddlerError(
                        "Job {} failed. View the job logs to debug this issue.".format(
                            job_name
                        )
                    )
            sleep(5)
        return 0


@click.group(help="Run OpenCart on Kubernetes")
def k8s() -> None:
    pass


@click.command(help="Configure and run OpenCart from scratch")
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.pass_context
def quickstart(context: click.Context, non_interactive: bool) -> None:
    click.echo(fmt.title("Interactive platform configuration"))
    config = interactive_config.update(
        context.obj.root, interactive=(not non_interactive)
    )
    if not config["RUN_CADDY"]:
        fmt.echo_alert(
            "Potentially invalid configuration: RUN_CADDY=false\n"
            "In Peddler, a Caddy-based load balancer is provided out of the box"
            " to handle SSL/TLS certificate generation at runtime. If you disable this"
            " service, you will have to configure an Ingress resource and a certificate manager yourself to redirect"
            " traffic to the nginx service. See the Kubernetes section in the Peddler documentation for more"
            " information."
        )
    click.echo(fmt.title("Updating the current environment"))
    peddler_env.save(context.obj.root, config)
    click.echo(fmt.title("Starting the platform"))
    context.invoke(start)
    click.echo(fmt.title("Database creation and migrations"))
    context.invoke(init, limit=None)
    fmt.echo_info(
        """Your OpenCart platform is ready and can be accessed at the following urls:

    {http}://{store_host}
    """.format(
            http="https" if config["ENABLE_HTTPS"] else "http",
            store_host=config["STORE_HOST"],
        )
    )


@click.command(help="Run all configured OpenCart services")
@click.pass_obj
def start(context: Context) -> None:
    # Create namespace
    utils.kubectl(
        "apply",
        "--kustomize",
        peddler_env.pathjoin(context.root),
        "--wait",
        "--selector",
        "app.kubernetes.io/component=namespace",
    )
    # Create volumes
    utils.kubectl(
        "apply",
        "--kustomize",
        peddler_env.pathjoin(context.root),
        "--wait",
        "--selector",
        "app.kubernetes.io/component=volume",
    )
    # Create everything else except jobs
    utils.kubectl(
        "apply",
        "--kustomize",
        peddler_env.pathjoin(context.root),
        "--selector",
        # Here use `notin (job, xxx)` when there are other components to ignore
        "app.kubernetes.io/component!=job",
    )


@click.command(help="Stop a running platform")
@click.pass_obj
def stop(context: Context) -> None:
    config = peddler_config.load(context.root)
    utils.kubectl(
        "delete",
        *resource_selector(config),
        "deployments,services,configmaps,jobs",
    )


@click.command(help="Reboot an existing platform")
@click.pass_context
def reboot(context: click.Context) -> None:
    context.invoke(stop)
    context.invoke(start)


def resource_selector(config: Dict[str, str], *selectors: str) -> List[str]:
    """
    Convenient utility for filtering only the resources that belong to this project.
    """
    selector = ",".join(
        ["app.kubernetes.io/instance=opencart-" + config["ID"]] + list(selectors)
    )
    return ["--namespace", config["K8S_NAMESPACE"], "--selector=" + selector]


@click.command(help="Completely delete an existing platform")
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation")
@click.pass_obj
def delete(context: Context, yes: bool) -> None:
    if not yes:
        click.confirm(
            "Are you sure you want to delete the platform? All data will be removed.",
            abort=True,
        )
    utils.kubectl(
        "delete",
        "-k",
        peddler_env.pathjoin(context.root),
        "--ignore-not-found=true",
        "--wait",
    )


@click.command(help="Initialise all applications")
@click.option("-l", "--limit", help="Limit initialisation to this service or plugin")
@click.pass_obj
def init(context: Context, limit: Optional[str]) -> None:
    config = peddler_config.load(context.root)
    runner = K8sJobRunner(context.root, config)
    for service in ["mysql"]:
        if peddler_config.is_service_activated(config, service):
            wait_for_pod_ready(config, service)
    jobs.initialise(runner, limit_to=limit)


# @click.command(
#     help="Set a theme for a given domain name. To reset to the default theme , use 'default' as the theme name."
# )
# @click.argument("theme_name")
# @click.argument("domain_names", metavar="domain_name", nargs=-1)
# @click.pass_obj
# def settheme(context: Context, theme_name: str, domain_names: List[str]) -> None:
#     config = peddler_config.load(context.root)
#     runner = K8sJobRunner(context.root, config)
#     for domain_name in domain_names:
#         jobs.set_theme(theme_name, domain_name, runner)


@click.command(name="exec", help="Execute a command in a pod of the given application")
@click.argument("service")
@click.argument("command")
@click.pass_obj
def exec_command(context: Context, service: str, command: str) -> None:
    config = peddler_config.load(context.root)
    kubectl_exec(config, service, command, attach=True)


@click.command(help="View output from containers")
@click.option("-c", "--container", help="Print the logs of this specific container")
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
@click.option("--tail", type=int, help="Number of lines to show from each container")
@click.argument("service")
@click.pass_obj
def logs(
    context: Context, container: str, follow: bool, tail: bool, service: str
) -> None:
    config = peddler_config.load(context.root)

    command = ["logs"]
    selectors = ["app.kubernetes.io/name=" + service] if service else []
    command += resource_selector(config, *selectors)

    if container:
        command += ["-c", container]
    if follow:
        command += ["--follow"]
    if tail is not None:
        command += ["--tail", str(tail)]

    utils.kubectl(*command)


@click.command(help="Wait for a pod to become ready")
@click.argument("name")
@click.pass_obj
def wait(context: Context, name: str) -> None:
    config = peddler_config.load(context.root)
    wait_for_pod_ready(config, name)


def kubectl_exec(
    config: Dict[str, Any], service: str, command: str, attach: bool = False
) -> int:
    selector = "app.kubernetes.io/name={}".format(service)
    pods = K8sClients.instance().core_api.list_namespaced_pod(
        namespace=config["K8S_NAMESPACE"], label_selector=selector
    )
    if not pods.items:
        raise exceptions.PeddlerError(
            "Could not find an active pod for the {} service".format(service)
        )
    pod_name = pods.items[0].metadata.name

    # Run command
    attach_opts = ["-i", "-t"] if attach else []
    return utils.kubectl(
        "exec",
        *attach_opts,
        "--namespace",
        config["K8S_NAMESPACE"],
        pod_name,
        "--",
        "sh",
        "-e",
        "-c",
        command,
    )


def wait_for_pod_ready(config: Dict[str, str], service: str) -> None:
    fmt.echo_info("Waiting for a {} pod to be ready...".format(service))
    utils.kubectl(
        "wait",
        *resource_selector(config, "app.kubernetes.io/name={}".format(service)),
        "--for=condition=ContainersReady",
        "--timeout=600s",
        "pod",
    )


k8s.add_command(quickstart)
k8s.add_command(start)
k8s.add_command(stop)
k8s.add_command(reboot)
k8s.add_command(delete)
k8s.add_command(init)
# k8s.add_command(settheme)
k8s.add_command(exec_command)
k8s.add_command(logs)
k8s.add_command(wait)
