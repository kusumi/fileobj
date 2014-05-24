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

from . import util

_ = util.str_to_bytes

def input_to_bytes(l):
    return util.str_to_bytes(
        ''.join([chr(x) for x in l]))

def __ord_2k(b):
    return builtin_ord(b)

def __ord_3k(b):
    if isinstance(b, bytes):
        return b[0]
    elif isinstance(b, int):
        return b
    else:
        assert 0, (b, type(b))

def join(l):
    return BLANK.join(l)

def __split_2k(b):
    return list(b)

def __split_3k(b):
    return [b[i : i + 1] for i in range(len(b))]

if util.is_python2():
    import __builtin__ as builtin
    TYPE = str
    ZERO = "\x00"
    BLANK = ''
    SPACE = ' '
    ord = __ord_2k
    split = __split_2k
else:
    import builtins as builtin
    TYPE = bytes
    ZERO = _("\x00")
    BLANK = _('')
    SPACE = _(' ')
    ord = __ord_3k
    split = __split_3k

builtin_ord = builtin.ord

def ordl(b):
    return [ord(x) for x in b]

def ordt(b):
    return tuple(ord(x) for x in b)
