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

    def __is_valid_class(self, cls, offset):
        return cls._enabled and \
            (cls._partial or not offset)

    def __is_ro_class(self, cls):
        return not (cls._insert or cls._replace or cls._delete)

    def __get_ro_class(self, cls):
        if self.__is_ro_class(cls):
            return cls
        return {
            self.rwmap: self.romap,
            self.rwbuf: self.robuf,
            self.rwfd : self.rofd,
            self.rwblk: self.roblk,
        }.get(cls)

    def __get_alt_class(self, cls):
        return { # no alternative for rofd and roblk
            self.romap: self.robuf,
            self.rwmap: self.rwbuf,
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
        f, offset = util.parse_file_path(f)
        o = path.Path(f)
        if not f or o.is_noent:
            return self.__alloc(f, 0, self.rwbuf)
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
            if self.__is_valid_class(cls, offset):
                if util.is_subclass(cls, self.romap):
                    size = kernel.get_buffer_size_safe(f)
                    if size == -1:
                        log.error("Failed to read size of {0}".format(f))
                    elif size < setting.mmap_thresh:
                        cls = self.__get_alt_class(cls)
                return self.__alloc(f, offset, cls)
            cls = self.__get_alt_class(cls)

    def __alloc(self, f, offset, cls):
        while cls:
            try:
                log.info("Using {0} for {1}".format(cls, repr(f)))
                ret = cls(f, offset)
                ret.set_magic()
                return ret
            except Exception:
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

def alloc(f):
    return _allocator.alloc(f)

_allocator = Allocator()
