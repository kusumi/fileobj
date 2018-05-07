# Copyright (c) 2014, Tomohiro Kusumi
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

from . import filebytes
from . import kernel
from . import romap
from . import setting
from . import util

class Fileobj (romap.Fileobj):
    _insert  = False
    _replace = True
    _delete  = False
    _enabled = romap.Fileobj._enabled
    _partial = romap.Fileobj._partial

    def __init__(self, f, offset=0, length=0):
        self.__dirty = False
        self.__stat = None
        super(Fileobj, self).__init__(f, offset, length)

    def ctr(self):
        self.update_fstat(self.get_path())
        super(Fileobj, self).ctr()

    def dtr(self):
        if not self.map:
            return
        t = self.get_fstat()
        self.restore_rollback_log(self)
        self.flush()
        self.cleanup_mapping()
        self.update_mtime(self.get_path(), t)

    def clear_dirty(self):
        self.__dirty = False

    def is_dirty(self):
        return self.__dirty

    def sync(self):
        self.map.flush()
        self.update_fstat(self.get_path())

    def utime(self):
        kernel.touch(self.get_path())
        self.update_fstat(self.get_path())

    def get_fstat(self):
        return self.__stat

    def update_fstat(self, f):
        self.__stat = os.stat(f)

    def update_mtime(self, f, st):
        current = os.stat(f)
        kernel.utime(f, (current.st_atime, st.st_mtime))

    def set_dirty(self):
        self.__dirty = True

    def read(self, x, n):
        if not self.is_empty():
            return super(Fileobj, self).read(x, n)
        else:
            return filebytes.BLANK

    def replace(self, x, l, rec=True):
        if x + len(l) > self.get_size():
            l = l[:self.get_size() - x]

        xorig = x
        x += self.get_mmap_offset()
        n = len(l)
        xx = x + n

        if rec:
            ubuf = filebytes.ords(self.read(xorig, n))
            rbuf = l[:]
            def ufn(ref):
                ref.replace(xorig, ubuf, False)
                return xorig
            def rfn(ref):
                ref.replace(xorig, rbuf, False)
                return xorig
            self.add_undo(ufn, rfn)

        self.map[x:xx] = filebytes.input_to_bytes(l)
        self.set_dirty()

    def get_no_support_string(self, s):
        msg = "use -B option to enable " + s
        if kernel.has_mremap():
            return "Can not {0}, {1}".format(s, msg)
        elif setting.use_debug:
            try:
                self.map.resize(self.get_size())
                assert False, "mmap resize should fail"
            except Exception as e:
                return "{0}, {1}".format(repr(e), msg)
        else:
            return "{0} has no mremap(2), {1}".format(util.get_os_name(), msg)
