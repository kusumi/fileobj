# Copyright (c) 2010-2015, TOMOHIRO KUSUMI
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

import collections
import os

from . import fileobj
from . import kernel
from . import log
from . import screen
from . import setting
from . import util

class Fileobj (fileobj.Fileobj):
    _insert  = False
    _replace = False
    _delete  = False
    _enabled = True
    _partial = True

    def __init__(self, f, offset=0, length=0):
        self.fd = None
        self.__size = -1
        self.__align = 0
        self.__ra_window = None
        self.__ra_queue = collections.deque()
        self.__ra_count = collections.defaultdict(int)
        self.__count = collections.defaultdict(int)
        super(Fileobj, self).__init__(f, offset, length)

    def __str__(self):
        sl = []
        sl.append("read align {0}".format(self.__align))
        sl.append("read_ahead window {0}".format(str(self.__ra_window)))
        sl.append("\nread_ahead size range")
        for i, o in enumerate(self.__ra_queue):
            sl.append("#{0} {1}[B] {2}-{3}[B]".format(
                i, o.end - o.beg, o.beg, o.end))
        sl.append("\nread_ahead count {0}".format(
            sum(self.__ra_count.values())))
        for k in sorted(self.__ra_count.keys()):
            sl.append("{0}[B] {1}".format(k, self.__ra_count[k]))
        sl.append("\nread count {0}".format(sum(self.__count.values())))
        for k in sorted(self.__count.keys()):
            sl.append("{0}[B] {1}".format(k, self.__count[k]))
        return '\n'.join(sl)

    def ctr(self):
        f = self.get_path()
        size = kernel.get_size(f)
        if size <= 0:
            raise fileobj.FileobjError(f + " is empty")
        self.set_size(size)
        self.set_align(0)
        self.set_window(1, 1)
        self.init_file()
        assert os.path.exists(self.get_path())

    def dtr(self):
        if self.fd and not self.fd.closed:
            self.fd.close()

    def init_file(self):
        if self.is_readonly():
            mode = 'r'
        else:
            mode = 'r+'
        self.fd = kernel.fopen(self.get_path(), mode)

    def is_dirty(self):
        return False

    def get_size(self):
        return self.__size

    def set_size(self, size):
        assert self.__size == -1
        length = self.get_mapping_length()
        if length:
            self.__size = length
        else:
            self.__size = size - self.get_mapping_offset()
        assert self.__size > 0

    def set_align(self, align):
        if align > 1:
            self.__align = align
        else:
            self.__align = 0

    def set_window(self, beg, end):
        assert beg >= 0 and end >= 0
        self.__ra_window = beg, end

    def find(self, x, s, end):
        n = kernel.PAGE_SIZE
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
        while True:
            if end != -1 and x <= end:
                return fileobj.NOTFOUND
            n = kernel.PAGE_SIZE
            i = x + 1 - n
            if i < 0:
                i = 0
                n = x + 1
            pos = util.rfind_string(
                self.read(i, n), s)
            if pos >= 0:
                return i + pos
            elif not i:
                return fileobj.NOTFOUND
            x -= (n - len(s))
            if screen.test_signal():
                return fileobj.INTERRUPT

    def read(self, x, n):
        x += self.get_mapping_offset()
        o = None
        for e in self.__ra_queue:
            if x >= e.beg and x + n <= e.end:
                o = e
                break
        if not o:
            beg = x
            beg -= n * self.__ra_window[0]
            if beg < 0:
                beg = 0
            end = x + n
            end += n * self.__ra_window[1]

            if self.__align:
                beg, end = util.align_range(
                    beg, end, self.__align)
            try:
                self.fd.seek(beg)
                b = self.fd.read(end - beg)
            except Exception as e:
                log.error((e, (beg, end)))
                beg = x
                end = x + n
                self.fd.seek(beg)
                b = self.fd.read(end - beg)

            o = util.Namespace(beg=beg, end=beg + len(b), buf=b)
            self.__ra_count[end - beg] += 1
            self.__ra_queue.appendleft(o)
            if len(self.__ra_queue) > setting.rofd_read_queue_size:
                self.__ra_queue.pop()

        self.__count[n] += 1
        x -= o.beg
        return o.buf[x : x + n]
