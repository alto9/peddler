.. _faq:

FAQ
===

What is Peddler?
----------------

Peddler is an open source distribution of `OpenCart <https://opencart.com>`_. It uses the original code from the OpenCart repository and packages everything in a way that makes it very easy to install, administer and upgrade OpenCart. In particular, all services are run inside Docker containers.

Peddler makes it possible to deploy OpenCart locally, with `docker-compose <https://docs.docker.com/compose/overview/>`_ or on an existing `Kubernetes cluster <http://kubernetes.io/>`_. Want to learn more? Take a look at the :ref:`getting started concepts <intro>`.

What is the purpose of Peddler?
-------------------------------

To make it possible to deploy, administer and upgrade OpenCart anywhere, easily.

.. _native:

What's the difference with the official "native" installation?
--------------------------------------------------------------

The `native installation <http://docs.opencart.com/en-gb/installation/>`_ is to deploy OpenCart on one server. This install suffers from a couple issues that Peddler tries to address:

1. The native installation procedure doesn't account for high-availability. There should be at least two copies of your store running, for resiliency. Docker makes this easy.
2. The native installation procedure recommends using FTP. FTP is ok if enabled for a short period of time but FTP is not very secure and we would prefer it not get used at all in this context.
3. Isolation from the OS: Peddler barely needs to touch your server because the entire platform is packaged inside Docker containers. You are thus free to run other services on your server without fear of indirectly crashing your OpenCart platform.
4. Security: with Peddler you are now free to install security-related upgrades as soon as they become available.
5. Portability: Peddler makes it easy to move your platform from one server to another. Just zip-compress your Peddler project root and database backup, send it to another server and you're done.

Is Peddler officially supported by OpenCart?
--------------------------------------------

Peddler remains developed independently from OpenCart, both by its parent company Alto9.com and the maintainers.
