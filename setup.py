import io
import os

from setuptools import find_packages, setup

PWD = os.path.abspath(os.path.dirname(__file__))

def load_readme():
    with io.open(os.path.join(PWD, "README.rst"), "rt", encoding="utf8") as f:
        readme = f.read()
    # Replace img src for publication on pypi
    return readme.replace("./docs/img/", "https://github.com/alto9/peddler/raw/master/docs/img/")

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
    entry_points={"console_scripts": ["peddler=peddler.commands.cli:main"]},
    author="alto9.com",
    author_email="contact@alto9.com",
    description="The Docker-based OpenCart distribution for control-freaks",
    long_description=load_readme(),
    long_description_content_type="text/x-rst",
)