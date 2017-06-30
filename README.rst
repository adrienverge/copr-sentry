Sentry
======

This repository provides unofficial packages of Sentry for CentOS 7. Sentry is
installed in a virtualenv using pip, and a systemd service is created for easy
management.

The packages are available at:

https://copr.fedorainfracloud.org/coprs/adrienverge/sentry/

Install
-------

.. code:: shell

 sudo yum copr enable adrienverge/sentry
 sudo yum install sentry

Hack
----

.. code:: shell

 rpmbuild -bs sentry.spec
 mock -r epel-7-x86_64 rebuild ~/rpmbuild/SRPMS/sentry-8*.src.rpm