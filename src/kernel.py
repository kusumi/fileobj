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

# using the module name 'kernel' since 'os' is used by inbox module

from __future__ import with_statement
import os
import re

from . import env
from . import filebytes
from . import log
from . import setting
from . import util

class KernelError (util.GenericError):
    pass

def is_linux():
    return __system_is("Linux")
def is_netbsd():
    return __system_is("NetBSD")
def is_openbsd():
    return __system_is("OpenBSD")
def is_freebsd():
    return __system_is("FreeBSD")
def is_dragonflybsd():
    return __system_is("DragonFly") # No "BSD"
def is_darwin():
    return __system_is("Darwin")
def is_windows():
    return __system_is("Windows")
def is_hurd():
    return __system_is("GNU") # is this right ?
def is_kfreebsd():
    return __system_is("GNU/kFreeBSD")
def is_minix():
    return __system_is("Minix")
def is_solaris():
    return __system_is("SunOS")
def is_hpux():
    return __system_is("HP-UX")
def is_aix():
    return __system_is("AIX")
def is_irix():
    return __system_is("IRIX") or __system_is("IRIX64")
def is_qnx():
    return __system_is("QNX")
def is_tru64():
    return __system_is("OSF1")
def is_haiku():
    return __system_is("Haiku")

def __system_is(s):
    return _system == s

def __is_xnix():
    return setting.use_xnix

def is_cygwin():
    if _system.startswith("CYGWIN"):
        return True
    if not is_windows():
        return False
    try:
        s = util.execute("uname")[0]
        return s.startswith("CYGWIN")
    except Exception:
        return False

def is_bsd():
    return \
        is_netbsd() or \
        is_openbsd() or \
        is_freebsd() or \
        is_dragonflybsd() # or ...

def is_bsd_derived():
    return is_bsd() or is_darwin()

def is_xnix():
    return \
        is_linux() or \
        is_bsd() or \
        is_darwin() or \
        is_cygwin() or \
        is_hurd() or \
        is_kfreebsd() or \
        is_minix() or \
        is_solaris() or \
        is_hpux() or \
        is_aix() or \
        is_irix() or \
        is_qnx() or \
        is_tru64() or \
        is_haiku() or \
        __is_xnix() # or ...

_system = util.get_os_name()
assert isinstance(_system, str)

if is_linux():
    from . import linux as _kmod
elif is_netbsd():
    from . import netbsd as _kmod
elif is_openbsd():
    from . import openbsd as _kmod
elif is_freebsd():
    from . import freebsd as _kmod
elif is_dragonflybsd():
    from . import dragonflybsd as _kmod
elif is_darwin():
    from . import darwin as _kmod
elif is_windows():
    from . import windows as _kmod
elif is_xnix():
    from . import xnix as _kmod
else:
    _kmod = None

def get_kernel_module():
    return _kmod

def is_detected():
    return get_kernel_module() is not None

def get_status_string():
    if is_detected():
        return ""
    elif __system_is(util.UNKNOWN):
        return "Unknown OS type"
    else:
        return "Unable to detect OS type for " + _system

def get_term_info():
    o = get_kernel_module()
    if o:
        return o.get_term_info()
    else:
        return ''

def get_lang_info():
    o = get_kernel_module()
    if o:
        return o.get_lang_info()
    else:
        return ''

def get_blkdev_info(f):
    if not is_blkdev(f):
        raise KernelError(f + " is not blkdev")
    o = get_kernel_module()
    if not o:
        raise KernelError("Failed to get kernel module")

    # NetBSD fails with -EBUSY if already opened
    with fopen(f) as fd:
        l = o.get_blkdev_info(fd)
        b = util.Namespace(name=f, size=l[0], sector_size=l[1], label=l[2])
        log.info("Block device {0} ({1}, {2}, '{3}')".format(
            b.name,
            util.get_size_repr(b.size),
            util.get_size_repr(b.sector_size),
            filebytes.repr(b.label)))
        return b

def get_size(f):
    # caller needs to catch exception
    if is_blkdev(f):
        return get_blkdev_info(f).size
    elif os.path.isfile(f):
        ret = stat_size(f)
        if ret > 0: # not 'ret >= 0'
            return ret
        else:
            return read_size(f)
    else:
        if path_to_pid(f) != -1:
            return util.get_address_space()
        else:
            return -1

def get_size_safe(f):
    # return -1 if exception is raised
    try:
        return get_size(f)
    except Exception:
        return -1

def stat_size(f):
    o = get_kernel_module()
    if o:
        return o.stat_size(f)
    else:
        return -1

def read_size(f):
    o = get_kernel_module()
    if o:
        return o.read_size(f)
    else:
        return -1

def get_inode(f):
    o = get_kernel_module()
    if o:
        return o.get_inode(f)
    else:
        return -1

# don't use "open" since it conflicts with builtin
def fopen(f, mode='r'):
    o = get_kernel_module()
    if o:
        return o.fopen(f, mode)
    else:
        return -1

def fopen_text(f, mode='r'):
    o = get_kernel_module()
    if o:
        return o.fopen_text(f, mode)
    else:
        return -1

def fcreat(f):
    o = get_kernel_module()
    if o:
        return o.fcreat(f)
    else:
        return -1

def fcreat_text(f):
    o = get_kernel_module()
    if o:
        return o.fcreat_text(f)
    else:
        return -1

def symlink(source, link_name):
    o = get_kernel_module()
    if o:
        return o.symlink(source, link_name)
    else:
        return -1

def fsync(fd):
    o = get_kernel_module()
    if o:
        return o.fsync(fd)
    else:
        return -1

def truncate(f, offset=0):
    o = get_kernel_module()
    if o:
        return o.truncate(f, offset)
    else:
        return -1

def utime(f, st):
    o = get_kernel_module()
    if o:
        return o.utime(f, st)
    else:
        return -1

def touch(f):
    o = get_kernel_module()
    if o:
        return o.touch(f)
    else:
        return -1

def stat_type(f):
    o = get_kernel_module()
    if o:
        ret = o.stat_type(f)
        if ret != -1:
            return ret
    return util.Namespace(
        is_file=False,
        is_dir=False,
        is_blkdev=False,
        is_chrdev=False,
        is_fifo=False,
        is_sock=False)

def get_page_size():
    o = get_kernel_module()
    if o:
        ret = o.get_page_size()
    else:
        ret = -1
    if ret == -1:
        return env.PSEUDO_PAGE_SIZE
    else:
        return ret

def get_buffer_size():
    if setting.general_buffer_size != -1:
        return setting.general_buffer_size
    o = get_kernel_module()
    if o:
        return o.get_buffer_size()
    else:
        return -1

def set_non_blocking(fd):
    o = get_kernel_module()
    if o:
        return o.set_non_blocking(fd)
    else:
        return -1

def get_terminal_size():
    o = get_kernel_module()
    if o:
        return o.get_terminal_size()
    else:
        return -1, -1

def get_tc(fd):
    o = get_kernel_module()
    if o:
        return o.get_tc(fd)
    else:
        return -1

def set_tc(fd):
    o = get_kernel_module()
    if o:
        return o.set_tc(fd)
    else:
        return -1

def set_cbreak(fd):
    o = get_kernel_module()
    if o:
        return o.set_cbreak(fd)
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
    """Return True if f is block device"""
    o = get_kernel_module()
    if o:
        return o.is_blkdev(f)
    else:
        return False

def is_blkdev_supported():
    """Return True if block device is supported"""
    o = get_kernel_module()
    if o:
        return o.is_blkdev_supported()
    else:
        return False

def mmap_full(fileno, readonly=False):
    o = get_kernel_module()
    if o:
        return o.mmap_full(fileno, readonly)
    else:
        return None

def mmap_partial(fileno, offset, length, readonly=False):
    o = get_kernel_module()
    if o:
        return o.mmap_partial(fileno, offset, length, readonly)
    else:
        return None

def has_mmap():
    """Return True if mmap(2) is supported"""
    o = get_kernel_module()
    if o:
        return o.has_mmap()
    else:
        return False

_has_mremap = None

def has_mremap():
    """Return True if mremap(2) is supported"""
    global _has_mremap
    if _has_mremap is None:
        _has_mremap = __has_mremap()
    assert isinstance(_has_mremap, bool)
    return _has_mremap

def __has_mremap():
    if not has_mmap():
        return False
    o = get_kernel_module()
    if not o:
        return False
    if o.has_mremap():
        return True
    elif setting.use_test_mmap_resize:
        return o.test_mmap_resize()[0] # should fail if above is False
    else:
        return False

def test_mmap_resize():
    """Return True,None if resizable otherwise False,str"""
    o = get_kernel_module()
    if o:
        return o.test_mmap_resize()
    else:
        return False, None

# this is for testing
def try_mmap_resize(osiz, nsiz):
    """Return mmap size after resize"""
    o = get_kernel_module()
    if o:
        return o.try_mmap_resize(osiz, nsiz)
    else:
        return -1

def has_pid_access(pid):
    """Return True if an user can see the existence of pid"""
    o = get_kernel_module()
    if o:
        return o.has_pid_access(pid)
    else:
        return False

def has_pid(pid):
    """Return True if pid exists"""
    o = get_kernel_module()
    if o:
        return o.has_pid(pid)
    else:
        return False

def get_pid_name(pid):
    """Return process name of pid if possible"""
    o = get_kernel_module()
    if o:
        return o.get_pid_name(pid)
    else:
        return ''

def is_pid_path_supported():
    """Return True if pid path is supported"""
    o = get_kernel_module()
    if o:
        return o.is_pid_path_supported()
    else:
        return False

def is_pid_path(f):
    pid = path_to_pid(f)
    return pid != -1 and has_pid(pid)

def path_to_pid(f):
    try:
        f = os.path.basename(f)
        m = re.match(r"^pid(\d+)$", f)
        if m:
            return int(m.group(1))
        else:
            return -1
    except Exception:
        return -1

def ptrace_peektext(pid, addr):
    o = get_kernel_module()
    if o:
        return o.ptrace_peektext(pid, addr)
    else:
        return None

def ptrace_peekdata(pid, addr):
    o = get_kernel_module()
    if o:
        return o.ptrace_peekdata(pid, addr)
    else:
        return None

def ptrace_poketext(pid, addr, data):
    o = get_kernel_module()
    if o:
        return o.ptrace_poketext(pid, addr, data)
    else:
        return None

def ptrace_pokedata(pid, addr, data):
    o = get_kernel_module()
    if o:
        return o.ptrace_pokedata(pid, addr, data)
    else:
        return None

def ptrace_cont(pid):
    o = get_kernel_module()
    if o:
        return o.ptrace_cont(pid)
    else:
        return None

def ptrace_kill(pid):
    o = get_kernel_module()
    if o:
        return o.ptrace_kill(pid)
    else:
        return None

def ptrace_attach(pid):
    o = get_kernel_module()
    if o:
        return o.ptrace_attach(pid)
    else:
        return None

def ptrace_detach(pid):
    o = get_kernel_module()
    if o:
        return o.ptrace_detach(pid)
    else:
        return None

def ptrace_peek(pid, addr):
    o = get_kernel_module()
    if o:
        return o.ptrace_peek(pid, addr)
    else:
        return None

def ptrace_poke(pid, addr, data):
    o = get_kernel_module()
    if o:
        return o.ptrace_poke(pid, addr, data)
    else:
        return None

def get_ptrace_word_size():
    o = get_kernel_module()
    if o:
        return o.get_ptrace_word_size()
    else:
        return -1

def waitpid(pid, opts):
    o = get_kernel_module()
    if o:
        return o.waitpid(pid, opts)
    else:
        return -1, -1

def parse_waitpid_result(status):
    o = get_kernel_module()
    if o:
        return o.parse_waitpid_result(status)
    else:
        return ''

def init():
    o = get_kernel_module()
    if o:
        try:
            return o.init()
        except Exception as e:
            log.error(e)
    return -1
init()
