import io
import os

from setuptools import find_packages, setup

PWD = os.path.abspath(os.path.dirname(__file__))

def load_about():
    about = {}
    with io.open(
        os.path.join(PWD, "peddler", "__about__.py"), "rt", encoding="utf-8"
    ) as f:
        exec(f.read(), about)  # pylint: disable=exec-used
    return about

def load_requirements():
    with io.open(
        os.path.join(PWD, "requirements", "base.in"), "rt", encoding="utf-8"
    ) as f:
        return [line.strip() for line in f if is_requirement(line)]


def is_requirement(line):
    return not (line.strip() == "" or line.startswith("#"))

ABOUT = load_about()

setup(
    name="peddler",
    version=ABOUT["__version__"],
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    license="AGPLv3",
    install_requires=load_requirements(),
    entry_points={"console_scripts": ["peddler=peddler.commands.cli:main"]}
)