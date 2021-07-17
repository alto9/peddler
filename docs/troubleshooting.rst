.. _troubleshooting:

Troubleshooting
===============

What should you do if you have a problem?

1. Read the error logs that appear in the console. When running a single server platform as daemon, you can view the logs with the ``peddler local logs`` command. (see :ref:`logging` below)
2. Check if your problem already has a solution right here in the :ref:`troubleshooting` section.
3. Search for your problem in the `open and closed Github issues <https://github.com/alto9/peddler/issues?utf8=%E2%9C%93&q=is%3Aissue>`_.

Do you need professional assistance with your peddler-managed OpenCart platform? Alto9 offers online support as part of its `Kubernetes Support Program <https://alto9.com/>`__.

.. _logging:

Logging
-------

.. note::
    Logs are of paramount importance for debugging Peddler. 

         peddler local logs --tail=100 -f

To view the logs from all containers use the ``peddler local logs`` command, which was modeled on the standard `docker-compose logs <https://docs.docker.com/compose/reference/logs/>`_ command::

    peddler local logs --follow

To view the logs from just one container, for instance the OpenCart server::

    peddler local logs --follow opencart

The last commands produce the logs since the creation of the containers, which can be a lot. Similar to a ``tail -f``, you can run::

    peddler local logs --tail=0 -f

If you'd rather use a graphical user interface for viewing logs, you are encouraged to try out :ref:`Portainer <portainer>`.