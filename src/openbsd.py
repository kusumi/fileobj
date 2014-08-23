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

from . import libc
from . import log
from . import netbsd
from . import path
from . import setting
from . import util

PT_READ_I   = 1
PT_READ_D   = 2
PT_WRITE_I  = 4
PT_WRITE_D  = 5
PT_CONTINUE = 7
PT_KILL     = 8
PT_ATTACH   = 9
PT_DETACH   = 10

def get_blkdev_info(fd):
    return netbsd.get_blkdev_info(fd)

def get_total_ram():
    """
    [root@openbsd ~]# sysctl hw.physmem
    hw.physmem=1073266688
    """
    try:
        s = util.execute("sysctl", "hw.physmem")[0]
        x = s.split("=")[-1]
        return int(x)
    except Exception as e:
        log.error(e)
        return -1

def get_free_ram():
    return -1

def is_blkdev(f):
    return path.is_blkdev(f)

def is_blkdev_supported():
    return True

def has_mremap():
    return False

def has_pid(pid):
    return netbsd.has_pid(pid)

def get_pid_name(pid):
    return netbsd.get_pid_name(pid)

def is_pid_path_supported():
    return setting.use_vm_non_linux and libc.has_ptrace()

def ptrace_peektext(pid, addr):
    return libc.ptrace(PT_READ_I, pid, addr, None)

def ptrace_peekdata(pid, addr):
    return libc.ptrace(PT_READ_D, pid, addr, None)

def ptrace_poketext(pid, addr, data):
    return libc.ptrace(PT_WRITE_I, pid, addr, data)

def ptrace_pokedata(pid, addr, data):
    return libc.ptrace(PT_WRITE_D, pid, addr, data)

def ptrace_cont(pid):
    return libc.ptrace(PT_CONTINUE, pid, 1, 0)

def ptrace_kill(pid):
    return libc.ptrace(PT_KILL, pid, None, None)

def ptrace_attach(pid):
    return libc.ptrace(PT_ATTACH, pid, None, None)

def ptrace_detach(pid):
    return libc.ptrace(PT_DETACH, pid, 1, 0)

ptrace_peek = ptrace_peektext
ptrace_poke = ptrace_poketext

def get_ptrace_word_size():
    return libc.get_ptrace_data_size()

def init():
    libc.init_ptrace("int")
