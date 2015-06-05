#!/bin/bash

# ZKPATH="/dcos-vpn"
# ZKCLI="/opt/mesosphere/bin/zkCli.sh"
# ZKHOST="leader.mesos:2181"
ZKPATH="/dcos-vpn"
ZKCLI="zk-shell"
ZKHOST="127.0.0.1:2181"
CONFIG_LOCATION="/tmp/openvpn"

run_command() {
  echo $($ZKCLI -server $ZKHOST $1 2>&1)
}

upload_file() {
  local zk_location=$(echo $1 | sed 's|'$CONFIG_LOCATION'/|/|')
  zk-shell --run-once "cp file://$1 zk://$ZKHOST$ZKPATH$zk_location"
}

if $(run_command "stat $ZKPATH" | grep -q "does not exist") ; then

  for fname in $(find $CONFIG_LOCATION -not -type d); do
    upload_file $fname
  done

fi
