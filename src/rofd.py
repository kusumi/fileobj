# Copyright (c) 2010-2013, TOMOHIRO KUSUMI
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
import sys

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

    def __init__(self, f):
        self.fd = None
        self.__size = -1
        super(Fileobj, self).__init__(f)
        assert os.path.exists(self.get_path())
        self.__ra_queue = collections.deque()
        self.__ra_stat = collections.defaultdict(int)
        self.__stat = collections.defaultdict(int)

    def __str__(self):
        sl = []
        sl.append("read align %d" % self.__align)
        sl.append("read mask %d" % self.__mask)
        sl.append("read_ahead window %s" % str(self.__ra_window))
        sl.append("\nread_ahead size range")
        for i, o in enumerate(self.__ra_queue):
            sl.append("#%d %d[B] %d-%d[B]" % (i, o.end - o.beg, o.beg, o.end))
        sl.append("\nread_ahead stat %d" % sum(self.__ra_stat.values()))
        for k in sorted(self.__ra_stat.keys()):
            sl.append("%d[B] %d" % (k, self.__ra_stat[k]))
        sl.append("\nread stat %d" % sum(self.__stat.values()))
        for k in sorted(self.__stat.keys()):
            sl.append("%d[B] %d" % (k, self.__stat[k]))
        return '\n'.join(sl)

    def init(self):
        self.set_align(0)
        self.set_window(1, 1)
        self.open_file('r+')
        self.set_size(
            kernel.get_buffer_size(self.get_path())) # may raise

    def cleanup(self):
        if self.fd and not self.fd.closed:
            self.fd.close()

    def is_dirty(self):
        return False

    def get_size(self):
        return self.__size

    def set_size(self, size):
        assert self.__size == -1
        self.__size = size

    def open_file(self, flag):
        self.fd = open(self.get_path(), flag)

    def set_align(self, align):
        if align > 1:
            self.__align = align
            self.__mask = ~(align - 1)
        else:
            self.__align = 0
            self.__mask = 0

    def set_window(self, beg, end):
        assert beg >= 0 and end >= 0
        self.__ra_window = beg, end

    def search(self, x, s, end=-1):
        if setting.use_ignorecase:
            s = s.lower()
        n = util.PAGE_SIZE
        while True:
            b = self.read(x, n)
            if setting.use_ignorecase:
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
        if setting.use_ignorecase:
            s = s.lower()
        while True:
            n = util.PAGE_SIZE
            i = x + 1 - n
            if i < 0:
                i = 0
                n = x + 1
            b = self.read(i, n)
            if setting.use_ignorecase:
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
                beg &= self.__mask
                end += (self.__align - 1)
                end &= self.__mask
            try:
                self.fd.seek(beg)
                b = self.fd.read(end - beg)
            except Exception:
                e = sys.exc_info()[1]
                log.error((e, (beg, end)))
                beg = x
                end = x + n
                self.fd.seek(beg)
                b = self.fd.read(end - beg)

            o = util.Namespace(beg=beg, end=beg + len(b), buf=b)
            self.__ra_stat[end - beg] += 1
            self.__ra_queue.appendleft(o)
            if len(self.__ra_queue) > setting.rofd_read_queue_size:
                self.__ra_queue.pop()

        self.__stat[n] += 1
        x -= o.beg
        return o.buf[x : x + n]
