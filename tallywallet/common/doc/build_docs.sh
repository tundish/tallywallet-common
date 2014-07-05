#! /bin/bash

# Builds TopicMob web to go. Outputs the source package names.
# eg:
# $ ./tallywallet/common/doc/build_docs.sh

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

REL=`$PYENV/bin/python3 setup.py --version`

# http://pythonhosted.org/tallywallet-common
cd $PARENT/tallywallet-common/tallywallet/common/doc/html
zip -r tallywallet-common-$REL-doc-html.zip *
cd -
