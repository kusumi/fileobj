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

import errno

from . import blk
from . import rwfd

class Fileobj (rwfd.Fileobj, blk.methods):
    _insert   = False
    _replace  = True
    _delete   = False
    _truncate = False
    _enabled  = blk.enabled
    _partial  = True

    def __str__(self):
        return super(Fileobj, self).__str__() + "\n\n" + self.get_string()

    def ctr(self):
        self.init_blk()

    def get_sector_size(self):
        return self.get_blk_sector_size()

    def creat(self, f):
        self.creat_blk()

    def read(self, x, n):
        try:
            return super(Fileobj, self).read(x, n)
        except IOError as e:
            return self.pad(e, n)

    def replace(self, x, l, rec=True):
        try:
            return super(Fileobj, self).replace(x, l, rec)
        except IOError as e:
            # XXX Added for Solaris.
            # If failed to read a block device beyond a certain sector
            # with ENXIO (even if it's within what ioctl had reported),
            # just ignore.
            if e.errno != errno.ENXIO:
                raise
