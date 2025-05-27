# Copyright (c) 2025, Tomohiro Kusumi
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
from . import fileobj
from . import fileops
from . import setting
from . import util

class Error (util.GenericError):
    pass

class Fileops (object):
    def __init__(self, opsl):
        assert opsl, opsl
        l = [ops.get_path() for ops in opsl]
        self.__has_dup = len(l) != len(set(l))
        if self.__has_dup and not setting.allow_dup_path:
            raise Error("Duplicate paths in {0}".format(l))
        self.__opsl = tuple(opsl)
        self.__init_ops()

    def __len__(self):
        return self.get_size()

    def __getitem__(self, arg):
        if isinstance(arg, int):
            pos = arg
            siz = 1
        elif isinstance(arg, slice):
            l = arg.indices(self.get_size())
            pos = l[0]
            siz = l[1] - l[0]
        else:
            assert False, arg
        pos = fileops.get_adjusted_pos(self, pos)
        siz = fileops.get_adjusted_size(self, siz)
        return self.read(pos, siz)

    def __str__(self):
        l = []
        for ops in self.__opsl:
            l.append(str(ops))
        return '\n'.join(l)

    def cleanup(self):
        for ops in self.__opsl:
            ops.cleanup()

    def clone(self):
        l = []
        for ops in self.__opsl:
            l.append(ops.clone())
        return Fileops(l)

    def test_access(self):
        for ops in self.__opsl:
            if not ops.test_access():
                return False
        return True

    def test_insert(self):
        return False # XXX
        if self.__has_dup:
            return False
        for ops in self.__opsl:
            if not ops.test_insert():
                return False
        return True

    def test_replace(self):
        if self.__has_dup:
            return False
        for ops in self.__opsl:
            if not ops.test_replace():
                return False
        return True

    def test_delete(self):
        return False # XXX
        if self.__has_dup:
            return False
        for ops in self.__opsl:
            if not ops.test_delete():
                return False
        return True

    def test_truncate(self):
        return False # XXX
        if self.__has_dup:
            return False
        for ops in self.__opsl:
            if not ops.test_truncate():
                return False
        return True

    def is_killed(self):
        for ops in self.__opsl:
            if not ops.is_killed():
                return False
        return True

    def is_buf(self):
        for ops in self.__opsl:
            if not ops.is_buf():
                return False
        return True

    def is_blk(self):
        for ops in self.__opsl:
            if not ops.is_blk():
                return False
        return True

    def is_vm(self):
        for ops in self.__opsl:
            if not ops.is_vm():
                return False
        return True

    def is_readonly(self):
        for ops in self.__opsl:
            if not ops.is_readonly():
                return False
        return True

    def is_empty(self):
        for ops in self.__opsl:
            if not ops.is_empty():
                return False
        return True

    def is_dirty(self):
        for ops in self.__opsl:
            if not ops.is_dirty():
                return False
        return True

    def get_size(self):
        return sum([ops.get_size() for ops in self.__opsl])

    def get_sector_size(self):
        return tuple(ops.get_sector_size() for ops in self.__opsl)

    def get_id(self):
        return tuple(ops.get_id() for ops in self.__opsl)

    def get_path(self):
        return tuple(ops.get_path() for ops in self.__opsl)

    def get_short_path(self):
        return tuple(ops.get_short_path() for ops in self.__opsl)

    def get_alias(self):
        return tuple(ops.get_alias() for ops in self.__opsl)

    def get_magic(self):
        return tuple(ops.get_magic() for ops in self.__opsl)

    def get_mapping_offset(self):
        return 0
        #return tuple(ops.get_mapping_offset() for ops in self.__opsl)

    def get_mapping_length(self):
        return 0
        #return tuple(ops.get_mapping_length() for ops in self.__opsl)

    def get_type(self):
        return tuple(ops.get_type() for ops in self.__opsl)

    def get_repr(self):
        return repr(tuple(ops.get_repr() for ops in self.__opsl))

    def get_pos_percentage(self):
        if self.is_empty():
            p = 0
        else:
            p = (self.get_pos() + 1) / self.get_size()
        return p * 100.0

    def get_max_pos(self):
        if self.is_empty():
            return 0
        return self.get_size() - 1 # no position support

    def get_pos(self):
        return 0

    def get_prev_pos(self):
        return 0

    def add_pos(self, d):
        return

    def set_pos(self, n):
        return

    def get_unit_pos(self):
        return 0

    def add_unit_pos(self, d):
        return

    def set_unit_pos(self, n):
        return

    def open_eof_insert(self):
        return

    def close_eof_insert(self):
        return

    def has_region(self):
        return False

    def init_region(self, orig, type):
        util.raise_no_impl("init_region")

    def cleanup_region(self):
        return

    def get_region_origin(self):
        util.raise_no_impl("get_region_origin")

    def get_region_type(self):
        util.raise_no_impl("get_region_type")

    def set_region_type(self, type):
        util.raise_no_impl("set_region_type")

    def get_region_range(self):
        util.raise_no_impl("get_region_range")

    def set_region_range(self, beg, end, map):
        util.raise_no_impl("set_region_range")

    def flush(self, f=None):
        return

    def get_search_word(self):
        return self.__opsl[0].get_search_word()

    def set_search_word(self, s):
        self.__opsl[0].set_search_word(s)

    def search(self, x, word, end=-1):
        return fileobj.generic_find(self, x, word, end)

    def rsearch(self, x, word, end=-1):
        return fileobj.generic_rfind(self, x, word, end)

    def iter_search(self, x, word):
        return fileobj.generic_iter_search(self,
            fileops.get_adjusted_pos(self, x), word)

    def iter_rsearch(self, x, word):
        return fileobj.generic_iter_rsearch(self,
            fileops.get_adjusted_pos(self, x), word)

    def init_buffer(self, b):
        util.raise_no_impl("init_buffer")

    def __init_ops(self):
        if setting.use_debug:
            self.read     = self.__debug_read
            self.insert   = self.__debug_insert
            self.replace  = self.__debug_replace
            self.delete   = self.__debug_delete
            self.truncate = self.__debug_truncate
        else:
            self.read     = self.__read
            self.insert   = self.__insert
            self.replace  = self.__replace
            self.delete   = self.__delete
            self.truncate = self.__truncate
        if fileops.not_builtin_script and setting.use_auto_fileops_adjust:
            self.read     = fileops.adjust_read(self, self.read)
            self.insert   = fileops.adjust_insert(self, self.insert)
            self.replace  = fileops.adjust_replace(self, self.replace)
            self.delete   = fileops.adjust_delete(self, self.delete)
            self.truncate = fileops.adjust_truncate(self, self.truncate)
        self.raw_read = self.__read

    def readall(self):
        return filebytes.BLANK.join([ops.readall() for ops in self.__opsl])

    buffer = property(lambda self: self.readall())
    binary = property(lambda self: filebytes.ords(self.buffer))

    def iter_read(self, x, n):
        return fileobj.generic_iter_read(self, x, n)

    def __debug_read(self, x, n):
        self.__assert_position(x)
        return self.__read(x, n)

    def __debug_insert(self, x, l, rec=True):
        self.__assert_position(x)
        self.__insert(x, l, rec)

    def __debug_replace(self, x, l, rec=True):
        self.__assert_position(x)
        self.__replace(x, l, rec)

    def __debug_delete(self, x, n, rec=True):
        self.__assert_position(x)
        self.__delete(x, n, rec)

    def __debug_truncate(self, n, rec=True):
        self.__truncate(n, rec)

    def __assert_position(self, x):
        _max_pos = self.get_max_pos()
        assert 0 <= x <= _max_pos, (x, _max_pos)

    def __read(self, x, n):
        if x + n > self.get_size():
            n = self.get_size() - x
        if n <= 0:
            return filebytes.BLANK
        return self.__read_impl(x, n)

    def __read_impl(self, x, n):
        ops_base = 0
        l = []
        for ops in self.__opsl:
            if n <= 0:
                assert n == 0, n
                break
            ops_size = ops.get_size()
            ops_pos = x - ops_base
            if ops_pos >= 0 and ops_pos < ops_size:
                siz = n
                if siz > ops_size:
                    siz = ops_size
                b = ops.raw_read(ops_pos, siz) # safe with debug mode
                n -= len(b)
                x += len(b)
                l.append(b)
            ops_base += ops_size
        return filebytes.BLANK.join(l)

    def __insert(self, x, l, rec=True):
        util.raise_no_impl("__insert")

    def __replace(self, x, l, rec=True):
        self.__replace_impl(x, l, rec)

    def __replace_impl(self, x, l, rec):
        ops_base = 0
        for ops in self.__opsl:
            if len(l) <= 0:
                assert len(l) == 0, l
                break
            ops_size = ops.get_size()
            ops_pos = x - ops_base
            if ops_pos >= 0 and ops_pos < ops_size:
                n = len(l)
                if n > ops_size:
                    n = ops_size
                ops.replace(ops_pos, l[:n])
                l = l[n:]
                x += n
            ops_base += ops_size

    def __delete(self, x, n, rec=True):
        if x + n > self.get_size():
            n = self.get_size() - x
        if n <= 0:
            return
        util.raise_no_impl("__delete")
        if self.get_pos() > self.get_max_pos():
            self.set_pos(self.get_max_pos())

    def __truncate(self, n, rec=True):
        if n < 0:
            n = 0
        util.raise_no_impl("__truncate")
        if self.get_pos() > self.get_max_pos():
            self.set_pos(self.get_max_pos())

    def has_undo(self):
        return False

    def has_redo(self):
        return False

    def get_undo_size(self):
        return 0

    def get_redo_size(self):
        return 0

    def get_rollback_log_size(self):
        return 0

    def merge_undo(self, n):
        util.raise_no_impl("merge_undo")

    def merge_undo_until(self, to):
        util.raise_no_impl("merge_undo_until")

    def undo(self, n=1):
        util.raise_no_impl("undo")

    def redo(self, n=1):
        util.raise_no_impl("redo")

    def rollback(self, n=1):
        util.raise_no_impl("rollback")

    def rollback_until(self, to):
        util.raise_no_impl("rollback_until")

    def rollback_restore_until(self, to):
        util.raise_no_impl("rollback_restore_until")

    def get_barrier(self, bsiz):
        util.raise_no_impl("get_barrier")

    def put_barrier(self):
        util.raise_no_impl("put_barrier")

def __alloc(opsl, printf):
    ops = Fileops(opsl)
    if setting.use_debug:
        fileops.print_fileops(ops, printf)
    return ops

def bulk_alloc(args, readonly, printf, printe):
    assert readonly
    opsl, cleanup = fileops.bulk_alloc(args, readonly, printf, printe)
    if opsl is None:
        return None, None
    return (__alloc(opsl, printf),), cleanup

def bulk_alloc_blk(args, readonly, printf, printe):
    assert readonly
    opsl, cleanup, blksiz = fileops.bulk_alloc_blk(args, readonly, printf,
        printe)
    if opsl is None:
        return None, None, None
    return (__alloc(opsl, printf),), cleanup, blksiz
