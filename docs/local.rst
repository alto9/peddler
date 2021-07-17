.. _local:

Local deployment
================

This method is for deploying OpenCart locally on a single server, where docker images are orchestrated with `docker-compose <https://docs.docker.com/compose/overview/>`_.

In the following, environment and data files will be generated in a user-specific project folder which will be referred to as the "**project root**". On Linux, the default project root is ``~/.local/share/peddler``. An alternative project root can be defined by passing the ``--root=...`` option to the ``peddler`` command, or defining the ``PEDDLER_ROOT=...`` environment variable::

    peddler --root=/path/to/peddlerroot run ...
    # Or equivalently:
    export PEDDLER_ROOT=/path/to/peddlerroot
    peddler run ...

Main commands
-------------

All available commands can be listed by running::

    peddler local help

All-in-one command
~~~~~~~~~~~~~~~~~~

A fully-functional platform can be configured and run in one command::

    peddler local quickstart

But you may want to run commands one at a time: it's faster when you need to run only part of the local deployment process, and it helps you understand how your platform works. In the following we decompose the ``quickstart`` command.

Configuration
~~~~~~~~~~~~~

::

    peddler config save --interactive

This is the only non-automatic step in the installation process. You will be asked various questions about your OpenCart platform and appropriate configuration files will be generated. If you would like to automate this step then you should run ``peddler config save --interactive`` once. After that, there will be a ``config.yml`` file at the root of the project folder: this file contains all the configuration values for your platform, such as randomly generated passwords, domain names, etc.

If you want to run a fully automated installation, upload the ``config.yml`` file to wherever you want to run OpenCart. You can then entirely skip the configuration step.

Update docker images
~~~~~~~~~~~~~~~~~~~~

::

    peddler local dc pull

This downloads the latest version of the Docker images from `Docker Hub <https://hub.docker.com/r/alto9/opencart/>`_. Depending on your bandwidth, this might take a long time. Minor image updates will be incremental, and thus much faster.

Running OpenCart
~~~~~~~~~~~~~~~~

::

    peddler local start

This will launch the various docker containers required for your OpenCart platform. The store and admin will then be reachable at the domain name you specified during the configuration step.

To stop the running containers, just hit Ctrl+C.

In production, you will probably want to daemonize the services. To do so, run::

    peddler local start --detach

And then, to stop all services::

    peddler local stop

Service initialisation
~~~~~~~~~~~~~~~~~~~~~~

::

    peddler local init

This command should be run just once. It will initialise all applications in a running platform. In particular, this will create the required databases tables and apply database migrations for all applications.

If initialisation is stopped with a ``Killed`` message, this certainly means the docker containers don't have enough RAM. See the :ref:`troubleshooting` section.

Logging
~~~~~~~

By default, logs from all containers are forwarded to the `default Docker logging driver <https://docs.docker.com/config/containers/logging/configure/>`_: this means that logs are printed to the standard output when running in non-daemon mode (``peddler local start``). In daemon mode, logs can still be accessed with ``peddler local logs`` commands (see :ref:`logging <logging>`).


.. _portainer:

Docker container web UI with `Portainer <https://portainer.io/>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Portainer is a web UI for managing docker containers. It lets you view your entire OpenCart platform at a glace. Try it! It's really cool::

    docker run --rm \
        --volume=/var/run/docker.sock:/var/run/docker.sock \
        --volume=/tmp/portainer:/data \
        -p 9000:9000 \
        portainer/portainer:latest --bind=:9000

.. .. image:: https://portainer.io/images/screenshots/portainer.gif
    ..:alt: Portainer demo

You can then view the portainer UI at `http://localhost:9000 <http://localhost:9000>`_. You will be asked to define a password for the admin user. Then, select a "Local environment" to work on; hit "Connect" and select the "local" group to view all running containers.

Among many other things, you'll be able to view the logs for each container, which is really useful.

Guides
------

.. _web_proxy:

Running OpenCart behind a web proxy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The containerized web server ([Caddy](caddyserver.com/)) needs to listen to ports 80 and 443 on the host. If there is already a webserver running on the host, such as Apache or Nginx, the caddy container will not be able to start. Peddler supports running behind a web proxy. To do so, add the following configuration::

       peddler config save --set RUN_CADDY=false --set NGINX_HTTP_PORT=81

In this example, the nginx container port would be mapped to 81 instead of 80. You must then configure the web proxy on the host. As of v11.0.0, configuration files are no longer provided for automatic configuration of your web proxy. Basically, you should setup a reverse proxy to `localhost:NGINX_HTTP_PORT` from the STORE_HOST, as well as any additional host exposed by your plugins.

.. warning::
    In this setup, the Nginx HTTP port will be exposed to the world. Make sure to configure your server firewall to block unwanted connections to your server's `NGINX_HTTP_PORT`. Alternatively, you can configure the Nginx container to accept only local connections::

        peddler config save --set NGINX_HTTP_PORT=127.0.0.1:81

Running multiple OpenCart platforms on a single server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With Peddler, it is easy to run multiple OpenCart instances on a single server. To do so, the following configuration parameters must be different for all platforms:

- ``PEDDLER_ROOT``: so that configuration, environment and data are not mixed up between platforms.
- ``LOCAL_PROJECT_NAME``: the various docker-compose projects cannot share the same name.
- ``NGINX_HTTP_PORT``: ports cannot be shared by two different containers.
- ``STORE_HOST``: the different platforms must be accessible from different domain (or subdomain) names.

In addition, a web proxy must be setup on the host, as described :ref:`above <web_proxy>`.

Upgrading from earlier versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Upgrading Peddler
*****************

Just upgrade Peddler using your :ref:`favorite installation method <install>` and run quickstart again::

    peddler local quickstart

Backups/Migrating to a different server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With Peddler, all data are stored in a single folder. This means that it's extremely easy to migrate an existing platform to a different server. For instance, it's possible to configure a platform locally on a laptop, and then move this platform to a production server.

1. Make sure `peddler` is installed on both servers with the same version.
2. Stop any running platform on server 1::

    peddler local stop

3. Transfer the configuration, environment and platform data from server 1 to server 2::

    rsync -avr "$(peddler config printroot)/" username@server2:/tmp/peddler/

4. On server 2, move the data to the right location::

    mv /tmp/peddler "$(peddler config printroot)"

5. Start the instance with::

    peddler local start -d

Making database dumps
~~~~~~~~~~~~~~~~~~~~~

To dump all data from the MySQL database used on the platform, run the following commands::

    peddler local exec -e MYSQL_ROOT_PASSWORD="$(peddler config printvalue MYSQL_ROOT_PASSWORD)" mysql \
        sh -c 'mysqldump --all-databases --password=$MYSQL_ROOT_PASSWORD > /var/lib/mysql/dump.sql'

The ``dump.sql`` file will be located in ``$(peddler config printroot)/data/mysql``.