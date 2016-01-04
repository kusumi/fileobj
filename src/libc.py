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

import errno
import sys

from . import setting

# taken from Linux Python 3.4 ctypes
def iter_type_name():
    yield "c_bool"
    yield "c_byte"
    yield "c_char"
    yield "c_char_p"
    yield "c_double"
    yield "c_float"
    yield "c_int"
    yield "c_int16"
    yield "c_int32"
    yield "c_int64"
    yield "c_int8"
    yield "c_long"
    yield "c_longdouble"
    yield "c_longlong"
    yield "c_short"
    yield "c_size_t"
    yield "c_ssize_t"
    yield "c_ubyte"
    yield "c_uint"
    yield "c_uint16"
    yield "c_uint32"
    yield "c_uint64"
    yield "c_uint8"
    yield "c_ulong"
    yield "c_ulonglong"
    yield "c_ushort"
    yield "c_void_p"
    yield "c_voidp"
    yield "c_wchar"
    yield "c_wchar_p"

TYPE_PREFIX = "c_"

def __init_libc():
    global _libc, get_errno
    name = ctypes.util.find_library("c")
    _libc = ctypes.CDLL(name, use_errno=True)
    def get_errno():
        ret = ctypes.get_errno()
        ctypes.set_errno(0)
        return ret

def get_errno():
    return errno.EPERM

def init_ptrace(data_type):
    if hasattr(_libc, "ptrace"):
        s = TYPE_PREFIX + data_type
        _ = getattr(ctypes, s, None)
        if _:
            _libc.ptrace.dattype = _
            _libc.ptrace.restype = _

def has_ptrace():
    if not hasattr(_libc, "ptrace"):
        return False
    if not hasattr(_libc.ptrace, "dattype"):
        return False # call init_ptrace() first
    return True

def get_ptrace_data_size():
    if has_ptrace():
        return ctypes.sizeof(_libc.ptrace.dattype)
    else:
        return -1

def ptrace(request, pid, addr, data):
    """Return None, errno on error"""
    if not has_ptrace():
        return None, 0
    if request == -1:
        return None, 0
    if addr is not None:
        addr = ctypes.c_long(addr)
    if data is not None:
        data = _libc.ptrace.dattype(data)
    ret = _libc.ptrace(request, pid, addr, data)
    err = get_errno()
    if ret == -1 and err != 0:
        return None, err
    else:
        return ret, err

def __init_types():
    for k in iter_type_name():
        try:
            v = getattr(ctypes, k)
            __register_type(k, ctypes.sizeof(v))
        except Exception:
            __register_type(k, -1)

# keep this separated from __init_types()
def __register_type(type_name, type_size):
    s = __get_type_function_name(type_name)
    setattr(this, s, lambda: type_size)

def iter_type():
    for k in iter_type_name():
        s = __get_type_function_name(k)
        fn = getattr(this, s)
        yield _(k), s, fn

def __get_type_function_name(type_name):
    return "get_sizeof_" + _(type_name)

def _(s):
    return s[len(TYPE_PREFIX):]

def iter_defined_type():
    for name, func_name, fn in iter_type():
        if fn() != -1:
            yield name, func_name, fn

def iter_undefined_type():
    for name, func_name, fn in iter_type():
        if fn() == -1:
            yield name, func_name, fn

this = sys.modules[__name__]
_libc = None

try:
    import ctypes
    import ctypes.util
except Exception:
    if setting.use_debug:
        raise
try:
    __init_types()
    if tuple(sys.version_info[:2]) >= (2, 6):
        __init_libc()
except Exception:
    if setting.use_debug:
        raise
