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

from __future__ import division

import fileobj.extension
import fileobj.util

def get_text(co, fo, args):
    l = list(co.iter_buffer())
    assert l
    title = '', "buffer", "#undo", "#redo", "#rollback"

    l1 = [len(fileobj.extension.get_path(o)) for o in l]
    l1.append(len(title[1]))
    l2 = [len(str(o.get_undo_size())) for o in l]
    l2.append(len(title[2]))
    l3 = [len(str(o.get_redo_size())) for o in l]
    l3.append(len(title[3]))
    l4 = [len(str(o.get_rollback_log_size())) for o in l]
    l4.append(len(title[4]))

    n = len(l)
    x = 0
    while n:
        n //= 10
        x += 1
    d = {   "num"      : x,
            "path"     : max(l1),
            "undo"     : max(l2),
            "redo"     : max(l3),
            "rollback" : max(l4), }
    f = fileobj.util.get_string_format(
        "%${num}s %-${path}s %${undo}s %${redo}s %${rollback}s", **d)
    sl = [f % title]
    for i, o in enumerate(l):
        sl.append(f % (i + 1, fileobj.extension.get_path(o),
            o.get_undo_size(), o.get_redo_size(),
            o.get_rollback_log_size()))
    return sl
