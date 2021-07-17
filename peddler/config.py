import os
from typing import Dict, Any, Tuple

from . import exceptions
from . import env
from . import fmt

# from . import plugins
from . import serialize
from . import utils


def update(root: str) -> Dict[str, Any]:
    """
    Load and save the configuration.
    """
    config, defaults = load_all(root)
    save_config_file(root, config)
    merge(config, defaults)
    return config


def load(root: str) -> Dict[str, Any]:
    """
    Load full configuration. This will raise an exception if there is no current
    configuration in the project root.
    """
    check_existing_config(root)
    return load_no_check(root)


def load_no_check(root: str) -> Dict[str, Any]:
    config, defaults = load_all(root)
    merge(config, defaults)
    return config


def load_all(root: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Return:
        current (dict): params currently saved in config.yml
        defaults (dict): default values of params which might be missing from the
        current config
    """
    defaults = load_defaults()
    current = load_current(root, defaults)
    return current, defaults


def merge(
    config: Dict[str, str], defaults: Dict[str, str], force: bool = False
) -> None:
    """
    Merge default values with user configuration and perform rendering of "{{...}}"
    values.
    """
    for key, value in defaults.items():
        if force or key not in config:
            config[key] = env.render_unknown(config, value)


def load_defaults() -> Dict[str, Any]:
    return serialize.load(env.read_template_file("config.yml"))


def load_config_file(path: str) -> Dict[str, Any]:
    with open(path) as f:
        return serialize.load(f.read())


def load_current(root: str, defaults: Dict[str, str]) -> Dict[str, Any]:
    """
    Load the configuration currently stored on disk.
    Note: this modifies the defaults with the plugin default values.
    """
    convert_json2yml(root)
    config = load_user(root)
    load_env(config, defaults)
    load_required(config, defaults)
    # load_plugins(config, defaults)
    return config


def load_user(root: str) -> Dict[str, Any]:
    path = config_path(root)
    if not os.path.exists(path):
        return {}

    config = load_config_file(path)
    return config


def load_env(config: Dict[str, str], defaults: Dict[str, str]) -> None:
    for k in defaults.keys():
        env_var = "PEDDLER_" + k
        if env_var in os.environ:
            config[k] = serialize.parse(os.environ[env_var])


def load_required(config: Dict[str, str], defaults: Dict[str, str]) -> None:
    """
    All these keys must be present in the user's config.yml. This includes all values
    that are generated once and must be kept after that, such as passwords.
    """
    for key in [
        "MYSQL_ROOT_PASSWORD",
        "OPENCART_MYSQL_PASSWORD",
        "ID",
    ]:
        if key not in config:
            config[key] = env.render_unknown(config, defaults[key])


# def load_plugins(config: Dict[str, str], defaults: Dict[str, str]) -> None:
#     """
#     Add, override and set new defaults from plugins.
#     """
#     for plugin in plugins.iter_enabled(config):
#         # Add new config key/values
#         for key, value in plugin.config_add.items():
#             new_key = plugin.config_key(key)
#             if new_key not in config:
#                 config[new_key] = env.render_unknown(config, value)
#
#         # Create new defaults
#         for key, value in plugin.config_defaults.items():
#             defaults[plugin.config_key(key)] = value
#
#         # Set existing config key/values: here, we do not override existing values
#         # This must come last, as overridden values may depend on plugin defaults
#         for key, value in plugin.config_set.items():
#             if key not in config:
#                 config[key] = env.render_unknown(config, value)


def is_service_activated(config: Dict[str, Any], service: str) -> bool:
    return config["RUN_" + service.upper()] is not False


def convert_json2yml(root: str) -> None:
    """
    Older versions of Peddler used to have json config files.
    """
    json_path = os.path.join(root, "config.json")
    if not os.path.exists(json_path):
        return
    if os.path.exists(config_path(root)):
        raise exceptions.PeddlerError(
            "Both config.json and config.yml exist in {}: only one of these files must exist to continue".format(
                root
            )
        )
    config = load_config_file(json_path)
    save_config_file(root, config)
    os.remove(json_path)
    fmt.echo_info(
        "File config.json detected in {} and converted to config.yml".format(root)
    )


def save_config_file(root: str, config: Dict[str, str]) -> None:
    path = config_path(root)
    utils.ensure_file_directory_exists(path)
    with open(path, "w") as of:
        serialize.dump(config, of)
    fmt.echo_info("Configuration saved to {}".format(path))


def check_existing_config(root: str) -> None:
    """
    Check there is a configuration on disk and the current environment is up-to-date.
    """
    if not os.path.exists(config_path(root)):
        raise exceptions.PeddlerError(
            "Project root does not exist. Make sure to generate the initial "
            "configuration with `peddler config save --interactive` or `peddler local "
            "quickstart` prior to running other commands."
        )
    env.check_is_up_to_date(root)


def config_path(root: str) -> str:
    return os.path.join(root, "config.yml")
