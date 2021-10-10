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

from __future__ import division

from . import filebytes
from . import kernel
from . import rofd
from . import util

class Fileobj (rofd.Fileobj):
    _insert  = False
    _replace = True
    _delete  = False
    _truncate= False
    _enabled = True
    _partial = True

    def __init__(self, f, offset=0, length=0):
        super(Fileobj, self).__init__(f, offset, length)
        self.__dirty = False
        self.__diff = {}
        self.__bbuf = {}

    def __str__(self):
        l = []
        l.append("diff size {0}".format(util.get_size_repr(len(self.__diff))))
        l.append("bbuf size {0}".format(util.get_size_repr(len(self.__bbuf))))
        return super(Fileobj, self).__str__() + "\n\n" + '\n'.join(l)

    def clear_dirty(self):
        self.__dirty = False

    def is_dirty(self):
        return self.__dirty

    def __get_block_size(self):
        siz = self.get_align()
        if siz:
            return siz
        else:
            return kernel.get_page_size()

    def sync(self):
        siz = self.__get_block_size()
        for lba in sorted(self.__bbuf.keys()):
            self.fd.seek(lba * siz)
            buf = filebytes.join(self.__bbuf[lba])
            self.fd.write(buf)
        self.__bbuf = {}
        kernel.fsync(self.fd)

    def utime(self):
        super(Fileobj, self).utime()
        self.__bbuf = {}

    def read(self, x, n):
        b = super(Fileobj, self).read(x, n)
        if not b or not self.__diff:
            return b
        l = filebytes.split(b)
        for i in util.get_xrange(x, x + n):
            if i in self.__diff:
                l[i - x] = self.__diff[i]
        return filebytes.join(l)

    def replace(self, x, l, rec=True):
        # don't use buf for both ufn/rfn because ufn lose original buf
        if x + len(l) > self.get_size():
            l = l[:self.get_size() - x]
        if rec:
            ubuf = filebytes.ords(self.read(x, len(l)))
            def ufn(ref):
                ref.replace(x, ubuf, False)
                return x

        for i, c in enumerate(l):
            b = filebytes.input_to_bytes((c,))
            self.__add_block_buffer(x + i, b) # call this first
            self.__diff[x + i] = b # and then update diff
        self.__dirty = not not self.__bbuf

        if rec:
            rbuf = l[:]
            def rfn(ref):
                ref.replace(x, rbuf, False)
                return x
            self.add_undo(ufn, rfn)

    def __add_block_buffer(self, x, b):
        siz = self.__get_block_size()
        x += self.get_mapping_offset() # abs offset
        lba = x // siz
        pos = x % siz

        if lba in self.__bbuf:
            self.__bbuf[lba][pos] = b
        else:
            self.fd.seek(lba * siz)
            buf = self.fd.read(siz) # may raise exception but don't catch
            self.__bbuf[lba] = filebytes.split(buf)
            self.__bbuf[lba][pos] = b
