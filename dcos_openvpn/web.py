
from __future__ import absolute_import, print_function

import json

from flask import Flask
from flask import request

from . import scheduler

app = Flask(__name__)

@app.route("/status")
def status():
    return "ok"
