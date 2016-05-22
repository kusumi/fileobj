#!/bin/bash

if [ ! -f ./script/installman.sh ]; then
	echo "### Invalid directory `pwd`"
	exit 1
fi

MANDIR=/usr/share/man/man1
if [ ! -d ${MANDIR} ]; then
	echo "### No such directory ${MANDIR}"
	exit 1
fi

TEMPFILE=`mktemp`
cat ./script/fileobj.1 | gzip -9 -n > ${TEMPFILE}
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
