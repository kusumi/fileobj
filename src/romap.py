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

from __future__ import with_statement
import mmap
import os

from . import fileobj
from . import kernel
from . import screen
from . import setting
from . import util

# no mmap rfind till Python 2.6
_has_rfind = util.is_python_version_or_ht(2, 6, 0)

class Fileobj (fileobj.Fileobj):
    _insert  = False
    _replace = False
    _delete  = False
    _enabled = True

    def __init__(self, f):
        self.map = None
        super(Fileobj, self).__init__(f)
        assert os.path.exists(self.get_path())

    def __str__(self):
        l = []
        l.append(str(self.map))
        l.append("mmap.tell %d" % self.map.tell())
        l.append("mmap.size %d" % self.map.size())
        l.append("size %d" % self.get_size())
        return '\n'.join(l)

    def init(self):
        f = self.get_path()
        if kernel.get_buffer_size_safe(f) <= 0:
            raise fileobj.FileobjError("%s is empty" % f)
        with open(f, 'r+') as fd:
            self.map = self.mmap(fd.fileno())

    def mmap(self, fileno):
        return mmap.mmap(fileno, 0,
            mmap.MAP_SHARED, mmap.PROT_READ)

    def cleanup(self):
        if self.map:
            self.map.close() # no exception on second time

    def is_dirty(self):
        return False

    def get_size(self):
        return len(self.map)

    def search(self, x, s, end=-1):
        if setting.use_ignorecase:
            ret = self.__find(x, s)
        else:
            ret = self.map.find(s, x)
        screen.cli()
        return ret

    def __find(self, x, s, ic=True):
        if ic:
            s = s.lower()
        n = util.PAGE_SIZE
        while True:
            b = self.read(x, n)
            if ic:
                b = b.lower()
            pos = b.find(s)
            if pos >= 0:
                return x + pos
            elif x + len(b) >= self.get_size():
                return -1
            x += (n - len(s))
            if screen.test_signal():
                return -2

    def rsearch(self, x, s, end=-1):
        if setting.use_ignorecase or not _has_rfind:
            ret = self.__rfind(x, s, setting.use_ignorecase)
        else:
            ret = self.map.rfind(s, 0, x)
        screen.cli()
        return ret

    def __rfind(self, x, s, ic=True):
        if ic:
            s = s.lower()
        while True:
            n = util.PAGE_SIZE
            i = x + 1 - n
            if i < 0:
                i = 0
                n = x + 1
            b = self.read(i, n)
            if ic:
                b = b.lower()
            pos = b.rfind(s)
            if pos >= 0:
                return i + pos
            elif not i:
                return -1
            x -= (n - len(s))
            if screen.test_signal():
                return -2

    def read(self, x, n):
        return self.map[x : x + n]
