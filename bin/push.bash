#!/bin/bash -x

# Shell lint tool: http://www.shellcheck.net
set -o errexit -o nounset -o pipefail

function usage {
cat <<USAGE
 USAGE: $(basename "$0")

  This script does things.
USAGE
}

#: ${REQUIRED_ENV_VAR:?"ERROR: REQUIRED_ENV_VAR must be set"}

function globals {
  export PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

  export CA_PASS=${CA_PASS:="nopass"}
  export CA_CN=${CA_CN:="openvpn.dcos"}
  export ZKPATH=${ZKPATH:="/dcos-vpn"}
  export ZKCLI=${ZKCLI:="zk-shell"}
  export ZKURL=${ZKURL:="master.mesos:2181"}
  export CONFIG_LOCATION=${CONFIG_LOCATION:="/etc/openvpn"}

  export HOST=${HOST:=127.0.0.1}
  export PORT0=${PORT0:=6000}

  export IMAGE=${IMAGE:="thomasr/dcos-openvpn"}
}; globals

for i in "$@"
do
  case "$i" in                                      # Munging globals, beware
    -h|--help)                usage                        ;;
    -c)                       conf="$2"          ; shift 2 ;;
    -v)                       verbose=true       ; shift 1 ;;
    --)                       break                        ;;
    *)                        # unknown option             ;;
  esac
done

function main {
  local version=$(($(cat version)+1))
  echo $version > version
  docker build -t thomasr/dcos-openvpn:$version .
  docker push thomasr/dcos-openvpn:$version
  cat marathon.json | \
    sed -i.bak "s/dcos-openvpn\:[0-9]\+/dcos-openvpn\:$version/g" marathon.json
}

function logged {
  exec 1> >(logger -p user.info -t "$name[$$]")
  exec 2> >(logger -p user.notice -t "$name[$$]")
  "$@"
}

function msg { out "$*" >&2 ;}
function err { local x=$? ; msg "$*" ; return $(( x == 0 ? 1 : x )) ;}
function out { printf '%s\n' "$*" ;}

if [[ ${1:-} ]] && declare -F | cut -d' ' -f3 | fgrep -qx -- "${1:-}"
then "$@"
else main "$@"
fi
