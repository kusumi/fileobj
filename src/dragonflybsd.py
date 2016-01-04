# Copyright (c) 2010-2016, TOMOHIRO KUSUMI
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
from . import linux
from . import log
from . import setting
from . import unix
from . import util

PT_READ_I   = 1
PT_READ_D   = 2
PT_WRITE_I  = 4
PT_WRITE_D  = 5
PT_CONTINUE = 7
PT_KILL     = 8
PT_ATTACH   = 10
PT_DETACH   = 11

def get_term_info():
    return unix.get_term_info()

def get_lang_info():
    return unix.get_lang_info()

def get_blkdev_info(fd):
    # ioctl value depends on sizeof(partinfo)
    if setting.dragonflybsd_sizeof_partinfo > 0:
        size = setting.dragonflybsd_sizeof_partinfo
    elif util.is_64bit_cpu(): # assume x86_64/gcc
        size = 144
    elif util.is_32bit_cpu(): # assume i386/gcc
        size = 136
    else: # forget it
        log.error("Unsupported processor " + util.get_cpu_name())
        return -1, -1, ''
    try:
        DIOCGPART = 0x40006468 | ((size & 0x1FFF) << 16)
        b = unix.ioctl(fd, DIOCGPART, size)
        size = util.host_to_int(b[8:16])
        sector_size = util.host_to_int(b[24:28])
        return size, sector_size, ''
    except Exception as e:
        log.error("ioctl({0}, {1}) failed, {2}".format(
            fd.name, "DIOCGPART", e))
        raise

def stat_size(f):
    return unix.stat_size(f)

def read_size(f):
    return unix.read_size(f)

def get_inode(f):
    return unix.get_inode(f)

def fopen(f, mode='r'):
    return unix.fopen(f, mode)

def fopen_text(f, mode='r'):
    return unix.fopen_text(f, mode)

def fcreat(f):
    return unix.fcreat(f)

def fcreat_text(f):
    return unix.fcreat_text(f)

def symlink(source, link_name):
    return unix.symlink(source, link_name)

def fsync(fd):
    return unix.fsync(fd)

def truncate(f, offset):
    return unix.truncate(f, offset)

def utime(f, st):
    return unix.utime(f, st)

def touch(f):
    return unix.touch(f)

def stat_type(f):
    return unix.stat_type(f)

def get_page_size():
    return unix.get_page_size()

def set_non_blocking(fd):
    return unix.set_non_blocking(fd)

def get_terminal_size():
    return unix.get_terminal_size()

def get_tc(fd):
    return unix.get_tc(fd)

def set_tc(fd):
    return unix.set_tc(fd)

def set_cbreak(fd):
    return unix.set_cbreak(fd)

def get_total_ram():
    """
    [root@dragonflybsd ~]# sysctl hw.physmem
    hw.physmem: 2117337088
    """
    try:
        s = util.execute("sysctl", "hw.physmem")[0]
        x = s.split()[-1]
        return int(x)
    except Exception as e:
        log.error(e)
        return linux.get_total_ram()

def get_free_ram():
    return linux.get_free_ram()

def is_blkdev(f):
    l = stat_type(f)
    if l != -1:
        return l[2] or l[3] # blk or chr
    else:
        return False

def is_blkdev_supported():
    return True

def has_mmap():
    return True

def has_mremap():
    return False

def has_pid_access(pid):
    return unix.kill_sig_zero(pid)

def has_pid(pid):
    return unix.fs_has_pid(pid) or unix.ps_has_pid(pid)

def get_pid_name(pid):
    ret = unix.get_pid_name_from_fs(pid, "cmdline")
    if not ret:
        return unix.get_pid_name_from_ps(pid)
    else:
        return ret

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

def parse_waitpid_result(status):
    return unix.parse_waitpid_result(status)

def init():
    libc.init_ptrace("int")
