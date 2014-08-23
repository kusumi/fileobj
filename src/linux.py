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
import re

from . import filebytes
from . import fs
from . import libc
from . import log
from . import path
from . import util

PTRACE_PEEKTEXT = 1
PTRACE_PEEKDATA = 2
PTRACE_POKETEXT = 4
PTRACE_POKEDATA = 5
PTRACE_CONT     = 7
PTRACE_KILL     = 8
PTRACE_ATTACH   = 16
PTRACE_DETACH   = 17

def get_blkdev_info(fd):
    try:
        d = {   "BLKSSZGET"  : 0x1268,
                "BLKGETSIZE" : 0x1260, }
        s = "BLKSSZGET"
        sector_size = util.host_to_int(
            fcntl.ioctl(fd, d[s], filebytes.pad(4)))
        s = "BLKGETSIZE"
        size = util.host_to_int(
            fcntl.ioctl(fd, d[s], filebytes.pad(8)))
        size <<= 9
        return size, sector_size, ''
    except Exception, e:
        log.error("ioctl(%s, %s) failed, %s" % (
            fd.name, s, e))
        raise

def get_total_ram():
    return get_meminfo("MemTotal")

def get_free_ram():
    return get_meminfo("MemFree")

def get_meminfo(s):
    f = fs.get_procfs_entry("meminfo")
    if not f:
        return -1
    try:
        s = util.escape_regex_pattern(s)
        for l in util.open_text_file(f):
            m = re.match(r"^%s.*\s+(\d+)" % s, l)
            if m:
                return int(m.group(1)) * util.KiB
    except Exception, e:
        log.error(e)
    return -1

def is_blkdev(f):
    return path.is_blkdev(f)

def is_blkdev_supported():
    return True

def has_mremap():
    return True

def has_pid(pid):
    return fs.has_pid(pid) or util.has_pid(pid)

def get_pid_name(pid):
    # comm does not exist on older kernels
    ret = fs.get_pid_name(pid, "comm", "cmdline")
    if not ret:
        return util.get_pid_name(pid)
    else:
        return ret

def is_pid_path_supported():
    return libc.has_ptrace()

def ptrace_peektext(pid, addr):
    return libc.ptrace(PTRACE_PEEKTEXT, pid, addr, None)

def ptrace_peekdata(pid, addr):
    return libc.ptrace(PTRACE_PEEKDATA, pid, addr, None)

def ptrace_poketext(pid, addr, data):
    return libc.ptrace(PTRACE_POKETEXT, pid, addr, data)

def ptrace_pokedata(pid, addr, data):
    return libc.ptrace(PTRACE_POKEDATA, pid, addr, data)

def ptrace_cont(pid):
    return libc.ptrace(PTRACE_CONT, pid, None, None)

def ptrace_kill(pid):
    return libc.ptrace(PTRACE_KILL, pid, None, None)

def ptrace_attach(pid):
    return libc.ptrace(PTRACE_ATTACH, pid, None, None)

def ptrace_detach(pid):
    return libc.ptrace(PTRACE_DETACH, pid, None, None)

ptrace_peek = ptrace_peektext
ptrace_poke = ptrace_poketext

def get_ptrace_word_size():
    return libc.get_ptrace_data_size()

def init():
    libc.init_ptrace("long")
