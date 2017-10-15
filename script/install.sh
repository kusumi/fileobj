#!/bin/bash

if [ ! -f ./script/install.sh ]; then
	echo "### Invalid directory `pwd`"
	exit 1
fi

MANDIR_LOCAL=/usr/local/share/man/man1
MANDIR_SYSTEM=/usr/share/man/man1

if [ ! -d ${MANDIR_LOCAL} ]; then
	if [ ! -d ${MANDIR_SYSTEM} ]; then
		echo "### Neither ${MANDIR_LOCAL} nor ${MANDIR_SYSTEM} exists"
		exit 1
	else
		MANDIR=${MANDIR_SYSTEM}
	fi
else
	MANDIR=${MANDIR_LOCAL}
fi

TEMPFILE=`mktemp`
cat ./doc/fileobj.1 | gzip -9 -n > ${TEMPFILE}
if [ $? -ne 0 ]; then
	echo "### Failed to gzip manpage"
	exit 1
fi

install -m 644 ${TEMPFILE} ${MANDIR}/fileobj.1.gz
if [ $? -ne 0 ]; then
	echo "### Failed to install manpage"
	exit 1
fi

file ${MANDIR}/fileobj.1.gz
rm ${TEMPFILE}
