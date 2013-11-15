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

from . import fileobj
from . import kernel
from . import rwfd
from . import util

class Fileobj (rwfd.Fileobj):
    _insert  = False
    _replace = True
    _delete  = True
    _enabled = True

    def __str__(self):
        l = []
        l.append("device size %s" %
            util.get_byte_string(self.get_size()))
        l.append("sector size %s" %
            util.get_byte_string(self.get_sector_size()))
        l.append("label %s" % self.__label)
        return "%s\n\n%s" % (super(Fileobj, self).__str__(), '\n'.join(l))

    def init(self):
        b = kernel.get_blkdev_info(self.get_path())
        assert b.sector_size % 512 == 0, b.sector_size
        self.__sector_size = b.sector_size
        self.__label = b.label
        self.set_size(b.size)
        self.set_align(self.get_sector_size())
        self.set_window(0, 1)
        self.open_file('r+')

    def get_sector_size(self):
        return self.__sector_size

    def creat(self, f):
        raise fileobj.FileobjError(
            "Can only write to %s" % self.get_path())
