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

from . import fileobj
from . import kernel
from . import log
from . import path
from . import setting
from . import util

class Allocator (object):
    def __init__(self):
        for s in iter_module_name():
            setattr(self, s, fileobj.get_class(s))
        self.set_default_class("rwmap")

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
            self.rwbuf: self.robuf,
            self.rwfd : self.rofd,
            self.rwblk: self.roblk,
        }.get(cls)

    def __get_alt_class(self, cls):
        return { # no alternative for rofd and roblk
            self.romap: self.robuf,
            self.rrmap: self.rwbuf,
            self.rwmap: self.rrmap,
            self.robuf: self.rofd,
            self.rwbuf: self.rwfd,
            self.rwfd : self.rofd,
            self.rwblk: self.roblk,
        }.get(cls)

    def __get_blk_class(self, cls):
        if self.__is_ro_class(cls):
            return self.roblk
        else:
            return self.rwblk

    def alloc(self, f):
        f = path.get_path(f)
        f, offset, length = util.parse_file_path(f)
        o = path.Path(f)
        if not f or o.is_noent:
            if setting.use_alloc_noent_rwbuf or \
                not self.__is_valid_class(self.rwmap, 0, 0):
                return self.__alloc(f, 0, 0, self.rwbuf)
            else:
                return self.__alloc(f, 0, 0, self.rwmap)
        ret = path.get_path_failure_message(o)
        if ret:
            log.error(ret)
            return

        cls = self.__def_class
        if setting.use_readonly or not util.is_writable(f):
            cls = self.__get_ro_class(cls)
        if kernel.is_blkdev(f):
            cls = self.__get_blk_class(cls)

        while cls:
            if self.__is_valid_class(cls, offset, length):
                if util.is_subclass(cls, self.romap):
                    cls = self.__test_mmap_class(f, offset, length, cls)
                return self.__alloc(f, offset, length, cls)
            cls = self.__get_alt_class(cls)

    def __test_mmap_class(self, f, offset, length, cls):
        size = kernel.get_buffer_size_safe(f)
        if size == -1:
            log.error("Failed to stat {0}".format(f))
        elif size < setting.mmap_thresh:
            if self.__is_ro_class(cls):
                cls = self.robuf
            else:
                cls = self.rwbuf
        if not setting.use_readonly and (offset or length):
            cls = self.__get_alt_class(cls)
        return cls

    def __alloc(self, f, offset, length, cls):
        while cls:
            try:
                log.info("Trying {0} for {1}".format(cls, repr(f)))
                ret = cls(f, offset, length)
                ret.set_magic()
                log.info("Using {0} for {1}".format(cls, repr(f)))
                return ret
            except Exception as e:
                log.error(e)
                if setting.use_alloc_raise:
                    raise
                elif setting.use_alloc_retry:
                    cls = self.__get_alt_class(cls)
                    if not cls:
                        return
                else:
                    return

def iter_module_name():
    yield "romap"
    yield "rrmap"
    yield "rwmap"
    yield "robuf"
    yield "rwbuf"
    yield "rofd"
    yield "rwfd"
    yield "roblk"
    yield "rwblk"

def get_default_class():
    return _allocator.get_default_class()

def set_default_class(s):
    return _allocator.set_default_class(s)

def set_default_buffer_class():
    return _allocator.set_default_buffer_class()

def alloc(f):
    return _allocator.alloc(f)

_allocator = Allocator()
