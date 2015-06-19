
from __future__ import absolute_import, print_function

import logging
import os
import re
import subprocess

def path(name):
    return os.path.join(os.environ.get("EASYRSA_PKI", ""),
        "private/{0}.key".format(name))

def generate(name):
    subprocess.check_call(
        "/dcos/bin/easyrsa build-client-full {0} nopass".format(
            name), shell=True)

def upload(name):
    subprocess.check_call(
        '$ZKCLI --run-once "cp file://{0} $ZKPATH/{1}" $ZKURL'.format(
            path(name), os.path.relpath(path(name),
                os.environ.get("CONFIG_LOCATION"))), shell=True)

def output(name):
    loc = subprocess.check_output("/dcos/bin/run.bash get_location", shell=True)
    return re.sub("remote .*", loc, subprocess.check_output(
        "ovpn_getclient {0}".format(name), shell=True))


def remove(name):
    return os.remove(path(name))
