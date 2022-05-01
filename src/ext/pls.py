# Copyright (c) 2022, Tomohiro Kusumi
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
from .. import fileops
from .. import panel
from .. import util

def get_text(co, fo, args):
    l = list(panel.iter_page_line_state())
    if not l:
        return "No page line state"
    title = '', "key", "value"

    kl = []
    vl = []
    for i, x in enumerate(l):
        assert isinstance(x, tuple), x
        assert len(x) == 2, x
        k, v = x
        assert isinstance(k, fileops.Fileops), k
        assert isinstance(v, util.Namespace), v
        ks, vs = panel.get_page_line_state_string(k)
        kl.append(ks)
        vl.append(vs)

    _ = [len(_) for _ in kl]
    _.append(len(title[1]))
    kn = max(_)

    _ = [len(_) for _ in vl]
    _.append(len(title[2]))
    vn = max(_)

    f = "{{0:{0}}} {{1:<{1}}} {{2:<{2}}}".format(extension.get_index_width(kl),
        kn, vn)
    sl = [f.format(*title)]
    for i in range(len(kl)):
        sl.append(f.format(i + 1, kl[i], vl[i]))
    return sl
