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
import shutil

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

    def __init__(self, f, offset=0, length=0):
        self.__dirty = False
        self.__sync = False
        self.__dead = False
        self.__stat = None
        self.__anon = None
        super(Fileobj, self).__init__(f, offset, length)

    def init(self):
        f = self.get_path()
        if os.path.isfile(f) and kernel.get_file_size(f) > 0:
            super(Fileobj, self).init()
        else:
            self.__init_anon()
            f = self.__get_backing_path()
            self.init_mapping(f)
        self.__sync_stat(f)

    def cleanup(self):
        if not self.map: # if closed if test raises exception
            return
        uptodate = self.__sync
        laststat = self.__stat
        try:
            self.restore_rollback_log(self)
            if self.__anon:
                self.__cleanup_anon()
            else:
                self.flush()
        except Exception, e:
            log.error(e)
        finally:
            super(Fileobj, self).cleanup()
            if not self.__anon:
                f = self.get_path()
                if self.__dead:
                    util.truncate_file(f)
                if not uptodate:
                    util.utime(f, laststat)
            self.__anon = None

    def __init_anon(self):
        if self.__anon:
            return -1
        self.__anon = util.open_temp_file()
        self.__anon.write(filebytes.ZERO)
        self.__anon.seek(0)
        self.__dead = True
        log.debug("Create backing file %s for %s" % (
            self.__get_backing_path(),
            self.get_path()))

    def __cleanup_anon(self):
        if not self.__anon:
            return -1
        if not self.__is_flushed():
            return -1
        util.fsync(self.__anon)
        src = self.__get_backing_path()
        dst = self.get_path()
        if src == dst:
            return -1
        if not os.path.isfile(src):
            return -1
        if os.path.exists(dst):
            return -1
        shutil.copy2(src, dst)
        self.__anon = None

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

    def __get_backing_path(self):
        if self.__anon:
            return self.__anon.name
        else:
            return self.get_path()

    def sync(self):
        f = self.__get_backing_path()
        self.map.flush()
        self.__sync = True
        self.__sync_stat(f)

    def utime(self):
        f = self.__get_backing_path()
        util.utime(f)
        self.__sync = True
        self.__sync_stat(f)

    def __sync_stat(self, f):
        ret = os.stat(f)
        if not self.__stat:
            initial = ret.st_mtime
            def is_flushed():
                return self.__stat.st_mtime != initial
            assert self.__is_flushed is not None
            self.__is_flushed = is_flushed
        self.__stat = ret

    def __is_flushed(self):
        return False

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
            ubuf = filebytes.ords(self.read(x, n))
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
            buf = filebytes.ords(self.read(x, n))
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
            util.utime(self.__get_backing_path())
            self.__dead = True
        self.__dirty = True
        self.__sync = False
