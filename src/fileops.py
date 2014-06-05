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

from __future__ import division

from . import filebytes
from . import setting
from . import util

class Fileops (object):
    def __init__(self, ref):
        self.__ref = ref
        self.__pos = 0
        self.__ppos = 0
        self.__trail = 0
        self.__reg = None
        self.__init_ops()

    def __getattr__(self, name):
        if name == "_Fileops__ref":
            raise AttributeError(name)
        return getattr(self.__ref, name)

    def __str__(self):
        return str(self.__ref)

    def cleanup(self):
        if not self.__ref:
            return -1
        self.__ref.cleanup()
        self.__ref = None

    def test_insert(self):
        return self.__ref.test_insert()
    def test_replace(self):
        return self.__ref.test_replace()
    def test_delete(self):
        return self.__ref.test_delete()

    def is_readonly(self):
        return self.__ref.is_readonly()
    def is_empty(self):
        return self.__ref.is_empty()
    def is_dirty(self):
        return self.__ref._is_dirty()

    def get_size(self):
        return self.__ref._get_size()
    def get_sector_size(self):
        return self.__ref.get_sector_size()
    def get_path(self):
        return self.__ref.get_path()
    def get_short_path(self):
        return self.__ref.get_short_path()
    def get_magic(self):
        return self.__ref.get_magic()
    def get_mapping_offset(self):
        return self.__ref.get_mapping_offset()
    def get_mapping_length(self):
        return self.__ref.get_mapping_length()
    def get_type(self):
        return util.get_class(self.__ref)

    def get_pos_percentage(self):
        if self.is_empty():
            return float(0)
        else:
            return 100.0 * (self.get_pos() + 1) / self.get_size()

    def get_max_pos(self):
        if self.is_empty():
            return 0
        else:
            return self.get_size() - 1 + self.__trail

    def get_pos(self):
        return self.__pos
    def get_prev_pos(self):
        return self.__ppos

    def add_pos(self, d):
        self.__set_pos(self.__pos + d)
    def set_pos(self, n):
        self.__set_pos(n)

    def __set_pos(self, pos):
        self.__ppos = self.__pos
        if pos > self.get_max_pos():
            self.__pos = self.get_max_pos()
        elif pos < 0:
            self.__pos = 0
        else:
            self.__pos = pos

    def discard_eof(self):
        self.__trail = self.test_insert() * 1
    def restore_eof(self):
        self.__trail = 0

    def init_region(self, orig, type):
        assert not self.__reg
        self.__reg = util.Namespace(orig=orig)
        self.set_region_type(type)
        self.set_region_range(None, None, None)

    def cleanup_region(self):
        self.__reg = None

    def get_region_origin(self):
        return self.__reg.orig

    def get_region_type(self):
        return self.__reg.type
    def set_region_type(self, type):
        self.__reg.set(type=type)

    def get_region_range(self):
        return self.__reg.beg, self.__reg.end, self.__reg.map
    def set_region_range(self, beg, end, map):
        self.__reg.set(beg=beg, end=end, map=map)

    def flush(self, f=None):
        return self.__ref.flush(f)

    def search(self, x, word, end=-1):
        return self.__ref.search(x, word, end)
    def rsearch(self, x, word, end=-1):
        return self.__ref.rsearch(x, word, end)

    def __init_ops(self):
        if setting.use_debug:
            self.read    = self.__read_debug
            self.insert  = self.__insert_debug
            self.replace = self.__replace_debug
            self.delete  = self.__delete_debug
        else:
            self.read    = self.__read
            self.insert  = self.__insert
            self.replace = self.__replace
            self.delete  = self.__delete

    def __read_debug(self, x, n):
        self.__assert_position(x)
        return self.__read(x, n)

    def __insert_debug(self, x, l, rec=True):
        self.__assert_position(x)
        self.__insert(x, l, rec)

    def __replace_debug(self, x, l, rec=True):
        self.__assert_position(x)
        self.__replace(x, l, rec)

    def __delete_debug(self, x, n, rec=True):
        self.__assert_position(x)
        self.__delete(x, n, rec)

    def __assert_position(self, x):
        assert 0 <= x <= self.get_max_pos(), x

    def __read(self, x, n):
        if x + n > self.get_size():
            n = self.get_size() - x
        if n <= 0:
            return filebytes.BLANK
        if self.__ref.is_barrier_active():
            return self.__ref.barrier_read(x, n)
        else:
            return self.__ref.read(x, n)

    def __insert(self, x, l, rec=True):
        if self.__ref.is_barrier_active():
            self.__ref.barrier_insert(x, l, rec)
        else:
            self.__ref.insert(x, l, rec)

    def __replace(self, x, l, rec=True):
        if self.__ref.is_barrier_active():
            self.__ref.barrier_replace(x, l, rec)
        else:
            self.__ref.replace(x, l, rec)

    def __delete(self, x, n, rec=True):
        if x + n > self.get_size():
            n = self.get_size() - x
        if n <= 0:
            return
        if self.__ref.is_barrier_active():
            self.__ref.barrier_delete(x, n, rec)
        else:
            self.__ref.delete(x, n, rec)

    def has_undo(self):
        return self.__ref.has_undo()
    def has_redo(self):
        return self.__ref.has_redo()

    def get_undo_size(self):
        return self.__ref.get_undo_size()
    def get_redo_size(self):
        return self.__ref.get_redo_size()
    def get_rollback_log_size(self):
        return self.__ref.get_rollback_log_size()

    def merge_undo(self, n):
        self.__ref.merge_undo(n)
    def merge_undo_until(self, to):
        """Merge until # of remaining undos is arg to"""
        self.merge_undo(self.get_undo_size() - to)

    def undo(self, n=1):
        return self.__ref.undo(n)
    def redo(self, n=1):
        return self.__ref.redo(n)

    def rollback(self, n=1):
        return self.__ref.rollback(n)
    def rollback_until(self, to):
        """Rollback until # of remaining undos is arg to"""
        return self.rollback(self.get_undo_size() - to)

    def rollback_restore_until(self, to):
        ret = self.rollback_until(to)
        if ret >= 0:
            self.set_pos(ret)

    def get_barrier(self, bsiz):
        if bsiz < 0:
            return -1
        assert not self.__ref.get_barrier_size()
        d = bsiz // 2
        pos = self.get_pos()
        beg = pos - d
        end = pos + d
        siz = self.get_size()
        if beg < 0:
            end -= beg
            if end > siz:
                end = siz
            beg = 0
        if end > siz:
            beg -= (end - siz)
            if beg < 0:
                beg = 0
            end = siz
        return self.__ref.get_barrier(pos, beg, end - beg)

    def put_barrier(self):
        return self.__ref.put_barrier()
