# Copyright (c) 2013, Tomohiro Kusumi
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

from . import path
from . import undo
from . import util

_attrd = {}

def clear():
    _attrd.clear()

def get_keys():
    return tuple(_attrd.keys())

def has_key(f):
    return f in _attrd

def get(f):
    f = path.get_path(f)
    if has_key(f):
        return _attrd.get(f)
    else:
        return _attrd.setdefault(f, __alloc())

def __alloc():
    return util.Namespace(
        magic = '',
        offset = 0,
        length = 0,
        word = util.str_to_bytes(''),
        marks = {},
        session = {},
        undo = undo.Undo())

def remove(f):
    f = path.get_path(f)
    if has_key(f):
        del _attrd[f]
    else:
        return -1

def rename(old, new):
    old = path.get_path(old)
    if not has_key(old):
        return -1
    new = path.get_path(new)
    if has_key(new):
        return -1
    if old == new:
        return -1
    _attrd[new] = _attrd[old]
    return remove(old)

def stash_save(name, tmp_name=None):
    attr = _attrd[name]
    assert attr, name
    _attrd[tmp_name] = attr

def stash_restore(name, tmp_name=None):
    attr = _attrd[tmp_name]
    assert attr, tmp_name
    _attrd[name] = attr
