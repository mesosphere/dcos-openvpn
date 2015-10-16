
from __future__ import absolute_import, print_function

import argparse
import logging
import os
import sys
import time
import threading

from . import web

OPTIONAL_ENV = [
    "MESOS_CONFIG",
    "IMAGE"
]

REQUIRED_ENV = [
    "HOST",
    "EASYRSA_PKI"
]

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    web.app.logger.addHandler(root)


def check_env():
    stop = False

    for k in REQUIRED_ENV:
        if not k in os.environ:
            logging.error("missing required env: {0}".format(k))
            stop = True

    if stop:
        sys.exit(1)


def main():
    setup_logging()

    check_env()

    web.app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()
