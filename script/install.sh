#!/bin/bash

if [ ! -f ./script/install.sh ]; then
	echo "### Invalid directory `pwd`"
	exit 1
fi
if [ ! -f ./doc/fileobj.1 ]; then
	echo "### Missing ./doc/fileobj.1"
	exit 1
fi

MANDIR_LOCAL=/usr/local/share/man/man1
MANDIR_SYSTEM=/usr/share/man/man1

if [ ! -d ${MANDIR_LOCAL} ]; then
	if [ ! -d ${MANDIR_SYSTEM} ]; then
		echo "### Missing target directory ${MANDIR_LOCAL} or ${MANDIR_SYSTEM}"
		exit 1
	else
		MANDIR=${MANDIR_SYSTEM}
	fi
else
	MANDIR=${MANDIR_LOCAL}
fi

case "`uname`" in
	Linux | *BSD | DragonFly | CYGWIN*)
		cat ./doc/fileobj.1 | gzip -9 -n > ./doc/fileobj.1.gz
		if [ $? -ne 0 ]; then
			echo "### Failed to gzip manpage"
			exit 1
		fi
		install -m 644 ./doc/fileobj.1.gz ${MANDIR}/fileobj.1.gz
		if [ $? -ne 0 ]; then
			echo "### Failed to install manpage"
			exit 1
		fi
		file ${MANDIR}/fileobj.1.gz
		rm ./doc/fileobj.1.gz
		;;
	SunOS)
		install -m 644 -f ${MANDIR} ./doc/fileobj.1
		if [ $? -ne 0 ]; then
			echo "### Failed to install manpage"
			exit 1
		fi
		file ${MANDIR}/fileobj.1
		;;
	*)
		echo "No manpage available" # XXX
		;;
esac
