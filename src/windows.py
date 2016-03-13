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

# >>> import curses
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "C:\Python34\lib\curses\__init__.py", line 13, in <module>
#     from _curses import *
# ImportError: No module named '_curses'

# no curses for Python on win32 however unofficial binary is available at
# http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses

import mmap
import nt
import os

from . import util

def get_term_info():
    return ''

def get_lang_info():
    return ''

def stat_size(f):
    if os.path.isfile(f):
        return os.stat(f).st_size
    else:
        return -1

def read_size(f):
    return -1

def get_inode(f):
    return -1

def fopen(f, mode='r'):
    return -1

def fopen_text(f, mode='r'):
    return -1

def fcreat(f):
    return -1

def fcreat_text(f):
    return -1

def symlink(source, link_name):
    if util.is_python_version_or_ht(3, 2) and \
        not os.path.exists(link_name):
        os.symlink(source, link_name)
        if not os.path.islink(link_name):
            return -1
    else:
        return -1

def fsync(fd):
    if fd and not fd.closed:
        fd.flush()
        os.fsync(fd.fileno())

def truncate(f, offset):
    return -1

def utime(f, st):
    if st is None:
        os.utime(f, None)
    elif isinstance(st, nt.stat_result):
        os.utime(f, (st.st_atime, st.st_mtime))
    else:
        os.utime(f, (st[0], st[1]))

def touch(f):
    return utime(f, None)

def stat_type(f):
    return -1

def get_page_size():
    ret = __get_mmap_page_size()
    if ret != -1:
        return ret
    return -1

def __get_mmap_page_size():
    try:
        return mmap.PAGESIZE
    except Exception:
        return -1

def get_buffer_size():
    return get_page_size()

def set_non_blocking(fd):
    return -1

def get_terminal_size():
    return -1, -1

def get_tc(fd):
    return -1

def set_tc(fd):
    return -1

def set_cbreak(fd):
    return -1

def get_total_ram():
    return -1

def get_free_ram():
    return -1

def is_blkdev(f):
    return False

def is_blkdev_supported():
    return False

def mmap_full(fileno, readonly=False):
    return None

def mmap_partial(fileno, offset, length, readonly=False):
    return None

def has_mmap():
    return False

def has_mremap():
    return False

def test_mmap_resize():
    return False, None

def try_mmap_resize(osiz, nsiz):
    return -1

def has_pid_access(pid):
    return False

def has_pid(pid):
    return False

def get_pid_name(pid):
    return ''

def is_pid_path_supported():
    return False

def ptrace_peektext(pid, addr):
    assert 0, "Not implemented"

def ptrace_peekdata(pid, addr):
    assert 0, "Not implemented"

def ptrace_poketext(pid, addr, data):
    assert 0, "Not implemented"

def ptrace_pokedata(pid, addr, data):
    assert 0, "Not implemented"

def ptrace_cont(pid):
    assert 0, "Not implemented"

def ptrace_kill(pid):
    assert 0, "Not implemented"

def ptrace_attach(pid):
    assert 0, "Not implemented"

def ptrace_detach(pid):
    assert 0, "Not implemented"

def ptrace_peek(pid, addr):
    assert 0, "Not implemented"

def ptrace_poke(pid, addr, data):
    assert 0, "Not implemented"

def get_ptrace_word_size():
    assert 0, "Not implemented"

def waitpid(pid, opts):
    return os.waitpid(pid, opts)

def parse_waitpid_result(status):
    return ''

def init():
    return
