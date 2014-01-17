#! /bin/bash

# Builds TopicMob web to go. Outputs the source package names.
# eg:
# $ ./topicmob/ops/scripts/build.sh --novenv --nopush --nosign > build.out

PYTHON=/usr/local/bin/python3.4
PYENV=~/py3.4
SETUPTOOLS=setuptools-0.9.6
PIP=pip-1.3.1

DIR=$( cd "$( dirname "$0" )" && pwd )
PARENT=$(readlink -e $DIR/../../../..)

echoerr() { echo "$@" 1>&2; }

cd $PARENT/tallywallet-common

echoerr "Installing package to $PYENV ..."
$PYENV/bin/python3 setup.py install > /dev/null

echoerr "Building project documentation ..."
$PYENV/bin/sphinx-build -b html \
    -c $PARENT/tallywallet-common/tallywallet/common/doc \
    $PARENT/tallywallet-common/tallywallet/common/doc \
    $PARENT/tallywallet-common/tallywallet/common/doc/html

# For Python hosted, zip up html
