
from __future__ import absolute_import, print_function

import logging
import json
import subprocess

from flask import Flask
from flask import request

from . import scheduler

app = Flask(__name__)

@app.route("/status")
def status():
    return "ok"

@app.route("/client", methods=["POST"])
def create_client():
    logging.info(request.args)
    # XXX - check that the arg is there, error if not
    # XXX - validate the arg to make sure it isn't an issue
    # XXX - throw an intelligent error if the client already exists
    subprocess.check_call(
        "/dcos/bin/easyrsa build-client-full {0} nopass".format(
            request.form.get("name")), shell=True)

    return subprocess.check_output(
        "ovpn_getclient {0}".format(request.form.get("name")), shell=True)

@app.route("/client/<name>", methods=["DELETE"])
def remove_client():
    pass
