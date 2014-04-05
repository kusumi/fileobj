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

# no mmap offset and rfind till Python 2.6
_has_mmap_offset = \
_has_mmap_rfind = util.is_python_version_or_ht(2, 6, 0)

_has_right_mapping_length = \
    util.is_python2_version_or_ht(2, 7, 0) or \
    util.is_python3_version_or_ht(3, 1, 0)

class Fileobj (fileobj.Fileobj):
    _insert  = False
    _replace = False
    _delete  = False
    _enabled = True
    _partial = _has_mmap_offset

    def __init__(self, f, offset=0):
        self.__set_delta(0, 0)
        self.map = None
        super(Fileobj, self).__init__(f, offset)
        assert os.path.exists(self.get_path())

    def __str__(self):
        l = []
        l.append(str(self.map))
        l.append("mmap.tell {0}".format(self.map.tell()))
        l.append("mmap.size {0}".format(self.map.size()))
        l.append("size {0}".format(self.get_size()))
        return '\n'.join(l)

    def init(self):
        f = self.get_path()
        if kernel.get_buffer_size_safe(f) <= 0:
            raise fileobj.FileobjError("{0} is empty".format(f))
        with util.open_file(f, 'r+') as fd:
            self.map = self.mmap(fd.fileno())

    def cleanup(self):
        if self.map:
            self.map.close() # no exception on second time

    def mmap(self, fileno):
        offset = self.get_offset()
        if offset == 0:
            return self.__do_mmap(fileno)
        else:
            assert self.__is_using_mmap_offset(offset)
            return self.__do_mmap_at(fileno, offset)

    def __is_using_mmap_offset(self, offset):
        return util.get_class(self)._partial and offset > 0

    def __do_mmap(self, fileno):
        return mmap.mmap(fileno, 0,
            mmap.MAP_SHARED, mmap.PROT_READ)

    def __do_mmap_at(self, fileno, offset):
        mask = ~(util.PAGE_SIZE - 1)
        start = offset & mask
        assert start % mmap.ALLOCATIONGRANULARITY == 0, start
        self.__set_delta(offset - start, offset)
        return mmap.mmap(fileno, 0,
            mmap.MAP_SHARED, mmap.PROT_READ, offset=start)

    def __set_delta(self, delta, offset):
        self.__offset_delta = delta
        if self.__is_using_mmap_offset(offset):
            if _has_right_mapping_length:
                self.__size_delta = self.__offset_delta
            else:
                self.__size_delta = offset
        else:
            self.__size_delta = 0

    def is_dirty(self):
        return False

    def get_size(self):
        return len(self.map) - self.__size_delta

    def search(self, x, s, end=-1):
        s = util.str_to_bytes(s)
        if setting.use_ignorecase:
            ret = self.__find(x, s)
        else:
            d = self.__offset_delta
            ret = self.map.find(s, x + d)
            if ret >= 0:
                ret -= d
        screen.cli()
        return ret

    def __find(self, x, s):
        n = util.PAGE_SIZE
        while True:
            b = self.read(x, n)
            pos = util.find_string(b, s)
            if pos >= 0:
                return x + pos
            elif x + len(b) >= self.get_size():
                return -1
            x += (n - len(s))
            if screen.test_signal():
                return -2

    def rsearch(self, x, s, end=-1):
        s = util.str_to_bytes(s)
        if setting.use_ignorecase or not _has_mmap_rfind:
            ret = self.__rfind(x, s)
        else:
            d = self.__offset_delta
            ret = self.map.rfind(s, 0, x + d + 1)
            if ret >= 0:
                ret -= d
        screen.cli()
        return ret

    def __rfind(self, x, s):
        while True:
            n = util.PAGE_SIZE
            i = x + 1 - n
            if i < 0:
                i = 0
                n = x + 1
            pos = util.rfind_string(
                self.read(i, n), s)
            if pos >= 0:
                return i + pos
            elif not i:
                return -1
            x -= (n - len(s))
            if screen.test_signal():
                return -2

    def read(self, x, n):
        x += self.__offset_delta
        return self.map[x : x + n]
