from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from . import env
from . import fmt
from . import plugins


class BaseJobRunner:
    def __init__(self, root: str, config: Dict[str, Any]):
        self.root = root
        self.config = config

    def run_job_from_template(self, service: str, *path: str) -> None:
        command = self.render(*path)
        self.run_job(service, command)

    def run_cmd_from_template(self, service: str, *path: str) -> None:
        command = self.render(*path)
        self.run_cmd(service, command)

    def render(self, *path: str) -> str:
        rendered = env.render_file(self.config, *path).strip()
        if isinstance(rendered, bytes):
            raise TypeError("Cannot load job from binary file")
        return rendered

    def run_job(self, service: str, command: str) -> int:
        raise NotImplementedError

    def run_cmd(self, service: str, command: str) -> int:
        raise NotImplementedError

    def iter_plugin_hooks(
        self, hook: str
    ) -> Iterator[Tuple[str, Union[Dict[str, str], List[str]]]]:
        yield from plugins.iter_hooks(self.config, hook)


def initialise(runner: BaseJobRunner, limit_to: Optional[str] = None) -> None:
    fmt.echo_info("Initialising all services...")
    if limit_to is None or limit_to == "mysql":
        runner.run_job_from_template("mysql", "hooks", "mysql", "init")
    for plugin_name, hook in runner.iter_plugin_hooks("pre-init"):
        if limit_to is None or limit_to == plugin_name:
            for service in hook:
                fmt.echo_info(
                    "Plugin {}: running pre-init for service {}...".format(
                        plugin_name, service
                    )
                )
                runner.run_job_from_template(
                    service, plugin_name, "hooks", service, "pre-init"
                )
    for service in ["opencart"]:
        if limit_to is None or limit_to == service:
            fmt.echo_info("Initialising {}...".format(service))
            runner.run_cmd_from_template(service, "cmd", service, "init")
    for plugin_name, hook in runner.iter_plugin_hooks("init"):
        if limit_to is None or limit_to == plugin_name:
            for service in hook:
                fmt.echo_info(
                    "Plugin {}: running init for service {}...".format(
                        plugin_name, service
                    )
                )
                runner.run_job_from_template(
                    service, plugin_name, "hooks", service, "init"
                )
    fmt.echo_info("All services initialised.")
