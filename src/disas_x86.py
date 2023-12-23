# Copyright (c) 2021, Tomohiro Kusumi
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

from . import log
from . import setting
from . import util

valid_mode = 16, 32, 64
default_mode = 64

try:
    import distorm3 as _distorm
except ImportError:
    try:
        # XXX not sure if this is really compatible
        import distorm as _distorm
    except ImportError:
        _distorm = None

def get_module():
    return _distorm

def get_module_name():
    distorm = get_module()
    if distorm:
        return distorm.__name__
    else:
        return "distorm3"

def get_module_install_cmd():
    return "{0} -m pip install {1}".format(util.get_python_string(),
        get_module_name())

def is_supported():
    return get_module() is not None

def decode(pos, buf, mode, greedy=-1):
    distorm = get_module()
    assert distorm is not None

    if mode == 16:
        mode = distorm.Decode16Bits
        mode_is_16 = True
    elif mode == 32:
        mode = distorm.Decode32Bits
        mode_is_16 = False
    elif mode == 64:
        mode = distorm.Decode64Bits
        mode_is_16 = False
    else:
        assert False, mode

    # decode the buffer
    l = []
    total_size = 0
    for x in distorm.Decode(pos, buf, mode):
        # offset(int), size(int), hexstr(str), mnemonic(str)
        l.append((x[0], x[1], x[3], x[2]))
        total_size += x[1]

    if setting.use_debug:
        for i, x in enumerate(l):
            if i != 0:
                prevx = l[i - 1]
                if prevx[0] < x[0]: # else overflowed
                    assert prevx[0] + prevx[1] == x[0], ("hole", i, prevx, x)
                else:
                    assert mode_is_16, mode

    last_offset, last_size, _, last_mnemonic = l[-1]
    next_asm_pos = last_offset + last_size
    next_buf_pos = pos + len(buf)
    delta = 0

    # adjust trailing bytes
    if next_asm_pos != next_buf_pos and not mode_is_16: # XXX
        d = next_buf_pos - next_asm_pos
        assert d > 0, (next_asm_pos, next_buf_pos)
        log.debug("{0} undo trailing unused {1} bytes".format(this_name, d))
        delta += d

    # undo trailing bytes
    if greedy == 1:
        if len(l) > 1 and last_mnemonic.startswith("DB "):
            log.debug("{0} undo trailing {1}".format(this_name, l[-1]))
            delta += last_size
            del l[-1]
        else:
            log.debug("{0} done trailing {1}".format(this_name, l[-1]))
        return l, delta
    elif greedy == 2:
        if total_size >= 15:
            resid = 15
            count = 0
            for x in reversed(l):
                resid -= x[1]
                if resid <= 0: # undo < 15 bytes
                    break
                index = len(l) - 1 - count
                log.debug("{0} undo trailing {1} at {2}".format(this_name, x,
                    index))
                delta += x[1]
                count += 1
            for x in range(count):
                del l[-1]
        else:
            log.debug("{0} done trailing {1} total {2} bytes".format(this_name,
                l, total_size))
        return l, delta
    else:
        return l, delta

this = sys.modules[__name__]
this_name = this.__name__
