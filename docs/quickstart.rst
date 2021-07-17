.. _quickstart:

Quickstart
----------------------------

1. `Download <https://github.com/alto9/peddler/releases>`_ the latest stable release of Peddler and place the ``peddler`` executable in your path. From the command line:

.. include:: download/binary.rst

Or:

    .. include:: download/pip.rst

2. Run ``peddler local quickstart``
3. You're done!

This is what happens when you run ``peddler local quickstart``:

1. You answer a few questions about the :ref:`configuration` of your OpenCart platform.
2. Configuration files are generated from templates.
3. Docker images are downloaded.
4. Docker containers are provisioned.
5. A full, production-ready OpenCart platform is run with docker-compose.

The whole procedure should require less than 10 minutes, on a server with a good bandwidth. Note that your host environment will not be affected in any way, since everything runs inside docker containers. Root access is not even necessary.

There's a lot more to Peddler than that! To learn more about what you can do with Peddler and OpenCart, check out the :ref:`whatnext` section. If the quickstart installation method above somehow didn't work for you, check out the :ref:`troubleshooting` guide.