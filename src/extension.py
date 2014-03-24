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

import re

from . import panel
from . import util

class ExtError (util.GenericError):
    pass

class ExtBinaryCanvas (panel.DisplayCanvas, panel.default_addon):
    def set_buffer(self, fileops):
        super(ExtBinaryCanvas, self).set_buffer(fileops)
        if self.fileops:
            self.fileops.ioctl(self.bufmap.x)

    def chgat_cursor(self, pos, attr, low):
        y, x = self.get_coordinate(pos)
        self.chgat(y, x, 1, attr)

    def alt_chgat_cursor(self, pos, attr, low):
        """Alternative for Python 2.5"""
        y, x = self.get_coordinate(pos)
        c = self.fileops.read(pos, 1)
        s = self.get_form_single(c) if c else ' '
        self.printl(y, x, s, attr)

class ExtTextCanvas (panel.DisplayCanvas, panel.default_addon):
    def iter_buffer(self):
        s = ' ' * self.bufmap.x
        for i in range(self.bufmap.y):
            yield i, s

def fail(s):
    raise ExtError(s)

def raw_to_buffer(raw, width):
    l = []
    for b in raw.split('\n'):
        if not b:
            l.append(' ' * width)
        else:
            b = b.replace('\t', '    ')
            s = b[:width]
            while s:
                if len(s) < width:
                    s += ' ' * (width - len(s))
                l.append(s)
                b = b[width:]
                s = b[:width]
    return ''.join(l).rstrip()

def get_path(o):
    f = o.get_path()
    if re.search(r"/<.+ object at .+>$", f):
        return o.get_short_path()
    else:
        return f
