
from __future__ import absolute_import, print_function

import logging
import os
import json
import re
import subprocess

from flask import Flask
from flask import request
from webargs import Arg
from webargs.flaskparser import use_args

from . import cert

app = Flask(__name__)

@app.route("/")
def root():
    return "OpenVPN running, to add users see: https://github.com/mesosphere/dcos-openvpn"

@app.route("/status")
def status():
    return "ok"

@app.route("/client", methods=["POST"])
@use_args({
    'name': Arg(str, required=True,
        validate=lambda x: bool(re.match("^[a-zA-Z\-0-9]+$", x)))
})
def create_client(args):
    if os.path.exists(cert.path(args.get("name"))):
        return json.dumps({ "type": "error", "msg": "client exists" }), 400

    cert.generate(args.get("name"))
    cert.upload(args.get("name"))

    return cert.output(args.get("name"))


@app.route("/client/<name>", methods=["DELETE"])
def remove_client(name):
    cert.remove(name)

    return json.dumps({ "type": "status", "msg": "success" })
