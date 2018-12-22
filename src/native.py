# Copyright (c) 2016, Tomohiro Kusumi
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

import sys

from . import setting
from . import util

class Error (util.GenericError):
    pass

try:
    from . import _native
    _e = None
except Exception: # not only ImportError
    _e = sys.exc_info()[1]
    _native = None
    if setting.use_debug:
        raise

def get_so(safe=False):
    if not _native:
        if safe:
            return None
        raise Error(repr(_e))
    return _native

def is_enabled():
    return get_so(True) is not None

def get_blkdev_info(f):
    return get_so().get_blkdev_info(f)

def has_ptrace():
    return get_ptrace_word_size() > 0

def ptrace_peektext(pid, addr):
    return get_so().ptrace_peektext(pid, addr)

def ptrace_peekdata(pid, addr):
    return get_so().ptrace_peekdata(pid, addr)

def ptrace_poketext(pid, addr, data):
    return get_so().ptrace_poketext(pid, addr, data)

def ptrace_pokedata(pid, addr, data):
    return get_so().ptrace_pokedata(pid, addr, data)

def ptrace_attach(pid):
    return get_so().ptrace_attach(pid)

def ptrace_detach(pid):
    return get_so().ptrace_detach(pid)

def get_ptrace_word_size():
    try:
        return get_so().get_ptrace_word_size()
    except Exception:
        return -1 # don't raise an exception
