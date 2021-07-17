from typing import Any, Dict, List, Tuple
import click

from . import config as peddler_config
from . import env
from . import exceptions
from . import fmt
from .__about__ import __version__


def update(root: str, interactive: bool = True) -> Dict[str, Any]:
    """
    Load and save the configuration.
    """
    config, defaults = load_all(root, interactive=interactive)
    peddler_config.save_config_file(root, config)
    peddler_config.merge(config, defaults)
    return config


def load_all(
    root: str, interactive: bool = True
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load configuration and interactively ask questions to collect param values from the user.
    """
    config, defaults = peddler_config.load_all(root)
    if interactive:
        ask_questions(config, defaults)
    return config, defaults


def ask_questions(config: Dict[str, Any], defaults: Dict[str, Any]) -> None:
    run_for_prod = config.get("STORE_HOST") != "localhost:8000/"
    run_for_prod = click.confirm(
        fmt.question(
            "Are you configuring a production ready store? Type 'n' if you are just testing Peddler on your local computer"
        ),
        prompt_suffix=" ",
        default=run_for_prod,
    )
    if not run_for_prod:
        dev_values = {
            "STORE_HOST": "localhost:8000/",
            "ENABLE_HTTPS": False,
        }
        fmt.echo_info(
            """As you are not running this store in production, we automatically set the following configuration values:"""
        )
        for k, v in dev_values.items():
            config[k] = v
            fmt.echo_info("    {} = {}".format(k, v))

    if run_for_prod:
        ask("Your shopping cart domain name ", "STORE_HOST", config, defaults)
        if "localhost" in config["STORE_HOST"]:
            raise exceptions.PeddlerError(
                "You may not use 'localhost' as the store domain name. To run a local store for testing purposes you should answer 'n' to the previous question."
            )

    ask("Your store name/title", "PLATFORM_NAME", config, defaults)
    ask("Your new admin account username", "OPENCART_ADMIN_USERNAME", config, defaults)
    ask("Your new admin account password", "OPENCART_ADMIN_PASSWORD", config, defaults)
    ask("Email address for admin account", "CONTACT_EMAIL", config, defaults)

    if run_for_prod:
        ask_bool(
            (
                "Activate SSL/TLS certificates for HTTPS access? Important note:"
                " this will NOT work in a development environment."
            ),
            "ENABLE_HTTPS",
            config,
            defaults,
        )


def ask(
    question: str, key: str, config: Dict[str, Any], defaults: Dict[str, Any]
) -> None:
    default = env.render_str(config, config.get(key, defaults[key]))
    config[key] = click.prompt(
        fmt.question(question), prompt_suffix=" ", default=default, show_default=True
    )


def ask_bool(
    question: str, key: str, config: Dict[str, Any], defaults: Dict[str, Any]
) -> None:
    default = config.get(key, defaults[key])
    config[key] = click.confirm(
        fmt.question(question), prompt_suffix=" ", default=default
    )


def ask_choice(
    question: str,
    key: str,
    config: Dict[str, Any],
    defaults: Dict[str, Any],
    choices: List[str],
) -> None:
    default = config.get(key, defaults[key])
    answer = click.prompt(
        fmt.question(question),
        type=click.Choice(choices),
        prompt_suffix=" ",
        default=default,
        show_choices=False,
    )
    config[key] = answer
