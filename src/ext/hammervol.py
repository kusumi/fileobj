# Copyright (c) 2010-2016, Tomohiro Kusumi
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
import fileobj.filebytes
import fileobj.util

_ = fileobj.util.str_to_bytes
_int = fileobj.util.le_to_int

HAMMER_FSBUF_VOLUME = _("\x31\x30\x52\xC5\x4D\x4D\x41\xC8")

def get_text(co, fo, args):
    l = []
    b = fo.read(args[-1], 1928)
    if len(b) != 1928:
        fileobj.extension.fail("Invalid length: {0}".format(len(b)))
    print_rsv = (args[0] == "all")

    sig = b[:8]
    if sig != HAMMER_FSBUF_VOLUME:
        fileobj.extension.fail(
            "Invalid signature: '{0}'".format(fileobj.filebytes.repr(sig)))
    l.append("vol_signature = 0x{0:016X}".format(_int(sig)))

    vol_bot_beg = _int(b[8:16])
    vol_mem_beg = _int(b[16:24])
    vol_buf_beg = _int(b[24:32])
    vol_buf_end = _int(b[32:40])
    vol_reserved00 = _int(b[40:48])
    l.append("vol_bot_beg = 0x{0:016X}".format(vol_bot_beg))
    l.append("vol_mem_beg = 0x{0:016X}".format(vol_mem_beg))
    l.append("vol_buf_beg = 0x{0:016X}".format(vol_buf_beg))
    l.append("vol_buf_end = 0x{0:016X}".format(vol_buf_end))
    if print_rsv:
        l.append("vol_reserved00 = 0x{0:016X}".format(vol_reserved00))

    vol_name = b[80:144]
    i = vol_name.find(fileobj.filebytes.ZERO)
    vol_name = fileobj.filebytes.repr(vol_name[:i])
    l.append("vol_name = \"{0}\"".format(vol_name))

    vol_no = _int(b[144:148])
    vol_count = _int(b[148:152])
    vol_version = _int(b[152:156])
    vol_crc = _int(b[156:160])
    vol_flags = _int(b[160:164])
    vol_rootvol = _int(b[164:168])
    vol_reserved04 = _int(b[168:172])
    vol_reserved05 = _int(b[172:176])
    vol_reserved06 = _int(b[176:180])
    vol_reserved07 = _int(b[180:184])
    vol_reserved08 = _int(b[184:192])
    vol_reserved09 = _int(b[192:200])
    l.append("vol_no = {0}".format(vol_no))
    l.append("vol_count = {0}".format(vol_count))
    l.append("vol_version = {0}".format(vol_version))
    l.append("vol_crc = 0x{0:08X}".format(vol_crc))
    l.append("vol_flags = {0}".format(vol_flags))
    l.append("vol_rootvol = {0}".format(vol_rootvol))
    if print_rsv:
        l.append("vol_reserved04 = 0x{0:08X}".format(vol_reserved04))
        l.append("vol_reserved05 = 0x{0:08X}".format(vol_reserved05))
        l.append("vol_reserved06 = 0x{0:08X}".format(vol_reserved06))
        l.append("vol_reserved07 = 0x{0:08X}".format(vol_reserved07))
        l.append("vol_reserved08 = 0x{0:016X}".format(vol_reserved08))
        l.append("vol_reserved09 = 0x{0:016X}".format(vol_reserved09))
    l.append("")

    vol0_stat_bigblocks = _int(b[200:208])
    vol0_stat_freebigblocks = _int(b[208:216])
    vol0_reserved11 = _int(b[216:224])
    vol0_stat_inodes = _int(b[224:232])
    vol0_reserved10 = _int(b[232:240])
    vol0_btree_root = _int(b[240:248])
    vol0_next_tid = _int(b[248:256])
    vol0_unused03 = _int(b[256:264])
    l.append("vol0_stat_bigblocks     = {0}".format(vol0_stat_bigblocks))
    l.append("vol0_stat_freebigblocks = {0}".format(vol0_stat_freebigblocks))
    if print_rsv:
        l.append("vol0_reserved11 = 0x{0:016X}".format(vol0_reserved11))
    l.append("vol0_stat_inodes = {0}".format(vol0_stat_inodes))
    if print_rsv:
        l.append("vol0_reserved10 = 0x{0:016X}".format(vol0_reserved10))
    l.append("vol0_btree_root = 0x{0:016X}".format(vol0_btree_root))
    l.append("vol0_next_tid = 0x{0:016X}".format(vol0_next_tid))
    if print_rsv:
        l.append("vol0_unused03 = 0x{0:016X}".format(vol0_unused03))
    l.append("")

    offset = 264

    for x in range(16):
        s = "vol0_blockmap[{0}]".format(x)
        buf = b[offset:offset+40]
        phys_offset = _int(buf[0:8])
        first_offset = _int(buf[8:16])
        next_offset = _int(buf[16:24])
        alloc_offset = _int(buf[24:32])
        reserved01 = _int(buf[32:36])
        entry_crc = _int(buf[36:40])
        l.append("{0} phys_offset  = 0x{1:016X}".format(s, phys_offset))
        l.append("{0} first_offset = 0x{1:016X}".format(s, first_offset))
        l.append("{0} next_offset  = 0x{1:016X}".format(s, next_offset))
        l.append("{0} alloc_offset = 0x{1:016X}".format(s, alloc_offset))
        if print_rsv:
            l.append("{0} reserved01 = 0x{1:08X}".format(s, reserved01))
        l.append("{0} entry_crc = 0x{1:08X}".format(s, entry_crc))
        l.append("")
        offset += 40

    for x in range(128):
        s = "vol0_undo_array[{0}]".format(x)
        vol0_undo_array = _int(b[offset:offset+8])
        l.append("{0} = 0x{1:016X}".format(s, vol0_undo_array))
        offset += 8

    assert offset == 1928
    return l
