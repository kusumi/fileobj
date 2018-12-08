# Copyright (c) 2010, Tomohiro Kusumi
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

from . import fileattr
from . import filebytes
from . import kernel
from . import log
from . import magic
from . import package
from . import path
from . import screen
from . import setting
from . import undo
from . import util

# fileobj.Fileobj
#     romap.Fileobj
#         rrmap.Fileobj
#             rwmap.Fileobj
#     robuf.Fileobj
#         roext.Fileobj
#         rovm.Fileobj
#         rrbuf.Fileobj
#             rrvm.Fileobj
#             rwbuf.Fileobj
#                 rwext.Fileobj
#     rofd.Fileobj
#         roblk.Fileobj
#         rwfd.Fileobj
#             rwblk.Fileobj

# any negative should work
ERROR     = -1
NOTFOUND  = -2
INTERRUPT = -3

class FileobjError (util.GenericError):
    pass

class Fileobj (object):
    def __init__(self, f, offset, length):
        self.__id = -1
        self.__path = self.__init_path(f)
        self.__attr = fileattr.get(self.get_path())
        self.__attr.offset, self.__attr.length = \
            self.__parse_mapping_attributes(offset, length)
        self.__clear_barrier()
        self.init()

    def init(self):
        self.init_id()
        self.ctr()

    def cleanup(self):
        self.dtr()
        self.__id = -1
        fileattr.remove(self.get_path())

    def ctr(self):
        return

    def dtr(self):
        return

    def __init_path(self, f):
        ret = path.Path(f)
        if not path.is_canonical_type(ret):
            raise FileobjError("Invalid type " + ret.type)
        else:
            return ret

    def init_id(self):
        self.__id = -1
        f = self.get_path()
        if not os.path.exists(f):
            return self.__id
        try:
            self.__id = kernel.get_inode(f)
        except Exception as e:
            log.debug(e)
        finally:
            return self.__id

    def test_id(self, f):
        if self.__id == -1:
            return True
        assert os.path.exists(f), (f, self.__id)
        try:
            return self.__id == kernel.get_inode(f)
        except Exception as e:
            log.debug(e)
            return True

    def set_magic(self):
        if self.__path.is_reg:
            self.__attr.magic = magic.get_string(self)
        elif kernel.is_blkdev(self.get_path()):
            self.__attr.magic = magic.get_blk_string(self)

    def test_access(self):
        return True

    def test_insert(self):
        return self._insert

    def test_replace(self):
        return self._replace

    def test_delete(self):
        return self._delete

    def test_enabled(self):
        return self._enabled

    def test_partial(self):
        return self._partial

    def is_readonly(self):
        assert self.test_enabled()
        if self.test_insert():
            return False
        if self.test_replace():
            return False
        if self.test_delete():
            return False
        return True

    def is_empty(self):
        size = self.get_size()
        if not self.is_barrier_active():
            return size <= 0
        elif size <= 0:
            return self.is_barrier_empty()
        else:
            size += self.get_barrier_delta()
            return size <= 0

    def clear_dirty(self):
        return

    def is_dirty(self):
        util.raise_no_impl("is_dirty")

    def get_size(self):
        util.raise_no_impl("get_size")

    def get_sector_size(self):
        return -1

    def get_id(self):
        return self.__id

    def get_path(self):
        return self.__path.path

    def get_short_path(self):
        return self.__path.short_path

    def get_alias(self):
        return ''

    def get_magic(self):
        return self.__attr.magic

    def get_mapping_offset(self):
        return self.__attr.offset

    def get_mapping_length(self):
        return self.__attr.length

    def get_buffer_size(self):
        # heuristic
        ret = kernel.get_buffer_size()
        siz = self.get_size()
        if ret >= siz:
            return ret
        elif siz > util.MiB: # ret < siz
            return util.MiB
        else:
            return ret

    def __parse_mapping_attributes(self, offset, length):
        f = self.get_path()
        try:
            bufsiz = kernel.get_size(f)
        except Exception:
            bufsiz = -1
        if bufsiz == -1:
            if os.path.isfile(f):
                log.error("Failed to stat {0}, using 0/0".format(f))
            return 0, 0

        if offset <= 0:
            _offset = 0
        elif offset >= bufsiz:
            _offset = 0
        else:
            _offset = offset

        if length <= 0:
            _length = 0
        elif _offset + length > bufsiz:
            _length = bufsiz - _offset
        else:
            _length = length
        return _offset, _length

    def flush(self, f=None):
        this = self.get_path()
        if not f:
            f = this
            if not f:
                raise FileobjError("No file name")
        if this == f:
            if self.is_readonly():
                raise FileobjError("Read only")
        elif os.path.isdir(f):
            raise FileobjError(f + " is a directory")
        elif os.path.exists(f):
            raise FileobjError(f + " exists")

        if this == f and not self.test_id(f):
            raise FileobjError(f + " has been changed since reading it!!!")

        o = path.Path(f)
        f = o.path
        ret = path.get_path_failure_message(o)
        if ret:
            raise FileobjError(ret)
        if os.path.exists(f):
            msg = ''
        else:
            msg = "[New] "

        try:
            creat = False
            if not this or this == f:
                if os.path.exists(this):
                    if self.is_dirty():
                        self.sync()
                    else:
                        self.utime()
                else:
                    self.creat(f)
                    creat = True
                self.sync_undo()
            else:
                assert not os.path.exists(f), f
                self.creat(f)
        except Exception as e:
            raise FileobjError("Failed to write: " +
                util.e_to_string(e, verbose=False))
        else:
            msg += "{0} {1}[B] written".format(f, self.get_size())
            if creat:
                fileattr.rename(this, f)
                return msg, f
            else:
                return msg, None

    def sync(self):
        raise FileobjError("Read only")

    def utime(self):
        kernel.touch(self.get_path())

    def creat(self, f):
        with kernel.fcreat(f) as fd:
            siz = self.get_buffer_size()
            pos = 0
            while True:
                b = self.read(pos, siz)
                if not b:
                    break
                fd.write(b)
                pos += len(b)
            kernel.fsync(fd)

    def get_search_word(self):
        return self.__attr.word

    def set_search_word(self, s):
        assert isinstance(s, filebytes.TYPE), (s, type(s))
        self.__attr.word = s

    def search(self, x, s, end=-1):
        self.set_search_word(s)
        return self.find(x, s, end)

    def rsearch(self, x, s, end=-1):
        self.set_search_word(s)
        return self.rfind(x, s, end)

    def iter_search(self, x, word):
        while True:
            ret = self.search(x, word)
            if ret == NOTFOUND or ret == INTERRUPT:
                break
            yield ret
            x = ret + 1
            if x >= self.get_size():
                break

    def iter_rsearch(self, x, word):
        while True:
            ret = self.rsearch(x, word)
            if ret == NOTFOUND or ret == INTERRUPT:
                break
            yield ret
            x = ret - 1
            if x < 0:
                break

    def read(self, x, n):
        self.raise_no_support("read")

    def insert(self, x, l, rec=True):
        self.raise_no_support("insert")

    def replace(self, x, l, rec=True):
        self.raise_no_support("replace")

    def delete(self, x, n, rec=True):
        self.raise_no_support("delete")

    def readall(self):
        return self.read(0, self.get_size())

    buffer = property(lambda self: self.readall())
    binary = property(lambda self: filebytes.ords(self.buffer))

    def iter_read(self, x, n):
        while True:
            ret = self.read(x, n)
            if not ret:
                break
            yield ret
            x += len(ret)
            if x >= self.get_size():
                break

    def raise_no_support(self, s):
        if setting.use_readonly and s in ("insert", "replace", "delete"):
            raise FileobjError("Using readonly mode")
        else:
            raise FileobjError(self.get_no_support_string(s))

    def get_no_support_string(self, s):
        return s + " not supported"

    def has_undo(self):
        return self.get_undo_size() > 0

    def has_redo(self):
        return self.get_redo_size() > 0

    def get_undo_size(self):
        return self.__attr.undo.get_undo_size()

    def get_redo_size(self):
        return self.__attr.undo.get_redo_size()

    def get_rollback_log_size(self):
        return self.__attr.undo.get_rollback_log_size()

    def add_undo(self, ufn, rfn):
        self.__attr.undo.add_undo(ufn, rfn)

    def merge_undo(self, n):
        self.__attr.undo.merge_undo(n)

    def sync_undo(self):
        self.__attr.undo.sync_base_pointer()
        self.clear_dirty()

    def restore_rollback_log(self, ref):
        self.__attr.undo.restore_rollback_log(ref)

    def undo(self, n=1):
        return self.__undo(n, self.__attr.undo.undo)

    def redo(self, n=1):
        return self.__undo(n, self.__attr.undo.redo)

    def __undo(self, n, fn):
        ret = NOTFOUND
        for i in util.get_xrange(n):
            ret, is_at_base, msg = fn(self)
            if is_at_base:
                self.clear_dirty()
            if ret == undo.ERROR:
                return ERROR, msg
            if ret == undo.NOTFOUND:
                return NOTFOUND, ''
            if screen.test_signal():
                return INTERRUPT, ''
        return ret, ''

    def rollback(self, n=1):
        if n < 1:
            return -1
        else:
            if n > 1:
                x = self.get_undo_size()
                self.merge_undo(n)
                if n <= x:
                    assert self.get_undo_size() == x - n + 1
            return self.undo(1)

    def get_mark(self, k):
        return self.__attr.marks.get(k, -1)

    def set_mark(self, k, v):
        if self.get_mark(k) == v:
            return -1
        self.__attr.marks[k] = v

    def get_marks(self):
        return dict(self.__attr.marks)

    def set_marks(self, d):
        self.__attr.marks = d

    def delete_mark(self, k):
        if k in self.__attr.marks:
            del self.__attr.marks[k]

    def clear_marks(self, cond):
        # Python 3 needs to cast to list or tuple
        for k in tuple(self.__attr.marks.keys()):
            if not cond or cond(k):
                del self.__attr.marks[k]

    def get_session_value(self, k):
        return self.__attr.session.get(k, -1)

    def set_session_value(self, k, v):
        if self.get_session_value(k) == v:
            return -1
        self.__attr.session[k] = v

    def get_session(self):
        return dict(self.__attr.session)

    def set_session(self, d):
        self.__attr.session = d

    def get_barrier(self, ret, offset, size):
        try:
            self.__bretval = ret
            self.__boffset = offset
            self.__bbuffer = self.__read_bbuffer(self.__boffset, size)
            self.__bsize = self.get_barrier_size()
            self.__bdirty = False
        except Exception as e:
            log.error(e)
            self.put_barrier()
            return -1

    def put_barrier(self):
        if self.__bretval == -1:
            return -1
        else:
            ret = self.__bretval
            self.__clear_barrier()
            return ret

    def __clear_barrier(self):
        self.__bretval = -1
        self.__boffset = -1
        self.__bbuffer = []
        self.__bsize = 0
        self.__bdirty = False

    def is_barrier_active(self):
        return self.__bretval != -1

    def is_barrier_empty(self):
        return self.get_barrier_size() <= 0

    def is_barrier_dirty(self):
        return self.__bdirty

    def get_barrier_size(self):
        return len(self.__bbuffer)

    def get_barrier_delta(self):
        return self.get_barrier_size() - self.__bsize

    def get_barrier_range(self):
        if self.is_barrier_active():
            return self.__boffset, \
                self.__boffset + self.get_barrier_size() - 1, \
                self.get_barrier_delta()
        else:
            return -1, -1, -1

    def __read_bbuffer(self, x, n):
        return list(filebytes.iter_ords(self.read(x, n)))

    def barrier_read(self, x, n):
        self.__test_barrier(x, n)
        if setting.use_debug:
            a, b, c = self.get_barrier_range()
            assert x >= a
            assert x + n <= b + 1
        x -= self.__boffset
        return filebytes.input_to_bytes(self.__bbuffer[x : x + n])

    def barrier_insert(self, x, l, rec=True):
        self.__test_barrier(x, 0)
        self.__bdirty = True
        x -= self.__boffset
        self.__bbuffer[x : x] = l
        if self.get_barrier_size() == len(l):
            self.__right_extend_barrier(1)

    def barrier_replace(self, x, l, rec=True):
        self.__test_barrier(x, 0)
        self.__bdirty = True
        x -= self.__boffset
        self.__bbuffer[x : x + len(l)] = l

    def barrier_delete(self, x, n, rec=True):
        self.__test_barrier(x, n)
        self.__bdirty = True
        x -= self.__boffset
        del self.__bbuffer[x : x + n]

    def __test_barrier(self, x, n):
        size = setting.barrier_extend
        while x - self.__boffset < 0:
            if self.__left_extend_barrier(size) == -1:
                break
        while x - self.__boffset + n > self.get_barrier_size():
            if self.__right_extend_barrier(size) == -1:
                break

    def __left_extend_barrier(self, size):
        pos = self.__boffset - size
        if pos < 0:
            size += pos
            pos = 0
        buf = self.__read_bbuffer(pos, size)
        assert len(buf) == size
        buf.extend(self.__bbuffer)
        self.__boffset = pos
        self.__bbuffer = buf
        self.__bsize += size
        if self.__boffset <= 0:
            return -1

    def __right_extend_barrier(self, size):
        pos = self.__boffset + self.__bsize
        if pos + size > self.get_size():
            size = self.get_size() - pos
        buf = self.__read_bbuffer(pos, size)
        assert len(buf) == size
        self.__bbuffer.extend(buf)
        self.__bsize += size
        if self.__boffset + self.get_barrier_size() >= self.get_size():
            return -1

    def ioctl(self, arg):
        return

def get_class(s):
    if s:
        o = util.import_module(package.get_prefix() + s)
        if o:
            for cls in util.iter_dir_values(o):
                if util.is_subclass(cls, Fileobj, False):
                    return cls
