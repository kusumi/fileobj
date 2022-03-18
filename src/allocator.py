# Copyright (c) 2013, Tomohiro Kusumi
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

from . import fileobj
from . import kernel
from . import log
from . import path
from . import setting
from . import util

class Error (util.GenericError):
    pass

class Allocator (object):
    def __init__(self):
        for s in iter_module_name():
            cls = fileobj.get_class(s)
            assert cls is not None, s
            setattr(self, s, cls)
        assert self.set_default_class("rwmap") != -1

    def iter_class(self):
        for s in iter_module_name():
            yield getattr(self, s)

    def iter_enabled_class(self):
        for cls in self.iter_class():
            if cls._enabled:
                yield cls

    def get_default_class(self):
        return self.__def_class

    def set_default_class(self, s):
        if hasattr(self, s):
            self.__def_class = getattr(self, s)
        else:
            return -1

    def set_default_buffer_class(self):
        return self.set_default_class("rwbuf")

    def __is_valid_class(self, cls, offset, length):
        if not cls._enabled:
            return False
        if offset and not cls._partial:
            return False
        if length and not cls._partial:
            return False
        return True

    def __is_ro_class(self, cls):
        return not (cls._insert or cls._replace or cls._delete)

    def __get_ro_class(self, cls):
        if self.__is_ro_class(cls):
            return cls
        return {
            self.rrmap: self.romap,
            self.rwmap: self.romap,
            self.rrbuf: self.robuf,
            self.rwbuf: self.robuf,
            self.rwfd : self.rofd,
            self.rwblk: self.roblk,
            self.rrvm : self.rovm,
        }.get(cls)

    def __get_alt_class(self, cls):
        return { # no alternative for rofd, roblk and rovm
            self.romap: self.robuf,
            self.rrmap: self.rwbuf,
            self.rwmap: self.rrmap,
            self.robuf: self.rofd,
            self.rrbuf: self.rwfd,
            self.rwbuf: self.rrbuf,
            self.rwfd : self.rofd,
            self.rwblk: self.roblk,
            self.rrvm : self.rovm,
        }.get(cls)

    def __get_blk_class(self, cls):
        if self.__is_ro_class(cls):
            return self.roblk
        else:
            return self.rwblk

    def __get_vm_class(self, cls):
        if self.__is_ro_class(cls):
            return self.rovm
        else:
            return self.rrvm

    def alloc(self, f, readonly):
        f = path.get_path(f)
        f, offset, length = kernel.parse_file_path(f)
        o = path.Path(f)
        is_non = not f or o.is_noent
        is_pid = setting.use_pid_path and kernel.is_pid_path(f)

        if is_non and not is_pid:
            # prefer rwmap to support truncate by default
            if self.rwmap._enabled:
                cls = self.rwmap
            else:
                cls = self.rwbuf
            return self.__alloc(f, 0, 0, cls)

        ret = path.get_path_failure_message(o)
        if ret:
            if setting.use_debug:
                log.error(ret)
            else:
                log.debug(ret)
            raise Error(ret)

        cls = self.__def_class
        if setting.use_readonly or readonly or \
            (not is_pid and not util.is_write_ok(f)):
            cls = self.__get_ro_class(cls)
        if kernel.is_blkdev(f):
            cls = self.__get_blk_class(cls)
        if is_non and is_pid:
            cls = self.__get_vm_class(cls)

        while cls:
            if self.__is_valid_class(cls, offset, length):
                if util.is_subclass(cls, self.romap):
                    cls = self.__test_mmap_class(f, offset, length, cls)
                return self.__alloc(f, offset, length, cls)
            cls = self.__get_alt_class(cls)
        assert False, "Failed to allocate fileobj"

    def __test_mmap_class(self, f, offset, length, cls):
        try:
            size = kernel.get_size(f)
        except Exception:
            size = -1
        if size == -1:
            log.error("Failed to stat " + f)
        elif size < kernel.get_page_size():
            # don't alter cls to support truncate by default
            pass
            #if self.__is_ro_class(cls):
            #    cls = self.robuf
            #else:
            #    cls = self.rwbuf
        return cls

    def __alloc(self, f, offset, length, cls):
        while cls:
            _ = None
            try:
                log.debug("Using {0} for '{1}'".format(cls, f))
                ret = cls(f, offset, length)
                ret.set_magic()
                log.debug("Allocated {0} for '{1}'".format(repr(ret), f))
                return ret
            except Exception as e:
                s = "Using {0} for '{1}' failed: {2}".format(cls, f, e)
                if isinstance(e, util.Message):
                    log.debug(s)
                else:
                    log.error(s)
                cls = self.__get_alt_class(cls)
                if not cls:
                    _ = e
            # can't raise another exception from except scope
            if _ is not None:
                raise Error(str(_))

def iter_module_name():
    yield "romap"
    yield "rrmap"
    yield "rwmap"
    yield "robuf"
    yield "rrbuf"
    yield "rwbuf"
    yield "rofd"
    yield "rwfd"
    yield "roblk"
    yield "rwblk"
    yield "rovm"
    yield "rrvm"
    yield "roext"
    yield "rwext"

def iter_class():
    return _allocator.iter_class()

def iter_enabled_class():
    return _allocator.iter_enabled_class()

def get_default_class():
    return _allocator.get_default_class()

def set_default_class(s):
    return _allocator.set_default_class(s)

def set_default_buffer_class():
    return _allocator.set_default_buffer_class()

def alloc(f, readonly=False):
    return _allocator.alloc(f, readonly)

_allocator = Allocator()
