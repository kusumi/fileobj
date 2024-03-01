# Copyright (c) 2015, Tomohiro Kusumi
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
import json
import os

from . import kernel
from . import log
from . import path
from . import setting
from . import util

class Marks (object):
    def __init__(self, f):
        self.__path = path.Path(f)
        self.__data = {}
        if _is_valid_path(self.__path):
            self.__read_marks()

    def __iter__(self):
        for f, d in sorted(self.__data.items()):
            yield f, dict(d)

    def flush(self):
        if _is_valid_path(self.__path):
            self.__write_marks()

    def __read_marks(self):
        f = self.__path.path
        if not self.__path.is_reg:
            if not self.__path.is_noent:
                log.error("Can not read " + f)
            return -1
        try:
            with kernel.fopen_text(f) as fd:
                self.__data = self.__load_db(fd) # unicode_to_str unneeded
        except Exception as e:
            log.error("Failed to read {0}, {1}".format(f, e))

    def __load_db(self, fd):
        d = json.load(fd)
        assert isinstance(d, dict), d
        return d

    def __write_marks(self):
        assert _is_valid_path(self.__path)
        f = self.__path.path
        try:
            if setting.use_fsync_config_file:
                fsync = kernel.fsync
            else:
                fsync = None
            with util.do_atomic_write(f, binary=False, fsync=fsync) as fd:
                self.__store_db(fd)
        except Exception as e:
            log.error("Failed to write to {0}, {1}".format(f, e))

    def __store_db(self, fd):
        d = {}
        for k, v in self:
            if (os.path.isfile(k) or kernel.is_blkdev(k)) and v:
                d[k] = v
        json.dump(d, fd)

    def get(self, f):
        d = self.__data.get(f)
        return dict(d) if d else dict()

    def set(self, f, d):
        self.__data[f] = d

def _is_valid_path(o):
    return o.is_reg or o.is_noent

def get_mark_repr(k, v):
    return "  '{0}' {1}[B]".format(k, v)
