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

from __future__ import division

import datetime
import timeit

from .. import disas_x86
from .. import extension
from .. import kernel
from .. import screen
from .. import setting
from .. import util

_debugint = -1
_debugstr = "#"

def get_text(co, fo, args):
    if not fo.get_size():
        return "Empty buffer"

    if not disas_x86.is_supported():
        return "Unsupported, install {0} (e.g. {1})".format(
            disas_x86.get_module_name(), disas_x86.get_module_install_cmd())

    arg_pos = args.pop()
    buf, beg, rem, typ = extension.parse_region(co, fo, arg_pos)
    pos = beg

    if len(args) > 0:
        try:
            mode = int(args[0])
            if mode not in disas_x86.valid_mode:
                return "Invalid mode {0}".format(mode)
        except ValueError as e:
            return "Invalid mode: {0}".format(e)
    else:
        mode = disas_x86.default_mode

    siz = kernel.get_buffer_size()
    time_beg = timeit.default_timer()
    l = []

    while True:
        if buf:
            relpos = pos - beg
            b = buf[relpos:relpos + siz]
        else:
            b = fo.read(pos, siz)
        assert b, (beg, pos, rem, len(b))
        try:
            ret, delta = disas_x86.decode(pos, b, mode, 2)
        except Exception as e:
            return "Failed to disassemble: {0}".format(e)
        l.extend(ret)
        if setting.use_debug:
            l.append((_debugint, _debugint, _debugstr, _debugstr))
        # cut trailing bytes of b if >0 delta
        if delta > 0:
            b = b[:-delta]
            if not b: # shouldn't happen
                if setting.use_debug:
                    assert False, (beg, pos, rem, len(b), delta)
                break
        pos += len(b)
        rem -= len(b)
        if rem <= 0:
            break
        if screen.test_signal():
            co.flash("Interrupted ({0})".format(pos))
            break

    sl = ["{0} {1}-{2}".format(typ, util.get_size_repr(beg),
        util.get_size_repr(pos - 1))]
    if setting.use_debug:
        sl.append("{0} {1}-{2}".format(typ, hex(beg), hex(pos - 1)))
    sl.append("Using {0}".format(disas_x86.get_module()))
    sl.append("Using decode mode {0}".format(mode))
    total_size = sum([x[1] for x in l if x[0] != _debugint]) # size
    sl.append("Found {0} instruction{1} in {2} byte{3}".format(len(l),
        "s" if len(l) > 1 else "", total_size, "s" if total_size > 1 else ""))
    time_index = len(sl)
    sl.append(None)

    if l:
        sl.append('')
        n0 = max([len(hex(x[0])[2:]) for x in l if x[0] != _debugint]) # offset
        if n0 % 2 == 0:
            n0 += 2
        else:
            n0 += 1 # make n0 even
        assert n0 % 2 == 0, n0
        n1 = max([len(x[2]) for x in l if x[0] != _debugint]) # hexstr
        assert n1 % 2 == 0, n1
        f = "{{0:0{0}x}} {{1:2d}} {{2:<{1}}} {{3:<{2}}} {{4}}".format(n0, n1,
            n1 // 2)
        for x in l:
            asciistr = conv_hexstr_to_asciistr(x[2])
            sl.append(f.format(x[0], x[1], x[2], asciistr, x[3]))

    time_end = timeit.default_timer()
    assert sl[time_index] is None, sl[time_index]
    sl[time_index] = "Time elapsed {0}".format(datetime.timedelta(
        seconds=time_end - time_beg))
    return sl

def conv_hexstr_to_asciistr(hexstr):
    if setting.use_debug:
        if hexstr == _debugstr:
            return _debugstr
    assert isinstance(hexstr, str), hexstr
    assert len(hexstr) % 2 == 0, hexstr
    l = []
    for _ in range(len(hexstr) // 2):
        i = _ * 2
        s = "0x" + hexstr[i:i+2]
        l.append(screen.chr_repr[int(s, 16)])
    return ''.join(l)
