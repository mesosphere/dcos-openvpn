from __future__ import print_function

import os
import sys

import requests
import toml

from dcos import marathon, util

def get_spark_webui():
    base_url = util.get_config().get('core.dcos_url')
    return base_url + '/service/spark/'

def get_spark_dispatcher():
    dcos_spark_url = os.getenv("DCOS_SPARK_URL")
    if dcos_spark_url is not None:
        return dcos_spark_url

    base_url = util.get_config().get('core.dcos_url')
    # Remove http:// prefix.
    return base_url[7:] + '/service/sparkcli/'
