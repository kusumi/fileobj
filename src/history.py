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

from __future__ import with_statement
import collections
import time

from . import literal
from . import log
from . import path
from . import setting
from . import stash
from . import util

class _data (object):
    def __init__(self, key):
        self.__key = key
        self.__cursor = -1
        self.__queue = collections.deque() # first is latest

    def __len__(self):
        return len(self.__queue)

    def __iter__(self):
        return iter(self.__queue) # yields latest first

    def __getitem__(self, n):
        if not self.__queue:
            return None
        elif n < 0 or n > len(self) - 1:
            return None
        else:
            return self.__queue[n]

    def reset_cursor(self):
        self.__cursor = -1

    def append(self, s):
        assert s.startswith(self.__key)
        if self.get_latest() != s:
            self.__queue.appendleft(s)
            if len(self) > setting.max_history:
                self.__queue.pop()

    def get_latest(self):
        if self.__queue:
            return self.__queue[0]
        else:
            return None

    def get_older(self, word=''):
        if not word:
            word = self.__key
        if self.__queue:
            while True:
                self.__cursor += 1
                if self.__cursor > len(self) - 1:
                    self.__cursor = len(self)
                    break
                if self.__queue[self.__cursor].startswith(word):
                    return self.__queue[self.__cursor]

    def get_newer(self, word=''):
        if not word:
            word = self.__key
        if self.__queue:
            while True:
                self.__cursor -= 1
                if self.__cursor < 0:
                    self.__cursor = -1
                    break
                if self.__queue[self.__cursor].startswith(word):
                    return self.__queue[self.__cursor]

class History (object):
    def __init__(self, f, prefix=None):
        if not f:
            f = setting.get_history_path()
        if not prefix:
            prefix = literal.get_slow_strings()
        assert "#" not in prefix
        self.__path = path.Path(f)
        self.__data = dict([(k, _data(k)) for k in prefix])
        if setting.use_history:
            self.__read_history()

    def __iter__(self):
        return iter(self.__data.items())

    def flush(self):
        if setting.use_history:
            self.__write_history()

    def __read_history(self):
        f = self.__path.path
        if not self.__path.is_file:
            if not self.__path.is_noent:
                log.error("Can not read {0}".format(f))
            return
        try:
            prefix = list(self.__data.keys())
            for s in util.open_text_file(f): # from old to new
                s = s.rstrip()
                if not s or s.startswith("#"):
                    continue
                k, v = _string_to_data(s)
                if k in prefix and util.is_graph_sequence(v):
                    self.append(k, v)
        except Exception as e:
            log.error("Failed to read {0}, {1}".format(f, e))

    def __write_history(self):
        f = self.__path.path
        if not self.__path.is_file and not self.__path.is_noent:
            log.error("Can not write to {0}".format(f))
            return
        try:
            tmp = stash.TemporaryFile(f, unlink=True)
            with util.open_text_file(f, 'w') as fd:
                fd.write("# {0}\n".format(time.ctime()))
                for k, v in self:
                    for s in reversed(list(v)): # from old to new
                        assert util.is_graph_sequence(s)
                        fd.write(_data_to_string(k, s))
                util.fsync(fd)
        except Exception as e:
            log.error("Failed to write to {0}, {1}".format(f, e))
            if tmp:
                tmp.restore()
        finally:
            if tmp:
                tmp.cleanup()

    def reset_cursor(self, k):
        self.__data[k].reset_cursor()

    def append(self, k, v):
        self.__data[k].append(v)

    def get_size(self, k):
        return len(self.__data[k])

    def get(self, k, n):
        return self.__data[k][n]

    def get_latest(self, k):
        return self.__data[k].get_latest()

    def get_older(self, k, word):
        return self.__data[k].get_older(word)

    def get_newer(self, k, word):
        return self.__data[k].get_newer(word)

def _string_to_data(s):
    return s.split(' ', 1)

def _data_to_string(k, v):
    return "{0} {1}\n".format(k, v)

def print_history(f):
    for k, v in History(f):
        for i in range(len(v)):
            if i == 0:
                s = " <NEW>"
            else:
                s = ''
            util.print_stdout("{0} \"{1}\"{2}".format(i, v[i], s))
