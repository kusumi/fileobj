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
import os
import sys
import time

from . import env
from . import log
from . import setting
from . import util

def read(tf):
    return tuple(iter_trace_word(tf))

def iter_trace_word(tf):
    buf = util.open_file(tf).read()
    n = setting.trace_word_size
    if len(buf) % n == 0:
        for i in range(0, len(buf), n):
            yield util.bin_to_int(buf[i : i + n])

def write(tf, l, e, tb):
    try:
        b = os.path.basename(tf)
        tf += time.strftime(
            "-%Y-%m-%d-%H:%M:%S", time.localtime())
        sf = tf + ".sh"
        _write_trace(tf, l)
        _write_script(sf, tf, e, tb)
        if setting.use_trace_symlink:
            _creat_symlink(tf, b)
            _creat_symlink(sf, b + ".sh")
    except Exception, e:
        log.error(e)

def _write_trace(tf, l):
    with util.create_file(tf) as fd:
        for x in l:
            fd.write(util.int_to_bin(x, setting.trace_word_size))
        util.fsync(fd)
        log.debug("Wrote trace to %s" % fd)

def _write_script(sf, tf, e, tb):
    with util.create_text_file(sf) as fd:
        ret = util.execute("which", "sh")
        if not ret[2]:
            fd.write("#!%s" % ret[0])
        if e:
            fd.write("# %s\n" % util.exc_to_string(e))
        for s in tb:
            fd.write("# %s\n" % s)
        fd.write("%s\n" % _get_cmdline(tf))
        util.fsync(fd)
        log.debug("Wrote text to %s" % fd)

def _get_cmdline(tf):
    l = list(env.iter_env_name())
    ret = ["FILEOBJ_STREAM_PATH=%s" % tf]
    for k in os.environ:
        if k in l and \
            k != "FILEOBJ_USE_TRACE" and \
            k != "FILEOBJ_STREAM_PATH":
            ret.append("%s=%s" % (k, os.getenv(k)))
    ret.extend(sys.argv)
    return ' '.join(ret)

def _creat_symlink(f, basename):
    if os.path.isfile(f):
        d = os.path.dirname(f)
        l = os.path.join(d, basename)
        if os.path.islink(l):
            os.unlink(l)
        os.symlink(f, l)
        if os.path.islink(l):
            log.debug("Create symlink %s -> %s" % (l, f))
