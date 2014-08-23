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

from __future__ import division

from . import panel

class NullFrame (panel.Frame):
    def repaint(self, focus):
        return
    def refresh(self):
        return
    def box(self, focus):
        return

class _canvas (panel.Canvas):
    def fill(self, low):
        """Update position before other canvas refer to it"""
        pos = self.fileops.get_pos()
        if pos > self.fileops.get_max_pos():
            self.go_to(self.fileops.get_max_pos())
        elif pos < 0:
            self.go_to(0)

    def refresh(self):
        return

    def go_up(self, n):
        self.fileops.add_pos(-self.bufmap.x * n)

    def go_down(self, n):
        self.fileops.add_pos(self.bufmap.x * n)

    def go_left(self, n):
        self.fileops.add_pos(-n)

    def go_right(self, n):
        self.fileops.add_pos(n)

    def go_pprev(self, n):
        self.fileops.add_pos(-self.get_capacity() * n)

    def go_hpprev(self, n):
        self.fileops.add_pos(-self.get_capacity() // 2 * n)

    def go_pnext(self, n):
        self.fileops.add_pos(self.get_capacity() * n)

    def go_hpnext(self, n):
        self.fileops.add_pos(self.get_capacity() // 2 * n)

    def go_head(self, n):
        pos = 0
        if n > 0:
            pos += self.bufmap.x * n
            x = self.fileops.get_max_pos()
            if pos > x:
                pos = x - x % self.bufmap.x
        self.fileops.set_pos(pos)

    def go_tail(self, n):
        if n > 0:
            self.go_head(n)
        else:
            self.fileops.set_pos(self.fileops.get_max_pos())

    def go_lhead(self):
        pos = self.fileops.get_pos()
        self.fileops.set_pos(pos - pos % self.bufmap.x)

    def go_ltail(self, n):
        pos = self.get_line_offset(
            self.fileops.get_pos()) + self.bufmap.x - 1
        if n > 0:
            pos += self.bufmap.x * n
        self.fileops.set_pos(pos)

    def go_phead(self, n):
        pos = self.get_page_offset()
        if n > 0:
            pos += self.bufmap.x * n
            if pos >= self.get_next_page_offset():
                pos = self.get_next_page_offset() - self.bufmap.x
            x = self.fileops.get_max_pos()
            if pos > x:
                pos = x - x % self.bufmap.x
        self.fileops.set_pos(pos)

    def go_pcenter(self):
        n = self.get_next_page_offset()
        if n > self.fileops.get_max_pos():
            n = self.fileops.get_max_pos()
        pgo = self.get_page_offset()
        pos = pgo + (n - pgo) // 2
        self.fileops.set_pos(pos - pos % self.bufmap.x)

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
        self.fileops.set_pos(pos)

    def go_to(self, n):
        self.fileops.set_pos(n)

class BinaryCanvas (_canvas, panel.binary_addon):
    pass
class ExtCanvas (_canvas, panel.default_addon):
    pass
