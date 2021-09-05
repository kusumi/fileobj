# Copyright (c) 2010, Tomohiro Kusumi
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

from .. import extension
from .. import filebytes
from .. import kernel
from .. import screen
from .. import setting
from .. import util

def get_text(co, fo, args):
    if not fo.get_size():
        return "Empty buffer"

    arg_pos = args.pop()
    buf, beg, rem, typ = extension.parse_region(co, fo, arg_pos)
    pos = beg

    # XXX properly handle string overlapping >1 siz sized buffers
    siz = kernel.get_buffer_size()
    lim = beg + rem - 1
    l = []

    while True:
        if buf:
            relpos = pos - beg
            b = buf[relpos:relpos + siz]
        else:
            b = fo.read(pos, siz)
        assert b, (beg, pos, rem, len(b))
        n = 0
        for i, c in enumerate(filebytes.iter_ords(b)):
            if util.isprint(c):
                n += 1
                if (pos + i == lim) or (i == len(b) - 1):
                    if n >= setting.ext_strings_thresh:
                        # +1 difference from below
                        s = filebytes.str(b[i - n + 1:i + 1])
                        l.append((pos + i - n + 1, s))
                        break
            else:
                if n >= setting.ext_strings_thresh:
                    s = filebytes.str(b[i - n:i])
                    l.append((pos + i - n, s))
                n = 0
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
    sl.append("Found {0} string{1}".format(len(l), "s" if len(l) > 1 else ""))

    if l:
        sl.append('')
        n0 = max([len(str(x[0])) for x in l])
        n1 = max([len(hex(x[0])) for x in l])
        f = "{{0:>{0}}} {{1:>{1}}} {{2}}".format(n0, n1)
        for i, x in enumerate(l):
            offset0 = x[0]
            offset1 = hex(offset0)
            sl.append(f.format(offset0, offset1, x[1]))
    return sl

def init():
    setting.ext_add_gt_zero("strings_thresh", 3,
        "Set number of minimum string length for :strings. "
        "Defaults to 3 if undefined.")

def cleanup():
    setting.ext_delete("strings_thresh")

init()
