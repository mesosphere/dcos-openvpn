DCOS OpenVPN
===============

Setup
-----
#. Make sure you meet requirements for installing packages_
#. Clone git repo for the project::

    git clone git@github.com:mesosphere/dcos-openvpn.git

#. Make sure that you have virtualenv installed. If not type::

    pip install virtualenv

#. Create a virtualenv for the project::

    make env


Running Tests:
--------------

#. Run all of the tests::

    make test

#. List all of the supported test environments::

    env/bin/tox --listenvs

#. Run a specific set of tests::

    env/bin/tox -e <testenv>

.. _packages: https://packaging.python.org/en/latest/installing.html#installing-requirements
