# Copyright (c) 2010-2016, TOMOHIRO KUSUMI
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
import os

from . import filebytes
from . import kernel
from . import log
from . import robuf
from . import util

class Fileobj (robuf.Fileobj):
    _insert  = False
    _replace = True
    _delete  = False
    _enabled = True
    _partial = True

    def __init__(self, f, offset=0, length=0):
        self.__dirty = False
        super(Fileobj, self).__init__(f, offset, length)

    def clear_dirty(self):
        self.__dirty = False

    def is_dirty(self):
        return self.__dirty

    def set_dirty(self):
        self.__dirty = True

    def sync(self):
        f = self.get_path()
        if os.path.islink(f):
            f = os.path.realpath(f) # must use realpath
        assert os.path.isfile(f), f
        assert not os.path.islink(f), f
        old = self.get_id()
        self.__overwrite_self(f) # renaming changes inode#
        new = self.init_id()
        log.info("%s: id has changed from %d to %d" % (
            f, old, new))

    def __overwrite_self(self, f):
        with util.do_atomic_write(f, fsync=kernel.fsync) as fd:
            log.debug("Renaming %s to %s" % (fd.name, f))
            hdr = self.__read_unmapped_header()
            if hdr:
                fd.write(hdr)
            fd.write(self.readall())
            trr = self.__read_unmapped_trailer()
            if trr:
                fd.write(trr)

    def __read_unmapped_header(self):
        offset = self.get_mapping_offset()
        if not offset:
            return filebytes.BLANK
        with kernel.fopen(self.get_path()) as fd:
            return fd.read(offset)

    def __read_unmapped_trailer(self):
        length = self.get_mapping_length()
        if not length:
            return filebytes.BLANK
        with kernel.fopen(self.get_path()) as fd:
            fd.seek(self.get_mapping_offset() + length)
            return fd.read()

    def seq_to_ords(self, l):
        # adaptive version of filebytes.seq_to_ords()
        if isinstance(l[0], filebytes.TYPE):
            return filebytes.seq_to_ords(l)
        else:
            return tuple(l)

    def replace(self, x, l, rec=True):
        if x + len(l) > self.get_size():
            l = l[:self.get_size() - x]

        xx, ll = x, l[:]
        buf = []
        for o in self.iter_chunk(x):
            ret, orig = o.replace(x, l)
            if rec:
                buf.extend(orig) # str or int
            l = l[ret:]
            x += ret
            if not l:
                self.set_dirty()
                if rec:
                    ubuf = self.seq_to_ords(buf)
                    rbuf = ll[:len(ubuf)]
                    def ufn1(ref):
                        ref.replace(xx, ubuf, False)
                        return xx
                    def rfn1(ref):
                        ref.replace(xx, rbuf, False)
                        return xx
                    self.add_undo(ufn1, rfn1)
                break
