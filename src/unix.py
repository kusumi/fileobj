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

from __future__ import with_statement
import mmap
import os
import re
import stat

from . import filebytes
from . import log
from . import util

def read_reg_size(f):
    if not os.path.isfile(f): # only for regfile
        return -1
    if is_procfs_path(f):
        return __read_procfs_size(f)
    else:
        return __read_reg_size(f)

def __read_reg_size(f):
    ret = os.stat(f).st_size
    if ret != -1:
        return ret
    return seek_end(f)

def __read_procfs_size(f):
    ret = os.stat(f).st_size
    if ret > 0: # procfs may return 0
        return ret
    return __read_buf_size(f) # XXX workaround for procfs

# suboptimal, don't use this unless this is the only way
def __read_buf_size(f):
    with fopen(f) as fd:
        if set_non_blocking(fd) == -1:
            return -1
        try:
            ret = fd.read() # XXX add heuristic to return -1 if too big
        except IOError: # Python 2.x raises exception
            return -1
        if ret is None: # Python 3.x returns None
            return -1
        else: # success
            return len(ret)

def seek_end(f):
    if not os.path.exists(f): # allow blkdev
        return -1
    with fopen(f) as fd:
        try:
            return os.lseek(fd.fileno(), 0, os.SEEK_END)
        except Exception:
            return -1

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

# Python 3.3+ raises subclass of OSError called FileExistsError
# https://docs.python.org/3/whatsnew/3.3.html
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
    import posix
    if st is None:
        os.utime(f, None)
    elif isinstance(st, posix.stat_result):
        os.utime(f, (st.st_atime, st.st_mtime))
    else:
        os.utime(f, (st[0], st[1]))

def touch(f):
    return utime(f, None)

def stat_type(f):
    try:
        mode = os.stat(f).st_mode
        path_type = "LINK", "REG", "DIR", "BLKDEV", "CHRDEV"
        stat_type = "lnk", "reg", "dir", "blk", "chr"
        l = [getattr(stat, "S_IS" + s.upper())(mode) for s in stat_type]
        return dict(zip(path_type, l)) # LINK always false
    except Exception:
        return -1

def stat_is_blkdev(f):
    return __stat_is(f, "BLKDEV")

def stat_is_chrdev(f):
    return __stat_is(f, "CHRDEV")

def stat_is_blkdev_or_chrdev(f):
    return __stat_is(f, "BLKDEV", "CHRDEV")

def __stat_is(f, *l):
    d = stat_type(f)
    if d == -1:
        return False
    for s in l:
        if d.get(s, False):
            return True
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
    import resource
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

def test_mmap_resize(osiz, nsiz):
    try:
        ret = __do_mmap_resize(osiz, nsiz)
        if ret != nsiz:
            return False, "Bad size {0} != {1}".format(ret, nsiz)
        return True, None
    except Exception as e:
        return False, str(e)

def __do_mmap_resize(osiz, nsiz):
    fd = util.open_temp_file()
    fd.write(filebytes.ZERO * osiz)
    fsync(fd)
    m = mmap_full(fd.fileno())
    m.resize(nsiz)
    nsiz = len(m[:])
    m.close()
    return nsiz

def set_non_blocking(fd):
    import fcntl
    try:
        fl = fcntl.fcntl(fd.fileno(), fcntl.F_GETFL)
        fl |= os.O_NONBLOCK
        fcntl.fcntl(fd.fileno(), fcntl.F_SETFL, fl)
    except Exception:
        return -1

def ioctl(fd, request, length):
    import fcntl
    return fcntl.ioctl(fd, request, filebytes.pad(length))

def ioctl_get_int(fd, request, length):
    return util.host_to_int(ioctl(fd, request, length))

def get_total_ram():
    page_size = get_page_size()
    if page_size == -1:
        return -1
    try:
        ret = os.sysconf("SC_PHYS_PAGES") # not standard
        return ret * page_size
    except Exception:
        return -1

def get_free_ram():
    page_size = get_page_size()
    if page_size == -1:
        return -1
    try:
        ret = os.sysconf("SC_AVPHYS_PAGES") # not standard
        return ret * page_size
    except Exception:
        return -1

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
    for l in iter_ps("aux"):
        if pid == l[0]:
            return True
    log.debug("ps aux failed, try ps ax for pid{0}".format(pid))
    for l in iter_ps("ax"):
        if pid == l[0]:
            return True
    return False

def get_pid_name_from_ps(pid):
    for i, s, in iter_ps("aux"):
        if pid == i:
            return s.split(" ")[0] # prefer abs (no basename)
    log.debug("ps aux failed, try ps ax for pid{0} name".format(pid))
    for i, s, in iter_ps("ax"):
        if pid == i:
            return s.split(" ")[0] # prefer abs (no basename)
    return ''

def iter_ps(opt=None):
    assert opt in ("aux", "ax"), opt
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
                return util.bytes_to_str(b) # prefer abs (no basename)
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
        # both need ? as "on" appears twice on Solaris
        m = re.search(r"^(.+?)\s+on\s+(.+?)\s", x)
        if m:
            name, where = m.groups()
            if __test_fs_mount_point(labels, name, where):
                return os.path.abspath(where)
            name, where = where, name # XXX Solaris has these opposite
            if __test_fs_mount_point(labels, name, where):
                return os.path.abspath(where)
    return ''

def __test_fs_mount_point(labels, name, where):
    return (name in labels) and os.path.isdir(where)

def is_procfs_path(f):
    if not os.path.isfile(f) and not os.path.isdir(f):
        return False
    if not os.path.isdir(_procfs_mnt):
        return False
    return f.startswith(_procfs_mnt + '/')

_procfs_mnt = ''

def init_procfs(label=''):
    global _procfs_mnt
    _procfs_mnt = "/proc"
    if not os.path.isdir(_procfs_mnt):
        _procfs_mnt = get_procfs_mount_point(label)

    # just make it a rule that it doesn't end with /
    if _procfs_mnt.endswith('/'):
        _procfs_mnt = _procfs_mnt.rstrip('/')
    assert not _procfs_mnt.endswith('/')

    if not os.path.isdir(_procfs_mnt):
        return -1
