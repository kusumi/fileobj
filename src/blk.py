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

import errno

from . import fileobj
from . import kernel
from . import util

enabled = kernel.is_blkdev_supported()

class methods (object):
    def get_string(self):
        l = []
        l.append("device size {0}".format(
            util.get_size_repr(self.get_size())))
        l.append("sector size {0}".format(
            util.get_size_repr(self.get_sector_size())))
        l.append("label '{0}'".format(self.blk_label))
        return '\n'.join(l)

    def init_blk(self):
        b = kernel.get_blkdev_info(self.get_path())
        align = 1 << 9
        assert b.sector_size % align == 0, b.sector_size
        assert b.size % align == 0, b.size
        self.blk_sector_size = b.sector_size
        self.blk_label = b.label
        self.set_size(b.size)
        self.set_align(self.get_sector_size())
        self.set_window(0, 1)
        self.init_file()

    def get_blk_sector_size(self):
        return self.blk_sector_size

    def creat_blk(self):
        raise fileobj.FileobjError(
            "Can only write to " + self.get_path())

    def pad(self, e, n):
        # XXX Added for Solaris.
        # If failed to read a block device beyond a certain sector
        # with ENXIO (even if it's within what ioctl had reported),
        # just pretend it's read by returning 0xff filled buffer.
        if isinstance(e, IOError) and e.errno == errno.ENXIO:
            return util.str_to_bytes("\xff" * n)
        raise e
