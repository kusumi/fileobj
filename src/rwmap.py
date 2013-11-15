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

import mmap
import os
import stat
import sys

from . import fileobj
from . import kernel
from . import log
from . import romap

class Fileobj (romap.Fileobj):
    _insert  = True
    _replace = True
    _delete  = True
    _enabled = kernel.has_mremap()

    def __init__(self, f):
        super(Fileobj, self).__init__(f)
        self.__dirty = False
        self.__sync = False
        self.__dead = False
        self.__stat = os.stat(self.get_path())

    def mmap(self, fileno):
        return mmap.mmap(fileno, 0)

    def cleanup(self):
        try:
            if not self.map: # if closed if test raises exception
                return
            a = self.__sync
            l = self.__stat
        except Exception: # error from __init__
            e = sys.exc_info()[1]
            log.error(e)
            return
        try:
            self.restore_rollback_log(self)
            self.flush()
        except Exception:
            e = sys.exc_info()[1]
            log.error(e)
        finally:
            super(Fileobj, self).cleanup()
            if not a:
                os.utime(self.get_path(),
                    (l[stat.ST_ATIME], l[stat.ST_MTIME]))

    def clear_dirty(self):
        self.__dirty = False

    def is_dirty(self):
        return self.__dirty

    def get_size(self):
        if self.__dead:
            return 0
        else:
            return super(Fileobj, self).get_size()

    def sync(self):
        self.map.flush()
        self.__get_stat()

    def utime(self):
        super(Fileobj, self).utime()
        self.__get_stat()

    def __get_stat(self):
        self.__sync = True
        self.__stat = os.stat(self.get_path())

    def read(self, x, n):
        if self.is_empty():
            return ''
        else:
            return super(Fileobj, self).read(x, n)

    def insert(self, x, s, rec=True):
        size = self.get_size()
        n = len(s)
        xx = x + n

        if rec:
            buf = s[:]
            def ufn(ref):
                ref.delete(x, n, False)
                return x
            def rfn(ref):
                ref.insert(x, buf, False)
                return x
            self.add_undo(ufn, rfn)

        self.map.resize(size + n)
        self.map.move(xx, x, size - x)
        self.map[x:xx] = s
        self.__dirty = True
        self.__sync = False
        self.__dead = False

    def replace(self, x, s, rec=True):
        if self.is_empty():
            self.insert(x, s, rec)
            return
        size = self.get_size()
        n = len(s)
        xx = x + n
        resized = False
        if x + n > size:
            self.map.resize(x + n)
            resized = True

        if rec:
            ubuf = self.read(x, n)
            rbuf = s[:]
            if not resized:
                def ufn1(ref):
                    ref.replace(x, ubuf, False)
                    return x
                def rfn1(ref):
                    ref.replace(x, rbuf, False)
                    return x
                self.add_undo(ufn1, rfn1)
            else:
                def ufn2(ref):
                    ref.map.resize(size) # shrink
                    ref.replace(x, ubuf[:size - x], False)
                    return x
                def rfn2(ref):
                    ref.map.resize(x + n) # expand
                    ref.replace(x, rbuf, False)
                    return x
                self.add_undo(ufn2, rfn2)

        self.map[x:xx] = s
        self.__dirty = True
        self.__sync = False

    def delete(self, x, n, rec=True):
        if self.is_empty():
            raise fileobj.FileobjError("Empty buffer")
        size = self.get_size()
        xx = x + n

        if rec:
            buf = self.read(x, n)
            def ufn(ref):
                ref.insert(x, buf, False)
                return x
            def rfn(ref):
                ref.delete(x, n, False)
                return x
            self.add_undo(ufn, rfn)

        self.map.move(x, xx, size - xx)
        if size > n:
            self.map.resize(size - n)
        else:
            self.__dead = True
        self.__dirty = True
        self.__sync = False
