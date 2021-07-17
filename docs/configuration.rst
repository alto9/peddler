.. _configuration_customisation:

Configuration and customisation
===============================

.. _configuration:

Configuration
-------------

With Peddler, all OpenCart deployment parameters are stored in a single ``config.yml`` file. This is the file that is generated when you run ``peddler local quickstart`` or ``peddler config save``. To view the content of this file, run::

    cat "$(peddler config printroot)/config.yml"

By default, this file contains only the required configuration parameters for running the platform. Optional configuration parameters may also be specified to modify the default behaviour. To do so, you can edit the ``config.yml`` file manually::

    vim "$(peddler config printroot)/config.yml"

Alternatively, you can set each parameter from the command line::

    peddler config save --set PARAM1=VALUE1 --set PARAM2=VALUE2

Or from the system environment::

    export PEDDLER_PARAM1=VALUE1

Once the base configuration is created or updated, the environment is automatically re-generated. The environment is the set of all files required to manage an OpenCart platform: You can view the environment files in the ``env`` folder::

    ls "$(peddler config printroot)/env"

With an up-to-date environment, Peddler is ready to launch an OpenCart platform and perform usual operations. Below, we document some of the configuration parameters.

Individual service activation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``RUN_STORE`` (default: ``true``)
- ``RUN_SMTP`` (default: ``true``)
- ``ENABLE_HTTPS`` (default: ``false``)

Every single OpenCart service may be (de)activated at will by these configuration parameters. This is useful if you want, for instance, to distribute the various OpenCart services on different servers.

Docker
~~~~~~

.. _docker_images:

Custom images
*************

- ``DOCKER_IMAGE_OPENCART`` (default: ``"{{ DOCKER_REGISTRY }}alto9/opencart:{{ PEDDLER_VERSION }}"``)

These configuration parameters define which image to run for each service. By default, the docker image tag matches the Peddler version it was built with.

Custom registry
***************

- ``DOCKER_REGISTRY`` (default: ``"docker.io/"``)

You may want to pull/push images from/to a custom docker registry. For instance, for a registry running on ``localhost:5000``, define::

    DOCKER_REGISTRY: localhost:5000/

(the trailing ``/`` is important)

Vendor services
~~~~~~~~~~~~~~~

Caddy
*****

- ``RUN_CADDY`` (default: ``true``)

`Caddy <https://caddyserver.com>`__ is a web server used in Peddler as a web proxy for the generation of SSL/TLS certificates at runtime. If ``RUN_CADDY`` is set to ``false`` then we assume that SSL termination does not occur in the Caddy container, and thus the ``caddy`` container is not started.

Nginx
*****

- ``NGINX_HTTP_PORT`` (default: ``80``)

Nginx is used to route web traffic to the various applications and to serve static assets. When ``RUN_CADDY`` is false, the ``NGINX_HTTP_PORT`` is exposed on the host.

MySQL
*****

- ``RUN_MYSQL`` (default: ``true``)
- ``MYSQL_HOST`` (default: ``"mysql"``)
- ``MYSQL_PORT`` (default: ``3306``)
- ``MYSQL_ROOT_USERNAME`` (default: ``"root"``)
- ``MYSQL_ROOT_PASSWORD`` (default: randomly generated) Note that you are responsible for creating the root user if you are using a managed database.

By default, a running OpenCart platform deployed with Peddler includes all necessary 3rd-party services, such as MySQL, MongoDb, etc. But it's also possible to store data on a separate database, such as `Amazon RDS <https://aws.amazon.com/rds/>`_. For instance, to store data on an external MySQL database, set the following configuration::

    RUN_MYSQL: false
    MYSQL_HOST: yourhost
    MYSQL_ROOT_USERNAME: <root user name>
    MYSQL_ROOT_PASSWORD: <root user password>

.. note::
    When configuring an external MySQL database, please make sure it is using version 5.7.

SMTP
****

- ``RUN_SMTP`` (default: ``true``)
- ``SMTP_HOST`` (default: ``"smtp"``)
- ``SMTP_PORT`` (default: ``25``)
- ``SMTP_USERNAME`` (default: ``""``)
- ``SMTP_PASSWORD`` (default: ``""``)
- ``SMTP_USE_TLS`` (default: ``false``)
- ``SMTP_USE_SSL`` (default: ``false``)

Note that the SMTP server shipped with Peddler by default does not implement TLS. With external servers, only one of SSL or TLS should be enabled, at most.

SSL/TLS certificates for HTTPS access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``ENABLE_HTTPS`` (default: ``false``)

By activating this feature, a free SSL/TLS certificate from the `Let's Encrypt <https://letsencrypt.org/>`_ certificate authority will be created for your platform. With this feature, **your platform will no longer be accessible in HTTP**. Calls to http urls will be redirected to https url.

The following DNS records must exist and point to your server::

    STORE_HOST (e.g: mystore.com)

Thus, **this feature will (probably) not work in development** because the DNS records will (probably) not point to your development machine.

The SSL/TLS certificates will automatically be generated and updated by the Caddy proxy server container at runtime. Thus, as of v11.0.0 you no longer have to generate the certificates manually.