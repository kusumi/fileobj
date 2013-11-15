# Copyright (c) 2010-2013, TOMOHIRO KUSUMI
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

import fileobj.extension
import fileobj.util

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
        fileobj.extension.fail("Invalid length: %d" % len(b))
    mag = b[-2:]
    if mag != "\x55\xAA":
        fileobj.extension.fail("Invalid magic: %s" % repr(mag))
    b = [ord(x) for x in b]
    n = 446
    l = []
    while n < 510:
        l.extend(__get_partition(b[n:n + 16], n))
        l.append('')
        n += 16
    return l

def __get_partition(p, offset):
    n = (offset - 446) / 16 + 1
    l = ["partition %d" % n]
    boot = '*' if p[0] else ''
    l.append("  %-15s= 0x%02X %s" % ("flag", p[0], boot))

    head = p[1]
    sect = p[2] & 0x3F
    cyli = ((p[2] & 0xC0) << 2) + p[3]
    l.append("  %-15s= %d" % ("first head", head))
    l.append("  %-15s= %d" % ("first sector", sect))
    l.append("  %-15s= %d" % ("first cylinder", cyli))

    t = p[4]
    if t in _partition_type:
        s = _partition_type[t]
    else:
        s = '?'
    l.append("  %-15s= 0x%02X %s" % ("type", t, s))

    head = p[5]
    sect = p[6] & 0x3F
    cyli = ((p[6] & 0xC0) << 2) + p[7]
    l.append("  %-15s= %d" % ("last head", head))
    l.append("  %-15s= %d" % ("last sector", sect))
    l.append("  %-15s= %d" % ("last cylinder", cyli))

    s = fileobj.util.to_string(p[8:12])
    l.append("  %-15s= %d" % ("first lba", fileobj.util.le_to_int(s)))
    s = fileobj.util.to_string(p[12:16])
    l.append("  %-15s= %d" % ("sectors", fileobj.util.le_to_int(s)))
    return l
