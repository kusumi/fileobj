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

import fileobj.filebytes
import fileobj.util

def get_text(co, fo, args):
    siz = fo.get_size()
    if not siz:
        return "Empty buffer"

    pos = args.pop()
    siz -= pos
    if siz > fileobj.setting.ext_strings_range:
        siz = fileobj.setting.ext_strings_range

    l = []
    b = fo.read(pos, siz)
    if b:
        n = 0
        for i, c in enumerate(b):
            if fileobj.util.is_graph(c):
                n += 1
            else:
                if n >= fileobj.setting.ext_strings_thresh:
                    s = b[i - n:i]
                    if fileobj.filebytes.TYPE is not str:
                        s = "{0}".format(s)[2:-1] # cut b' and '
                    l.append((pos + i - n, s))
                    if len(l) >= fileobj.setting.ext_strings_count:
                        break
                n = 0
        if len(b) == n:
            l = [(pos, b)]

    sl = ["Range {0}-{1}".format(
        fileobj.util.get_size_string(pos),
        fileobj.util.get_size_string(pos + siz))]
    sl.append("Found {0} strings".format(len(l)))

    if l:
        sl.append('')
        n = max([len(str(x[0])) for x in l])
        f = "{{0:{0}}} {{1}}".format(n)
        for i, x in enumerate(l):
            sl.append(f.format(x[0], x[1]))
    return sl
