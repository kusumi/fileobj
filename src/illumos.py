# Copyright (c) 2017, Tomohiro Kusumi
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
import errno

from . import libc
from . import log
from . import unix
from . import util

def get_term_info():
    return unix.get_term_info()

def get_lang_info():
    return unix.get_lang_info()

def get_blkdev_info(f):
    with fopen(f) as fd:
        return __get_blkdev_info(fd)

def __get_blkdev_info(fd):
    try:
        DKIOC = (0x04 << 8)
        DKIOCGMEDIAINFO = (DKIOC | 42)
        sizeof_uint = libc.get_sizeof_uint()
        sizeof_ulonglong = libc.get_sizeof_ulonglong()
        size = sizeof_uint*2 + sizeof_ulonglong
        b = unix.ioctl(fd, DKIOCGMEDIAINFO, size)

        buf = b[sizeof_uint:sizeof_uint*2]
        sector_size = util.host_to_int(buf)
        buf = b[sizeof_uint*2:sizeof_uint*2 + sizeof_ulonglong]
        size = util.host_to_int(buf) * sector_size
        return size, sector_size, ''
    except Exception as e:
        log.error("ioctl({0}, {1}) failed, {2}".format(
            fd.name, "DKIOCGMEDIAINFO", e))
        raise

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
    return __get_meminfo("physmem")

def get_free_ram():
    return __get_meminfo("freemem")

def __get_meminfo(name):
    ret = __get_kstat_system_pages(name)
    if ret == -1:
        return -1
    return ret * get_page_size()

def __get_kstat_system_pages(name):
    """
    [root@unknown ~]# kstat -n system_pages -p -s physmem
    unix:0:system_pages:physmem     522126
    """
    try:
        cmd = "kstat", "-n", "system_pages", "-p", "-s", name
        s = util.execute(*cmd).stdout
        x = s.split("\t")[-1]
        return int(x)
    except Exception as e:
        log.error(e)
        return -1

def is_blkdev(f):
    return unix.stat_is_chrdev(f)

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

def test_mmap_resize(osiz, nsiz):
    return unix.test_mmap_resize(osiz, nsiz)

def has_pid_access(pid):
    return unix.kill_sig_zero(pid)

def has_pid(pid):
    return unix.has_pid(pid)

def get_pid_name(pid):
    return unix.get_pid_name(pid)

# The ptrace() function is available only with the 32-bit version of
# libc(3LIB). It is not available with the 64-bit version of this library.
def has_ptrace():
    return False

def ptrace_peektext(pid, addr):
    return None, errno.EOPNOTSUPP

def ptrace_peekdata(pid, addr):
    return None, errno.EOPNOTSUPP

def ptrace_poketext(pid, addr, data):
    return None, errno.EOPNOTSUPP

def ptrace_pokedata(pid, addr, data):
    return None, errno.EOPNOTSUPP

def ptrace_attach(pid):
    return None, errno.EOPNOTSUPP

def ptrace_detach(pid):
    return None, errno.EOPNOTSUPP

def get_ptrace_word_size():
    return -1

def waitpid(pid, opts):
    return unix.waitpid(pid, opts)

def parse_waitpid_result(status):
    return unix.parse_waitpid_result(status)

def init():
    unix.init_procfs()
