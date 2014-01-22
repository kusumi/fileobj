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
import stat

from . import util

# no os.path.relpath till Python 2.6
_has_relpath = util.is_python_version_or_ht(2, 6, 0)

_t_noent, \
_t_noperm, \
_t_link, \
_t_file, \
_t_dir, \
_t_blkdev, \
_t_chrdev, \
_t_unknown, \
_t_error = [2 ** x for x in range(9)]

_sep = os.path.sep
_cwd = os.getcwd()
_home = os.getenv("HOME", '')

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
    def is_file(self):
        return _test(self.__type, _t_file)
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

    def _get_type_string(self):
        ret = []
        if self.is_noent:
            ret.append("noent")
        if self.is_noperm:
            ret.append("noperm")
        if self.is_link:
            ret.append("link")
        if self.is_file:
            ret.append("file")
        if self.is_dir:
            ret.append("dir")
        if self.is_blkdev:
            ret.append("blkdev")
        if self.is_chrdev:
            ret.append("chrdev")
        if self.is_unknown:
            ret.append("unknown")
        if self.is_error:
            ret.append("error")
        return '|'.join(ret)
    type = property(_get_type_string)

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
    if not f:
        return ''
    if f == _cwd:
        return '.'
    if f.startswith(_cwd + _sep): # no os.path.join here
        return f.replace(_cwd, '.')
    if f == _home:
        return '~'
    if _home and f.startswith(_home + _sep): # no os.path.join here
        return f.replace(_home, '~')
    if _has_relpath:
        rel = os.path.relpath(f, _cwd)
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
            a = os.access(s, os.R_OK)

    if os.path.isfile(f):
        return _t_file
    elif os.path.isdir(f):
        return _t_dir
    elif stat.S_ISBLK(os.stat(f).st_mode):
        return _t_blkdev
    elif stat.S_ISCHR(os.stat(f).st_mode):
        return _t_chrdev
    else:
        return _t_unknown

def is_noent(f):
    return _test(get_type(f), _t_noent)
def is_noperm(f):
    return _test(get_type(f), _t_noperm)
def is_link(f):
    return _test(get_type(f), _t_link)
def is_file(f):
    return _test(get_type(f), _t_file)
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

def get_path_failure_message(o):
    f = o.path
    if o.is_dir:
        return f + " is a directory"
    elif o.is_noperm:
        return "Permission denied: " + f
    elif o.is_unknown:
        return "Unknown path: " + f
    elif o.is_error:
        return "Invalid path: " + f
