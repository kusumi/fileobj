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

import mmap
import os
import stat

from . import filebytes
from . import fileobj
from . import kernel
from . import log
from . import romap
from . import util

class Fileobj (romap.Fileobj):
    _insert  = True
    _replace = True
    _delete  = True
    _enabled = kernel.has_mremap()
    _partial = False

    def __init__(self, f, offset=0):
        super(Fileobj, self).__init__(f, offset)
        self.__dirty = False
        self.__sync = False
        self.__dead = False
        self.__stat = os.stat(self.get_path())

    def cleanup(self):
        try:
            if not self.map: # if closed if test raises exception
                return
            a = self.__sync
            l = self.__stat
        except Exception as e: # error from __init__
            log.error(e)
            return
        try:
            self.restore_rollback_log(self)
            self.flush()
        except Exception as e:
            log.error(e)
        finally:
            super(Fileobj, self).cleanup()
            if self.__dead:
                util.truncate_file(self.get_path())
            if not a:
                os.utime(self.get_path(),
                    (l[stat.ST_ATIME], l[stat.ST_MTIME]))

    def mmap(self, fileno):
        return mmap.mmap(fileno, 0)

    def clear_dirty(self):
        self.__dirty = False

    def is_dirty(self):
        return self.__dirty

    def get_size(self):
        if not self.__dead:
            return super(Fileobj, self).get_size()
        else:
            return 0

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
        if not self.is_empty():
            return super(Fileobj, self).read(x, n)
        else:
            return filebytes.BLANK

    def insert(self, x, l, rec=True):
        size = self.get_size()
        n = len(l)
        xx = x + n

        if rec:
            buf = l[:]
            def ufn(ref):
                ref.delete(x, n, False)
                return x
            def rfn(ref):
                ref.insert(x, buf, False)
                return x
            self.add_undo(ufn, rfn)

        self.map.resize(size + n)
        self.map.move(xx, x, size - x)
        self.map[x:xx] = filebytes.input_to_bytes(l)
        self.__dirty = True
        self.__sync = False
        self.__dead = False

    def replace(self, x, l, rec=True):
        if self.is_empty():
            self.insert(x, l, rec)
            return
        size = self.get_size()
        n = len(l)
        xx = x + n
        resized = False
        if x + n > size:
            self.map.resize(x + n)
            resized = True

        if rec:
            ubuf = filebytes.ordt(self.read(x, n))
            rbuf = l[:]
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

        self.map[x:xx] = filebytes.input_to_bytes(l)
        self.__dirty = True
        self.__sync = False

    def delete(self, x, n, rec=True):
        if self.is_empty():
            raise fileobj.FileobjError("Empty buffer")
        size = self.get_size()
        xx = x + n

        if rec:
            buf = filebytes.ordt(self.read(x, n))
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
            os.utime(self.get_path(), None)
            self.__dead = True
        self.__dirty = True
        self.__sync = False
