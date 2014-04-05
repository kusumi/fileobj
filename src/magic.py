# Copyright (c) 2010-2014, TOMOHIRO KUSUMI
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
        return b"\x7fELF"
    def get_name(self):
        return "ELF"

class EXEMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)
    def get_magic(self):
        return b"MZ"
    def get_name(self):
        return "EXE"

class PythonMagic (_magic):
    """Magic definition is taken from
Python-3.4.0/Lib/importlib/_bootstrap.py"""
    def __init__(self):
        self.__name = "PYC"

    def test(self, fo):
        v = self.__get_version(fo)
        if v < 0:
            return False
        else:
            if v >= 1.5:
                self.__name = "PYC|{0}".format(v)
            return True

    def get_name(self):
        return self.__name

    def __get_version(self, fo):
        v = -1
        b = self.read(fo, 0, 4)
        if b[2:4] != b"\r\n":
            return v
        l = filebytes.ordt(b)
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
        elif 3000 <= x < 4000: # is this good ?
            v = 3
        return v

class JavaMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)
    def get_magic(self):
        return b"\xCA\xFE\xBA\xBE"
    def get_name(self):
        return "CLASS"

class RPMMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)
    def get_magic(self):
        return b"\xED\xAB\xEE\xDB"
    def get_name(self):
        return "RPM"

class BMPMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)
    def get_magic(self):
        return b"BM"
    def get_name(self):
        return "BMP"

class JPEGMagic (_magic):
    def test(self, fo):
        a, b = self.get_magic()
        return self.test_head(fo, a) and self.test_tail(fo, b)
    def get_magic(self):
        return b"\xFF\xD8", b"\xFF\xD9"
    def get_name(self):
        return "JPEG"

class GIFMagic (_magic):
    def test(self, fo):
        a, b = self.get_magic()
        return self.test_head(fo, a) or self.test_head(fo, b)
    def get_magic(self):
        return b"GIF87a", b"GIF89a"
    def get_name(self):
        return "GIF"

class PNGMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)
    def get_magic(self):
        return b"\x89PNG"
    def get_name(self):
        return "PNG"

class PDFMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)
    def get_magic(self):
        return b"%PDF"
    def get_name(self):
        return "PDF"

class PSMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)
    def get_magic(self):
        return b"%!"
    def get_name(self):
        return "PS"

class MSOfficeMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)
    def get_magic(self):
        return b"\xD0\xCF\x11\xE0"
    def get_name(self):
        return "MSOffice"

class LHAMagic (_magic):
    def test(self, fo):
        b = self.read(fo, 2, 5)
        return \
            (b[:3] == b"-lh") and \
            (b[3:4] in b"01234567") and \
            (b[4:5] == b"-")
    def get_name(self):
        return "LHA"

class ZIPMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)
    def get_magic(self):
        return b"PK"
    def get_name(self):
        return "ZIP"

class GZIPMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)
    def get_magic(self):
        return b"\x1F\x8B"
    def get_name(self):
        return "GZIP"

class BZIPMagic (_magic):
    def test(self, fo):
        return self.test_head(fo)
    def get_magic(self):
        return b"BZh"
    def get_name(self):
        return "BZIP"

class _blk_magic (_magic):
    pass

# define and initialize before MBRMagic
class ISO9660Magic (_blk_magic):
    def test(self, fo):
        for x in (0x8001, 0x8801, 0x9001):
            if self.read(fo, x, 5) == self.get_magic():
                return True
        return False
    def get_magic(self):
        return b"CD001"
    def get_name(self):
        return "ISO9660"

class MBRMagic (_blk_magic):
    def test(self, fo):
        return self.read(fo, 510, 2) == self.get_magic()
    def get_magic(self):
        return b"\x55\xAA"
    def get_name(self):
        return "MBR"

def get_string(fo):
    return _get_string(fo, _magics)

def get_blk_string(fo):
    return _get_string(fo, _blk_magics)

def _get_string(fo, l):
    if fo.is_empty():
        return ''
    for cls in l:
        o = cls()
        if o.test(fo):
            return o.get_name()
    return ''

_magics = \
ELFMagic, \
EXEMagic, \
PythonMagic, \
JavaMagic, \
RPMMagic, \
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
ISO9660Magic, \
MBRMagic,

_blk_magics = tuple(cls for cls in _magics
    if util.is_subclass(cls, _blk_magic, False))
