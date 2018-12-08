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

import fileobj.env
import fileobj.extension
import fileobj.filebytes
import fileobj.kbd
import fileobj.kernel
import fileobj.screen
import fileobj.setting
import fileobj.util

def get_text(co, fo, args):
    tot = fo.get_size()
    if not tot:
        return "Empty buffer"

    beg = args.pop()
    pos = beg
    rem = tot - pos
    if fileobj.extension.test_dryrun():
        if rem > 1024:
            rem = 1024

    siz = fileobj.kernel.get_buffer_size()
    l = []

    while True:
        b = fo.read(pos, siz)
        if b:
            n = 0
            for i, c in enumerate(fileobj.filebytes.iter_ords(b)):
                if fileobj.kbd.isprint(c):
                    n += 1
                else:
                    if n >= fileobj.setting.ext_strings_thresh:
                        s = fileobj.filebytes.str(b[i - n:i])
                        l.append((pos + i - n, s))
                    n = 0
            if len(b) == n:
                l = [(pos, b)]
        pos += len(b)
        rem -= len(b)
        if rem <= 0:
            break
        if fileobj.screen.test_signal():
            co.flash("Interrupted ({0})".format(pos))
            break

    sl = ["Range {0}-{1}".format(
        fileobj.util.get_size_repr(beg),
        fileobj.util.get_size_repr(pos - 1))]
    sl.append("Found {0} strings".format(len(l)))

    if l:
        sl.append('')
        n = max([len(str(x[0])) for x in l])
        f = "{{0:{0}}} {{1}}".format(n)
        for i, x in enumerate(l):
            sl.append(f.format(x[0], x[1]))
    return sl

def init():
    fileobj.setting.ext_add_gt_zero("strings_thresh", 3)

def cleanup():
    fileobj.setting.ext_delete("strings_thresh")

init()
