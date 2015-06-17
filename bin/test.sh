#!/bin/bash -e

CA_PASS="asdf" CA_CN="openvpn.dcos" MESOS_HOSTNAME=127.0.0.1 PORT0=6000 bin/run.bash

# BASEDIR=`dirname $0`/..

# cd $BASEDIR
# $BASEDIR/env/bin/tox
