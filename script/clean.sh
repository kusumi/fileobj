#!/bin/bash

if [ ! -f ./script/clean.sh ]; then
	echo "### Invalid directory `pwd`"
	exit 1
fi

PYTHON=$1
if [ "${PYTHON}" = "" ]; then
	PYTHON=python
fi

which ${PYTHON} >/dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "### ${PYTHON} does not exist"
	exit 1
fi

${PYTHON} ./setup.py clean --all
if [ $? -ne 0 ]; then
	echo "### Failed to clean"
	exit 1
fi
