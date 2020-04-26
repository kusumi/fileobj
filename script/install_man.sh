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

MANDIR=$1
MANNAME=fileobj.1
GZNAME=fileobj.1.gz

if [ ! -f ./doc/${MANNAME} ]; then
	echo "Missing ./doc/${MANNAME}"
	exit 1
fi

if [ "${MANDIR}" = "" ]; then
	echo "No directory specified"
	exit 1
elif [ ! -d "${MANDIR}" ]; then
	echo "No such directory ${MANDIR}"
	exit 1
fi

UNAME=`uname`
case "${UNAME}" in
	Linux | FreeBSD | DragonFly | CYGWIN*)
		if [ -f ./doc/${GZNAME} ]; then
			echo "Remove existing ./doc/${GZNAME}"
			rm ./doc/${GZNAME}
			exit 1
		fi
		cat ./doc/${MANNAME} | gzip -9 -n > ./doc/${GZNAME}
		if [ $? -ne 0 ]; then
			if [ -f ./doc/${GZNAME} ]; then
				rm ./doc/${GZNAME}
			fi
			echo "Failed to gzip man page"
			exit 1
		fi
		install -m 644 ./doc/${GZNAME} ${MANDIR}/${GZNAME}
		if [ $? -ne 0 ]; then
			if [ -f ./doc/${GZNAME} ]; then
				rm ./doc/${GZNAME}
			fi
			echo "Failed to install man page"
			exit 1
		fi
		file ${MANDIR}/${GZNAME}
		rm ./doc/${GZNAME}
		;;
	NetBSD | OpenBSD | Darwin)
		install -m 644 ./doc/${MANNAME} ${MANDIR}/${MANNAME}
		if [ $? -ne 0 ]; then
			echo "Failed to install man page"
			exit 1
		fi
		file ${MANDIR}/${MANNAME}
		;;
	SunOS)
		install -m 644 -f ${MANDIR} ./doc/${MANNAME}
		if [ $? -ne 0 ]; then
			echo "Failed to install man page"
			exit 1
		fi
		file ${MANDIR}/${MANNAME}
		;;
	*)
		echo "Not installing man page for ${UNAME}"
		;;
esac
