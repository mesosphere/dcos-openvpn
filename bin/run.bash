#!/bin/bash

CA_PASS=${CA_PASS:="nopass"}
CA_CN=${CA_CN:="openvpn.dcos"}
ZKPATH=${ZKPATH:="/dcos-vpn"}
ZKCLI=${ZKCLI:="zk-shell"}
ZKURL=${ZKURL:="127.0.0.1:2181"}
CONFIG_LOCATION=${CONFIG_LOCATION:="/etc/openvpn"}

MESOS_HOSTNAME=${MESOS_HOSTNAME:=127.0.0.1}
PORT0=${PORT0:=6000}

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
