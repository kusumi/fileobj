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

import array

from . import setting
from . import util

class Chunk (object):
    def __init__(self, offset, buffer, last=False):
        assert offset >= 0
        assert isinstance(buffer, str)
        self.offset = offset
        self.buffer = alloc_buffer(buffer)
        self.last = last

    def __contains__(self, x):
        x -= self.offset
        if not self.last:
            return 0 <= x < len(self)
        else:
            return 0 <= x

    def __len__(self):
        return len(self.buffer)

    def __str__(self):
        return ("%d %d %s" %
            (self.offset, len(self),
            "<last>" * self.last)).rstrip()

    def search(self, x, s, next_buffer):
        b = self.read(x, len(self))
        if next_buffer:
            b += next_buffer
        n = util.find_string(b, s)
        if n >= 0:
            return x + n
        else:
            return -1

    def rsearch(self, x, s, next_buffer):
        b = self.read(self.offset, x + 1 - self.offset)
        if next_buffer:
            b = next_buffer + b
        n = util.rfind_string(b, s)
        if n >= 0:
            ret = self.offset + n
            if next_buffer:
                return ret - len(next_buffer)
            else:
                return ret
        else:
            return -1

    def read(self, x, n):
        x = self.__get_local_offset(x)
        return ''.join(self.buffer[x : x + n])

    def insert(self, x, s):
        x = self.__get_local_offset(x)
        self.buffer[x : x] = alloc_buffer(s)
        return len(s)

    def replace(self, x, s):
        x = self.__get_local_offset(x)
        size = len(self)
        if x + len(s) > size:
            if self.last:
                nullsize = x + len(s) - size
                self.buffer[size:] = alloc_buffer(chr(0) * nullsize)
            else:
                s = s[:size - x]
        xx = x + len(s)
        orig = ''.join(self.buffer[x : xx])
        self.buffer[x : xx] = alloc_buffer(s)
        return len(s), orig

    def delete(self, x, n):
        x = self.__get_local_offset(x)
        if x + n > len(self):
            n = len(self) - x
        xx = x + n
        orig = ''.join(self.buffer[x : xx])
        self.buffer[x : xx] = alloc_buffer('')
        return n, orig

    def __get_local_offset(self, x):
        if setting.use_debug:
            assert x in self, (x, len(self))
        return x - self.offset

if setting.use_array_chunk:
    def alloc_buffer(s):
        return array.array('c', s)
else:
    def alloc_buffer(s):
        return list(s)
