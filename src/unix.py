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

from __future__ import with_statement
import fcntl
import mmap
import os
import posix
import re
import resource
import stat
import struct
import termios
import tty

from . import filebytes
from . import setting
from . import util

def get_term_info():
    return os.getenv("TERM", "")

def get_lang_info():
    return os.getenv("LANG", "")

def stat_size(f):
    if os.path.isfile(f):
        return os.stat(f).st_size
    else:
        return -1

def read_size(f):
    if not os.path.isfile(f):
        return -1
    with fopen(f) as fd: # binary
        if set_non_blocking(fd) == -1:
            return -1
        try:
            ret = fd.read()
        except IOError: # Python 2.x raises exception
            return -1
        if ret is None: # Python 3.x returns None
            return -1
        else: # success
            return len(ret)

def get_inode(f):
    if os.path.exists(f):
        return os.stat(f).st_ino
    else:
        return -1

def fopen(f, mode='r'):
    return open(f, mode + 'b')

def fopen_text(f, mode='r'):
    return open(f, mode)

def fcreat(f):
    return os.fdopen(__creat_file(f), 'w+b')

def fcreat_text(f):
    return os.fdopen(__creat_file(f), 'w+')

def __creat_file(f):
    """Raise 'OSError: [Errno 17] File exists: ...' if f exists"""
    return os.open(f, os.O_RDWR | os.O_CREAT | os.O_EXCL, 420) # 0644

def symlink(source, link_name):
    if not os.path.exists(link_name):
        os.symlink(source, link_name)
        if not os.path.islink(link_name):
            return -1
    else:
        return -1

def fsync(fd):
    if fd and not fd.closed:
        fd.flush()
        os.fsync(fd.fileno()) # calls fsync(2)

def truncate(f, offset):
    with fopen(f, 'r+') as fd:
        fd.seek(offset)
        fd.truncate()

def utime(f, st):
    if st is None:
        os.utime(f, None)
    elif isinstance(st, posix.stat_result):
        os.utime(f, (st.st_atime, st.st_mtime))
    else:
        os.utime(f, (st[0], st[1]))

def touch(f):
    return utime(f, None)

def __stat_type(f):
    _ = os.stat(f).st_mode
    t = "reg", "dir", "blk", "chr", "fifo", "sock"
    l = [getattr(stat, "S_IS" + s.upper())(_) for s in t]
    return dict(
        reg=l[0],
        dir=l[1],
        blkdev=l[2],
        chrdev=l[3],
        fifo=l[4],
        sock=l[5])

def stat_type(f):
    try:
        return __stat_type(f)
    except Exception:
        return -1

def stat_is_blkdev(f):
    d = stat_type(f)
    if d != -1:
        return d.get("blkdev", False)
    else:
        return False

def stat_is_blkdev_or_chrdev(f):
    d = stat_type(f)
    if d != -1:
        return d.get("blkdev", False) or d.get("chrdev", False)
    else:
        return False

def get_page_size():
    ret = __get_resource_page_size()
    if ret != -1:
        return ret
    ret = __get_sysconf_page_size()
    if ret != -1:
        return ret
    ret = __get_mmap_page_size()
    if ret != -1:
        return ret
    return -1

def __get_resource_page_size():
    try:
        return resource.getpagesize()
    except Exception:
        return -1

def __get_sysconf_page_size():
    try:
        return os.sysconf("SC_PAGE_SIZE")
    except Exception:
        return -1

def __get_mmap_page_size():
    try:
        return mmap.PAGESIZE
    except Exception:
        return -1

def get_buffer_size():
    return get_page_size()

def mmap_full(fileno, readonly=False):
    prot = __get_mmap_prot(readonly)
    return mmap.mmap(fileno, 0, mmap.MAP_SHARED, prot)

def mmap_partial(fileno, offset, length, readonly=False):
    prot = __get_mmap_prot(readonly)
    assert offset % mmap.ALLOCATIONGRANULARITY == 0, offset
    return mmap.mmap(fileno, length, mmap.MAP_SHARED, prot, offset=offset)

def __get_mmap_prot(readonly):
    if readonly:
        return mmap.PROT_READ
    else:
        return mmap.PROT_READ | mmap.PROT_WRITE

def test_mmap_resize():
    try:
        ll = ((1024, 2048), (1024, 512), (4096, 17123), (5678, 1024))
        for l in ll:
            nsiz = __try_mmap_resize(*l)
            if nsiz != l[1]:
                return False, "Bad size {0} != {1}".format(nsiz, l[1])
        return True, None
    except Exception as e:
        return False, str(e)

def try_mmap_resize(osiz, nsiz):
    try:
        return __try_mmap_resize(osiz, nsiz)
    except Exception:
        return -1

def __try_mmap_resize(osiz, nsiz):
    fd = util.open_temp_file()
    fd.write(filebytes.ZERO * osiz)
    fsync(fd)
    m = mmap_full(fd.fileno())
    m.resize(nsiz)
    nsiz = len(m[:])
    m.close()
    return nsiz

def set_non_blocking(fd):
    try:
        fl = fcntl.fcntl(fd.fileno(), fcntl.F_GETFL)
        fl |= os.O_NONBLOCK
        fcntl.fcntl(fd.fileno(), fcntl.F_SETFL, fl)
    except Exception:
        return -1

def ioctl(fd, request, length):
    return fcntl.ioctl(fd, request, filebytes.pad(length))

def ioctl_get_int(fd, request, length):
    return util.host_to_int(ioctl(fd, request, length))

def get_terminal_size():
    """Return a tuple of (y, x)"""
    b = ioctl(0, termios.TIOCGWINSZ, 8)
    return struct.unpack(util.S2F * 4, b)[:2]

_tattr = None
def get_tc(fd):
    global _tattr
    if not _tattr:
        _tattr = termios.tcgetattr(fd)
    else:
        return -1

def set_tc(fd):
    global _tattr
    if _tattr:
        termios.tcsetattr(fd, termios.TCSANOW, _tattr)
        _tattr = None
    else:
        return -1

def set_cbreak(fd):
    tty.setcbreak(fd)

def waitpid(pid, opts):
    return os.waitpid(pid, opts)

def parse_waitpid_result(status):
    l = []
    if os.WIFEXITED(status):
        l.append("WIFEXITED({0})".format(os.WEXITSTATUS(status)))
    if os.WIFSIGNALED(status):
        l.append("WIFSIGNALED({0})".format(os.WTERMSIG(status)))
    if os.WCOREDUMP(status):
        l.append("WCOREDUMP")
    if os.WIFSTOPPED(status):
        l.append("WIFSTOPPED({0})".format(os.WSTOPSIG(status)))
    return '|'.join(l)

def kill_sig_zero(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def ps_has_pid(pid):
    for l in iter_ps():
        if pid == l[0]:
            return True
    return False

def get_pid_name_from_ps(pid, fn=None):
    if not fn:
        fn = __parse_ps_name
    for l in iter_ps():
        if pid == l[0]:
            return fn(l[1])
    return ''

def __parse_ps_name(name):
    cmd = name.split(" ")[0]
    return os.path.basename(cmd)

def iter_ps(opt=None):
    if not opt:
        opt = "aux" if setting.use_ps_aux else "ax"
    try:
        s = util.execute("ps", opt).stdout
    except Exception:
        s = ''
    l = s.split('\n')
    for x in l[1:]:
        if x:
            if opt == "ax":
                ret = __split_ps_ax_line(x)
            elif opt == "aux":
                ret = __split_ps_aux_line(x)
            else:
                ret = None
            if ret is not None:
                yield ret

def __split_ps_ax_line(s):
    # e.g.
    #  PID TTY      STAT   TIME COMMAND
    #    1 ?        Ss     0:01 /sbin/init
    # 2391 ?        Sl     0:00 libvirtd --daemon
    try:
        s = s.strip()
        s = re.sub(r" +", " ", s)
        l = s.split(" ", 4)
        return int(l[0]), l[-1]
    except Exception:
        pass

def __split_ps_aux_line(s):
    # e.g.
    # USER  PID %CPU %MEM    VSZ   RSS TTY STAT START   TIME COMMAND
    # root    1  0.0  0.0  19356  1536 ?   Ss   Dec17   0:01 /sbin/init
    # root 2391  0.0  0.2 339704 10604 ?   Sl   Dec17   0:00 libvirtd --daemon
    try:
        s = s.strip()
        s = re.sub(r" +", " ", s)
        l = s.split(" ", 10)
        return int(l[1]), l[-1]
    except Exception:
        pass

def fs_has_pid(pid):
    return os.path.isdir(get_procfs_entry(pid))

def get_pid_name_from_fs(pid, *entries):
    for s in entries:
        f = get_procfs_entry("{0}/{1}".format(pid, s))
        if os.path.isfile(f):
            try:
                b = fopen(f).read()
                b = filebytes.rstrip(b)
                return os.path.basename(util.bytes_to_str(b))
            except Exception:
                pass
    return ''

def has_pid(pid):
    return fs_has_pid(pid) or ps_has_pid(pid)

def get_pid_name(pid):
    ret = get_pid_name_from_fs(pid, "cmdline")
    if not ret:
        return get_pid_name_from_ps(pid)
    else:
        return ret

def get_procfs_entry(s):
    if isinstance(s, int): # /proc/<pid>
        s = str(s)
    if not os.path.isdir(_procfs_mnt):
        return ''
    e = os.path.join(_procfs_mnt, s)
    if not os.path.exists(e):
        return ''
    return e

def get_procfs_mount_point(label=''):
    l = ["proc", "procfs"] # default labels
    if label:
        l.insert(0, label) # give higher priority
    return get_fs_mount_point(*l)

def get_fs_mount_point(*labels):
    try:
        s = util.execute("mount").stdout
    except Exception:
        return ''
    for x in s.split('\n'):
        m = re.search(r"^(.+)\s+on\s+(.+?)\s", x)
        if m:
            name, where = m.groups()
            if name in labels:
                if os.path.isdir(where):
                    return os.path.abspath(where)
    return ''

_procfs_mnt = ''

def init_procfs(label=''):
    global _procfs_mnt
    _procfs_mnt = setting.procfs_mount_point
    if not os.path.isdir(_procfs_mnt):
        _procfs_mnt = get_procfs_mount_point(label)
    if not os.path.isdir(_procfs_mnt):
        return -1
