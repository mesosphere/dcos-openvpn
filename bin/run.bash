#!/bin/bash

ZKPATH="/dcos-vpn"
ZKCLI="zk-shell"
ZKURL="127.0.0.1:2181"
CONFIG_LOCATION="/etc/openvpn"

run_command() {
  $ZKCLI --run-once "$1" $ZKURL 2>&1
  return $?
}

build_configuration() {
  ovpn_genconfig -u udp://$CA_CN
  (echo $CA_CN) | PATH=/dcos/bin:$PATH ovpn_initpki
}

upload_files() {
  ls $CONFIG_LOCATION/openvpn.conf || build_configuration

  for fname in $(find $CONFIG_LOCATION -not -type d); do
    local zk_location=$(echo $fname | sed 's|'$CONFIG_LOCATION'/|/|')
    run_command "cp file://$fname $ZKPATH$zk_location"
  done
}

(run_command "ls $ZKPATH") || upload_files

python -m dcos_openvpn.main
