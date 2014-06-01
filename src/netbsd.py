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
from . import linux
from . import log
from . import path
from . import util

def get_blkdev_info(fd):
    try:
        DIOCGDINFO = 0x41946465
        b = fcntl.ioctl(fd, DIOCGDINFO,
            filebytes.SPACE * 1000) # struct disklabel
        d_typename   = b[8:24]
        d_secsize    = util.host_to_int(b[40:44])
        d_nsectors   = util.host_to_int(b[44:48])
        d_ntracks    = util.host_to_int(b[48:52])
        d_ncylinders = util.host_to_int(b[52:56])
        d_secperunit = util.host_to_int(b[60:64])
        x = d_nsectors * d_ntracks * d_ncylinders
        if d_secperunit > x:
            x = d_secperunit
        return x * d_secsize, d_secsize, d_typename
    except Exception, e:
        log.error("ioctl(%s, DIOCGDINFO) failed, %s" % (fd.name, e))
        raise

def get_total_ram():
    """
    [root@netbsd ~]# sysctl hw.physmem
    hw.physmem = 393039872
    """
    try:
        s = util.execute("sysctl", "hw.physmem")[0]
        x = s.split()[-1]
        return int(x)
    except Exception, e:
        log.error(e)
        return linux.get_total_ram()

def get_free_ram():
    return linux.get_free_ram()

def is_blkdev(f):
    return path.is_blkdev(f)

def has_mremap():
    return True
