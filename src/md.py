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

from . import fileops
from . import util

def md(args, hash_algo, verbose):
    try:
        if _md(args, hash_algo, verbose, util.printf, util.printe) == -1:
            return -1
        else: # tuple
            return None
    except KeyboardInterrupt as e:
        util.printe(e)
        return -1

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

    if verbose:
        l = []
        for x in util.get_available_hash_algorithms():
            if " " in x:
                x = "'{0}'".format(x)
            if x == hash_algo:
                x = "[{0}]".format(x)
            l.append(x)
        printf(" ".join(l))

    # walk if args contains directory
    ret = []
    for x in args:
        if os.path.isdir(x):
            for f in util.iter_directory(x):
                l = print_md(f, hash_algo, printf, printe)
                if l == -1:
                    return -1
                ret.append(l)
        else:
            l = print_md(x, hash_algo, printf, printe)
            if l == -1:
                return -1
            ret.append(l)
    return tuple(ret) # unittest

def print_md(f, hash_algo, printf, printe):
    opsl, cleanup, blksiz, = fileops.bulk_alloc_blk((f,), True, printf, printe)
    if opsl is None:
        return -1
    assert len(opsl) == 1, opsl
    ops = opsl[0]

    resid = ops.get_size()
    offset = 0
    m = util.get_hash_object(hash_algo)
    while resid > 0:
        buf = ops.read(offset, blksiz)
        if not buf:
            break
        m = util.update_hash_object(m, buf)
        resid -= len(buf)
        offset += len(buf)

    l = ops.get_path(), m.hexdigest()
    cleanup()
    fmt = "{0}  {1}" # shaXsum compatible, but with abs path
    printf(fmt.format(l[1], l[0]))
    return l
