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

import sys

from . import setting

_ = [
"NUL",
"SOH",
"STX",
"ETX",
"EOT",
"ENQ",
"ACK",
"BEL",
"BS",
"HT",
"LF",
"VT",
"FF",
"CR",
"SO",
"SI",
"DLE",
"DC1",
"DC2",
"DC3",
"DC4",
"NAK",
"SYN",
"ETB",
"CAN",
"EM",
"SUB",
"ESC",
"FS",
"GS",
"RS",
"US",
]
_.extend([chr(x) for x in range(32, 127)])
_.append("DEL")
assert len(_) == 128, _

_list = tuple(_)
_dict = dict([(i, _list[i]) for i in range(len(_list))])
del _

this = sys.modules[__name__]
for _ in _dict.items():
    try:
        setattr(this, _[1], _[0]) # reverse map
    except Exception:
        if setting.use_debug:
            raise
del _
setattr(this, "SP", 0x20)

def get_binary(x):
    return getattr(this, x, -1)

def get_symbol(x):
    return _dict.get(x, '')

def iter_ascii_symbol():
    for s in _list:
        yield s
