# Copyright (c) 2010-2016, Tomohiro Kusumi
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
import csv
import os
import re
import time

from . import kernel
from . import log
from . import path
from . import setting
from . import util

class Marks (object):
    def __init__(self, f):
        if not f:
            f = setting.get_marks_path()
        self.__path = path.Path(f)
        self.__data = {}
        if _is_valid_path(self.__path):
            self.__read_marks()

    def __iter__(self):
        for f in sorted(self.__data):
            yield f, dict(self.__data.get(f))

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
                fd.readline() # time
                for ff, d in self.__iter_csv(fd):
                    self.__data[ff] = d
        except Exception as e:
            log.error("Failed to read {0}, {1}".format(f, e))
            raise e

    def __iter_csv(self, fd):
        for l in csv.reader(fd):
            ff = l[0]
            d = {}
            for s in l[1:]:
                k, v = _string_to_data(s)
                d[k] = v
            assert ff, ff
            assert d, d
            yield ff, d

    def __write_marks(self):
        assert _is_valid_path(self.__path)
        f = self.__path.path
        try:
            fsync = kernel.fsync
            with util.do_atomic_write(f, binary=False, fsync=fsync) as fd:
                fd.write("# {0}\n".format(time.ctime()))
                self.__store_csv(fd)
        except Exception as e:
            log.error("Failed to write to {0}, {1}".format(f, e))

    def __store_csv(self, fd):
        writer = csv.writer(fd, lineterminator=os.linesep)
        for ff, d in self:
            if (os.path.isfile(ff) or kernel.is_blkdev(ff)) and d:
                l = [ff]
                for x in d.items():
                    l.append(_data_to_string(*x))
                writer.writerow(l)

    def get(self, f):
        d = self.__data.get(f)
        return dict(d) if d else dict()

    def set(self, f, d):
        self.__data[f] = d

def _is_valid_path(o):
    return o.is_reg or o.is_noent

def _string_to_data(s):
    m = re.match(r"^(\S)(\d+)$", s)
    assert m
    k = m.group(1)
    v = int(m.group(2))
    return k, v

def _data_to_string(k, v):
    assert isinstance(k, str)
    assert isinstance(v, int)
    assert len(k) == 1
    return k + str(v)

def print_marks(f):
    l = []
    for ff, d in Marks(f):
        l.append(ff)
        for k, v in sorted(d.items()):
            l.append(get_mark_repr(k, v))
        l.append('')
    if l:
        s = '\n'.join(l)
    else:
        s = "No mark"
    util.printf(s.rstrip())

def get_mark_repr(k, v):
    return "  '{0}' {1}[B]".format(k, v)
