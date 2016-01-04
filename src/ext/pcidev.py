# Copyright (c) 2010-2016, TOMOHIRO KUSUMI
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
import struct

import fileobj.filebytes
import fileobj.util
from fileobj.extension import fail

PCI_HDR_DEV = 0x00
PCI_HDR_PPB = 0x01
PCI_HDR_PCB = 0x02

def get_text(co, fo, args):
    size = fileobj.util.KiB * 4
    b = fo.read(args[-1], size + 1)
    n = len(b)
    if n > size:
        fail("Invalid length: >{0}".format(size))
    elif n < 0x40 or (n % 4):
        fail("Invalid length: {0}".format(n))

    cfg = fileobj.filebytes.ords(b)
    vend = cfg[0:2]
    if vend in ((0, 0), (0xFF, 0xFF)): # 0000 for Gammagraphx ?
        fail("Invalid vendor id: " +
            repr(struct.pack(fileobj.util.U1F * 2, vend[1], vend[0])))

    type = cfg[0x0E] & 0x7F
    if type not in (PCI_HDR_DEV, PCI_HDR_PPB, PCI_HDR_PCB):
        fail("Invalid header type: {0}".format(type))

    cap = ((cfg[0x06] & 0x10) != 0)
    capaddr = []
    if cap:
        if type in (PCI_HDR_DEV, PCI_HDR_PPB):
            ptr = cfg[0x34]
        elif type == PCI_HDR_PCB:
            ptr = cfg[0x14]
        else:
            assert 0
        next = ptr
        while next:
            if next % 4:
                fail("Invalid cap address: 0x{0:04X}".format(next))
            capaddr.append(next)
            next = cfg[next + 1]

    l = [' '*7 + "3  2  1  0"]
    n = 0
    buf = cfg[:]

    while buf:
        b = buf[:4]
        buf = buf[4:]
        s = "|{0:04X}| {1:02X} {2:02X} {3:02X} {4:02X}".format(
            n, b[3], b[2], b[1], b[0])
        if (type == PCI_HDR_DEV and 0x10 <= n < 0x28) or \
            (type == PCI_HDR_PPB and 0x10 <= n < 0x18):
            s += " "
            s += __get_bar(n, b)
        if n in capaddr:
            s += " CAP{0} {1}".format(capaddr.index(n), cfg[n])
        l.append(s)
        n += 4
        if n == 0x40:
            l.append('')
    return l

def __get_bar(n, word):
    addr = fileobj.util.le_to_int(
        fileobj.filebytes.input_to_bytes(word))
    if word[0] & 0x01:
        s = "I/O {0:04X}".format(addr & 0xFFFFFFFC)
    elif word[0] & 0x06:
        s = "MEMORY"
    else:
        s = "MEMORY {0:08X}".format(addr & 0xFFFFFFF0)
    return "BAR{0} {1}".format((n - 0x10) // 4, s)
