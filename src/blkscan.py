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

from . import cfileops
from . import filebytes
from . import fileops
from . import path
from . import setting
from . import util

def blkscan(args, s, verbose, concat):
    try:
        return _blkscan(args, s, verbose, concat, util.printf, util.printe)
    except KeyboardInterrupt as e:
        util.printe(e)
        return -1

def _blkscan(args, s, verbose, concat, printf, printe):
    # require minimum 1 paths
    if len(args) < 1:
        printe("Not enough paths {0}".format(args))
        return -1

    # extract option string
    if "," in s:
        l = s.split(",", 1)
        typ = l[0]
        if typ == "":
            typ = "zero"
        opt = l[1]
    else:
        typ = s
        opt = ""

    # allocate fileops
    afn = cfileops.bulk_alloc_blk if concat else fileops.bulk_alloc_blk
    opsl, cleanup, blksiz = afn(args, True, printf, printe)
    if opsl is None:
        return -1

    # define callback
    if typ == "zero":
        z = filebytes.ZERO * blksiz
        def fn(b):
            return b == z, None
    elif typ == "nonzero":
        z = filebytes.ZERO * blksiz
        def fn(b):
            return b != z, None
    elif typ == "ff":
        ff = filebytes.FF * blksiz
        def fn(b):
            return b == ff, None
    elif typ == "nonff":
        ff = filebytes.FF * blksiz
        def fn(b):
            return b != ff, None
    elif typ.startswith("file:") or typ.startswith("FILE:"):
        f = typ.split(":", 1)[1]
        assert setting.allow_dup_path # f may be in args
        try:
            fops = fileops.alloc(f, True)
        except Exception as e:
            printe(e)
            cleanup()
            return -1
        if setting.use_debug:
            printf(fops.get_path())
            printf(fops)
        f = fops.get_path()
        o = path.Path(f)
        if o.is_noent or o.is_noperm or o.is_unknown or o.is_error:
            printe("No such file {0}".format(f))
            cleanup()
            return -1
        if not (o.is_reg or o.is_blkdev or o.is_chrdev):
            printe("Invalid file {0}".format(f))
            cleanup()
            return -1
        if fops.is_empty():
            printe("Empty file {0}".format(f))
            cleanup()
            return -1
        if fops.get_size() > blksiz:
            printe("{0} size {1} larger than block size {2}".format(f,
                fops.get_size(), blksiz))
            cleanup()
            return -1
        xbuf = fops.readall()
        xfmt = util.get_offset_format(blksiz)
        def fn_impl(b):
            if xbuf not in b:
                return False, None
            l = []
            offset = 0
            while True:
                i = b[offset:].find(xbuf)
                if i == -1:
                    break
                l.append(xfmt.format(offset + i))
                offset += i
                offset += len(xbuf)
            return True, "({0})".format(", ".join([x for x in l]))
        if typ.startswith("file:"):
            fn = fn_impl
        else:
            def fn(b):
                matched, extra = fn_impl(b)
                return not matched, extra
    elif ":" in typ:
        hash_algo, h = typ.split(":", 1)
        if hash_algo == "":
            hash_algo = "sha256"
        fn = get_md_callback(hash_algo, h, printe)
    else:
        fn = get_md_callback(s, None, printe)
    if not fn:
        cleanup()
        return -1

    # invalidate printf if "get"
    if opt == "get":
        def printf(o):
            return
        opt_get = True
    else:
        opt_get = False

    # start block scan
    ret = []
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
                if opt_get:
                    ret.append((offset, extra))
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
    assert opt_get or not ret, (opt, ret)
    return ret

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
