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
import os

from . import filebytes
from . import fileobj
from . import log
from . import rrbuf
from . import setting
from . import util

class Fileobj (rrbuf.Fileobj):
    _insert   = True
    _replace  = True
    _delete   = True
    _truncate = False
    _enabled  = True
    _partial  = True

    def __init__(self, f, offset=0, length=0):
        self.__count = 0
        super(Fileobj, self).__init__(f, offset, length)

    def ctr(self):
        assert not self.cbuf
        if os.path.isfile(self.get_path()):
            super(Fileobj, self).ctr()
        else:
            self.init_chunk(filebytes.BLANK)

    def __sync_size(self, o, delta):
        for i in util.get_xrange(self.cbuf.index(o) + 1, len(self.cbuf)):
            self.cbuf[i].offset += delta
        self.set_size(self.get_size() + delta)

    def __test_balance(self, iosize):
        if iosize >= self.get_chunk_size():
            return True
        self.__count += 1
        if self.__count == setting.buffer_chunk_balance_interval:
            self.__count = 0
            return True
        else:
            return False

    def __balance_chunk(self):
        for o in self.cbuf:
            if len(o) < self.__get_chunk_size_low():
                if self.__merge_chunk(o, self.get_chunk_size()) != -1:
                    break
        for o in self.cbuf:
            if len(o) > self.__get_chunk_size_high():
                if self.__split_chunk(o, self.get_chunk_size()) != -1:
                    break
        if setting.use_debug:
            l = [len(o) for o in self.cbuf]
            log.debug("{0} chunks exist min={1}[B] max={2}[B]".format(len(l),
                min(l), max(l)))
        self.set_search_thresh()

    def __get_chunk_size_low(self):
        ret = self.get_chunk_size() // 10
        assert ret > 0, ret
        return ret

    def __get_chunk_size_high(self):
        ret = self.get_chunk_size() * 10
        assert ret > 0, ret
        return ret

    def __merge_chunk(self, beg, merge_thresh):
        if len(beg) >= merge_thresh:
            return -1
        l = self.cbuf[self.cbuf.index(beg):]
        size = 0
        for o in l:
            size += len(o)
            if size >= merge_thresh:
                ll = l[:l.index(o) + 1]
                if len(ll) > 1:
                    b = filebytes.join([o.read(o.offset, len(o)) for o in ll])
                    new = self.alloc_chunk(beg.offset, b)
                    self.cbuf.insert(self.cbuf.index(beg), new)
                    log.debug("Merge {0} chunks -> #{1}/{2} ({3},{4})".format(
                        len(ll), self.cbuf.index(new), len(self.cbuf),
                        new.offset, len(new)))
                    for o in ll:
                        self.cbuf.remove(o)
                self.mark_chunk()
                break

    def __split_chunk(self, beg, split_thresh):
        if len(beg) <= split_thresh:
            return -1
        offset = beg.offset
        size = len(beg)
        i = 0
        while size > 0:
            b = beg.read(offset, split_thresh)
            o = self.alloc_chunk(offset, b)
            self.cbuf.insert(self.cbuf.index(beg) + 1 + i, o)
            offset += len(b)
            size -= len(b)
            i += 1
        log.debug("Split into {0} chunks <- #{1}/{2} ({3},{4})".format(i,
            self.cbuf.index(beg), len(self.cbuf) - i, beg.offset, len(beg)))
        self.cbuf.remove(beg)
        self.mark_chunk()

    def insert(self, x, l, rec=True):
        o = self.cbuf[self.get_chunk_index(x)]
        n = o.insert(x, l)
        self.__sync_size(o, n)
        self.set_dirty()
        if self.__test_balance(len(l)):
            self.__balance_chunk()
        if rec:
            buf = l[:n]
            def ufn(ref):
                ref.delete(x, n, False)
                return x
            def rfn(ref):
                ref.insert(x, buf, False)
                return x
            self.add_undo(ufn, rfn)

    def replace(self, x, l, rec=True):
        if self.is_empty():
            self.insert(x, l, rec)
            return
        xx, ll = x, l[:]
        buf = []
        oldsize = self.get_size()
        endsize = len(self.cbuf[-1])
        for o in self.iter_chunk(x):
            ret, orig = o.replace(x, l)
            if rec:
                buf.extend(orig) # str or int
            l = l[ret:]
            x += ret
            if not l:
                delta = len(self.cbuf[-1]) - endsize
                if delta:
                    self.__sync_size(self.cbuf[-1], delta)
                self.set_dirty()
                if self.__test_balance(len(ll)):
                    self.__balance_chunk()
                if rec:
                    ubuf = self.seq_to_ords(buf)
                    rbuf = ll[:len(ubuf)]
                    newsize = self.get_size()
                    if newsize == oldsize:
                        def ufn1(ref):
                            ref.replace(xx, ubuf, False)
                            return xx
                        def rfn1(ref):
                            ref.replace(xx, rbuf, False)
                            return xx
                        self.add_undo(ufn1, rfn1)
                    else:
                        assert newsize > oldsize
                        def ufn2(ref): # shrink
                            ref.replace(xx, ubuf, False)
                            ref.delete(oldsize, xx + len(ll) - oldsize, False)
                            return xx
                        def rfn2(ref): # expand
                            ref.replace(xx, rbuf, False)
                            return xx
                        self.add_undo(ufn2, rfn2)
                break

    def delete(self, x, n, rec=True):
        if self.is_empty():
            raise fileobj.Error("Empty buffer")
        xx, nn = x, n
        buf = []
        dead = []
        for o in self.iter_chunk(x):
            ret, orig = o.delete(x, n)
            if rec:
                buf.extend(orig) # str or int
            if not len(o):
                dead.append(o)
            n -= ret
            x += ret
            if n <= 0:
                break # may not come here

        if dead:
            log.debug("Delete {0} dead chunks".format(len(dead)))
            for o in dead:
                self.cbuf.remove(o)
            self.mark_chunk()
        size = 0
        for o in self.cbuf:
            o.offset = size
            size += len(o)
        self.set_size(size)
        self.set_dirty()
        if self.__test_balance(nn):
            self.__balance_chunk()
        if rec:
            buf = self.seq_to_ords(buf)
            def ufn(ref):
                ref.insert(xx, buf, False)
                return xx
            def rfn(ref):
                ref.delete(xx, nn, False)
                return xx
            self.add_undo(ufn, rfn)
