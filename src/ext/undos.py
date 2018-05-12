# Copyright (c) 2013, Tomohiro Kusumi
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

import os

import fileobj.extension

def get_text(co, fo, args):
    l = list(co.iter_buffer())
    assert l
    title = '', " ", "buffer", "#undo", "#redo", "#rollback"

    l1 = [len(fileobj.extension.get_verbose_path(o)) for o in l]
    l1.append(len(title[2]))
    l2 = [len(str(o.get_undo_size())) for o in l]
    l2.append(len(title[3]))
    l3 = [len(str(o.get_redo_size())) for o in l]
    l3.append(len(title[4]))
    l4 = [len(str(o.get_rollback_log_size())) for o in l]
    l4.append(len(title[5]))

    f = "{{0:{0}}} {{1}} {{2:<{1}}} {{3:{2}}} {{4:{3}}} {{5:{4}}}".format(
        fileobj.extension.get_index_width(l),
        max(l1), max(l2), max(l3), max(l4))
    sl = [f.format(*title)]
    for i, o in enumerate(l):
        c = " " if os.path.exists(o.get_path()) else "!"
        sl.append(f.format(i + 1, c, fileobj.extension.get_verbose_path(o),
            o.get_undo_size(), o.get_redo_size(), o.get_rollback_log_size()))
    return sl
