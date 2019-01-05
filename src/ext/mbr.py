# Copyright (c) 2011, Tomohiro Kusumi
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

from .. import extension
from .. import filebytes
from .. import util

_ = util.str_to_bytes

_partition_type = {
    0x00 : '',
    0x82 : "Linux swap",
    0x83 : "Linux native",
    0x85 : "Linux extended",
    0x8E : "Linux LVM",
    0xA5 : "FreeBSD",
    0xA6 : "OpenBSD",
    0xA9 : "NetBSD", }

def get_text(co, fo, args):
    b = fo.read(args[-1], 512)
    if len(b) != 512:
        extension.fail("Invalid length: {0}".format(len(b)))
    mag = b[-2:]
    if mag != _("\x55\xAA"):
        extension.fail("Invalid magic: '{0}'".format(filebytes.str(mag)))
    b = filebytes.ords(b)
    n = 446
    l = []
    while n < 510:
        l.extend(__get_partition(b[n:n + 16], n))
        l.append('')
        n += 16
    return l

def __get_partition(p, offset):
    n = (offset - 446) // 16 + 1
    l = ["partition {0}".format(n)]
    boot = '*' if p[0] else ''
    l.append("  {0:<15}= 0x{1:02X} {2}".format("flag", p[0], boot))

    head = p[1]
    sect = p[2] & 0x3F
    cyli = ((p[2] & 0xC0) << 2) + p[3]
    l.append("  {0:<15}= {1}".format("first head", head))
    l.append("  {0:<15}= {1}".format("first sector", sect))
    l.append("  {0:<15}= {1}".format("first cylinder", cyli))

    t = p[4]
    if t in _partition_type:
        s = _partition_type[t]
    else:
        s = '?'
    l.append("  {0:<15}= 0x{1:02X} {2}".format("type", t, s))

    head = p[5]
    sect = p[6] & 0x3F
    cyli = ((p[6] & 0xC0) << 2) + p[7]
    l.append("  {0:<15}= {1}".format("last head", head))
    l.append("  {0:<15}= {1}".format("last sector", sect))
    l.append("  {0:<15}= {1}".format("last cylinder", cyli))

    b = filebytes.input_to_bytes(p[8:12])
    l.append("  {0:<15}= {1}".format("first lba", util.le_to_int(b)))
    b = filebytes.input_to_bytes(p[12:16])
    l.append("  {0:<15}= {1}".format("sectors", util.le_to_int(b)))
    return l
