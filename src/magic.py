# Copyright (c) 2009, Tomohiro Kusumi
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

from . import filebytes
from . import util

_ = util.str_to_bytes

class _magic (object):
    def test(self, fo):
        util.raise_no_impl("test")

    def get_magic(self):
        return filebytes.BLANK

    def get_name(self):
        util.raise_no_impl("name")

    def test_head(self, fo, b=None):
        if b is None:
            b = self.get_magic()
            assert isinstance(b, filebytes.TYPE)
        return self.read(fo, 0, len(b)) == b

    def test_tail(self, fo, b=None):
        if b is None:
            b = self.get_magic()
            assert isinstance(b, filebytes.TYPE)
        return self.read(fo, fo.get_size() - len(b), len(b)) == b

    def read(self, fo, x, n):
        """Must use this instead of directly calling fo.read()"""
        size = fo.get_size()
        if x > size - 1:
            return filebytes.BLANK
        if x + n > size:
            n = size - x
        return fo.read(x, n)

class ELFMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("\x7fELF")

    def get_name(self):
        return "elf"

class EXEMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("MZ")

    def get_name(self):
        return "exe"

class PythonMagic (_magic):
    """Magic definition is taken from Lib/importlib/_bootstrap_external.py"""
    def __init__(self):
        self.__name = "pyc"

    def test(self, fo):
        v = self.__get_version(fo)
        if v < 0:
            return False
        else:
            if v >= 1.5:
                self.__name = "pyc|{0}".format(v)
            return True

    def get_name(self):
        return self.__name

    def __get_version(self, fo):
        v = -1
        b = self.read(fo, 0, 4)
        if b[2:4] != _("\r\n"):
            return v
        l = filebytes.ords(b)
        x = l[0] + (l[1] << 8)
        if x in (20121,):
            v = 1.5
        elif x in (50428,):
            v = 1.6
        elif x in (50823,):
            v = 2.0
        elif x in (60202,):
            v = 2.1
        elif x in (60717,):
            v = 2.2
        elif x in (62011, 62021):
            v = 2.3
        elif x in (62041, 62051, 62061):
            v = 2.4
        elif x in (62071, 62081, 62091, 62092, 62101, 62111, 62121, 62131):
            v = 2.5
        elif x in (62151, 62161):
            v = 2.6
        elif x in (62171, 62181, 62191, 62201, 62211):
            v = 2.7
        elif x > 62000: # is this good ?
            v = 2
        elif x in (3111, 3131):
            v = 3.0
        elif x in (3141, 3151):
            v = 3.1
        elif x in (3160, 3170, 3180):
            v = 3.2
        elif x in (3190, 3200, 3210, 3220, 3230):
            v = 3.3
        elif x in (3250, 3260, 3270, 3280, 3290, 3300, 3310):
            v = 3.4
        elif x in (3320, 3330, 3340, 3350, 3351):
            v = 3.5
        elif x in (3360, 3361, 3370, 3371, 3372, 3373, 3375, 3376, 3377, 3378,
            3379):
            v = 3.6
        elif x in (3390, 3391, 3392, 3393, 3394):
            v = 3.7
        elif x in (3400, 3401, 3410, 3411, 3412, 3413):
            v = 3.8
        elif x in (3420, 3421, 3422, 3423, 3424, 3425):
            v = 3.9
        elif x in (3430, 3431, 3432, 3433, 3434, 3435, 3436, 3437, 3438, 3439):
            v = 3.10
        elif x in (3450, 3451, 3452, 3453, 3454, 3455, 3456, 3457, 3458, 3459,
            3460, 3461, 3462, 3463, 3464, 3465, 3466, 3467, 3468, 3469, 3470,
            3471, 3472, 3473, 3474, 3475, 3476, 3477, 3478, 3479, 3480, 3481,
            3482, 3483, 3484, 3485, 3486, 3487, 3488, 3489, 3490, 3491, 3492,
            3493, 3494, 3495):
            v = 3.11
        elif x in (3500, 3501, 3502, 3503, 3504, 3505, 3506, 3507, 3508, 3509,
            3510, 3511, 3512, 3513, 3514, 3515, 3516, 3517, 3518, 3519, 3520,
            3521, 3522, 3523, 3524, 3525, 3526, 3527, 3528, 3529, 3530, 3531):
            v = 3.12
        elif 3000 <= x < 4000: # is this good ?
            v = 3
        return v

class JavaMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("\xCA\xFE\xBA\xBE")

    def get_name(self):
        return "class"

class RPMMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("\xED\xAB\xEE\xDB")

    def get_name(self):
        return "rpm"

class DEBMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("!<arch>\x0Adebian-binary   ")

    def get_name(self):
        return "deb"

class BMPMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("BM")

    def get_name(self):
        return "bmp"

class JPEGMagic (_magic):
    def test(self, fo):
        a, b = self.get_magic()
        return self.test_head(fo, a) and self.test_tail(fo, b)

    def get_magic(self):
        return _("\xFF\xD8"), _("\xFF\xD9")

    def get_name(self):
        return "jpeg"

class GIFMagic (_magic):
    def test(self, fo):
        a, b = self.get_magic()
        return self.test_head(fo, a) or self.test_head(fo, b)

    def get_magic(self):
        return _("GIF87a"), _("GIF89a")

    def get_name(self):
        return "gif"

class PNGMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("\x89PNG")

    def get_name(self):
        return "png"

class PDFMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("%PDF")

    def get_name(self):
        return "pdf"

class PSMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("%!")

    def get_name(self):
        return "ps"

class MSOfficeMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("\xD0\xCF\x11\xE0")

    def get_name(self):
        return "msoffice"

class LHAMagic (_magic):
    def test(self, fo):
        b = self.read(fo, 2, 5)
        return \
            (b[:3] == _("-lh")) and \
            (b[3:4] in _("01234567")) and \
            (b[4:5] == _("-"))

    def get_name(self):
        return "lha"

class ZIPMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("PK")

    def get_name(self):
        return "zip"

class GZIPMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("\x1F\x8B")

    def get_name(self):
        return "gzip"

class BZIPMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("BZh")

    def get_name(self):
        return "bzip"

class ARMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)

    def get_magic(self):
        return _("!<arch>\x0A")

    def get_name(self):
        return "ar"

class TARMagic (_magic):
    def test(self, fo):
        b = self.read(fo, 257, 6)
        if b == _("ustar\x00"):
            return True # POSIX
        b = self.read(fo, 257, 8)
        if b == _("ustar  \x00"):
            return True # GNU
        return False

    def get_name(self):
        return "tar"

class CPIOMagic (_magic):
    def test(self, fo):
        b = self.read(fo, 0, 2)
        if b == _("\xC7\x71") or b == _("\x71\xC7"): # 070707
            return True # binary
        b = self.read(fo, 0, 6)
        if b == _("070701"):
            return True # ascii
        return False

    def get_name(self):
        return "cpio"

class _blk_magic (_magic):
    pass

class ISO9660Magic (_blk_magic):
    def test(self, fo):
        for x in (0x8001, 0x8801, 0x9001):
            if self.read(fo, x, 5) == self.get_magic():
                return True
        return False

    def get_magic(self):
        return _("CD001")

    def get_name(self):
        return "iso9660"

class LVM2PVMagic (_blk_magic):
    def test(self, fo):
        return self.read(fo, 512, 8) == self.get_magic()

    def get_magic(self):
        return _("LABELONE")

    def get_name(self):
        return "lvm2|pv"

class HAMMERFSMagic (_blk_magic):
    """Magic definition is taken from
HAMMER_FSBUF_VOLUME in sys/vfs/hammer/hammer_disk.h"""
    def test(self, fo):
        return self.read(fo, 0, 8) == self.get_magic()

    def get_magic(self):
        return _("\x31\x30\x52\xC5\x4D\x4D\x41\xC8") # le

    def get_name(self):
        return "hammerfs"

class HAMMER2FSMagic (_blk_magic):
    """Magic definition is taken from
HAMMER2_VOLUME_ID_HBO in sys/vfs/hammer2/hammer2_disk.h"""
    def test(self, fo):
        return self.read(fo, 0, 8) == self.get_magic()

    def get_magic(self):
        return _("\x11\x20\x17\x05\x32\x4d\x41\x48") # le

    def get_name(self):
        return "hammer2fs"

class MBRMagic (_blk_magic):
    def test(self, fo):
        return self.read(fo, 510, 2) == self.get_magic()

    def get_magic(self):
        return _("\x55\xAA")

    def get_name(self):
        return "mbr"

def get_string(fo):
    return __get_sring(fo, _magics)

def get_blk_string(fo):
    return __get_sring(fo, _blk_magics)

def __get_sring(fo, l):
    if fo.is_empty():
        return ''
    for cls in l:
        o = cls()
        if o.test(fo):
            return o.get_name()
    return ''

# DEBMagic comes before ARMagic
_magics = \
    ELFMagic, \
    EXEMagic, \
    PythonMagic, \
    JavaMagic, \
    RPMMagic, \
    DEBMagic, \
    BMPMagic, \
    JPEGMagic, \
    GIFMagic, \
    PNGMagic, \
    PDFMagic, \
    PSMagic, \
    MSOfficeMagic, \
    LHAMagic, \
    ZIPMagic, \
    GZIPMagic, \
    BZIPMagic, \
    ARMagic, \
    TARMagic, \
    CPIOMagic, \
    ISO9660Magic, \
    LVM2PVMagic, \
    HAMMERFSMagic, \
    HAMMER2FSMagic, \
    MBRMagic, # MBRMagic comes last

_blk_magics = tuple(cls for cls in _magics
    if util.is_subclass(cls, _blk_magic, False))
