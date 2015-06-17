#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

source $DIR/test_env.sh

bin/run.bash

# BASEDIR=`dirname $0`/..

# cd $BASEDIR
# $BASEDIR/env/bin/tox
