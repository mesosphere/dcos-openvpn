#!/bin/bash

# Shell lint tool: http://www.shellcheck.net
set -o errexit -o nounset -o pipefail

function usage {
cat <<USAGE
 USAGE: $(basename "$0") server|admin

  This script runs the openvpn server or admin interface. Both need
  to be deployed to your cluster. The server is the endpoint clients
  connect to, where admin runs a web api to create users in ZK.

USAGE
}

#: ${REQUIRED_ENV_VAR:?"ERROR: REQUIRED_ENV_VAR must be set"}

function globals {

  export CA_PASS=${CA_PASS:="nopass"}
  export CA_CN=${CA_CN:="openvpn.dcos"}
  export ZKPATH=${ZKPATH:="/dcos-vpn"}
  export ZKCLI=${ZKCLI:="zk-shell"}
  export ZKURL=${ZKURL:="master.mesos:2181"}
  export CONFIG_LOCATION=${CONFIG_LOCATION:="/etc/openvpn"}

  export HOST=${HOST:=127.0.0.1}
  export PORT0=${PORT0:=6000}

}; globals

for i in "$@"
do
  case "$i" in                                      # Munging globals, beware
    -h|--help)                usage              ; exit 0  ;;
    -c)                       conf="$2"          ; shift 2 ;;
    -v)                       verbose=true       ; shift 1 ;;
    --)                       break                        ;;
    *)                        # unknown option             ;;
  esac
done

function get_location {
  echo $(run_command "get $ZKPATH/location.conf")
}

function run_command {
  $ZKCLI --run-once "$1" $ZKURL 2>&1
  return $?
}

function build_configuration {
  ovpn_genconfig -u udp://$CA_CN
  (echo $CA_CN) | PATH=/dcos/bin:$PATH ovpn_initpki
}

function upload_files {
  ls $CONFIG_LOCATION/openvpn.conf || build_configuration

  for fname in $(find $CONFIG_LOCATION -not -type d); do
    local zk_location=$(echo $fname | sed 's|'$CONFIG_LOCATION'/|/|')
    run_command "cp file://$fname $ZKPATH$zk_location"
  done
}

function admin {
  if (run_command "ls $ZKPATH"); then
    download_files
  else
    upload_files
  fi

  exec python -m dcos_openvpn.main
}

function download_files {
  for fname in $(run_command "find $ZKPATH"); do
    local sub_path=$(echo $fname | cut -d/ -f3-)

    # If the sub_path is empty, there's no reason to copy
    [[ -z $sub_path ]] && continue

    if [ "$sub_path" == "Failed" ]; then
      err "Unable to get data from $ZKURL$ZKPATH. Check your zookeeper."
    fi

    local fs_path=$CONFIG_LOCATION/$sub_path
    run_command "cp $fname file://$fs_path"
    # Directories are copied as empty files, remove them so that the
    # subsequent copies actually work.
    [ -s $fs_path ] || rm $fs_path
  done
}

function set_public_location {
  local loc=$ZKPATH/location.conf
  source $OPENVPN/ovpn_env.sh
  (run_command "ls $loc") || (run_command "create $loc ''")

  run_command "set $loc \"remote $(wget -O - -U curl ifconfig.me) $PORT0 $OVPN_PROTO\""
}

function server {
  env

  download_files
  set_public_location

  mkdir "$OPENVPN/ccd"
  exec ovpn_run
}

function logged {
  exec 1> >(logger -p user.info -t "$name[$$]")
  exec 2> >(logger -p user.notice -t "$name[$$]")
  "$@"
}

function msg { out "$*" >&2 ;}
function err { local x=$? ; msg "$*" ; return $(( x == 0 ? 1 : x )) ;}
function out { printf '%s\n' "$*" ;}


case "$@" in
  server) server ;;
  admin)  admin  ;;
  get_location) get_location ;;
  *)      usage;  exit 1 ;;
esac
