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

from . import util

_ = util.str_to_bytes

def input_to_bytes(l):
    return util.str_to_bytes(
        ''.join([chr(x) for x in l]))

def bytes_to_input(b):
    return ords(b)

def __ord_2k(b):
    return __builtin_ord(b)

def __ord_3k(b):
    return b[0]

def __split_2k(b):
    return list(b)

def __split_3k(b):
    return [b[i : i + 1] for i in range(len(b))]

def __iter_2k(b):
    for x in b:
        yield x

def __iter_3k(b):
    for i in range(len(b)):
        yield b[i : i + 1]

def __riter_2k(b):
    for x in reversed(b):
        yield x

def __riter_3k(b):
    for i in reversed(range(len(b))):
        yield b[i : i + 1]

# Remove extra stuff from builtin repr
def __str_2k(b):
    if b is None:
        return __builtin_str(None)
    else:
        return __builtin_repr(b)[1:-1] # cut ' and '

def __str_3k(b):
    if b is None:
        return __builtin_str(None)
    elif isinstance(b, TYPE):
        return __builtin_repr(b)[2:-1] # cut b' and '
    else:
        return __str_2k(b)

def join(l):
    return BLANK.join(l)

def ords(b, cls=tuple):
    return cls(ord(x) for x in iter(b))

def seq_to_ords(l, cls=tuple):
    return cls(ord(x) for x in l)

def pad(x):
    return ZERO * x

def rstrip(b):
    i = b.find(ZERO)
    if i != -1:
        b = b[:i]
    return b.rstrip()

__builtin_ord = util.get_builtin("ord")
__builtin_str = util.get_builtin("str")
__builtin_repr = util.get_builtin("repr")

if util.is_python2():
    TYPE = str
    ZERO = "\x00"
    BLANK = ''
    ord = __ord_2k
    split = __split_2k
    iter = __iter_2k
    riter = __riter_2k
    str = __str_2k
else:
    TYPE = bytes
    ZERO = _("\x00")
    BLANK = _('')
    ord = __ord_3k
    split = __split_3k
    iter = __iter_3k
    riter = __riter_3k
    str = __str_3k
