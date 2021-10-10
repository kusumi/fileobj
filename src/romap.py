# Copyright (c) 2011, Tomohiro Kusumi
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

from . import fileobj
from . import kernel
from . import screen
from . import setting
from . import util

# no mmap offset and rfind till Python 2.6
_has_mmap_offset = _has_mmap_rfind = util.is_python_version_or_ht(2, 6, 0)

_has_right_mapping_length = \
    util.is_python2_version_or_ht(2, 7, 0) or \
    util.is_python3_version_or_ht(3, 1, 0)

"""
0        aligned          offset                            bufsiz
|--------+----------------+---------------------------------| file
         |----------------+----------------------| mmap
                          |<-------length------->|
         |<------------real_length-------------->|
         |<---offset_d--->|
         |<------------len(mapping)------------->|  _has_right_mapping_length
         |<----size_d---->|                         _has_right_mapping_length
|<---------------------len(mapping)------------->| !_has_right_mapping_length
|<-------------size_d---->|                        !_has_right_mapping_length
"""

class Fileobj (fileobj.Fileobj):
    _insert  = False
    _replace = False
    _delete  = False
    _truncate= False
    _enabled = kernel.has_mmap()
    _partial = _has_mmap_offset

    def __init__(self, f, offset=0, length=0):
        self.__set_delta(0, 0)
        self.map = None
        super(Fileobj, self).__init__(f, offset, length)

    def __str__(self):
        l = []
        l.append(str(self.map))
        l.append("map.tell {0}".format(self.map.tell()))
        l.append("map.size {0}".format(self.map.size()))
        l.append("size {0}".format(self.get_size()))
        return '\n'.join(l)

    def ctr(self):
        if self.is_mappable():
            self.init_mapping(self.get_path())
        else:
            raise fileobj.Error("Can not mmap(2) " + self.get_path())

    def dtr(self):
        self.cleanup_mapping()

    def init_mapping(self, f):
        with kernel.fopen(f, 'r+') as fd:
            try:
                self.map = self.mmap(fd.fileno())
            except mmap.error as e:
                raise util.Message("mmap(2) failed, {0}".format(repr(e)))

    def cleanup_mapping(self):
        if self.map:
            self.map.close() # no exception on second time
            self.map = None

    def is_mappable(self):
        return kernel.read_reg_size(self.get_path()) > 0

    def mmap(self, fileno):
        offset = self.get_mapping_offset()
        length = self.get_mapping_length()
        if offset == 0:
            return self.__do_mmap(fileno, length)
        else:
            assert self.__is_using_mmap_offset(offset)
            return self.__do_mmap_at(fileno, offset, length)

    def __is_using_mmap_offset(self, offset):
        return self.test_partial() and offset > 0

    def __do_mmap(self, fileno, length):
        return kernel.mmap_partial(fileno, 0, length, self.is_readonly())

    def __do_mmap_at(self, fileno, offset, length):
        start = util.align_head(offset, kernel.get_page_size())
        delta = offset - start
        self.__set_delta(delta, offset)
        if length:
            length += delta
        return kernel.mmap_partial(fileno, start, length, self.is_readonly())

    def __set_delta(self, delta, offset):
        self.__offset_delta = delta
        if self.__is_using_mmap_offset(offset):
            if _has_right_mapping_length:
                self.__size_delta = self.get_mmap_offset()
            else:
                self.__size_delta = offset
        else:
            self.__size_delta = 0

    def get_mmap_offset(self):
        return self.__offset_delta

    def is_dirty(self):
        return False

    def get_size(self):
        return len(self.map) - self.__size_delta

    def find(self, x, s, end):
        if setting.use_ignorecase:
            ret = self.__find(x, s, end)
        else:
            d = self.get_mmap_offset()
            ret = self.map.find(s, x + d)
            if ret >= 0:
                ret -= d
            else:
                ret = fileobj.NOTFOUND
        screen.cli()
        return ret

    def __find(self, x, s, end):
        n = self.get_buffer_size()
        while True:
            if end != -1 and x >= end:
                return fileobj.NOTFOUND
            b = self.read(x, n)
            pos = util.find_string(b, s)
            if pos >= 0:
                return x + pos
            elif x + len(b) >= self.get_size():
                return fileobj.NOTFOUND
            x += (n - len(s))
            if screen.test_signal():
                return fileobj.INTERRUPT

    def rfind(self, x, s, end):
        if setting.use_ignorecase or not _has_mmap_rfind:
            ret = self.__rfind(x, s, end)
        else:
            d = self.get_mmap_offset()
            ret = self.map.rfind(s, 0, x + d + 1)
            if ret >= 0:
                ret -= d
            else:
                ret = fileobj.NOTFOUND
        screen.cli()
        return ret

    def __rfind(self, x, s, end):
        bufsiz = self.get_buffer_size()
        while True:
            if end != -1 and x <= end:
                return fileobj.NOTFOUND
            n = bufsiz
            i = x + 1 - n
            if i < 0:
                i = 0
                n = x + 1
            pos = util.rfind_string(self.read(i, n), s)
            if pos >= 0:
                return i + pos
            elif not i:
                return fileobj.NOTFOUND
            x -= (n - len(s))
            if screen.test_signal():
                return fileobj.INTERRUPT

    def read(self, x, n):
        x += self.get_mmap_offset()
        return self.map[x : x + n]
