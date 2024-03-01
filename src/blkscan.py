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

from . import filebytes
from . import fileops
from . import util

def blkscan(args, scan_type, verbose):
    try:
        return _blkscan(args, scan_type, verbose, util.printf, util.printe)
    except KeyboardInterrupt as e:
        util.printe(e)
        return -1

def _blkscan(args, scan_type, verbose, printf, printe):
    # require minimum 1 paths
    if len(args) < 1:
        printe("Not enough paths {0}".format(args))
        return -1

    # allocate fileops
    s = scan_type.lower()
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

    # define callback
    if s in ("z", "zero"):
        z = filebytes.ZERO * blksiz
        def fn(b):
            return b == z, None
    elif s in ("nz", "nzero", "nonzero", "notzero"):
        z = filebytes.ZERO * blksiz
        def fn(b):
            return b != z, None
    elif s in ("f", "ff"):
        ff = filebytes.FF * blksiz
        def fn(b):
            return b == ff, None
    elif s in ("nf", "nff", "nonff", "notff"):
        ff = filebytes.FF * blksiz
        def fn(b):
            return b != ff, None
    elif ":" in s:
        hash_algo, h = s.split(":")
        if hash_algo == "":
            hash_algo = "sha256"
        fn = get_md_callback(hash_algo, h, printe)
    else:
        fn = get_md_callback(s, None, printe)
    if not fn:
        cleanup()
        return -1

    # start block scan
    for i, ops in enumerate(opsl):
        if len(opsl) > 1:
            printf(ops.get_path())
        mapping_offset = ops.get_mapping_offset()
        fmt = util.get_offset_format(mapping_offset + ops.get_size())
        resid = ops.get_size()
        remain = resid - util.rounddown(resid, blksiz)
        assert 0 <= remain < blksiz, (remain, blksiz)
        offset = 0
        match_blk = 0
        total_blk = 0

        while resid > 0:
            buf = ops.read(offset, blksiz)
            matched, extra = fn(buf)
            if matched:
                if extra is None:
                    extra = ""
                sp = fmt.format(mapping_offset + offset)
                if mapping_offset:
                    s = "{0}|{1} {2}".format(sp, fmt.format(offset), extra)
                else:
                    s = "{0} {1}".format(sp, extra)
                s = s.rstrip()
                if len(buf) != blksiz:
                    assert len(buf) == resid, (offset, blksiz, len(buf))
                    assert len(buf) == remain, (offset, blksiz, len(buf))
                    s += " *"
                printf(s)
                match_blk += 1
            resid -= len(buf)
            offset += len(buf)
            total_blk += 1
        assert resid == 0, resid

        printf("{0}/{1} {2} bytes blocks matched".format(match_blk, total_blk,
            blksiz))
        if remain:
            printf("last {0} bytes not block sized".format(remain))
        if len(opsl) > 1 and i != len(opsl) - 1:
            printf("")

    # done
    cleanup()

def get_md_callback(hash_algo, h, printe):
    # taken from src/md.py
    m = util.get_hash_object(hash_algo)
    if m is None:
        printe("No such hash algorithm \"{0}\", "
            "supported hash algorithms are as follows".format(hash_algo))
        printe("{0}".format(" ".join(util.get_available_hash_algorithms())))
        return
    if h:
        for x in h:
            if x not in "0123456789abcdef":
                printe("Invalid hash string {0}".format(h))
                return
        def fn(b):
            return util.get_hash_string(hash_algo, b) == h, None
    else:
        def fn(b):
            return True, util.get_hash_string(hash_algo, b)
    return fn
