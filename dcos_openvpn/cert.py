
from __future__ import absolute_import, print_function

import logging
import os
import re
import subprocess

def key_path(name):
    return os.path.join(os.environ.get("EASYRSA_PKI", ""),
        "private/{0}.key".format(name))

def req_path(name):
    return os.path.join(os.environ.get("EASYRSA_PKI", ""),
        "reqs/{0}.req".format(name))

def issued_path(name):
    return os.path.join(os.environ.get("EASYRSA_PKI", ""),
        "issued/{0}.crt".format(name))

def generate(name):
    subprocess.check_call(
        "/dcos/bin/easyrsa build-client-full {0} nopass".format(
            name), shell=True)

def upload(name):
    subprocess.check_call(
        '$ZKCLI --run-once "cp file://{0} $ZKPATH/{1}" $ZKURL'.format(
            key_path(name), os.path.relpath(key_path(name),
                os.environ.get("CONFIG_LOCATION"))), shell=True)

def output(name):
    loc = subprocess.check_output("/dcos/bin/run.bash get_location", shell=True)
    return re.sub("remote .*", loc, subprocess.check_output(
        "ovpn_getclient {0}".format(name), shell=True))


def remove(name):
    subprocess.check_call(
        '$ZKCLI --run-once "rm $ZKPATH/{0}" $ZKURL'.format(
            os.path.relpath(key_path(name),
                os.environ.get("CONFIG_LOCATION"))), shell=True)
    p = subprocess.Popen(
        ["/dcos/bin/easyrsa", "--batch", "revoke", name], stdin=subprocess.PIPE)
    p.communicate(input=b'nopass\n')[0]
    os.remove(req_path(name))
    os.remove(issued_path(name))
    os.remove(key_path(name))
