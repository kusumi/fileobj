# Copyright (c) 2010-2016, Tomohiro Kusumi
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
from . import setting
from . import unix
from . import util

PT_READ_I   = 1
PT_READ_D   = 2
PT_WRITE_I  = 4
PT_WRITE_D  = 5
PT_CONTINUE = 7
PT_KILL     = 8
PT_ATTACH   = 9
PT_DETACH   = 10

def get_term_info():
    return unix.get_term_info()

def get_lang_info():
    return unix.get_lang_info()

# get_blkdev_info() which used to just call netbsd version of this
# is no longer compatible with NetBSD based on the result from 5.9.
# size part seems to have changed ever since this code was originally
# written in 2014. The size in IA32 has probably changed too.

# XXX Recent OpenBSD need below, but C extension support for native
# ioctls was added in v0.7.43, so this is no longer too important.

if util.get_os_release() >= "5.9" and setting.netbsd_sizeof_disklabel == -1:
    if util.is_64bit_cpu(): # assume x86_64/gcc
        setting.netbsd_sizeof_disklabel = 404 # was 408
    elif util.is_32bit_cpu(): # assume i386/gcc
        setting.netbsd_sizeof_disklabel = 404 # XXX this is probably wrong

def get_blkdev_info(f):
    return netbsd.get_blkdev_info(f)

def read_reg_size(f):
    return unix.read_reg_size(f)

def seek_end(f):
    return unix.seek_end(f)

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

def get_buffer_size():
    return unix.get_buffer_size()

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
    [root@openbsd ~]# sysctl hw.physmem
    hw.physmem=1073266688
    """
    try:
        s = util.execute("sysctl", "hw.physmem").stdout
        x = s.split("=")[-1]
        return int(x)
    except Exception as e:
        log.error(e)
        return -1

def get_free_ram():
    return -1

def is_blkdev(f):
    return unix.stat_is_blkdev(f)

def is_blkdev_supported():
    return True

def mmap_full(fileno, readonly=False):
    return unix.mmap_full(fileno, readonly)

def mmap_partial(fileno, offset, length, readonly=False):
    return unix.mmap_partial(fileno, offset, length, readonly)

def has_mmap():
    return True

def has_mremap():
    return False

def test_mmap_resize():
    return unix.test_mmap_resize()

def try_mmap_resize(osiz, nsiz):
    return unix.try_mmap_resize(osiz, nsiz)

def has_pid_access(pid):
    return unix.kill_sig_zero(pid)

def has_pid(pid):
    return unix.has_pid(pid)

def get_pid_name(pid):
    return unix.get_pid_name(pid)

def is_pid_path_supported():
    return False

def has_ptrace():
    return libc.has_ptrace()

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

def waitpid(pid, opts):
    return unix.waitpid(pid, opts)

def parse_waitpid_result(status):
    return unix.parse_waitpid_result(status)

def init():
    unix.init_procfs()
    libc.init_ptrace("int")
