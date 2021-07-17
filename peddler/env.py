import codecs
from copy import deepcopy
import os
from typing import Dict, Any, Iterable, List, Optional, Type, Union

import jinja2
import pkg_resources

from . import exceptions
from . import fmt
from . import plugins
from . import utils
from .__about__ import __version__


TEMPLATES_ROOT = pkg_resources.resource_filename("peddler", "templates")
VERSION_FILENAME = "version"
BIN_FILE_EXTENSIONS = [".ico", ".jpg", ".png", ".ttf", ".woff", ".woff2"]


class Renderer:
    @classmethod
    def instance(cls: Type["Renderer"], config: Dict[str, Any]) -> "Renderer":
        # Load template roots: these are required to be able to use
        # {% include .. %} directives
        template_roots = [TEMPLATES_ROOT]
        for plugin in plugins.iter_enabled(config):
            if plugin.templates_root:
                template_roots.append(plugin.templates_root)

        return cls(config, template_roots, ignore_folders=["partials"])

    def __init__(
        self,
        config: Dict[str, Any],
        template_roots: List[str],
        ignore_folders: Optional[List[str]] = None,
    ):
        self.config = deepcopy(config)
        self.template_roots = template_roots
        self.ignore_folders = ignore_folders or []
        self.ignore_folders.append(".git")

        # Create environment
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_roots),
            undefined=jinja2.StrictUndefined,
        )
        environment.filters["common_domain"] = utils.common_domain
        environment.filters["encrypt"] = utils.encrypt
        environment.filters["list_if"] = utils.list_if
        environment.filters["long_to_base64"] = utils.long_to_base64
        environment.filters["random_string"] = utils.random_string
        environment.filters["reverse_host"] = utils.reverse_host
        environment.filters["rsa_private_key"] = utils.rsa_private_key
        environment.filters["walk_templates"] = self.walk_templates
        environment.globals["patch"] = self.patch
        environment.globals["rsa_import_key"] = utils.rsa_import_key
        environment.globals["PEDDLER_VERSION"] = __version__
        self.environment = environment

    def iter_templates_in(self, *prefix: str) -> Iterable[str]:
        """
        The elements of `prefix` must contain only "/", and not os.sep.
        """
        full_prefix = "/".join(prefix)
        for template in self.environment.loader.list_templates():  # type: ignore
            if template.startswith(full_prefix) and self.is_part_of_env(template):
                yield template

    def walk_templates(self, subdir: str) -> Iterable[str]:
        """
        Iterate on the template files from `templates/<subdir>`.

        Yield:
            path: template path relative to the template root
        """
        yield from self.iter_templates_in(subdir + "/")

    def is_part_of_env(self, path: str) -> bool:
        """
        Determines whether a template should be rendered or not. Note that here we don't
        rely on the OS separator, as we are handling templates
        """
        parts = path.split("/")
        basename = parts[-1]
        is_excluded = False
        is_excluded = (
            is_excluded or basename.startswith(".") or basename.endswith(".pyc")
        )
        is_excluded = is_excluded or basename == "__pycache__"
        for ignore_folder in self.ignore_folders:
            is_excluded = is_excluded or ignore_folder in parts
        return not is_excluded

    def find_os_path(self, template_name: str) -> str:
        path = template_name.replace("/", os.sep)
        for templates_root in self.template_roots:
            full_path = os.path.join(templates_root, path)
            if os.path.exists(full_path):
                return full_path
        raise ValueError("Template path does not exist")

    def patch(self, name: str, separator: str = "\n", suffix: str = "") -> str:
        """
        Render calls to {{ patch("...") }} in environment templates from plugin patches.
        """
        patches = []
        for plugin, patch in plugins.iter_patches(self.config, name):
            patch_template = self.environment.from_string(patch)
            try:
                patches.append(patch_template.render(**self.config))
            except jinja2.exceptions.UndefinedError as e:
                raise exceptions.PeddlerError(
                    "Missing configuration value: {} in patch '{}' from plugin {}".format(
                        e.args[0], name, plugin
                    )
                )
        rendered = separator.join(patches)
        if rendered:
            rendered += suffix
        return rendered

    def render_str(self, text: str) -> str:
        template = self.environment.from_string(text)
        return self.__render(template)

    def render_template(self, template_name: str) -> Union[str, bytes]:
        """
        Render a template file. Return the corresponding string. If it's a binary file
        (as indicated by its path), return bytes.

        The template_name *always* uses "/" separators, and is not os-dependent. Do not pass the result of
        os.path.join(...) to this function.
        """
        if is_binary_file(template_name):
            # Don't try to render binary files
            with open(self.find_os_path(template_name), "rb") as f:
                return f.read()

        try:
            template = self.environment.get_template(template_name)
        except Exception:
            fmt.echo_error("Error loading template " + template_name)
            raise

        try:
            return self.__render(template)
        except (jinja2.exceptions.TemplateError, exceptions.PeddlerError):
            fmt.echo_error("Error rendering template " + template_name)
            raise
        except Exception:
            fmt.echo_error("Unknown error rendering template " + template_name)
            raise

    def render_all_to(self, root: str, *prefix: str) -> None:
        """
        `prefix` can be used to limit the templates to render.
        """
        for template_name in self.iter_templates_in(*prefix):
            rendered = self.render_template(template_name)
            dst = os.path.join(root, template_name.replace("/", os.sep))
            write_to(rendered, dst)

    def __render(self, template: jinja2.Template) -> str:
        try:
            return template.render(**self.config)
        except jinja2.exceptions.UndefinedError as e:
            raise exceptions.PeddlerError(
                "Missing configuration value: {}".format(e.args[0])
            )


def save(root: str, config: Dict[str, Any]) -> None:
    """
    Save the full environment, including version information.
    """
    root_env = pathjoin(root)
    for prefix in [
        "android/",
        "apps/",
        "build/",
        "dev/",
        "k8s/",
        "local/",
        "webui/",
        VERSION_FILENAME,
        "kustomization.yml",
    ]:
        save_all_from(prefix, root_env, config)

    for plugin in plugins.iter_enabled(config):
        if plugin.templates_root:
            save_plugin_templates(plugin, root, config)

    fmt.echo_info("Environment generated in {}".format(base_dir(root)))


def save_plugin_templates(
    plugin: plugins.BasePlugin, root: str, config: Dict[str, Any]
) -> None:
    """
    Save plugin templates to plugins/<plugin name>/*.
    Only the "apps" and "build" subfolders are rendered.
    """
    plugins_root = pathjoin(root, "plugins")
    for subdir in ["apps", "build"]:
        subdir_path = os.path.join(plugin.name, subdir)
        save_all_from(subdir_path, plugins_root, config)


def save_all_from(prefix: str, root: str, config: Dict[str, Any]) -> None:
    """
    Render the templates that start with `prefix` and store them with the same
    hierarchy at `root`. Here, `prefix` can be the result of os.path.join(...).
    """
    renderer = Renderer.instance(config)
    renderer.render_all_to(root, prefix.replace(os.sep, "/"))


def write_to(content: Union[str, bytes], path: str) -> None:
    """
    Write some content to a path. Content can be either str or bytes.
    """
    utils.ensure_file_directory_exists(path)
    if isinstance(content, bytes):
        with open(path, mode="wb") as of_binary:
            of_binary.write(content)
    else:
        with open(path, mode="w", encoding="utf8", newline="\n") as of_text:
            of_text.write(content)


def render_file(config: Dict[str, Any], *path: str) -> Union[str, bytes]:
    """
    Return the rendered contents of a template.
    """
    renderer = Renderer.instance(config)
    template_name = "/".join(path)
    return renderer.render_template(template_name)


def render_dict(config: Dict[str, Any]) -> None:
    """
    Render the values from the dict. This is useful for rendering the default
    values from config.yml.

    Args:
        config (dict)
    """
    rendered = {}
    for key, value in config.items():
        if isinstance(value, str):
            rendered[key] = render_str(config, value)
        else:
            rendered[key] = value
    for k, v in rendered.items():
        config[k] = v


def render_unknown(config: Dict[str, Any], value: Any) -> Any:
    if isinstance(value, str):
        return render_str(config, value)
    return value


def render_str(config: Dict[str, Any], text: str) -> str:
    """
    Args:
        text (str)
        config (dict)

    Return:
        substituted (str)
    """
    return Renderer.instance(config).render_str(text)


def check_is_up_to_date(root: str) -> None:
    if not is_up_to_date(root):
        message = (
            "The current environment stored at {} is not up-to-date: it is at "
            "v{} while the 'peddler' binary is at v{}. You should upgrade "
            "the environment by running:\n"
            "\n"
            "    peddler config save"
        )
        fmt.echo_alert(
            message.format(base_dir(root), current_version(root), __version__)
        )


def is_up_to_date(root: str) -> bool:
    """
    Check if the currently rendered version is equal to the current peddler version.
    """
    return current_version(root) == __version__


def needs_major_upgrade(root: str) -> bool:
    """
    Return the current version as a tuple of int. E.g: (1, 0, 2).
    """
    current = int(current_version(root).split(".")[0])
    required = int(__version__.split(".")[0])
    return 0 < current < required


def current_version(root: str) -> str:
    """
    Return the current environment version. If the current environment has no version,
    return "0.0.0".
    """
    path = pathjoin(root, VERSION_FILENAME)
    print(path)
    if not os.path.exists(path):
        return "0.0.0"
    return open(path).read().strip()


def read_template_file(*path: str) -> str:
    """
    Read raw content of template located at `path`.
    """
    src = template_path(*path)
    with codecs.open(src, encoding="utf-8") as fi:
        return fi.read()


def is_binary_file(path: str) -> bool:
    ext = os.path.splitext(path)[1]
    return ext in BIN_FILE_EXTENSIONS


def template_path(*path: str, templates_root: str = TEMPLATES_ROOT) -> str:
    """
    Return the template file's absolute path.
    """
    return os.path.join(templates_root, *path)


def data_path(root: str, *path: str) -> str:
    """
    Return the file's absolute path inside the data directory.
    """
    return os.path.join(root_dir(root), "data", *path)


def pathjoin(root: str, *path: str) -> str:
    """
    Return the file's absolute path inside the environment.
    """
    return os.path.join(base_dir(root), *path)


def base_dir(root: str) -> str:
    """
    Return the environment base directory.
    """
    return os.path.join(root_dir(root), "env")


def root_dir(root: str) -> str:
    """
    Return the project root directory.
    """
    return os.path.abspath(root)
