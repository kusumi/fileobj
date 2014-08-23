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

import os
import re

from . import filebytes
from . import setting
from . import util

def get_procfs_entry(s):
    if not os.path.isdir(_mount):
        return ''
    e = os.path.join(_mount, s)
    if not os.path.exists(e):
        return ''
    return e

def get_pid_dir(pid):
    return get_procfs_entry(str(pid))

def get_pid_entry(pid, s):
    return get_procfs_entry("%d/%s" % (pid, s))

def has_pid(pid):
    return os.path.isdir(get_pid_dir(pid))

def get_pid_name(pid, *entries):
    for s in entries:
        f = get_pid_entry(pid, s)
        if os.path.isfile(f):
            try:
                return __read_proc_name(f)
            except Exception:
                pass
    return ''

def __read_proc_name(f):
    b = util.open_file(f).read()
    i = b.find(filebytes.ZERO)
    if i != -1:
        b = b[:i]
    b = b.rstrip()
    return os.path.basename(
        util.bytes_to_str(b))

def get_procfs_mount_point():
    return get_fs_mount_point("proc", "procfs")

def get_fs_mount_point(*fs):
    try:
        s = util.execute("mount")[0]
    except Exception:
        return ''
    for x in s.split('\n'):
        m = re.search(r"^(.+)\s+on\s+(.+?)\s", x)
        if m:
            name, where = m.groups()
            if name in fs:
                if os.path.isdir(where):
                    return os.path.abspath(where)
    return ''

_mount = setting.procfs_mount_point
if not os.path.isdir(_mount):
    try:
        _mount = get_procfs_mount_point()
    except Exception:
        _mount = ''
        if setting.use_debug:
            raise
