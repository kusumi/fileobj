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

import struct
import sys

# taken from linux Python 3.4 ctypes
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

def __normalize_name(s):
    if s.startswith("c_"):
        s = s[2:]
    return s

def __init_ctypes():
    for k in iter_type_name():
        if not hasattr(ctypes, k):
            __register_sizeof_function(k, -1)
            continue
        try:
            v = getattr(ctypes, k)
            type_size = ctypes.sizeof(v)
            __register_sizeof_function(k, type_size)
        except Exception:
            __register_sizeof_function(k, -1)

def __init_pseudo():
    for k in iter_type_name():
        __register_sizeof_function(k, -1)

def __register_sizeof_function(type_name, type_size):
    s = __build_sizeof_function_name(type_name)
    def fn():
        return type_size
    setattr(this, s, fn)

def __build_sizeof_function_name(type_name):
    return "get_sizeof_%s" % __normalize_name(type_name)

def iter_type():
    for k in iter_type_name():
        s = __build_sizeof_function_name(k)
        fn = getattr(this, s)
        yield __normalize_name(k), s, fn

def iter_defined_type():
    for name, func_name, fn in iter_type():
        if fn() != -1:
            yield name, func_name, fn

def iter_undefined_type():
    for name, func_name, fn in iter_type():
        if fn() == -1:
            yield name, func_name, fn

def get_pointer_size():
    ret = this.get_sizeof_void_p()
    if ret != -1:
        return ret
    else:
        return struct.calcsize('P')

this = sys.modules[__name__]
try:
    import ctypes
    __init_ctypes()
except ImportError:
    __init_pseudo()
