import os
from typing import Dict, Any

import click

from .. import config as peddler_config
from .. import env as peddler_env
from .. import fmt
from .. import utils
from . import compose
from .config import save as config_save_command
from .context import Context


def docker_compose(root: str, config: Dict[str, Any], *command: str) -> int:
    """
    Run docker-compose with local and production yml files.
    """
    args = []
    override_path = peddler_env.pathjoin(root, "local", "docker-compose.override.yml")
    if os.path.exists(override_path):
        args += ["-f", override_path]
    return utils.docker_compose(
        "-f",
        peddler_env.pathjoin(root, "local", "docker-compose.yml"),
        *args,
        "--project-name",
        config["LOCAL_PROJECT_NAME"],
        *command
    )


@click.group(help="Run OpenCart locally from scratch")
@click.pass_obj
def local(context: Context) -> None:
    context.docker_compose_func = docker_compose


@click.command(help="Configure and run OpenCart in docker-compose")
@click.option("-I", "--non-interactive", is_flag=True, help="Run non-interactively")
@click.option("-p", "--pullimages", is_flag=True, help="Update docker images")
@click.pass_context
def quickstart(context: click.Context, non_interactive: bool, pullimages: bool) -> None:
    click.echo(fmt.title("Interactive platform configuration"))
    context.invoke(
        config_save_command,
        interactive=(not non_interactive),
        set_vars=[],
        unset_vars=[],
    )
    click.echo(fmt.title("Stopping any existing platform"))
    context.invoke(compose.stop)
    if pullimages:
        click.echo(fmt.title("Docker image updates"))
        context.invoke(compose.dc_command, command="pull")
    click.echo(fmt.title("Starting the platform in detached mode"))
    context.invoke(compose.start, detach=True)
    click.echo(fmt.title("Database creation and migrations"))
    context.invoke(compose.init)
    # click.echo(fmt.title("Initial store configuration"))
    # context.invoke(compose.init)

    config = peddler_config.load(context.obj.root)
    fmt.echo_info(
        """The OpenCart platform is now running in detached mode
Your OpenCart platform is ready and can be accessed at the following urls:

    {http}://{store_host}
    {http}://{store_host}admin
    """.format(
            http="https" if config["ENABLE_HTTPS"] else "http",
            store_host=config["STORE_HOST"],
        )
    )


local.add_command(quickstart)
compose.add_commands(local)
