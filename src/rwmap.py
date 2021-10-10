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

import os
import shutil

from . import filebytes
from . import fileobj
from . import kernel
from . import log
from . import rrmap
from . import setting
from . import util

class Fileobj (rrmap.Fileobj):
    _insert  = True
    _replace = True
    _delete  = True
    _truncate= True
    _enabled = kernel.has_mremap()
    _partial = False

    def __init__(self, f, offset=0, length=0):
        self.__dead = False
        self.__sync = 0
        self.__anon = None
        super(Fileobj, self).__init__(f, offset, length)

    def ctr(self):
        if self.is_mappable():
            super(Fileobj, self).ctr()
        else:
            self.__init_anon()
            f = self.__get_backing_path()
            self.init_mapping(f)
            self.update_fstat(f)

    def dtr(self):
        if not self.map:
            return
        t = self.get_fstat()
        self.restore_rollback_log(self)
        if not self.__anon:
            self.flush()
            shcopy = False
        else:
            shcopy = self.__flush_anon()
        self.cleanup_mapping()

        if not self.__anon:
            self.update_mtime(self.get_path(), t)
        if self.__dead and not self.is_dirty():
            f = self.__get_backing_path()
            kernel.truncate(f)
            self.update_mtime(f, t)
        if self.__anon and shcopy:
            self.__copy_anon()
        self.__anon = None

    def mmap(self, fileno):
        return kernel.mmap_full(fileno)

    def __init_anon(self):
        assert not self.__anon
        self.__anon = util.open_temp_file()
        self.__anon.write(filebytes.ZERO)
        self.__anon.seek(0)
        self.__die()
        log.debug("Create backing file {0} for {1}".format(
            self.__get_backing_path(), self.get_path()))

    def __copy_anon(self):
        kernel.fsync(self.__anon)
        src = self.__get_backing_path()
        dst = self.get_path()
        if src == dst:
            return -1
        if not os.path.isfile(src):
            return -1
        if kernel.read_reg_size(dst) > 0:
            return -1
        shutil.copy2(src, dst)

    def __flush_anon(self):
        self.sync()
        self.clear_dirty()
        assert self.__sync >= 1
        return self.__sync >= 2 # need copying

    def __get_backing_path(self):
        if self.__anon:
            return self.__anon.name
        else:
            return self.get_path()

    def get_size(self):
        if not self.__dead:
            return super(Fileobj, self).get_size()
        else:
            return 0

    def sync(self):
        self.map.flush()
        self.update_fstat(self.__get_backing_path())
        self.__sync += 1

    def utime(self):
        kernel.touch(self.__get_backing_path())
        self.update_fstat(self.__get_backing_path())
        self.__sync += 1

    def __die(self, is_dying=True):
        if not self.__dead and is_dying:
            kernel.touch(self.__get_backing_path())
        self.__dead = is_dying

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
        self.set_dirty()
        self.__die(False)

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
        self.set_dirty()

    def delete(self, x, n, rec=True):
        if self.is_empty():
            raise fileobj.Error("Empty buffer")
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
            self.__die()
        self.set_dirty()

    def truncate(self, n, rec=True):
        size = self.get_size()
        if size == n:
            return # nothing to do
        if n < 0:
            raise fileobj.Error("Invalid size {0}".format(
                util.get_size_repr(n)))

        # both >= 0, but not both 0 at the same time
        assert (size >= 0 and n >= 0) and (size > 0 or n > 0), (size, n)

        # XXX limitation to prevent expand from 0
        if size == 0:
            raise fileobj.Error("Empty buffer unsupported")
        # XXX limitation to prevent shrink to 0
        if n == 0:
            raise fileobj.Error("Can not truncate to {0}".format(
                util.get_size_repr(n)))

        if rec:
            if n > size: # expand
                def ufn(ref):
                    ref.map.resize(size) # shrink
                    self.set_dirty()
                    return size - 1
                def rfn(ref):
                    ref.map.resize(n) # expand
                    self.set_dirty()
                    return size - 1
            else: # shrink
                assert setting.use_truncate_shrink
                def ufn(ref):
                    ref.map.resize(size) # expand
                    self.set_dirty()
                    return n - 1
                def rfn(ref):
                    ref.map.resize(n) # shrink
                    self.set_dirty()
                    return n - 1
            self.add_undo(ufn, rfn)

        self.map.resize(n) # expand or shrink
        self.set_dirty()
