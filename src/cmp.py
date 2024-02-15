# Copyright (c) 2022, Tomohiro Kusumi
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
from . import util

def cmp(args, verbose):
    try:
        ret = _cmp(args, verbose, util.printf, util.printe)
        if ret == -1:
            return -1
        assert ret in (0, 1), ret
        return ret
    except KeyboardInterrupt as e:
        util.printe(e)
        return -1

def _cmp(args, verbose, printf, printe):
    # require minimum 2 paths
    if len(args) < 2:
        printe("Not enough paths {0}".format(args))
        return -1

    # allocate fileops
    opsl, cleanup, blksiz = fileops.bulk_alloc_blk(args, True, printf, printe)
    if opsl is None:
        return -1

    # test if paths are unique
    l = [ops.get_path() for ops in opsl]
    if len(set(l)) != len(l):
        printe("Not unique paths {0}".format(l))
        cleanup()
        return -1

    # determine output format
    n = max([ops.get_mapping_offset() + ops.get_size() for ops in opsl])
    fmt = util.get_offset_format(n)

    # start comparison
    cmpsiz = max([ops.get_size() for ops in opsl])
    resid = cmpsiz
    offset = 0
    mismatch = False

    while resid > 0:
        # collect block buffers
        bufl = []
        shal = []
        phyl = [] # physical
        rell = [] # relative (nonexistent unless with @)
        for ops in opsl:
            mapping_offset = ops.get_mapping_offset()
            if offset <= ops.get_max_pos():
                buf = ops.read(offset, blksiz)
            else:
                buf = filebytes.BLANK # for debug mode
            bufl.append(buf)
            shal.append(util.get_sha256(buf))
            phyl.append(mapping_offset + offset)
            if mapping_offset:
                rell.append(offset)
            else:
                rell.append(None)
        if not verbose and len(set(phyl)) == 1:
            phyl = phyl[:1]
            rell = rell[:1]
        assert len(phyl) == len(rell), (len(phyl), len(rell))

        maxsiz = max([len(buf) for buf in bufl])
        assert maxsiz <= blksiz, (blksiz, maxsiz)

        # test if block buffer matches
        if len(set(shal)) != 1:
            mismatch = True
            blkidx = offset // blksiz
            blkper = offset / cmpsiz * 100
            l = []
            l.append("#{0} {1:.1f}% ".format(blkidx, blkper))
            l.append(concat_offsets(fmt, phyl, rell, 0))
            l.append(" -> ")
            index, values, contig, count = scan_buffer_list(bufl)
            l.append("{0} ".format(index))
            l.append(concat_offsets(fmt, phyl, rell, index))
            misper = count / maxsiz * 100
            l.append(" {0} {1} {2}/{3} {4:.1f}%".format(values, contig, count,
                maxsiz, misper))
            printf("".join(l))

        # must be last if maxsiz != blksiz
        offset += maxsiz
        resid -= maxsiz
        if maxsiz != blksiz:
            assert resid == 0, (offset, resid, cmpsiz, blksiz, maxsiz)

    printf("scanned {0} blocks".format(util.howmany(cmpsiz, blksiz)))
    if not mismatch:
        printf("success")

    # done
    cleanup()
    return 1 if mismatch else 0

def concat_offsets(fmt, phyl, rell, delta):
    l = []
    for i, phy in enumerate(phyl):
        rel = rell[i]
        if rel is not None:
            l.append("[{0}|{1}]".format(fmt.format(phy + delta),
                fmt.format(rel + delta)))
        else:
            l.append(fmt.format(phy + delta))
        if i != len(phyl) - 1:
            l.append("|")
    return "".join(l)

def scan_buffer_list(bufl):
    maxsiz = max([len(buf) for buf in bufl])
    first_bad_index = 0
    first_bad_values = None # tuple if found mismatch
    contig_good_count = 0
    max_contig_good_count = 0
    bad_count = 0

    def fn(x):
        ret = []
        for buf in bufl:
            if x < len(buf):
                _ = filebytes.ord(buf[x:x+1])
                if util.isprint(_):
                    ret.append((_, chr(_)))
                else:
                    ret.append(_)
            else:
                ret.append(None)
        return tuple(ret)

    for x in range(maxsiz):
        prev = None
        for buf in bufl:
            if x >= len(buf):
                if first_bad_values is None:
                    first_bad_index = x
                    first_bad_values = fn(x)
                bad_count += maxsiz - x
                return first_bad_index, first_bad_values, \
                    max_contig_good_count, bad_count
            b = buf[x]
            if prev is None:
                prev = b
            elif b != prev:
                if first_bad_values is None:
                    first_bad_index = x
                    first_bad_values = fn(x)
                bad_count += 1
                contig_good_count = 0
                break # avoid double count
        else:
            contig_good_count += 1
            if contig_good_count > max_contig_good_count:
                max_contig_good_count = contig_good_count

    assert 0 <= first_bad_index < maxsiz, first_bad_index
    assert 0 <= bad_count <= maxsiz, bad_count
    if bad_count:
        assert isinstance(first_bad_values, tuple), first_bad_values
        assert len(set(first_bad_values)) != 1, first_bad_values
    else:
        assert first_bad_values is None, first_bad_values
    assert 0 <= max_contig_good_count <= maxsiz, max_contig_good_count
    return first_bad_index, first_bad_values, max_contig_good_count, bad_count
