# Copyright (c) 2014, Tomohiro Kusumi
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

# >>> import curses
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "C:\Python34\lib\curses\__init__.py", line 13, in <module>
#     from _curses import *
# ImportError: No module named '_curses'

# no curses for Python on win32 however unofficial binary is available at
# http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses

# windows-curses is available as of 2018
# https://pypi.org/project/windows-curses/
# $ pip install windows-curses

from __future__ import with_statement
import ctypes
import errno
import mmap
import os
import stat
import struct

from . import util

def read_reg_size(f):
    if not os.path.isfile(f): # only for regfile
        return -1
    ret = os.stat(f).st_size
    if ret != -1:
        return ret
    return seek_end(f)

def seek_end(f):
    if not os.path.exists(f):
        return -1
    with fopen(f) as fd:
        try:
            return os.lseek(fd.fileno(), 0, os.SEEK_END)
        except Exception:
            return -1

# https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/stat-functions
# .st_ino shows non-zero value since Python 3.x (not exactly sure which),
# but not on Python 2. There is no guarantee this value is compatible with inode
# number concept in *nix, so simply unsupport get_inode().
def get_inode(f):
    return 0
    #if os.path.exists(f):
    #    return os.stat(f).st_ino
    #else:
    #    return -1

def fopen(f, mode='r'):
    return open(f, mode + 'b')

def fopen_text(f, mode='r'):
    return open(f, mode)

def fcreat(f):
    return os.fdopen(__creat_file(f), 'w+b')

def fcreat_text(f):
    return os.fdopen(__creat_file(f), 'w+')

# https://docs.python.org/3/library/os.html#os.open
def __creat_file(f):
    """Raise 'FileExistsError: [Errno 17] File exists: ...' if f exists"""
    return os.open(f, os.O_RDWR | os.O_CREAT | os.O_EXCL, 420) # 0644

# https://docs.python.org/3/library/os.html#os.symlink
if util.is_python2():
    def symlink(source, link_name):
        return -1 # os.symlink unsupported, and so is Python 2.x
else:
    def symlink(source, link_name):
        if os.path.exists(link_name):
            return -1
        try:
            os.symlink(source, link_name)
        except NotImplementedError: # pre Windows Vista
            return -1
        except OSError: # "symbolic link privilege not held"
            return -1
        if not os.path.islink(link_name):
            return -1

def fsync(fd):
    if fd and not fd.closed:
        fd.flush()
        os.fsync(fd.fileno())

def truncate(f, offset):
    with fopen(f, 'r+') as fd:
        fd.seek(offset)
        fd.truncate()

def utime(f, st):
    import nt
    if st is None:
        os.utime(f, None)
    elif isinstance(st, nt.stat_result):
        os.utime(f, (st.st_atime, st.st_mtime))
    else:
        os.utime(f, (st[0], st[1]))

def touch(f):
    return utime(f, None)

def stat_type(f):
    try:
        mode = os.stat(f).st_mode
    except Exception:
        return -1
    return {
        "LINK" : stat.S_ISLNK(mode),
        "REG" : stat.S_ISREG(mode),
        "DIR" : stat.S_ISDIR(mode),
        "BLKDEV" : stat.S_ISBLK(mode),
        "CHRDEV" : stat.S_ISCHR(mode), }

def get_page_size():
    try:
        return mmap.PAGESIZE
    except Exception:
        return -1

def get_buffer_size():
    pg_siz = get_page_size()
    buf_siz = 0x10000
    if pg_siz > buf_siz:
        return pg_siz
    else:
        return buf_siz

def get_terminal_size():
    h = ctypes.windll.kernel32.GetStdHandle(-11) # STD_OUTPUT_HANDLE
    b = ctypes.create_string_buffer(22)
    if ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, b) != 0:
        # https://docs.microsoft.com/en-us/windows/console/console-screen-buffer-info-str
        l = struct.unpack(util.S2F * 4 + util.U2F + util.S2F * 6, b.raw)
        assert len(l) == 11, l
        left, top, right, bottom = l[5:9]
        return bottom - top + 1, right - left + 1
    else:
        return -1, -1

def get_total_ram():
    return -1

def get_free_ram():
    return -1

def has_blkdev():
    return False

def is_blkdev(f):
    return False

def is_blkdev_supported():
    return False

# https://docs.python.org/3/library/mmap.html
def mmap_full(fileno, readonly=False):
    return mmap.mmap(fileno, 0)

def mmap_partial(fileno, offset, length, readonly=False):
    return mmap.mmap(fileno, length, offset=offset)

def has_mmap():
    return False # XXX supported by Windows, but disable for now

def has_mremap():
    return False # XXX supported by Windows, but disable for now

def test_mmap_resize(osiz, nsiz):
    return False, None

def has_pid_access(pid):
    return False

def has_pid(pid):
    return False

def get_pid_name(pid):
    return ''

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
    return os.waitpid(pid, opts)

def parse_waitpid_result(status):
    return ''

try:
    FileNotFoundError # since Python 3.3
except NameError:
    FileNotFoundError = OSError
try:
    WindowsError
except NameError:
    WindowsError = OSError

def execute(*l):
    try:
        return util.execute(False, *l)
    except (WindowsError, FileNotFoundError):
        return util.execute(True, *l)

def execute_sh(cmd):
    return util.execute(True, cmd)

def init():
    return
