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

import os
import time

from . import filebytes
from . import fileobj
from . import kernel
from . import log
from . import ptrace
from . import setting
from . import util

enabled = setting.use_pid_path and \
    kernel.is_pid_path_supported()

class methods (object):
    def get_string(self, s):
        l = []
        l.append("pid {0}".format(self.pid))
        l.append("name {0}".format(self.name))
        l.append("word size {0}".format(self.word))
        return self.add_string(s, '\n'.join(l))

    def init_vm(self):
        self.word = ptrace.get_word_size()
        assert self.word != -1
        self.pid = kernel.to_pid(self.get_path())
        self.name = kernel.get_pid_name(self.pid)
        self.test_vm()

        offset = self.get_mapping_offset()
        length = self.get_mapping_length()
        if not length:
            length = util.get_address_space() # will fail
            length -= offset
        self.init_chunk(
            self.__load_buffer(offset, length))

    def __load_buffer(self, offset, length):
        beg, end = util.align_range(
            offset, offset + length, self.word)
        buf = self.read_vm(beg, end - beg)
        x = offset - beg
        b = buf[x : x + length]
        assert len(b) == length, len(b)
        return b

    def get_vm_alias(self):
        return self.name

    def get_address(self, x):
        return self.get_mapping_offset() + x

    def __wait(self):
        pid, status = os.waitpid(self.pid, 0)
        if setting.use_debug:
            ret = util.parse_waitpid_result(status)
            log.debug("Wait pid {0}: {1}".format(pid, ret))

    def __delay(self):
        time.sleep(setting.ptrace_delay)

    def test_vm(self):
        if not util.has_pid_access(self.pid):
            raise fileobj.FileobjError(
                "Can not access pid {0}".format(self.pid))

    def __attach_vm(self):
        ret, err = ptrace.attach(self.pid)
        if ret == ptrace.ERROR:
            raise fileobj.FileobjError(
                "Failed to attach pid {0}: {1}".format(
                    self.pid, os.strerror(err)))
        self.__wait()

    def __detach_vm(self):
        ret, err = ptrace.detach(self.pid)
        if ret == ptrace.ERROR:
            raise fileobj.FileobjError(
                "Failed to detach pid {0}: {1}".format(
                    self.pid, os.strerror(err)))

    def __assert_vm(self, addr, size):
        assert addr % self.word == 0, addr
        assert size % self.word == 0, size

    def read_vm(self, addr, size):
        self.__assert_vm(addr, size)
        self.__attach_vm()
        try:
            return self.__peek_vm(addr, size)
        except Exception as e:
            log.error("{0}, retrying".format(e))
            self.__delay()
            return self.__peek_vm(addr, size)
        finally:
            self.__detach_vm()

    def __peek_vm(self, addr, size):
        l = []
        while True:
            ret, err = ptrace.peek(self.pid, addr)
            if ret == ptrace.ERROR:
                raise fileobj.FileobjError(
                    "Failed to peek pid {0} at 0x{1:X}: {2}".format(
                        self.pid, addr, os.strerror(err)))
            l.append(ret)
            addr += self.word
            size -= self.word
            if size <= 0:
                break
        buf = filebytes.join(l)
        assert len(buf) % self.word == 0, len(buf)
        return buf

    def write_vm(self, addr, buf):
        self.__assert_vm(addr, 0)
        self.__attach_vm()
        try:
            return self.__poke_vm(addr, buf)
        except Exception as e:
            log.error("{0}, retrying".format(e))
            self.__delay()
            return self.__poke_vm(addr, buf)
        finally:
            self.__detach_vm()

    def __poke_vm(self, addr, buf):
        ret = 0
        for data in buf:
            ret, err = ptrace.poke(self.pid, addr, data)
            if ret == ptrace.ERROR:
                raise fileobj.FileobjError(
                    "Failed to poke pid {0} at 0x{1:X}: {2}".format(
                        self.pid, addr, os.strerror(err)))
            ret += 1
            addr += self.word
        return ret
