# Copyright (c) 2019, Tomohiro Kusumi
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

HAMMER2_VOLUME_ID_HBO = _("\x11\x20\x17\x05\x32\x4d\x41\x48")
HAMMER2_VOLUME_ID_ABO = _("\x48\x41\x4d\x32\x05\x17\x20\x11")

def get_text(co, fo, args):
    l = []
    b = fo.read(args[-1], 65536)
    if len(b) != 65536:
        extension.fail("Invalid length: {0}".format(len(b)))
    print_rsv = (args[0] == "all")

    # sector #0
    magic = b[:8]
    if magic not in (HAMMER2_VOLUME_ID_HBO, HAMMER2_VOLUME_ID_ABO):
        extension.fail("Invalid magic: '{0}'".format(filebytes.str(magic)))
    if filebytes.ord(magic[:1]) == 0x11:
        endian = "LE"
    else:
        endian = "BE" # invalid
    l.append("magic = 0x{0:016X} {1}".format(_int(magic), endian))

    boot_beg = _int(b[8:16])
    boot_end = _int(b[16:24])
    aux_beg = _int(b[24:32])
    aux_end = _int(b[32:40])
    volu_size = _int(b[40:48])
    l.append("boot_beg  = 0x{0:016X}".format(boot_beg))
    l.append("boot_end  = 0x{0:016X}".format(boot_end))
    l.append("aux_beg   = 0x{0:016X}".format(aux_beg))
    l.append("aux_end   = 0x{0:016X}".format(aux_end))
    l.append("volu_size = 0x{0:016X}".format(volu_size))
    l.append("")

    version = _int(b[48:52])
    flags = _int(b[52:56])
    copyid = _int(b[56:57])
    freemap_version = _int(b[57:58])
    peer_type = _int(b[58:59])
    reserved003B = _int(b[59:60])
    reserved003C = _int(b[60:64])
    l.append("version = {0}".format(version))
    l.append("flags = 0x{0:08X}".format(flags))
    l.append("copyid = {0}".format(copyid))
    l.append("freemap_version = {0}".format(freemap_version))
    l.append("peer_type = {0}".format(peer_type))
    if print_rsv:
        l.append("reserved003B = {0}".format(reserved003B))
        l.append("reserved003C = 0x{0:08X}".format(reserved003C))
    l.append("")

    # b[:] are (supposed to be) in le, but swap byte order for 4-2-2 part
    fsid = uuid.UUID(bytes=b[64:80]).bytes_le
    fstype = uuid.UUID(bytes=b[80:96]).bytes_le
    # since str(uuid) simply converts bytes to string
    fsid_str = str(uuid.UUID(bytes=fsid))
    fstype_str = str(uuid.UUID(bytes=fstype))
    if fstype_str == "5cbb9ad1-862d-11dc-a94d-01301bb8a9f5":
        fstype_dfly = " \"{0}\"".format("DragonFly HAMMER2")
    else:
        fstype_dfly = ""
    l.append("fsid = {0}".format(fsid_str))
    l.append("fstype = {0}{1}".format(fstype_str, fstype_dfly))
    l.append("")

    allocator_size = _int(b[96:104])
    allocator_free = _int(b[104:112])
    allocator_beg = _int(b[112:120])
    l.append("allocator_size = 0x{0:016X}".format(allocator_size))
    l.append("allocator_free = 0x{0:016X}".format(allocator_free))
    l.append("allocator_beg  = 0x{0:016X}".format(allocator_beg))
    l.append("")

    mirror_tid = _int(b[120:128])
    reserved0080 = _int(b[128:136])
    reserved0088 = _int(b[136:144])
    freemap_tid = _int(b[144:152])
    bulkfree_tid = _int(b[152:160])
    reserved00A0 = []
    reserved00A0.append(_int(b[160:168]))
    reserved00A0.append(_int(b[168:176]))
    reserved00A0.append(_int(b[176:184]))
    reserved00A0.append(_int(b[184:192]))
    reserved00A0.append(_int(b[192:200]))
    l.append("mirrod_tid   = 0x{0:016X}".format(mirror_tid))
    if print_rsv:
        l.append("reserved0080 = 0x{0:016X}".format(reserved0080))
        l.append("reserved0088 = 0x{0:016X}".format(reserved0088))
    l.append("freemap_tid  = 0x{0:016X}".format(freemap_tid))
    l.append("bulkfree_tid = 0x{0:016X}".format(bulkfree_tid))
    if print_rsv:
        for x in util.get_xrange(5):
            l.append("reserved00A0[{0}] = 0x{1:016X}".format(
                x, reserved00A0[x]))
    l.append("")

    copyexists = []
    copyexists.append(_int(b[200:204]))
    copyexists.append(_int(b[204:208]))
    copyexists.append(_int(b[208:212]))
    copyexists.append(_int(b[212:216]))
    copyexists.append(_int(b[216:220]))
    copyexists.append(_int(b[220:224]))
    copyexists.append(_int(b[224:228]))
    copyexists.append(_int(b[228:232]))
    for x in util.get_xrange(8):
        l.append("copyexists[{0}] = 0x{1:08X}".format(x, copyexists[x]))
    # ignore reserved0140
    l.append("")

    icrc_sects = []
    icrc_sects.append(_int(b[480:484]))
    icrc_sects.append(_int(b[484:488]))
    icrc_sects.append(_int(b[488:492]))
    icrc_sects.append(_int(b[492:496]))
    icrc_sects.append(_int(b[496:500]))
    icrc_sects.append(_int(b[500:504]))
    icrc_sects.append(_int(b[504:508]))
    icrc_sects.append(_int(b[508:512]))
    for x in util.get_xrange(8):
        l.append("icrc_sects[{0}] = 0x{1:08X}".format(x, icrc_sects[x]))
    l.append("")

    # sector #1
    offset = 512
    l.append("sroot_blockset")
    for x in range(4):
        l.append("blockref[{0}]".format(x))
        l.extend(get_blockref(b[offset:offset+128], 1))
        offset += 128
    l.append("")

    # sector #2
    # ignore sector2

    # sector #3
    # ignore sector3

    # sector #4
    offset = 2048
    l.append("freemap_blockset")
    for x in range(4):
        l.append("blockref[{0}]".format(x))
        l.extend(get_blockref(b[offset:offset+128], 1))
        offset += 128
    l.append("")

    # sector #5
    # ignore sector5

    # sector #6
    # ignore sector6

    # sector #7
    # ignore sector7

    # sector #8-
    # XXX copyinfo
    # ignore reserved0400

    icrc_volheader = _int(b[65532:65536])
    l.append("icrc_volheader = 0x{0:08X}".format(icrc_volheader))

    return l

def get_blockref(b, indent):
    l = []
    type_ = _int(b[0:1])
    methods = _int(b[1:2])
    copyid = _int(b[2:3])
    keybits = _int(b[3:4])
    vradix = _int(b[4:5])
    flags = _int(b[5:6])
    leaf_count = _int(b[6:8])
    key = _int(b[8:16])
    mirror_tid = _int(b[16:24])
    modify_tid = _int(b[24:32])
    data_off = _int(b[32:40])
    update_tid = _int(b[40:48])

    l.append("type = {0}".format(type_))
    l.append("methods = {0}".format(methods))
    l.append("copyid = {0}".format(copyid))
    l.append("keybits = {0}".format(keybits))
    l.append("vradix = {0}".format(vradix))
    l.append("flags = 0x{0:02X}".format(flags))
    l.append("leaf_count = {0}".format(leaf_count))
    l.append("key = 0x{0:016X}".format(key))
    l.append("mirror_tid = 0x{0:016X}".format(mirror_tid))
    l.append("modify_tid = 0x{0:016X}".format(modify_tid))
    l.append("data_off = 0x{0:016X}".format(data_off))
    l.append("update_tid = 0x{0:016X}".format(update_tid))

    for i in util.get_xrange(len(l)):
        l[i] = " " * 4 * indent + l[i]
    return l
