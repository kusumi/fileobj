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

from . import allocator
from . import filebytes
from . import fileobj
from . import path
from . import setting
from . import util

class Fileops (object):
    def __init__(self, ref, o=None):
        assert isinstance(ref, fileobj.Fileobj)
        self.__ref = ref
        self.__pos = o.get_pos() if o else 0
        self.__ppos = o.get_prev_pos() if o else 0
        self.__trail = 0
        self.__reg = None
        self.__init_ops()

    def __getattr__(self, name):
        if name == "_Fileops__ref":
            raise AttributeError(name)
        return getattr(self.__ref, name)

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
        assert self.__trail == 0
        pos = self.__get_normalized_pos(pos)
        siz = self.__get_normalized_size(siz)
        return self.read(pos, siz)

    def __str__(self):
        return str(self.__ref)

    def cleanup(self):
        if not self.__ref:
            return -1
        self.__ref.cleanup()
        self.__ref = None

    def clone(self):
        return Fileops(self.__ref, self)

    def test_access(self):
        return self.__ref.test_access()

    def test_insert(self):
        return self.__ref.test_insert()

    def test_replace(self):
        return self.__ref.test_replace()

    def test_delete(self):
        return self.__ref.test_delete()

    def test_truncate(self):
        return self.__ref.test_truncate()

    def is_killed(self):
        return self.__ref is None

    def is_buf(self):
        from . import robuf
        return isinstance(self.__ref, robuf.Fileobj)

    def is_blk(self):
        from . import blk
        return isinstance(self.__ref, blk.methods)

    def is_vm(self):
        from . import vm
        return isinstance(self.__ref, vm.methods)

    def is_readonly(self):
        return self.__ref.is_readonly()

    def is_empty(self):
        return self.__ref.is_empty()

    def is_dirty(self):
        return self.__ref.is_dirty() or self.__ref.is_barrier_dirty()

    def get_size(self):
        return self.__ref.get_size() + self.__ref.get_barrier_delta()

    def get_sector_size(self):
        return self.__ref.get_sector_size()

    def get_id(self):
        return self.__ref.get_id()

    def get_path(self):
        return self.__ref.get_path()

    def get_short_path(self):
        return self.__ref.get_short_path()

    def get_alias(self):
        return self.__ref.get_alias()

    def get_magic(self):
        return self.__ref.get_magic()

    def get_mapping_offset(self):
        return self.__ref.get_mapping_offset()

    def get_mapping_length(self):
        return self.__ref.get_mapping_length()

    def get_type(self):
        return util.get_class(self.__ref)

    def get_repr(self):
        return repr(self.__ref)

    def get_pos_percentage(self):
        if self.is_empty():
            p = 0
        else:
            p = (self.get_pos() + 1) / self.get_size()
        return p * 100.0

    def get_max_pos(self):
        if self.is_empty():
            return 0
        pos = self.get_size() - 1 + self.__trail
        if not setting.use_unit_based:
            return pos
        else:
            return util.rounddown(pos, setting.bytes_per_unit)

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

    def get_unit_pos(self):
        return util.rounddown(self.get_pos(), setting.bytes_per_unit)

    def add_unit_pos(self, d):
        self.set_pos(util.rounddown(self.__pos + d, setting.bytes_per_unit))

    def set_unit_pos(self, n):
        self.set_pos(util.rounddown(n, setting.bytes_per_unit))

    def open_eof_insert(self):
        self.__trail = self.test_insert() * 1

    def close_eof_insert(self):
        self.__trail = 0

    def has_region(self):
        return self.__reg is not None

    def init_region(self, orig, type):
        if setting.use_debug:
            # XXX Opening a new buffer in visual mode without using
            # visual._queue_input() cleans up visual region of the new buffer,
            # not the original one with visual region.
            # e.g. v -> l -> :open_sha1 -> <TAB> -> v
            assert self.__reg is None, self.__reg
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

    def get_search_word(self):
        return self.__ref.get_search_word()

    def set_search_word(self, s):
        self.__ref.set_search_word(s)

    def search(self, x, word, end=-1):
        return self.__ref.search(x, word, end)

    def rsearch(self, x, word, end=-1):
        return self.__ref.rsearch(x, word, end)

    def iter_search(self, x, word):
        return self.__ref.iter_search(self.__get_normalized_pos(x), word)

    def iter_rsearch(self, x, word):
        return self.__ref.iter_rsearch(self.__get_normalized_pos(x), word)

    def init_buffer(self, b):
        return self.__ref.init_buffer(b)

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
        if _not_builtin_script and setting.use_auto_fileops_adjust:
            self.read     = self.__decorate_read(self.read)
            self.insert   = self.__decorate_insert(self.insert)
            self.replace  = self.__decorate_replace(self.replace)
            self.delete   = self.__decorate_delete(self.delete)
            self.truncate = self.__decorate_truncate(self.truncate)
        self.raw_read = self.__read

    def __decorate_read(self, fn):
        def _(x, n):
            x = self.__get_normalized_pos(x)
            n = self.__get_normalized_size(n)
            return fn(x, n)
        return _

    def __decorate_insert(self, fn):
        def _(x, l, rec=True):
            try:
                self.open_eof_insert()
                x = self.__get_normalized_pos(x)
                l = self.__get_normalized_input(l)
                fn(x, l, rec)
            finally:
                self.close_eof_insert()
        return _

    def __decorate_replace(self, fn):
        def _(x, l, rec=True):
            x = self.__get_normalized_pos(x)
            l = self.__get_normalized_input(l)
            fn(x, l, rec)
        return _

    def __decorate_delete(self, fn):
        def _(x, n, rec=True):
            x = self.__get_normalized_pos(x)
            n = self.__get_normalized_size(n)
            fn(x, n, rec)
        return _

    def __decorate_truncate(self, fn):
        def _(n, rec=True):
            n = self.__get_normalized_size(n)
            fn(n, rec)
        return _

    def __get_normalized_pos(self, pos):
        _ = self.get_max_pos()
        if pos < 0:
            pos = _ + 1 + pos
        if pos < 0:
            return 0
        elif pos > _:
            return _
        else:
            return pos

    def __get_normalized_size(self, siz):
        if siz < 0:
            return 0
        elif siz > self.get_size():
            return self.get_size()
        else:
            return siz

    def __get_normalized_input(self, arg):
        if util.is_seq(arg):
            if isinstance(arg[0], str):
                arg = ''.join(arg)
            elif isinstance(arg[0], filebytes.TYPE):
                arg = filebytes.join(arg)
        if isinstance(arg, str):
            arg = util.str_to_bytes(arg)
        if isinstance(arg, filebytes.TYPE):
            arg = filebytes.bytes_to_input(arg)
        assert isinstance(arg[0], int), arg
        return arg

    def readall(self):
        return self.__ref.readall()

    def iter_read(self, x, n):
        return self.__ref.iter_read(x, n)

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
        if self.get_pos() > self.get_max_pos():
            self.set_pos(self.get_max_pos())

    def __truncate(self, n, rec=True):
        if n < 0:
            n = 0
        if self.__ref.is_barrier_active():
            self.__ref.barrier_truncate(n, rec)
        else:
            self.__ref.truncate(n, rec)
        if self.get_pos() > self.get_max_pos():
            self.set_pos(self.get_max_pos())

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
        ret = self.__ref.undo(n)
        if self.get_pos() > self.get_max_pos(): # delete on undo
            self.set_pos(self.get_max_pos())
        return ret

    def redo(self, n=1):
        ret = self.__ref.redo(n)
        if self.get_pos() > self.get_max_pos(): # delete on redo
            self.set_pos(self.get_max_pos())
        return ret

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
        siz = self.get_size()
        beg = pos - d
        end = pos + d
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

def __alloc(f, readonly):
    f = path.get_path(f)
    obj = allocator.alloc(f, readonly)
    return Fileops(obj)

def __alloc_class(f, name):
    f = path.get_path(f)
    cls = fileobj.get_class(name)
    if cls:
        obj = cls(f)
        obj.set_magic()
    else:
        obj = allocator.alloc(f)
    return Fileops(obj)

_not_builtin_script = not util.is_running_script_fileobj() and \
    not util.is_running_script_perf()

def __cleanup(args):
    ops, printf = args
    if not ops.is_killed():
        l = ops.get_path(), ops.get_type() # get before cleanup
        if ops.cleanup() != -1 and setting.use_debug:
            printf("cleanup {0} {1}".format(*l))

if _not_builtin_script and setting.use_auto_fileops_cleanup:
    import atexit

    def alloc(f, readonly=False):
        ops = __alloc(f, readonly)
        atexit.register(__cleanup, (ops, util.printf))
        return ops

    def alloc_class(f, name=""):
        ops = __alloc_class(f, name)
        atexit.register(__cleanup, (ops, util.printf))
        return ops
else:
    def alloc(f, readonly=False):
        return __alloc(f, readonly)

    def alloc_class(f, name=""):
        return __alloc_class(f, name)

class ConcatenatedFileops (object):
    def __init__(self, opsl):
        assert opsl, opsl
        self.__opsl = tuple(opsl)

    def cleanup(self):
        for ops in self.__opsl:
            ops.cleanup()

    def get_size(self):
        return sum([ops.get_size() for ops in self.__opsl])

    def get_path(self):
        return tuple(ops.get_path() for ops in self.__opsl)

    def get_mapping_offset(self):
        return self.__opsl[0].get_mapping_offset()

    def get_mapping_length(self):
        has_valid_mlen = False
        total_mlen = 0
        for ops in self.__opsl:
            mlen = ops.get_mapping_length()
            if mlen > 0:
                has_valid_mlen = True
                total_mlen += mlen
            else:
                total_mlen += ops.get_size()
        if has_valid_mlen:
            return total_mlen
        else:
            return self.get_size()

    def get_type(self):
        return tuple(ops.get_type() for ops in self.__opsl)

    def read(self, x, n):
        read_next = False
        ops_base = 0
        l = []
        for ops in self.__opsl:
            if n <= 0:
                assert n == 0, n
                break
            ops_size = ops.get_size()
            if x >= ops_base or read_next:
                pos = x - ops_base
                siz = n
                if siz > ops_size:
                    siz = ops_size
                b = ops.raw_read(pos, siz) # safe with debug mode
                n -= len(b)
                if n > 0:
                    read_next = True
                l.append(b)
            ops_base += ops_size
        return filebytes.BLANK.join(l)

def is_concatenated(ops):
    return isinstance(ops, ConcatenatedFileops)

def __alloc_concatenated_fileops(opsl, printf):
    ops = ConcatenatedFileops(opsl)
    if setting.use_debug:
        __debug_print_fileops(ops, printf)
    return ops

def __debug_print_fileops(ops, printf):
    printf("{0} {1} {2}".format(repr(ops), ops.get_path(), ops.get_type()))
    x = ops.get_size()
    printf("\tsize: {0} 0x{1:x}".format(x, x))
    x = ops.get_mapping_offset()
    printf("\tmapping offset: {0} 0x{1:x}".format(x, x))
    x = ops.get_mapping_length()
    printf("\tmapping length: {0} 0x{1:x}".format(x, x))

# bulk fileops allocation used by non editor options
def bulk_alloc(args, readonly, printf, printe):
    # allow None for print functions
    if printf is None:
        def printf(o):
            pass
    if printe is None:
        def printe(o):
            pass

    # disallow buf as default at this point
    cls = allocator.get_default_class()
    if setting.use_debug:
        printf("default class {0}".format(cls))
    if fileobj.is_subclass(cls, "robuf"):
        printe("Invalid default class {0}".format(cls))
        return None, None

    # define cleanup closure
    opsl = []
    def cleanup():
        for ops in opsl:
            __cleanup((ops, printf))
        setting.allow_dup_path = False

    # allow dup paths for underlying fileobj's
    setting.allow_dup_path = True

    # allocate fileops
    assert args, args
    for f in args:
        try:
            ops = __alloc(f, readonly)
        except Exception as e:
            printe(e)
            cleanup()
            return None, None
        assert isinstance(ops, Fileops), ops
        if setting.use_debug:
            __debug_print_fileops(ops, printf)
        opsl.append(ops)

    # sanity checks
    for ops in opsl:
        f = ops.get_path()
        if not os.path.exists(f):
            printe("No such file {0}".format(f))
            cleanup()
            return None, None
        assert os.path.exists(f), f
        assert not readonly or ops.is_readonly()
    return tuple(opsl), cleanup

def concat_alloc(args, readonly, printf, printe):
    assert readonly
    opsl, cleanup = bulk_alloc(args, readonly, printf, printe)
    if opsl is None:
        return None, None
    return __alloc_concatenated_fileops(opsl, printf), cleanup

# bulk_alloc variant
def bulk_alloc_blk(args, readonly, printf, printe):
    # determine block size
    if setting.logical_block_size > 0:
        blksiz = setting.logical_block_size
    else:
        blksiz = 1 << 16
    assert blksiz % 512 == 0, blksiz

    # allocate fileops
    opsl, cleanup = bulk_alloc(args, readonly, printf, printe)
    if opsl is None:
        return None, None, None
    for ops in opsl:
        if ops.is_blk():
            if blksiz & (ops.get_sector_size() - 1):
                printe("Invalid block size {0} for {1}".format(blksiz,
                    ops.get_path()))
                cleanup()
                return None, None, None
    return opsl, cleanup, blksiz

def concat_alloc_blk(args, readonly, printf, printe):
    assert readonly
    opsl, cleanup, blksiz = bulk_alloc_blk(args, readonly, printf, printe)
    if opsl is None:
        return None, None, None
    return __alloc_concatenated_fileops(opsl, printf), cleanup, blksiz
