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

from . import cfileops
from . import fileops
from . import setting
from . import util

def md(args, s, verbose, concat):
    try:
        ret = _md(args, s, verbose, concat, util.printf, util.printe)
        if ret == -1:
            return -1
        assert isinstance(ret, tuple), ret
        return None
    except KeyboardInterrupt as e:
        util.printe(e)
        return -1

def _md(args, s, verbose, concat, printf, printe):
    # require minimum 1 paths
    if len(args) < 1:
        printe("Not enough paths {0}".format(args))
        return -1

    # extract option string
    s = s.lower()
    if "," in s:
        l = s.split(",", 1)
        hash_algo = l[0]
        if hash_algo == "":
            hash_algo = "sha256"
        opt = l[1]
    else:
        hash_algo = s
        opt = ""

    # test if hash_algo exists
    m = util.get_hash_object(hash_algo)
    if m is None:
        printe("No such hash algorithm \"{0}\", "
            "supported hash algorithms are as follows".format(hash_algo))
        printe("{0}".format(" ".join(util.get_available_hash_algorithms())))
        return -1

    # define callback
    if opt == "get":
        ll = []
        def fn(l):
            ll.append(l)
        def retfn():
            return tuple(ll)
    else:
        def fn(l):
            fmt = "{0}  {1}" # shaXsum compatible, but with abs path
            printf(fmt.format(l[1], l[0]))
        def retfn():
            return tuple()

    if verbose:
        l = []
        for x in util.get_available_hash_algorithms():
            if " " in x:
                x = "'{0}'".format(x)
            if x == hash_algo:
                x = "[{0}]".format(x)
            l.append(x)
        printf(" ".join(l))

    # collect paths first
    fl = []
    for x in args:
        if os.path.isdir(x):
            for f in util.iter_directory(x):
                fl.append(f)
        else:
            fl.append(x)
    if opt == "sort":
        fl.sort()

    # allocate fileops
    afn = cfileops.bulk_alloc_blk if concat else fileops.bulk_alloc_blk
    opsl, cleanup, blksiz = afn(fl, True, printf, printe)
    if opsl is None:
        return -1

    for ops in opsl:
        resid = ops.get_size()
        offset = 0
        m = util.get_hash_object(hash_algo)
        while resid > 0:
            buf = ops.read(offset, blksiz)
            if not buf:
                break
            m.update(buf)
            resid -= len(buf)
            offset += len(buf)
        if not concat or setting.use_debug:
            fn((ops.get_path(), m.hexdigest()))
        else:
            fn(("-", m.hexdigest()))
    cleanup()
    return retfn()
