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
import sys

from . import linux
from . import log
from . import path
from . import util

def get_blkdev_info(fd):
    try:
        d = {   "DIOCGSECTORSIZE" : 0x40046480,
                "DIOCGMEDIASIZE"  : 0x40086481,
                "DIOCGIDENT"      : 0x41006489, }
        s = "DIOCGSECTORSIZE"
        sector_size = ioctl(fd, d[s])
        s = "DIOCGMEDIASIZE"
        size = ioctl(fd, d[s])
        s = "DIOCGIDENT"
        b = fcntl.ioctl(fd, d[s], ' ' * 256) # DISK_IDENT_SIZE
        label = b.strip("\x00")
        return size, sector_size, label
    except Exception:
        e = sys.exc_info()[1]
        log.error("ioctl(%s, %s) failed, %s" % (fd.name, s, e))
        raise

def ioctl(fd, n):
    b = fcntl.ioctl(fd, n, ' ' * 8)
    b = b.replace(' ', '\x00')
    return util.host_to_int(b)

def get_total_ram():
    """
    [root@freebsd ~]# sysctl hw.physmem
    hw.physmem: 1056395264
    """
    try:
        s = util.run_subprocess("sysctl", "hw.physmem")[0]
        x = s.split()[-1]
        return int(x)
    except Exception:
        e = sys.exc_info()[1]
        log.error(e)
        return linux.get_total_ram()

def get_free_ram():
    return linux.get_free_ram()

def is_blkdev(f):
    return path.is_blkdev(f) or path.is_chrdev(f)

def has_mremap():
    return False
