"""Manage OpenVPN Certificates and Config

Usage:
    dcos openvpn --help
    dcos openvpn --info
    dcos openvpn --version
    dcos openvpn <command> [options] [<arguments>...]
    dcos opennvpn config <config-name>

Commands:
    config <config-name>

Options:
    --help                  Show this screen
    --info                  Show info
    --version               Show version
"""

from __future__ import absolute_import, print_function

import docopt
import cmd

import dcos_openvpn
import dcos_openvpn.config

class Dispatch(cmd.Cmd):


def dispatch(args):


def main():
    args = docopt.docopt(
        __doc__,
        version='dcos-openvpn version {}'.format(
            dcos_openvpn.__version__), help=False)

    if args['--info']:
        print(__doc__.split('\n')[0])
    else:
        print(__doc__)
        return 1

    return 0
