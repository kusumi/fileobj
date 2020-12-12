# Copyright (c) 2009, Tomohiro Kusumi
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

from . import kernel
from . import setting
from . import util

# no os.path.relpath till Python 2.6
_has_relpath = util.is_python_version_or_ht(2, 6, 0)

_t_noent   = 1 << 0
_t_noperm  = 1 << 1
_t_link    = 1 << 2
_t_reg     = 1 << 3
_t_dir     = 1 << 4
_t_blkdev  = 1 << 5
_t_chrdev  = 1 << 6
_t_unknown = 1 << 7
_t_error   = 1 << 8

_sep = os.path.sep
_home = setting.get_home_dir()

class Path (object):
    def __init__(self, f):
        f = get_path(f)
        self.__path = f
        self.__short_path = _get_short_path(f)
        self.__type = _get_type(f)

    path = property(lambda self: self.__path)
    short_path = property(lambda self: self.__short_path)

    @property
    def is_noent(self):
        return _test(self.__type, _t_noent)

    @property
    def is_noperm(self):
        return _test(self.__type, _t_noperm)

    @property
    def is_link(self):
        return _test(self.__type, _t_link)

    @property
    def is_reg(self):
        return _test(self.__type, _t_reg)

    @property
    def is_dir(self):
        return _test(self.__type, _t_dir)

    @property
    def is_blkdev(self):
        return _test(self.__type, _t_blkdev)

    @property
    def is_chrdev(self):
        return _test(self.__type, _t_chrdev)

    @property
    def is_unknown(self):
        return _test(self.__type, _t_unknown)

    @property
    def is_error(self):
        return _test(self.__type, _t_error)

    def __get_type_string(self):
        ret = []
        if self.is_noent:
            ret.append("NOENT")
        if self.is_noperm:
            ret.append("NOPERM")
        if self.is_link:
            ret.append("LINK")
        if self.is_reg:
            ret.append("REG")
        if self.is_dir:
            ret.append("DIR")
        if self.is_blkdev:
            ret.append("BLKDEV")
        if self.is_chrdev:
            ret.append("CHRDEV")
        if self.is_unknown:
            ret.append("UNKNOWN")
        if self.is_error:
            ret.append("ERROR")
        return '|'.join(ret)
    type = property(__get_type_string)

def get_path(f):
    if not f:
        return ''
    if os.path.isabs(f):
        a = os.path.normpath(f)
    else:
        x = os.path.expanduser(f)
        a = os.path.abspath(x)

    # behave differently from os.path.xxxpath()
    if a.startswith(_sep * 2):
        a = a[len(_sep):]
    if a != _sep and f.endswith(_sep):
        a += _sep
    return a

def get_short_path(f):
    return _get_short_path(get_path(f))

def _get_short_path(f):
    # unittests cd to other dirs, so get cwd for each call
    cwd = os.getcwd()
    if not f:
        return ''
    if f == cwd:
        return '.'
    if f.startswith(cwd + _sep): # no os.path.join here
        return f.replace(cwd, '.')
    if f == _home:
        return '~'
    if f.startswith(_home + _sep): # no os.path.join here
        return f.replace(_home, '~')
    if _has_relpath:
        rel = os.path.relpath(f, cwd)
        if len(rel) < len(f):
            return rel
    return f

def get_type(f):
    return _get_type(get_path(f))

def _get_type(f):
    if os.path.islink(f):
        f = os.path.realpath(f)
        return _get_type_real(f) | _t_link
    else:
        return _get_type_real(f)

def _get_type_real(f):
    if not f:
        return _t_error
    if not os.path.exists(f):
        i = -1
        a = False
        while True:
            i = f.find(_sep, i + 1)
            if i == -1:
                s = f
            else:
                s = f[:i + 1]
            if not os.path.exists(s):
                if a:
                    if i == -1:
                        return _t_noent
                    else:
                        return _t_error
                else:
                    return _t_noperm
            a = util.is_read_ok(s)
    ret = 0
    d = kernel.stat_type(f)
    if d.get("REG", False):
        ret |= _t_reg
    if d.get("DIR", False):
        ret |= _t_dir
    if d.get("BLKDEV", False):
        ret |= _t_blkdev
    if d.get("CHRDEV", False):
        ret |= _t_chrdev
    if not ret:
        return _t_unknown
    else:
        return ret

def is_noent(f):
    return _test(get_type(f), _t_noent)

def is_noperm(f):
    return _test(get_type(f), _t_noperm)

def is_link(f):
    return _test(get_type(f), _t_link)

def is_reg(f):
    return _test(get_type(f), _t_reg)

def is_dir(f):
    return _test(get_type(f), _t_dir)

def is_blkdev(f):
    return _test(get_type(f), _t_blkdev)

def is_chrdev(f):
    return _test(get_type(f), _t_chrdev)

def is_unknown(f):
    return _test(get_type(f), _t_unknown)

def is_error(f):
    return _test(get_type(f), _t_error)

def _test(x, bits):
    return (x & bits) != 0

def is_canonical_type(o):
    if o.is_noperm or o.is_dir or o.is_unknown:
        return False
    elif o.is_error and o.path != '':
        return False
    else:
        return True

def get_path_failure_message(o, allow_link=True):
    if not kernel.get_kernel_module():
        return "Failure: " + kernel.get_status_string()
    f = o.path
    if o.is_dir:
        return f + " is a directory"
    if o.is_link and not allow_link:
        return "Ignoring a link: " + f
    elif o.is_noperm:
        return "Permission denied: " + f
    elif o.is_unknown:
        return "Unknown path: " + f
    elif o.is_error:
        return "Invalid path: " + f

def iter_blkdev(ignore_symlink=True):
    d = "/dev"
    if kernel.is_xnix() and os.path.isdir(d):
        l = []
        for root, dirs, files in os.walk(d):
            for x in files:
                f = os.path.join(root, x)
                if kernel.is_blkdev(f):
                    if not is_link(f) or not ignore_symlink:
                        l.append(f)
        for f in sorted(l):
            yield f
