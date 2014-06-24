# Copyright (c) 2010-2014, TOMOHIRO KUSUMI
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

import fcntl

from . import filebytes
from . import freebsd
from . import log
from . import path
from . import setting
from . import util

# FIX_ME need to find a portable way regarding ioctl args,
# maybe time to use C bindings

def get_blkdev_info(fd):
    # ioctl value depends on sizeof(partinfo)
    if setting.dragonflybsd_sizeof_partinfo > 0:
        size = setting.dragonflybsd_sizeof_partinfo
    elif util.is_64bit_cpu(): # assume x86_64/gcc
        size = 144
    elif util.is_32bit_cpu(): # assume i386/gcc
        size = 136
    else: # forget it
        log.error("Unsupported processor %s" %
            util.get_cpu_string())
        return -1, -1, ''
    try:
        DIOCGPART = 0x40006468 | ((size & 0x1FFF) << 16)
        partinfo = filebytes.pad(size)
        b = fcntl.ioctl(fd, DIOCGPART, partinfo)
        size = util.host_to_int(b[8:16])
        sector_size = util.host_to_int(b[24:28])
        return size, sector_size, ''
    except Exception, e:
        log.error("ioctl(%s, %s) failed, %s" % (
            fd.name, "DIOCGPART", e))
        raise

def get_total_ram():
    """
    [root@dragonflybsd ~]# sysctl hw.physmem
    hw.physmem: 2117337088
    """
    return freebsd.get_total_ram()

def get_free_ram():
    return freebsd.get_free_ram()

def is_blkdev(f):
    o = path.Path(f)
    return o.is_blkdev or o.is_chrdev

def has_mremap():
    return False