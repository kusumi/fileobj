# Copyright (c) 2010-2016, TOMOHIRO KUSUMI
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

from . import rrbuf
from . import util
from . import setting
from . import vm

class Fileobj (rrbuf.Fileobj, vm.methods):
    _insert  = False
    _replace = True
    _delete  = False
    _enabled = vm.enabled
    _partial = True

    def __str__(self):
        return super(Fileobj, self).__str__() + \
            "\n\n" + \
            self.get_string()

    def ctr(self):
        self.init_vm()
        self.__sbuf = []

    def test_access(self):
        return self.test_vm()

    def get_alias(self):
        return self.get_vm_alias()

    def flush(self, f=None):
        if f and f != self.get_path():
            return super(Fileobj, self).flush(f)
        else:
            return self.__flush()

    def __flush(self):
        self.test_access()
        ret = 0
        while self.__sbuf:
            ret += self.__sync_buffer(
                *self.__sbuf.pop())
        self.sync_undo()
        return "Poke {0}".format(ret), None

    def __sync_buffer(self, pos, siz):
        l = []
        buf = self.__read_buffer(pos, siz)
        for x in range(len(buf) // self.word):
            b = buf[:self.word]
            buf = buf[self.word:]
            l.append(util.host_to_int(b))
        addr = self.get_address(pos)
        addr = util.align_head(addr, self.word)
        return self.write_vm(addr, l)

    def __read_buffer(self, pos, siz):
        buf = self.read(pos, siz)
        pad = self.__read_left_pad(pos, siz)
        if pad:
            buf = pad + buf
        pad = self.__read_right_pad(pos, siz)
        if pad:
            buf = buf + pad
        assert len(buf) % self.word == 0
        return buf

    def __read_left_pad(self, pos, siz):
        addr = self.get_address(pos)
        r = addr % self.word
        if r:
            addr -= r
            buf = self.read_vm(addr, self.word)
            return buf[:r]

    def __read_right_pad(self, pos, siz):
        addr = self.get_address(pos + siz)
        r = addr % self.word
        if r:
            addr -= r
            buf = self.read_vm(addr, self.word)
            return buf[r:]

    def replace(self, x, l, rec=True):
        if setting.use_rrvm_raw:
            self.test_access()
        if x + len(l) > self.get_size():
            l = l[:self.get_size() - x]

        super(Fileobj, self).replace(x, l, rec)
        if setting.use_rrvm_raw:
            self.__sync_buffer(x, len(l))
        else:
            ll = x, len(l)
            if ll not in self.__sbuf:
                self.__sbuf.append(ll)
