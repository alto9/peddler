.. _k8s:

Kubernetes deployment
=====================

With the same docker images we created for :ref:`single server deployment <local>`, we can launch an OpenCart platform on Kubernetes.

A word of warning: managing a Kubernetes platform is a fairly advanced endeavour. In this documentation, we assume familiarity with Kubernetes. Running an OpenCart platform with Peddler on a single server or in a Kubernetes cluster are two very different things. The local OpenCart install was designed such that users with no prior experience with system administration could still launch an OpenCart platform. It is *not* the case for the installation method outlined here.

Consider yourself warned :)

Requirements
------------

Version
~~~~~~~

Peddler was tested with server version 1.14.1 and client 1.14.3.

Memory
~~~~~~

In the following, we assume you have access to a working Kubernetes cluster. `kubectl` should use your cluster configuration by default. To launch a cluster locally, you may try out Minikube. Just follow the `official installation instructions <https://kubernetes.io/docs/setup/minikube/>`_.

The Kubernetes cluster should have at least 4Gb of RAM on each node. When running Minikube, the virtual machine should have that much allocated memory. See below for an example with VirtualBox:

Ingress controller and SSL/TLS certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Caddy exposes a LoadBalancer service and SSL/TLS certificates are transparently generated at runtime.

Technical details
-----------------

Under the hood, Peddler wraps ``kubectl`` commands to interact with the cluster. The various commands called by Peddler are printed in the console, so that you can reproduce and modify them yourself.

Basically, the whole platform is described in manifest files stored in ``$(peddler config printroot)/env/k8s``. There is also a ``kustomization.yml`` file at the project root for `declarative application management <https://kubectl.docs.kubernetes.io/pages/app_management/apply.html>`_. This allows us to start and update resources with commands similar to ``kubectl apply -k $(peddler config printroot) --selector=...`` (see the ``kubectl apply`` `official documentation <https://kubectl.docs.kubernetes.io/pages/app_management/apply.html>`_).

The other benefit of ``kubectl apply`` is that it allows you to customise the Kubernetes resources as much as you want. For instance, the default Peddler configuration can be extended by a ``kustomization.yml`` file stored in ``$(peddler config printroot)/env-custom/`` and which would start with::

    apiVersion: kustomize.config.k8s.io/v1beta1
    kind: Kustomization
    bases:
    - ../env/
    ...

To learn more about "kustomizations", refer to the `official documentation <https://kubectl.docs.kubernetes.io/pages/app_customization/introduction.html>`__.

Quickstart
----------

Launch the platform on Kubernetes in one command::

    peddler k8s quickstart

All Kubernetes resources are associated to the "opencart" namespace. If you don't see anything in the Kubernetes dashboard, you are probably looking at the wrong namespace... 😉

.. image:: img/k8s-dashboard.png
    :alt: Kubernetes dashboard ("opencart" namespace)

The same ``peddler k8s quickstart`` command can be used to upgrade the cluster to the latest version.

Other commands
--------------

As with the :ref:`local installation <local>`, there are multiple commands to run operations on your OpenCart platform. To view those commands, run::

    peddler k8s -h

In particular, the `peddler k8s start` command restarts and reconfigures all services by running ``kubectl apply``. That means that you can delete containers, deployments or just any other kind of resources, and Peddler will re-create them automatically. You should just beware of not deleting any persistent data stored in persistent volume claims. For instance, to restart from a "blank slate", run::

    peddler k8s stop
    peddler k8s start

All non-persisting data will be deleted, and then re-created.