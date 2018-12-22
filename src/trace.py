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

from __future__ import with_statement
import os
import random
import sys

from . import env
from . import kbd
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
        for i in util.get_xrange(0, len(buf), n):
            yield util.bin_to_int(buf[i : i + n])

def __get_path(trace_path):
    trace_base = os.path.basename(trace_path)
    uniq_path = trace_path + util.get_stamp()
    return trace_base, uniq_path

def write(trace_path, l, e, tb):
    try:
        base, uniq = __get_path(trace_path)
        tf = uniq + ".bin"
        sf = uniq + ".sh"
        __write_trace(tf, l)
        __write_script(sf, tf, e, tb)
        __creat_symlink(tf, base + ".bin")
        __creat_symlink(sf, base + ".sh")
    except Exception as e:
        log.error(e)

def creat_random(trace_path, beg, end, cnt, quit, blacklist=None):
    try:
        base, uniq = __get_path(trace_path)
        tf = uniq + ".rand.bin"
        l = []
        for _ in util.get_xrange(cnt):
            x = random.randint(beg, end)
            if not blacklist or x not in blacklist:
                l.append(x)
        if quit:
            __append_slow_cmd(l, ":only")
            __append_slow_cmd(l, ":q!")
        __write_trace(tf, l)
        __creat_symlink(tf, base + ".rand.bin")
    except Exception as e:
        log.error(e)

def __append_slow_cmd(l, s):
    cmd = []
    cmd.append(kbd.ESCAPE)
    cmd.extend([ord(x) for x in s])
    cmd.append(kbd.ENTER)
    for x in cmd:
        assert isinstance(x, int), x
    l.extend(cmd)

def __write_trace(tf, l):
    with kernel.fcreat(tf) as fd:
        for x in l:
            fd.write(util.int_to_bin(x, setting.trace_word_size))
        kernel.fsync(fd)
        log.debug("Wrote trace to {0}".format(fd))

def __write_script(sf, tf, e, tb):
    with kernel.fcreat_text(sf) as fd:
        ret = util.execute("which", "sh")
        if not ret.retval:
            fd.write("#!{0}".format(ret.stdout))
        if e:
            fd.write("# {0}\n".format(util.e_to_string(e)))
        for s in tb:
            fd.write("# {0}\n".format(s))
        fd.write("{0}\n".format(__get_cmdline(tf)))
        kernel.fsync(fd)
        log.debug("Wrote text to {0}".format(fd))

def __get_cmdline(tf):
    ret = ["__FILEOBJ_PATH_STREAM=" + os.path.basename(tf)]
    for k, v in env.iter_defined_env():
        if k not in ("__FILEOBJ_USE_TRACE", "__FILEOBJ_PATH_STREAM"):
            ret.append(k + "=" + v)
    for k, v in env.iter_defined_ext_env():
        ret.append(k + "=" + v)
    ret.extend(sys.argv)
    return ' '.join(ret)

def __creat_symlink(f, basename):
    if os.path.isfile(f):
        d = os.path.dirname(f)
        l = os.path.join(d, basename)
        if os.path.islink(l):
            os.unlink(l)
        f = os.path.basename(f)
        if kernel.symlink(f, l) != -1:
            log.debug("Create symlink {0} -> {1}".format(l, f))
