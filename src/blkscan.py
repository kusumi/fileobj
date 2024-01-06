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

from . import filebytes
from . import fileops
from . import setting
from . import util

def blkscan(args, scan_type, verbose):
    printf = util.printf
    printe = util.printe
    ret = _blkscan(args, scan_type, verbose, printf, printe)
    if ret == -1:
        return -1

def _blkscan(args, scan_type, verbose, printf, printe):
    # require 1 path
    if len(args) != 1:
        printe("Invalid number of paths {0}".format(len(args)))
        return -1

    # determine block size
    if setting.logical_block_size > 0:
        blksiz = setting.logical_block_size
    else:
        blksiz = -1

    # allocate fileops
    fileopsl, bulk_cleanup = fileops.bulk_alloc(args, True, printf, printe)
    if fileopsl is None:
        return -1
    ops = fileopsl[0]

    # set default block size if unset
    if blksiz == -1:
        if ops.is_blk():
            blksiz = ops.get_sector_size()
        else:
            blksiz = 512
    assert blksiz != -1, blksiz

    # blksiz must be multiple of 512
    if blksiz % 512 != 0:
        printe("Invalid block size {0}".format(blksiz))
        bulk_cleanup()
        return -1

    # define callback
    s = scan_type.lower()
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
        bulk_cleanup()
        return -1

    # start block scan
    resid = util.rounddown(ops.get_size(), blksiz)
    assert resid % blksiz == 0, (resid, blksiz)
    remain = ops.get_size() - resid
    assert 0 <= remain < blksiz, (remain, blksiz)
    offset = 0
    total_blk = 0
    l = []

    while resid > 0:
        buf = read_fileops(ops, offset, blksiz)
        assert len(buf) == blksiz, (offset, blksiz, len(buf))
        matched, extra = fn(buf)
        if matched:
            l.append((offset, extra if extra else ""))
        resid -= len(buf)
        offset += len(buf)
        total_blk += 1
    assert resid == 0, resid

    # print result
    if l:
        mapping_offset = ops.get_mapping_offset()
        if setting.address_radix == 16:
            fmt = "{0:x}"
        elif setting.address_radix == 10:
            fmt = "{0:d}"
        elif setting.address_radix == 8:
            fmt = "{0:o}"
        else:
            assert False, setting.address_radix
        lp = [] # physical
        lr = [] # relative
        le = [] # extra
        for offset, extra in l:
            if mapping_offset:
                lp.append(fmt.format(mapping_offset + offset))
            else:
                lp.append(None)
            lr.append(fmt.format(offset))
            le.append(extra)

        nr = max([len(x) for x in lr])
        fmtr = "{{:>0{0}}}".format(nr)
        fmte = "{}"
        if mapping_offset:
            np = max([len(x) for x in lp])
            fmtp = "{{:>0{0}}}".format(np)
            fmt = "{0}|{1} {2}".format(fmtp, fmtr, fmte)
            for x in range(len(l)):
                printf(fmt.format(lp[x], lr[x], le[x]).rstrip())
        else:
            fmt = "{0} {1}".format(fmtr, fmte)
            for x in range(len(l)):
                printf(fmt.format(lr[x], le[x]).rstrip())
    printf("{0} / {1} {2} bytes blocks matched".format(len(l), total_blk,
        blksiz))
    if remain:
        printf("{0} bytes ignored".format(remain))

    # done
    bulk_cleanup()

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

def read_fileops(ops, offset, size):
    if setting.use_debug:
        try:
            return ops.read(offset, size)
        except AssertionError:
            return filebytes.ZERO * size
    else:
        return ops.read(offset, size)
