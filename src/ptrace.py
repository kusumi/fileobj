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

from . import kernel
#from . import native
from . import setting
from . import util

ERROR = None

def _I(ret, err):
    if ret is None or ret == -1:
        ret = ERROR
    return ret, err

def _B(ret, err):
    if ret is None:
        ret = ERROR
    else:
        ret = util.int_to_host(ret, get_word_size())
    return ret, err

def peektext(pid, addr):
    return _B(*_.ptrace_peektext(pid, addr))

def peekdata(pid, addr):
    return _B(*_.ptrace_peekdata(pid, addr))

def poketext(pid, addr, data):
    return _I(*_.ptrace_poketext(pid, addr, data))

def pokedata(pid, addr, data):
    return _I(*_.ptrace_pokedata(pid, addr, data))

def cont(pid):
    return _I(*_.ptrace_cont(pid))

def kill(pid):
    return _I(*_.ptrace_kill(pid))

def attach(pid):
    return _I(*_.ptrace_attach(pid))

def detach(pid):
    return _I(*_.ptrace_detach(pid))

def get_word_size():
    return _.get_ptrace_word_size()

try:
    _ = kernel
    # XXX disable native ptrace until peek/poke are added
    #if setting.use_native:
    #    native.get_so()
    #    _ = native
except Exception as e:
    if setting.use_debug:
        raise
