# Copyright (c) 2009, Tomohiro Kusumi
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
from __future__ import with_statement

import os
import re

from . import filebytes
from . import kernel
from . import panel
from . import screen
from . import util

class Error (util.GenericError):
    pass

class methods (object):
    def init_raw(self, raw):
        self.raw = raw
        self.__first_fill = True

    def fill_chunk(self, width):
        if self.is_empty() and self.__first_fill:
            self.init_chunk(self.__get(width))
            self.__first_fill = False

    def write_raw(self, f):
        with kernel.fcreat_text(f) as fd:
            fd.write(self.raw)
            kernel.fsync(fd)

    def __get(self, width):
        if not width:
            return ''
        l = []
        for b in self.raw.split('\n'):
            if b:
                b = b.replace('\t', '    ')
                s = b[:width]
                while s:
                    if len(s) < width:
                        s += ' ' * (width - len(s))
                    l.append(s)
                    b = b[width:]
                    s = b[:width]
            else:
                l.append(' ' * width)
        return ''.join(l).rstrip()

class ExtBinaryCanvas (panel.DisplayCanvas, panel.default_attribute):
    def set_buffer(self, fileops):
        super(ExtBinaryCanvas, self).set_buffer(fileops)
        if self.fileops is not None:
            self.fileops.ioctl(self.bufmap.x)

    def get_str_single(self, x):
        return _get_str_single(x)

    def get_str_line(self, buf):
        return ''.join([self.get_str_single(x) for x in filebytes.ords(buf)])

    def chgat_cursor(self, pos, attr1, attr2, low):
        y, x = self.get_coordinate(pos)
        self.chgat(y, x, 1, attr1)

    def alt_chgat_cursor(self, pos, attr1, attr2, low):
        y, x = self.get_coordinate(pos)
        s = self.read_form_single(pos)
        self.addstr(y, x, s, attr1)

    def chgat_search(self, pos, attr1, attr2, here):
        y, x = self.get_coordinate(pos)
        if here:
            self.chgat(y, x, 1, attr1)
        else:
            self.chgat(y, x, 1, attr2)

    def alt_chgat_search(self, pos, attr1, attr2, here):
        y, x = self.get_coordinate(pos)
        s = self.read_form_single(pos)
        if here:
            self.addstr(y, x, s, attr1)
        else:
            self.addstr(y, x, s, attr2)

class ExtTextCanvas (panel.DisplayCanvas, panel.default_attribute):
    def iter_line_buffer(self):
        s = filebytes.SPACE * self.bufmap.x
        for i in util.get_xrange(self.bufmap.y):
            yield i, s, screen.A_NONE

    def get_str_single(self, x):
        return _get_str_single(x)

    def get_str_line(self, buf):
        return ''.join([self.get_str_single(x) for x in filebytes.ords(buf)])

    def get_geom_pos(self, y, x):
        return -1

# Avoid returning "\x00", scr.addstr("\x00") raises
# ValueError: embedded null character (Python 3)
# TypeError: must be string without null bytes, not str (Python 2)
def _get_str_single(x):
    if x == 0:
        return '.'
    return chr(x)

def fail(s):
    raise Error(s)

def get_path(o):
    f = o.get_path()
    s = r"{0}<.+ object at .+>$".format(os.path.sep)
    if re.search(s, f):
        return o.get_short_path()
    else:
        return f

def get_verbose_path(o):
    f = get_path(o)
    if not f:
        return util.NO_NAME
    else:
        return f

def get_index_width(l):
    n = len(l)
    x = 0
    while n:
        n //= 10
        x += 1
    return x

def set_dryrun():
    global _dryrun
    _dryrun = True

def clear_dryrun():
    global _dryrun
    _dryrun = False

def test_dryrun():
    return _dryrun

_dryrun = False
