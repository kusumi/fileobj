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

from __future__ import division

from . import panel
from . import setting
from . import util

class NullFrame (panel.Frame):
    def repaint(self, *arg):
        return

    def noutrefresh(self):
        return

    def box(self, current):
        return

class _canvas (panel.PageLineCanvas):
    def fill(self, low):
        super(_canvas, self).fill(low)
        pos = self.fileops.get_pos()
        # XXX There are still a few cases where current position doesn't meet
        # below after previous command (e.g. Gr<RIGHT> for not moving -1/left),
        # so keep auto adjustment until all gone.
        #assert 0 <= pos <= self.fileops.get_max_pos(), pos
        if pos > self.fileops.get_max_pos():
            self.go_to(self.fileops.get_max_pos())
        elif pos < 0:
            self.go_to(0)
        # XXX Adjust if current position isn't aligned with bpu.
        if setting.use_unit_based:
            if pos % setting.bytes_per_unit:
                self.fileops.set_unit_pos(pos)

    def noutrefresh(self):
        return

    def go_up(self, n):
        d = -self.bufmap.x * n
        if not setting.use_unit_based:
            self.fileops.add_pos(d)
        else:
            self.fileops.add_unit_pos(d)

    def go_down(self, n):
        d = self.bufmap.x * n
        if not setting.use_unit_based:
            self.fileops.add_pos(d)
        else:
            self.fileops.add_unit_pos(d)

    def go_left(self, n):
        d = -n
        if not setting.use_unit_based:
            self.fileops.add_pos(d)
        else:
            pos = self.fileops.get_pos()
            unitlen = setting.bytes_per_unit
            if pos % unitlen and n > 0:
                pos += unitlen
            pos = util.rounddown(pos, unitlen)
            pos += d * unitlen # don't set+add (do in 1 step)
            self.fileops.set_unit_pos(pos)

    def go_right(self, n):
        d = n
        if not setting.use_unit_based:
            self.fileops.add_pos(d)
        else:
            pos = self.fileops.get_pos()
            unitlen = setting.bytes_per_unit
            if pos % unitlen and n < 0:
                pos += unitlen
            pos = util.rounddown(pos, unitlen)
            pos += d * unitlen # don't set+add (do in 1 step)
            self.fileops.set_unit_pos(pos)

    def go_pprev(self, n):
        d = -self.get_capacity() * n
        if not setting.use_unit_based:
            self.fileops.add_pos(d)
        else:
            self.fileops.add_unit_pos(d)

    def go_hpprev(self, n):
        d = -self.get_capacity() // 2 * n
        if not setting.use_unit_based:
            self.fileops.add_pos(d)
        else:
            self.fileops.add_unit_pos(d)

    def go_pnext(self, n):
        d = self.get_capacity() * n
        if not setting.use_unit_based:
            self.fileops.add_pos(d)
        else:
            self.fileops.add_unit_pos(d)

    def go_hpnext(self, n):
        d = self.get_capacity() // 2 * n
        if not setting.use_unit_based:
            self.fileops.add_pos(d)
        else:
            self.fileops.add_unit_pos(d)

    def go_head(self, n):
        pos = 0
        if n > 0:
            pos += self.bufmap.x * n
            x = self.fileops.get_max_pos()
            if pos > x:
                pos = x - x % self.bufmap.x
        if not setting.use_unit_based:
            self.fileops.set_pos(pos)
        else:
            self.fileops.set_unit_pos(pos)

    def go_tail(self, n):
        if n > 0:
            self.go_head(n)
            return
        pos = self.fileops.get_max_pos()
        if not setting.use_unit_based:
            self.fileops.set_pos(pos)
        else:
            self.fileops.set_unit_pos(pos)

    def go_lhead(self):
        pos = self.fileops.get_pos()
        pos -= pos % self.bufmap.x
        if not setting.use_unit_based:
            self.fileops.set_pos(pos)
        else:
            self.fileops.set_unit_pos(pos)

    def go_ltail(self, n):
        pos = self.get_line_offset(self.fileops.get_pos()) + self.bufmap.x - 1
        if n > 0:
            pos += self.bufmap.x * n
        if not setting.use_unit_based:
            self.fileops.set_pos(pos)
        else:
            self.fileops.set_unit_pos(pos)

    def go_phead(self, n):
        pos = self.get_page_offset()
        if n > 0:
            pos += self.bufmap.x * n
            if pos >= self.get_next_page_offset():
                pos = self.get_next_page_offset() - self.bufmap.x
            x = self.fileops.get_max_pos()
            if pos > x:
                pos = x - x % self.bufmap.x
        if not setting.use_unit_based:
            self.fileops.set_pos(pos)
        else:
            self.fileops.set_unit_pos(pos)

    def go_pcenter(self):
        n = self.get_next_page_offset()
        if n > self.fileops.get_max_pos():
            n = self.fileops.get_max_pos()
        pgo = self.get_page_offset()
        pos = pgo + (n - pgo) // 2
        pos -= pos % self.bufmap.x
        if not setting.use_unit_based:
            self.fileops.set_pos(pos)
        else:
            self.fileops.set_unit_pos(pos)

    def go_ptail(self, n):
        if self.get_next_page_offset() >= self.fileops.get_size():
            pos = self.fileops.get_max_pos()
            pos -= pos % self.bufmap.x
        else:
            pos = self.get_next_page_offset() - self.bufmap.x
        if n > 0:
            pos -= self.bufmap.x * n
            if pos < self.get_page_offset():
                pos = self.get_page_offset()
        if not setting.use_unit_based:
            self.fileops.set_pos(pos)
        else:
            self.fileops.set_unit_pos(pos)

    def go_to(self, n):
        if not setting.use_unit_based:
            self.fileops.set_pos(n)
        else:
            self.fileops.set_unit_pos(n) # XXX move to nth unit ?

class BinaryCanvas (_canvas, panel.binary_attribute):
    pass

class ExtCanvas (_canvas, panel.default_attribute):
    pass
