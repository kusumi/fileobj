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

from __future__ import with_statement
import os

from . import log
from . import path
from . import util

class KernelError (util.GenericError):
    pass

def get_kernel_module():
    if is_linux():
        from . import linux
        return linux
    elif is_netbsd():
        from . import netbsd
        return netbsd
    elif is_openbsd():
        from . import openbsd
        return openbsd
    elif is_freebsd():
        from . import freebsd
        return freebsd
    elif is_dragonflybsd():
        from . import dragonflybsd
        return dragonflybsd

_system = util.get_system_string()
def is_linux():
    return _system == "Linux"
def is_netbsd():
    return _system == "NetBSD"
def is_openbsd():
    return _system == "OpenBSD"
def is_freebsd():
    return _system == "FreeBSD"
def is_dragonflybsd():
    return _system == "DragonFly" # No "BSD"

def get_blkdev_info(f):
    f = path.get_path(f)
    o = get_kernel_module()
    if not o:
        raise KernelError(
            "Failed to get kernel module for %s" % _system)
    if not o.is_blkdev(f):
        raise KernelError("%s is not blkdev" % f)

    # NetBSD fails with -EBUSY if already opened
    with util.open_file(f) as fd:
        l = o.get_blkdev_info(fd)
        b = util.Namespace(name=f, size=l[0], sector_size=l[1], label=l[2])
        log.info("Block device %s (%s, %s, %s)" % (
            b.name,
            util.get_size_string(b.size),
            util.get_size_string(b.sector_size),
            repr(b.label)))
        return b

def get_buffer_size(f):
    # caller need to catch exception
    if is_blkdev(f):
        return get_blkdev_info(f).size
    if not os.path.isfile(f):
        return -1
    ret = get_file_size(f)
    if ret > 0:
        return ret

    with util.open_file(f) as fd: # binary
        if util.set_non_blocking(fd) == -1:
            return -1
        try:
            ret = fd.read()
        except IOError: # Python 2.x raises exception
            return -1
        if ret is None: # Python 3.x returns None
            return -1
        else: # success
            return len(ret)

def get_buffer_size_safe(f):
    # return -1 if exception is raised
    try:
        return get_buffer_size(f)
    except Exception:
        return -1

def get_file_size(f):
    if os.path.isfile(f):
        return os.stat(f).st_size
    else:
        return -1

def get_total_ram():
    o = get_kernel_module()
    if o:
        return o.get_total_ram()
    else:
        return -1

def get_free_ram():
    o = get_kernel_module()
    if o:
        return o.get_free_ram()
    else:
        return -1

def is_blkdev(f):
    """Return True if block device is supported"""
    o = get_kernel_module()
    if o:
        return o.is_blkdev(f)
    else:
        return False

def has_mremap():
    """Return True if mremap(2) is supported"""
    o = get_kernel_module()
    if o:
        return o.has_mremap()
    else:
        return False
