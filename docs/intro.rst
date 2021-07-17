.. _intro:

Concepts
========

What is OpenCart?
-----------------

`OpenCart <https://opencart.com/>`_ is the best FREE and open-source eCommerce platform, backed by a great community. OpenCart comes with a fully customizable storefront where customers can buy your products, a plugin system for extensibility, and a few other components to provide more services to store-owners, customers and platform administrators.

Should I use OpenCart?
----------------------

OpenCart competitors include `Prestashop <https://www.prestashop.com/>`__, `osCommerce <https://www.oscommerce.com/Products>`__, `Zen Cart <https://www.zen-cart.com/content.php?2-FAQs-and-Tutorials&s=7d6f8bc78eed456cfa9c131a169109d3>`__, as well as many hosted, open and closed source alternatives - including with OpenCart themselves. OpenCart is the only open source e-commerce system that satisfies all following properties:

* Open source software to avoid vendor lock-in
* Scales well in all directions (number of users and products)
* Multiple extension points for comprehensive customization
* Modern, intuitive user interface to keep students engaged

Should I self-host OpenCart or rely on a hosting provider?
----------------------------------------------------------

Third-party OpenCart providers can provide you with custom, cloud-based shopping cart solution. However, the low cost usually comes at the expense of being on a shared infrastructure with other clients. This adds an element of risk, you are trusting the hosting provider to secure and segregate your store, your customers, their transations, everything. Simply put, being on a shared server increases the likelyhood that your store can go down through no fault of your own.

On the other hand, running OpenCart on your own servers, helps you maintain complete control and segregation of your store. Because you own your servers and data, you will always be able to migrate your platform, either to a different cloud provider or an OpenCart service provider. This is the true power of open source.

Should I use Peddler?
---------------------

Running software on premises is cheaper only if your management costs don't go through the roof. You do not want to hire a full-time devops team just for managing your e-commerce platform. This is why we created Peddler: to make it easy to run a state-of-the-art e-commerce platform without breaking the bank. Peddler makes it possible even to non-technical users to launch, manage and upgrade OpenCart at any scale. Should you choose at some point that Peddler is not the right solution for you, you always have an escape route: because Peddler is open source software, you can easily dump your data and switch to a different installation method. But we are confident you will not do that 😉

How does Peddler work, technically speaking?
--------------------------------------------

Peddler simplifies the deployment of OpenCart by:

1. Separating the configuration logic from the deployment platforms.
2. Running application processes in cleanly separated `docker containers <https://www.docker.com/resources/what-container>`_.
3. Providing user-friendly, reliable commands for common administration tasks, including upgrades and monitoring.

Because Docker containers are becoming an industry-wide standard, that means that with Peddler it becomes possible to run OpenCart anywhere: for now, Peddler supports deploying on a local server, with `docker-compose <https://docs.docker.com/compose/overview/>`_, and in a large cluster, with `Kubernetes <http://kubernetes.io/>`_. But in the future, Peddler may support other deployment platforms.

How does Peddler work?
----------------------

Peddler is a piece of software that takes care of exactly three things:

1. Project configuration: user-specific settings (such as secrets) are stored in a single ``config.yml`` file.
2. Template rendering: all the files that are necessary to run your platform are generated from a set of templates and the user-specific settings.
3. Command-line interface (CLI): frequently-used administration commands are gathered in a convenient, unified CLI.

You can experiment with Peddler very quickly: start by `installing <install>`_ Peddler. Then run::

    $ peddler config save --interactive

Then, to view the result of the above command::

    $ cd "$(peddler config printroot)"
    $ ls
    config.yml  env

The ``config.yml`` file contains your user-specific OpenCart settings (item #1 above). The ``env/`` folder contains the rendered templates which will be used to run your OpenCart platform (item #2). For instance, the ``env/local`` folder contains the ``docker-compose.yml`` file to run OpenCart locally.

The values from ``config.yml`` are used to generate the environment files in ``env/``. As a consequence, **every time the values from** ``config.yml`` **are modified, the environment must be regenerated** with ``peddler config save``..

Because the Peddler environment is generated entirely from the values in ``config.yml``, you can ``rm -rf`` the ``env/`` folder at any time and re-create it with ``peddler config save``. Another consequence is that **any manual change made to a file in** ``env/`` **will be overwritten by** ``peddler config save`` **commands**. Consider yourself warned!

You can now take advantage of the Peddler-powered CLI (item #3) to bootstrap your OpenCart platform::

    peddler local quickstart

Under the hood, Peddler simply runs ``docker-compose`` and ``docker`` commands to launch your platform. These commands are printed in the standard output, such that you are free to replicate the same behaviour by simply copy/pasting the same commands.

I'm ready, where do I start?
----------------------------

Right :ref:`here <gettingstarted>`!