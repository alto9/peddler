.. _install:

Install Peddler
===============

.. _requirements:

Requirements
------------

* Supported OS: Peddler runs on any 64-bit, UNIX-based system. If you plan to try to use Windows, you will need to install from source.
* Required software:

    - `Docker <https://docs.docker.com/engine/installation/>`__: v18.06.0+
    - `Docker Compose <https://docs.docker.com/compose/install/>`__: v1.22.0+

.. warning::
    Do not attempt to simply run ``apt-get install docker docker-compose`` on older Ubuntu platforms, such as 16.04 (Xenial), as you will get older versions of these utilities.

* Ports 80 and 443 should be open. If other web services run on these ports, check the section on :ref:`how to setup a web proxy <web_proxy>`.
* Hardware:

    - Minimum configuration: 4 GB RAM, 2 CPU, 8 GB disk space
    - Recommended configuration: 8 GB RAM, 4 CPU, 25 GB disk space

.. note::
    On Mac OS, by default, containers are allocated 2 GB of RAM, which is not enough. You should follow `these instructions from the official Docker documentation <https://docs.docker.com/docker-for-mac/#advanced>`__ to allocate at least 4-5 GB to the Docker daemon. If the deployment fails because of insufficient memory during database migrations, check the :ref:`relevant section in the troubleshooting guide <migrations_killed>`.

.. _install_binary:

Direct binary download
----------------------

The latest binaries can be downloaded from https://github.com/alto9/peddler/releases. From the command line:

.. include:: download/binary.rst

This is the simplest and recommended installation method for most people. Note however that you will not be able to use custom plugins with this pre-compiled binary. The only plugins you can use with this approach are those that are already bundled with the binary: see the :ref:`existing plugins <existing_plugins>`.

.. _install_source:

Alternative installation methods
--------------------------------

If you would like to inspect the Peddler source code, you are most welcome to install Peddler from `Pypi <https://pypi.org/project/peddler/>`_ or directly from `the Github repository <https://github.com/alto9/peddler>`_. You will need python >= 3.6 with pip and the libyaml development headers. On Ubuntu, these requirements can be installed by running::

    sudo apt install python3 python3-pip libyaml-dev

Installing from pypi
~~~~~~~~~~~~~~~~~~~~

.. include:: download/pip.rst

Installing from source
~~~~~~~~~~~~~~~~~~~~~~

::

    git clone https://github.com/alto9/peddler
    cd peddler
    pip install -e .

DNS records
-----------

When running a server in production, it is necessary to define `DNS records <https://en.wikipedia.org/wiki/Domain_Name_System#Resource_records>`__ which will make it possible to access your OpenCart platform by name in your browser. The precise procedure to create DNS records vary from one provider to the next and is beyond the scope of these docs. You should create a record of type A with a name equal to your store hostname (given by ``peddler config printvalue STORE_HOST``) and a value that indicates the IP address of your server. Applications other than the store, such as SMTP, etc. typically reside in subdomains of the store. Thus, you should also create a CNAME record to point all subdomains of the store to the STORE_HOST.

Autocomplete
------------

Peddler is built on top of `Click <https://click.palletsprojects.com>`_, which is a great library for building command line interface (CLI) tools. As such, Peddler benefits from all Click features, including `auto-completion <https://click.palletsprojects.com/en/8.x/bashcomplete/>`_. After installing Peddler, auto-completion can be enabled in bash by running::

    _PEDDLER_COMPLETE=bash_source peddler >> ~/.bashrc

If you are running zsh, run instead::

    _PEDDLER_COMPLETE=zsh_source peddler >> ~/.zshrc

After opening a new shell, you can test auto-completion by typing::

    peddler <tab><tab>

Uninstallation
--------------

It is fairly easy to completely uninstall Peddler and to delete the OpenCart platform that is running locally.

First of all, stop any locally-running platform::

    peddler local stop
    peddler dev stop

Then, delete all data associated to your OpenCart platform::

    # WARNING: this step is irreversible
    sudo rm -rf "$(peddler config printroot)"

Finally, uninstall Peddler itself::

    # If you installed peddler from source
    pip uninstall peddler

    # If you downloaded the peddler binary
    sudo rm /usr/local/bin/peddler