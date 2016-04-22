from __future__ import absolute_import, print_function

import os
import re
import subprocess


def build_path(directory, filename):
    return os.path.join(
        os.environ.get("EASYRSA_PKI", ""),
        "{0}/{1}".format(directory, filename)
    )


def generate(name):
    subprocess.check_call(
        "/dcos/bin/easyrsa build-client-full {0} nopass".format(
            name), shell=True)


def upload(name):
    subprocess.check_call(
        '$ZKCLI --run-once "cp file://{0} $ZKPATH/{1}" $ZKURL'.format(
            build_path("private", "{0}.key".format(name)),
            os.path.relpath(
                build_path("private", "{0}.key".format(name)),
                os.environ.get("CONFIG_LOCATION")
            )
        ),
        shell=True
    )


def output(name):
    loc = subprocess.check_output('$ZKCLI --run-once "get $ZKPATH/location.conf" $ZKURL', shell=True)
    return re.sub(
        "remote .*",
        loc,
        subprocess.check_output("ovpn_getclient {0}".format(name), shell=True)
    )


def remove(name):
    subprocess.check_call(
        '$ZKCLI --run-once "rm $ZKPATH/{0}" $ZKURL'.format(
            os.path.relpath(
                build_path("private", "{0}.key".format(name)),
                os.environ.get("CONFIG_LOCATION")
            )
        ),
        shell=True
    )
    subprocess.check_output(
        "/dcos/bin/easyrsa --batch revoke {0}".format(name).split(),
        input=b'nopass\n'
    )

    os.remove(build_path("private", "{0}.key".format(name)))
    os.remove(build_path("reqs", "{0}.req".format(name)))
    os.remove(build_path("issued", "{0}.crt".format(name)))
