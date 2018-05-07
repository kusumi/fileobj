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

import array

from . import filebytes
from . import fileobj
from . import setting
from . import util

class Chunk (object):
    def __init__(self, offset, buffer, islast=False):
        assert offset >= 0
        if isinstance(buffer, str):
            buffer = util.str_to_bytes(buffer)
        self.offset = offset
        self.buffer = alloc_buffer(buffer)
        self.islast = islast

    def __contains__(self, x):
        x -= self.offset
        if not self.islast:
            return 0 <= x < len(self)
        else:
            return 0 <= x

    def __len__(self):
        return len(self.buffer)

    def __str__(self):
        return "{0} {1}{2}".format(self.offset, len(self),
            " <last>" * self.islast)

    def search(self, x, s, next_buffer):
        b = self.read(x, len(self))
        if next_buffer:
            b += next_buffer
        n = util.find_string(b, s)
        if n >= 0:
            return x + n
        else:
            return fileobj.NOTFOUND

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
            return fileobj.NOTFOUND

    def read(self, x, n):
        x = self.__get_local_offset(x)
        return filebytes.join(self.buffer[x : x + n])

    def insert(self, x, l):
        x = self.__get_local_offset(x)
        b = filebytes.input_to_bytes(l)
        self.buffer[x : x] = alloc_buffer(b)
        return len(l)

    def replace(self, x, l):
        x = self.__get_local_offset(x)
        size = len(self)
        if x + len(l) > size:
            if self.islast:
                nullsize = x + len(l) - size
                self.buffer[size:] = alloc_buffer(filebytes.pad(nullsize))
            else:
                l = l[:size - x]
        xx = x + len(l)
        orig = filebytes.join(self.buffer[x : xx])
        b = filebytes.input_to_bytes(l)
        self.buffer[x : xx] = alloc_buffer(b)
        return len(l), orig

    def delete(self, x, n):
        x = self.__get_local_offset(x)
        if x + n > len(self):
            n = len(self) - x
        xx = x + n
        orig = filebytes.join(self.buffer[x : xx])
        self.buffer[x : xx] = alloc_buffer(filebytes.BLANK)
        return n, orig

    def __get_local_offset(self, x):
        if setting.use_debug:
            assert x in self, (x, len(self), self.offset)
        return x - self.offset

if util.is_python2(): # only works with python2
    def alloc_buffer(b):
        return array.array('c', b)
else: # works with both python2 and python3
    def alloc_buffer(b):
        return filebytes.split(b)
