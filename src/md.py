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

import os

from . import filebytes
from . import fileops
from . import setting
from . import util

def md(args, hash_algo, verbose):
    printf = util.printf
    printe = util.printe
    ret = _md(args, hash_algo, verbose, printf, printe)
    if ret == -1:
        return -1
    assert isinstance(ret, tuple), ret

    # shaXsum compatible format, but always abs path
    fmt = "{0}  {1}"
    for f, md in ret:
        printf(fmt.format(md, f))

def _md(args, hash_algo, verbose, printf, printe):
    # require minimum 1 paths
    if len(args) < 1:
        printe("Not enough paths {0}".format(args))
        return -1

    # test if hash_algo exists
    hash_algo = hash_algo.lower()
    m = util.get_hash_object(hash_algo)
    if m is None:
        printe("No such hash algorithm \"{0}\", "
            "supported hash algorithms are as follows".format(hash_algo))
        printe("{0}".format(" ".join(util.get_available_hash_algorithms())))
        return -1

    # determine block size
    if setting.logical_block_size > 0:
        blksiz = setting.logical_block_size
    else:
        blksiz = 1 << 16

    # walk if args contains directory
    real_args = []
    for x in args:
        if os.path.isdir(x):
            for f in util.iter_directory(x):
                real_args.append(f)
                if len(real_args) > 10000: # XXX do one by one ?
                    printe("Too many files in {0}".format(args))
                    return -1
        else:
            real_args.append(x)

    # allocate fileops
    fileopsl, bulk_cleanup = fileops.bulk_alloc(real_args, True, printf, printe)
    if fileopsl is None:
        return -1
    for ops in fileopsl:
        if ops.is_blk():
            if blksiz & (ops.get_sector_size() - 1):
                printe("Invalid block size {0} for {1}".format(blksiz,
                    ops.get_path()))
                bulk_cleanup()
                return -1

    if setting.use_debug:
        printf("hash algorithm {0}".format(hash_algo))
        printf("block size {0} 0x{1:x}".format(blksiz, blksiz))
        printf("-" * 50)
    if verbose:
        l = []
        for x in util.get_available_hash_algorithms():
            if " " in x:
                x = "'{0}'".format(x)
            if x == hash_algo:
                x = "[{0}]".format(x)
            l.append(x)
        printf(" ".join(l))

    # start calculation
    ret = []
    for ops in fileopsl:
        offset = 0
        m = util.get_hash_object(hash_algo)
        while True:
            buf = read_fileops(ops, offset, blksiz)
            if not buf:
                break
            m = util.update_hash_object(m, buf)
            offset += len(buf)
        ret.append((ops.get_path(), m.hexdigest()))

    # done
    bulk_cleanup()
    return tuple(ret)

def read_fileops(ops, offset, size):
    if setting.use_debug:
        try:
            return ops.read(offset, size)
        except AssertionError:
            return filebytes.BLANK
    else:
        return ops.read(offset, size)
