# Copyright (c) 2024, Tomohiro Kusumi
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
import sys

from . import filebytes
from . import fileops
from . import panel
from . import screen
from . import setting
from . import util

def blkdump(args, dump_type, verbose):
    try:
        return _blkdump(args, dump_type, verbose, util.printf, util.printe)
    except KeyboardInterrupt as e:
        util.printe(e)
        return -1

def _blkdump(args, dump_type, verbose, printf, printe):
    # require minimum 1 paths
    if len(args) < 1:
        printe("Not enough paths {0}".format(args))
        return -1

    # allocate fileops
    s = dump_type.lower()
    if s.endswith("x"):
        afn = fileops.bulk_alloc_blk
        s = s[:-1]
    else:
        afn = fileops.concat_alloc_blk

    opsl, cleanup, blksiz = afn(args, True, printf, printe)
    if opsl is None:
        return -1
    elif fileops.is_concatenated(opsl):
        opsl = opsl,
    assert isinstance(opsl, tuple), opsl

    if s == "text":
        blkdump_text(opsl, blksiz, verbose, printf, printe)
    else:
        if setting.use_debug:
            printe("Debug mode unsupported")
        else:
            blkdump_raw(opsl, blksiz, verbose, sys.stdout)

    # done
    cleanup()

def get_bpl(blksiz):
    assert blksiz % 512 == 0, blksiz
    default = 32
    bpl = setting.bytes_per_line
    if bpl is None:
        return default
    assert isinstance(bpl, str), bpl
    try:
        bpl = int(bpl)
    except Exception:
        bpl = default
    if blksiz % bpl != 0:
        bpl = default
    assert blksiz % bpl == 0, (blksiz, bpl)
    return bpl

def get_bpu(bpl):
    assert bpl % 2 == 0, bpl
    default = 1
    bpu = setting.bytes_per_unit
    assert isinstance(bpu, int), bpu
    if bpl % bpu != 0:
        bpu = default
    assert bpl % bpu == 0, (bpl, bpu)
    return bpu

def build_offset_string(fmt, mapping_offset, offset):
    s = fmt.format(mapping_offset + offset)
    if mapping_offset:
        s = "{0}|{1}".format(s, fmt.format(offset))
    return "{0}|".format(s)

def build_binary_line(b, fn, bpl, bpu):
    blank = "  "
    space = " "
    if bpu == 1:
        extra = (blank + space) * (bpl - len(b))
        return space.join([fn(x) for x in b]) + extra
    else:
        l = []
        n = bpl // bpu
        for i in range(n):
            for j in range(bpu):
                k = i * bpu + j
                if k >= len(b):
                    l.append(blank)
                else:
                    l.append(fn(b[k]))
            if i != n - 1:
                l.append(space)
        return "".join(l)

def build_text_line(b, fn):
    return "".join([fn(x) for x in b])

def blkdump_text(opsl, blksiz, verbose, printf, printe):
    bpl = get_bpl(blksiz)
    bpu = get_bpu(bpl)
    screen.init_chr_repr()
    d = panel.get_binary_str_single()

    if util.is_python2():
        def bfn(x):
            return d[filebytes.ord(x)]
        def tfn(x):
            return screen.chr_repr[filebytes.ord(x)]
    else:
        def bfn(x):
            return d[x]
        def tfn(x):
            return screen.chr_repr[x]

    for i, ops in enumerate(opsl):
        if len(opsl) > 1:
            printf(ops.get_path())
        mapping_offset = ops.get_mapping_offset()
        fmt = util.get_offset_format(mapping_offset + ops.get_size())
        resid = ops.get_size()
        offset = 0
        prev = None
        prev_was_asterisk = False

        while resid > 0:
            buf = ops.read(offset, blksiz)
            assert len(buf) > 0, (offset, blksiz, len(buf))
            x = offset
            while x < offset + len(buf):
                s = build_offset_string(fmt, mapping_offset, x)
                b = buf[x-offset:x-offset+bpl]
                if b != prev or verbose:
                    printf("{0} {1} {2}".format(s,
                        build_binary_line(b, bfn, bpl, bpu),
                        build_text_line(b, tfn)))
                    prev_was_asterisk = False
                elif not prev_was_asterisk:
                    printf("*")
                    prev_was_asterisk = True
                prev = b
                x += bpl
            resid -= len(buf)
            offset += len(buf)
        assert resid == 0, resid

        # print last byte offset + 1 (sync with od(1))
        printf(build_offset_string(fmt, mapping_offset, offset))
        if len(opsl) > 1 and i != len(opsl) - 1:
            printf("")

def blkdump_raw(opsl, blksiz, verbose, fd):
    if util.is_python2():
        def fn(b):
            fd.write(b)
    else:
        def fn(b):
            fd.buffer.write(b)

    for ops in opsl:
        resid = ops.get_size()
        offset = 0
        while resid > 0:
            buf = ops.read(offset, blksiz)
            assert len(buf) > 0, (offset, blksiz, len(buf))
            fn(buf)
            resid -= len(buf)
            offset += len(buf)
        assert resid == 0, resid
    fd.flush()
