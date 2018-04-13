#!/bin/sh

# Copyright (c) 2016, Tomohiro Kusumi
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

if [ ! -f ./doc/fileobj.1 ]; then
	echo "Missing ./doc/fileobj.1"
	exit 1
fi

MANDIR_USER=$1
MANDIR_LOCAL=/usr/local/share/man/man1 # default
MANDIR_SYSTEM=/usr/share/man/man1

if [ "${MANDIR_USER}" != "" ]; then
	if [ -d ${MANDIR_USER} ]; then
		MANDIR=${MANDIR_USER}
	else
		echo "No such directory ${MANDIR_USER}"
		exit 1
	fi
elif [ -d ${MANDIR_LOCAL} ]; then
	MANDIR=${MANDIR_LOCAL}
elif [ -d ${MANDIR_SYSTEM} ]; then
	MANDIR=${MANDIR_SYSTEM}
else
	echo "Missing target directory ${MANDIR_LOCAL} or ${MANDIR_SYSTEM}"
	exit 1
fi

UNAME=`uname`
case "${UNAME}" in
	Linux | *BSD | DragonFly | CYGWIN*)
		if [ -f ./doc/fileobj.1.gz ]; then
			echo "./doc/fileobj.1.gz exists"
			exit 1
		fi
		cat ./doc/fileobj.1 | gzip -9 -n > ./doc/fileobj.1.gz
		if [ $? -ne 0 ]; then
			echo "Failed to gzip manpage"
			exit 1
		fi
		install -m 644 ./doc/fileobj.1.gz ${MANDIR}/fileobj.1.gz
		if [ $? -ne 0 ]; then
			echo "Failed to install manpage"
			exit 1
		fi
		file ${MANDIR}/fileobj.1.gz
		rm ./doc/fileobj.1.gz
		;;
	Darwin)
		install -m 644 ./doc/fileobj.1 ${MANDIR}/fileobj.1
		if [ $? -ne 0 ]; then
			echo "Failed to install manpage"
			exit 1
		fi
		file ${MANDIR}/fileobj.1
		;;
	SunOS)
		install -m 644 -f ${MANDIR} ./doc/fileobj.1
		if [ $? -ne 0 ]; then
			echo "Failed to install manpage"
			exit 1
		fi
		file ${MANDIR}/fileobj.1
		;;
	*)
		echo "No manpage available for ${UNAME}" # XXX
		;;
esac
