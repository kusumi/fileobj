# Copyright (c) 2016, Tomohiro Kusumi
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

import uuid

from .. import extension
from .. import filebytes
from .. import util

_ = util.str_to_bytes
_int = util.le_to_int

HAMMER_FSBUF_VOLUME = _("\x31\x30\x52\xC5\x4D\x4D\x41\xC8")
HAMMER_FSBUF_VOLUME_REV = _("\xC8\x41\x4D\x4D\xC5\x52\x30\x31")

def get_text(co, fo, args):
    l = []
    b = fo.read(args[-1], 1928)
    if len(b) != 1928:
        extension.fail("Invalid length: {0}".format(len(b)))
    print_rsv = (args[0] == "all")

    sig = b[:8]
    if sig not in (HAMMER_FSBUF_VOLUME, HAMMER_FSBUF_VOLUME_REV):
        extension.fail("Invalid signature: '{0}'".format(filebytes.str(sig)))
    if filebytes.ord(sig[:1]) == 0x31:
        endian = "LE"
    else:
        endian = "BE" # invalid
    l.append("vol_signature = 0x{0:016X} {1}".format(_int(sig), endian))

    vol_bot_beg = _int(b[8:16])
    vol_mem_beg = _int(b[16:24])
    vol_buf_beg = _int(b[24:32])
    vol_buf_end = _int(b[32:40])
    vol_reserved01 = _int(b[40:48])
    l.append("vol_bot_beg = 0x{0:016X}".format(vol_bot_beg))
    l.append("vol_mem_beg = 0x{0:016X}".format(vol_mem_beg))
    l.append("vol_buf_beg = 0x{0:016X}".format(vol_buf_beg))
    l.append("vol_buf_end = 0x{0:016X}".format(vol_buf_end))
    if print_rsv:
        l.append("vol_reserved01 = 0x{0:016X}".format(vol_reserved01))

    # b[:] are (supposed to be) in le, but swap byte order for 4-2-2 part
    vol_fsid = uuid.UUID(bytes=b[48:64]).bytes_le
    vol_fstype = uuid.UUID(bytes=b[64:80]).bytes_le
    # since str(uuid) simply converts bytes to string
    vol_fsid_str = str(uuid.UUID(bytes=vol_fsid))
    vol_fstype_str = str(uuid.UUID(bytes=vol_fstype))
    if vol_fstype_str == "61dc63ac-6e38-11dc-8513-01301bb8a9f5":
        vol_fstype_dfly = " \"{0}\"".format("DragonFly HAMMER")
    else:
        vol_fstype_dfly = ""
    l.append("vol_fsid = {0}".format(vol_fsid_str))
    l.append("vol_fstype = {0}{1}".format(vol_fstype_str, vol_fstype_dfly))

    vol_label = b[80:144]
    i = vol_label.find(filebytes.ZERO)
    vol_label = filebytes.str(vol_label[:i])
    l.append("vol_label = \"{0}\"".format(vol_label))

    vol_no = _int(b[144:148])
    vol_count = _int(b[148:152])
    vol_version = _int(b[152:156])
    vol_crc = _int(b[156:160])
    vol_flags = _int(b[160:164])
    vol_rootvol = _int(b[164:168])
    vol_reserved = []
    vol_reserved.append(_int(b[168:172]))
    vol_reserved.append(_int(b[172:176]))
    vol_reserved.append(_int(b[176:180]))
    vol_reserved.append(_int(b[180:184]))
    vol_reserved.append(_int(b[184:188]))
    vol_reserved.append(_int(b[188:192]))
    vol_reserved.append(_int(b[192:196]))
    vol_reserved.append(_int(b[196:200]))
    l.append("vol_no = {0}".format(vol_no))
    l.append("vol_count = {0}".format(vol_count))
    l.append("vol_version = {0}".format(vol_version))
    l.append("vol_crc = 0x{0:08X}".format(vol_crc))
    l.append("vol_flags = {0}".format(vol_flags))
    l.append("vol_rootvol = {0}".format(vol_rootvol))
    if print_rsv:
        for x in util.get_xrange(8):
            l.append("vol_reserved[{0}] = 0x{1:08X}".format(x, vol_reserved[x]))
    l.append("")

    vol0_stat_bigblocks = _int(b[200:208])
    vol0_stat_freebigblocks = _int(b[208:216])
    vol0_reserved01 = _int(b[216:224])
    vol0_stat_inodes = _int(b[224:232])
    vol0_reserved02 = _int(b[232:240])
    vol0_btree_root = _int(b[240:248])
    vol0_next_tid = _int(b[248:256])
    vol0_reserved03 = _int(b[256:264])
    l.append("vol0_stat_bigblocks     = {0}".format(vol0_stat_bigblocks))
    l.append("vol0_stat_freebigblocks = {0}".format(vol0_stat_freebigblocks))
    if print_rsv:
        l.append("vol0_reserved01 = 0x{0:016X}".format(vol0_reserved01))
    l.append("vol0_stat_inodes = {0}".format(vol0_stat_inodes))
    if print_rsv:
        l.append("vol0_reserved02 = 0x{0:016X}".format(vol0_reserved02))
    l.append("vol0_btree_root = 0x{0:016X}".format(vol0_btree_root))
    l.append("vol0_next_tid = 0x{0:016X}".format(vol0_next_tid))
    if print_rsv:
        l.append("vol0_reserved03 = 0x{0:016X}".format(vol0_reserved03))
    l.append("")

    offset = 264

    for x in util.get_xrange(16):
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

    for x in util.get_xrange(128):
        s = "vol0_undo_array[{0}]".format(x)
        vol0_undo_array = _int(b[offset:offset+8])
        l.append("{0} = 0x{1:016X}".format(s, vol0_undo_array))
        offset += 8

    assert offset == 1928
    return l
