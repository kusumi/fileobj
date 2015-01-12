# Copyright (c) 2010-2015, TOMOHIRO KUSUMI
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
import os
import sys

from . import env
from . import kernel
from . import log
from . import setting
from . import util

def read(tf):
    return tuple(iter_trace_word(tf))

def iter_trace_word(tf):
    buf = kernel.fopen(tf).read()
    n = setting.trace_word_size
    if len(buf) % n == 0:
        for i in range(0, len(buf), n):
            yield util.bin_to_int(buf[i : i + n])

def write(trace_path, l, e, tb):
    try:
        trace_base = os.path.basename(trace_path)
        uniq_path = trace_path + util.get_stamp()
        tf = uniq_path + ".bin"
        sf = uniq_path + ".sh"
        __write_trace(tf, l)
        __write_script(sf, tf, e, tb)
        if setting.use_trace_symlink:
            __creat_symlink(tf, trace_base + ".bin")
            __creat_symlink(sf, trace_base + ".sh")
    except Exception, e:
        log.error(e)

def __write_trace(tf, l):
    with kernel.fcreat(tf) as fd:
        for x in l:
            fd.write(util.int_to_bin(x, setting.trace_word_size))
        kernel.fsync(fd)
        log.debug("Wrote trace to %s" % fd)

def __write_script(sf, tf, e, tb):
    with kernel.fcreat_text(sf) as fd:
        ret = util.execute("which", "sh")
        if not ret[2]:
            fd.write("#!%s" % ret[0])
        if e:
            fd.write("# %s\n" % util.e_to_string(e))
        for s in tb:
            fd.write("# %s\n" % s)
        fd.write("%s\n" % __get_cmdline(tf))
        kernel.fsync(fd)
        log.debug("Wrote text to %s" % fd)

def __get_cmdline(tf):
    ret = ["FILEOBJ_STREAM_PATH=" + tf]
    for k, v in env.iter_defined_env():
        if k not in ("FILEOBJ_USE_TRACE", "FILEOBJ_STREAM_PATH"):
            ret.append(k + "=" + v)
    ret.extend(sys.argv)
    return ' '.join(ret)

def __creat_symlink(f, basename):
    if os.path.isfile(f):
        d = os.path.dirname(f)
        l = os.path.join(d, basename)
        if os.path.islink(l):
            os.unlink(l)
        if kernel.symlink(f, l) != -1:
            log.debug("Create symlink %s -> %s" % (l, f))
