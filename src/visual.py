# Copyright (c) 2011, Tomohiro Kusumi
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

import sys

from . import console
from . import edit
from . import extension
from . import kbd
from . import literal
from . import methods
from . import panel
from . import screen
from . import setting
from . import util

VISUAL = "VISUAL"
VISUAL_LINE = "VISUAL LINE"
VISUAL_BLOCK = "VISUAL BLOCK"

class _visual_methods (object):
    def init(self):
        if setting.color_visual is None:
            if screen.use_alt_chgat():
                self.__chgat_head = self.__alt_chgat_head
                self.__chgat_tail = self.__alt_chgat_tail
                self.__chgat_single = self.__alt_chgat_single
                self.__chgat_inside = self.__alt_chgat_inside
                self.__chgat_outside = self.__alt_chgat_outside
        else:
            if screen.use_alt_chgat():
                self.__chgat_head = self.__alt_chgat_head_attr
                self.__chgat_tail = self.__alt_chgat_tail_attr
                self.__chgat_single = self.__alt_chgat_single_attr
                self.__chgat_outside = self.__alt_chgat_outside_attr
            else: # default
                self.__chgat_head = self.__chgat_head_attr
                self.__chgat_tail = self.__chgat_tail_attr
                self.__chgat_single = self.__chgat_single_attr
                self.__chgat_outside = self.__chgat_outside_attr

    def update_visual(self, full):
        if not self.fileops.has_region():
            return # last repaint before exit
        t = self.fileops.get_region_type()
        if t == VISUAL_BLOCK:
            self.__update_block_visual(full)
        else:
            self.__update_visual(t, full)
        pos = self.fileops.get_pos()
        self.page_update_search(pos)
        self.chgat_cursor(pos, screen.A_COLOR_CURRENT, screen.A_COLOR_CURRENT,
            False)

    def __update_visual(self, t, full):
        pos = self.fileops.get_pos()
        ppos = self.fileops.get_prev_pos()
        if self.in_same_page(pos, ppos):
            self.chgat_posstr(ppos, screen.A_NONE)
        else:
            full = True
        self.chgat_posstr(pos, self.attr_posstr)

        beg = self.fileops.get_region_origin()
        end = pos
        if beg > end:
            beg, end = end, beg
        mapx = self.bufmap.x
        if t == VISUAL_LINE:
            beg -= beg % mapx
            end += (mapx - 1 - end % mapx)
        if setting.use_unit_based and (end % setting.bytes_per_unit == 0):
            end += (setting.bytes_per_unit - 1) # round up before set region
        self.fileops.set_region_range(beg, end, self.bufmap)

        pgo = self.get_page_offset()
        npgo = self.get_next_page_offset()
        if beg < pgo:
            beg = pgo
        if end > npgo - 1:
            end = npgo - 1
        lcur = pgo

        l = []
        if not full:
            a = self.get_line_offset(pos)
            b = self.get_line_offset(ppos)
            if a == b:
                l = [a]
            else:
                if a < b:
                    a, b = b, a
                l = [b + i for i in util.get_xrange(0, a - b + mapx, mapx)]

        limit = self.fileops.get_max_pos()
        y = self.offset.y
        x = self.offset.x
        for _ in util.get_xrange(self.bufmap.y):
            if lcur > limit:
                break
            lnext = lcur + mapx
            if full or (lcur in l):
                head = lcur <= beg < lnext
                tail = lcur <= end < lnext
                if head and tail:
                    self.__chgat_single(y, x, beg, end, lcur)
                elif head:
                    self.__chgat_head(y, x, beg, lcur)
                elif tail:
                    self.__chgat_tail(y, x, end, lcur)
                elif beg < lcur < end:
                    self.__chgat_inside(y, x, lcur)
                else:
                    self.__chgat_outside(y, x, lcur)
            lcur = lnext
            y += 1

    def __update_block_visual(self, full):
        pos = self.fileops.get_pos()
        ppos = self.fileops.get_prev_pos()
        if self.in_same_page(pos, ppos):
            self.chgat_posstr(ppos, screen.A_NONE)
        else:
            full = True
        self.chgat_posstr(pos, self.attr_posstr)

        beg = self.fileops.get_region_origin()
        end = pos
        if beg > end:
            beg, end = end, beg
        mapx = self.bufmap.x
        d1 = beg % mapx
        d2 = end % mapx
        lbeg = beg - d1
        lend = end - d2
        if d1 > d2:
            d2, d1 = d1, d2
        if setting.use_unit_based:
            d2 += (setting.bytes_per_unit - 1) # round up before set region
        self.fileops.set_region_range(lbeg + d1, lend + d2, self.bufmap)

        lcur = self.get_page_offset()
        lpos = self.get_line_offset(pos)
        lppos = self.get_line_offset(ppos)
        lr = abs(pos - ppos) != mapx # move left/right

        l = []
        if not full:
            a, b = lpos, lppos
            if a == b:
                l = [a]
            else:
                if a < b:
                    a, b = b, a
                l = [b + i for i in util.get_xrange(0, a - b + mapx, mapx)]

        limit = self.fileops.get_max_pos()
        y = self.offset.y
        x = self.offset.x
        for _ in util.get_xrange(self.bufmap.y):
            if lcur > limit:
                break
            if full or lr or (lcur in l):
                # XXX second and third conditionals are redundant
                if lbeg <= lcur <= lend:
                    self.__chgat_single(y, x, lcur + d1, lcur + d2, lcur)
                elif lppos <= lcur < lbeg and lpos == lbeg and lppos < lpos:
                    self.__chgat_outside(y, x, lcur) # down
                elif lend < lcur <= lppos and lpos == lend and lpos < lppos:
                    self.__chgat_outside(y, x, lcur) # up
                elif lppos < lbeg: # jump down to other side of region
                    self.__chgat_outside(y, x, lcur)
                elif lend < lppos: # jump up to other side of region
                    self.__chgat_outside(y, x, lcur)
            lcur += mapx
            y += 1

    def post_fill_line(self, y, x, buf):
        if not self.cell[1]:
            return
        # need to drop visual color from space within unit
        upl, xpu = self.get_units_per_line(len(buf))
        for i in util.get_xrange(upl):
            extra = ' ' * self.cell[1]
            pos = x + self.get_unit_width(i + 1) - len(extra)
            if pos < self.get_size_x():
                # pos + len(extra) - 1 still needs to fit
                self.addstr(y, pos, extra)

    # head
    def __chgat_head(self, y, x, beg, offset):
        pos = self.get_cell_width(beg - offset)
        siz = self.get_cell_edge(self.bufmap.x) - pos
        self.chgat(y, x, pos)
        if x + pos < self.get_size_x():
            self.chgat(y, x + pos, siz, self.attr_visual)

    def __alt_chgat_head(self, y, x, beg, offset):
        pos = self.get_cell_width(beg - offset)
        buf = self.fileops.read(offset, self.bufmap.x)
        s = self.get_str_line(buf)
        d = self.get_cell_edge(self.bufmap.x) - len(s)
        if d > 0:
            s += ' ' * d
        self.addstr(y, x, s[:pos])
        if x + pos < self.get_size_x():
            self.addstr(y, x + pos, s[pos:], self.attr_visual)

    def __chgat_head_attr(self, y, x, beg, offset):
        pos = self.get_cell_width(beg - offset)
        siz = self.get_cell_edge(self.bufmap.x) - pos
        buf = self.fileops.read(offset, beg - offset)
        self.fill_line(y, x, buf, screen.A_NONE,
            self.get_units_per_line(len(buf)))
        self.post_fill_line(y, x, buf)
        if x + pos < self.get_size_x():
            self.chgat(y, x + pos, siz, self.attr_visual)

    def __alt_chgat_head_attr(self, y, x, beg, offset):
        pos = self.get_cell_width(beg - offset)
        buf = self.fileops.read(offset, self.bufmap.x)
        s = self.get_str_line(buf)
        d = self.get_cell_edge(self.bufmap.x) - len(s)
        if d > 0:
            s += ' ' * d
        buf = self.fileops.read(offset, beg - offset)
        self.fill_line(y, x, buf, screen.A_NONE,
            self.get_units_per_line(len(buf)))
        self.post_fill_line(y, x, buf)
        if x + pos < self.get_size_x():
            self.addstr(y, x + pos, s[pos:], self.attr_visual)

    # tail
    def __chgat_tail(self, y, x, end, offset):
        pos = self.get_cell_edge(end - offset + 1)
        siz = self.get_cell_edge(self.bufmap.x) - pos
        self.chgat(y, x, pos, self.attr_visual)
        if x + pos < self.get_size_x():
            self.chgat(y, x + pos, siz)

    def __alt_chgat_tail(self, y, x, end, offset):
        pos = self.get_cell_edge(end - offset + 1)
        buf = self.fileops.read(offset, self.bufmap.x)
        s = self.get_str_line(buf)
        d = pos - len(s)
        if d > 0:
            s += ' ' * d
        self.addstr(y, x, s[:pos], self.attr_visual)
        if x + pos < self.get_size_x():
            self.addstr(y, x + pos, s[pos:])

    def __chgat_tail_attr(self, y, x, end, offset):
        siz = self.get_cell_edge(end - offset + 1)
        self.chgat(y, x, siz, self.attr_visual)
        if end + 1 <= self.fileops.get_max_pos():
            self.__chgat_tail_attr_clear(y, x, end, offset)

    def __alt_chgat_tail_attr(self, y, x, end, offset):
        siz = self.get_cell_edge(end - offset + 1)
        buf = self.fileops.read(offset, self.bufmap.x)
        s = self.get_str_line(buf)
        d = siz - len(s)
        if d > 0:
            s += ' ' * d
        self.addstr(y, x, s[:siz], self.attr_visual)
        if end + 1 <= self.fileops.get_max_pos():
            self.__chgat_tail_attr_clear(y, x, end, offset)

    def __chgat_tail_attr_clear(self, y, x, end, offset):
        num = end - offset + 1
        buf = self.fileops.read(end + 1, self.bufmap.x - num)
        pos = self.get_cell_width(num)
        xx = self.fill_line_nth(y, x + pos, buf, num, screen.A_NONE)
        self.post_fill_line(y, xx, buf)
        if (end + 1) % self.bufmap.x: # not rightmost
            # clear right side of newly fill'd line (needed when moving left/up)
            unitlen = setting.bytes_per_unit
            if (num % unitlen) == 0:
                self.addstr(y, x + pos - 1, ' ' * self.cell[1])
            else:
                skip = unitlen - (num % unitlen)
                skip *= self.cell[2]
                xx = x + pos + skip
                if xx <= self.get_size_x() - 1:
                    # xx + len(...) - 1 still needs to fit
                    self.addstr(y, xx, ' ' * self.cell[1])

    # single
    def __chgat_single(self, y, x, beg, end, offset):
        pos = self.get_cell_width(beg - offset)
        siz = self.get_cell_distance(beg, end)
        wid = self.get_cell_edge(self.bufmap.x)
        self.chgat(y, x, wid)
        if x + pos < self.get_size_x():
            self.chgat(y, x + pos, siz, self.attr_visual)

    def __alt_chgat_single(self, y, x, beg, end, offset):
        pos = self.get_cell_width(beg - offset)
        siz = self.get_cell_distance(beg, end)
        end = pos + siz
        buf = self.fileops.read(offset, self.bufmap.x)
        s = self.get_str_line(buf)
        d = end - len(s)
        if d > 0:
            s += ' ' * d
        self.addstr(y, x, s[:pos])
        if x + pos < self.get_size_x():
            self.addstr(y, x + pos, s[pos:end], self.attr_visual)
        if x + end < self.get_size_x():
            self.addstr(y, x + end, s[end:])

    def __chgat_single_attr(self, y, x, beg, end, offset):
        pos = self.get_cell_width(beg - offset)
        siz = self.get_cell_distance(beg, end)
        buf = self.fileops.read(offset, self.bufmap.x)
        self.fill_line(y, x, buf, screen.A_NONE,
            self.get_units_per_line(len(buf)))
        self.post_fill_line(y, x, buf)
        if x + pos < self.get_size_x():
            self.chgat(y, x + pos, siz, self.attr_visual)

    def __alt_chgat_single_attr(self, y, x, beg, end, offset):
        pos = self.get_cell_width(beg - offset)
        siz = self.get_cell_distance(beg, end)
        end = pos + siz
        buf = self.fileops.read(offset, self.bufmap.x)
        s = self.get_str_line(buf)
        d = end - len(s)
        if d > 0:
            s += ' ' * d
        buf = self.fileops.read(offset, self.bufmap.x)
        self.fill_line(y, x, buf, screen.A_NONE,
            self.get_units_per_line(len(buf)))
        self.post_fill_line(y, x, buf)
        if x + pos < self.get_size_x():
            self.addstr(y, x + pos, s[pos:end], self.attr_visual)

    # inside
    def __chgat_inside(self, y, x, offset):
        self.__chgat_body(y, x, offset, self.attr_visual)

    def __alt_chgat_inside(self, y, x, offset):
        self.__alt_chgat_body(y, x, offset, self.attr_visual)

    # outside
    def __chgat_outside(self, y, x, offset):
        self.__chgat_body(y, x, offset, screen.A_NONE)

    def __alt_chgat_outside(self, y, x, offset):
        self.__alt_chgat_body(y, x, offset, screen.A_NONE)

    def __chgat_outside_attr(self, y, x, offset):
        self.__chgat_body_attr(y, x, offset, screen.A_NONE)

    def __alt_chgat_outside_attr(self, y, x, offset):
        self.__chgat_body_attr(y, x, offset, screen.A_NONE)

    # body
    def __chgat_body(self, y, x, offset, attr):
        siz = self.get_cell_edge(self.bufmap.x)
        self.chgat(y, x, siz, attr)

    def __alt_chgat_body(self, y, x, offset, attr):
        buf = self.fileops.read(offset, self.bufmap.x)
        s = self.get_str_line(buf)
        d = self.get_cell_edge(self.bufmap.x) - len(s)
        if d > 0:
            s += ' ' * d
        self.addstr(y, x, s, attr)

    def __chgat_body_attr(self, y, x, offset, attr):
        buf = self.fileops.read(offset, self.bufmap.x)
        if self.fileops.get_region_type() == VISUAL_LINE and \
            len(buf) != self.bufmap.x:
            self.clrl(y, x) # clear last line beyond max position
        self.fill_line(y, x, buf, attr,
            self.get_units_per_line(len(buf)))
        self.post_fill_line(y, x, buf)

class BinaryCanvas (panel.BinaryCanvas, _visual_methods):
    def __init__(self, siz, pos):
        self.init()
        super(BinaryCanvas, self).__init__(siz, pos)

    def fill(self, low):
        self.require_full_repaint()
        super(BinaryCanvas, self).fill(low)
        self.update_visual(True)

    def update_highlight(self, low, range_update):
        self.require_full_repaint()
        self.update_visual(False)

class TextCanvas (panel.TextCanvas, _visual_methods):
    def __init__(self, siz, pos):
        self.init()
        super(TextCanvas, self).__init__(siz, pos)

    def fill(self, low):
        self.require_full_repaint()
        super(TextCanvas, self).fill(low)
        self.update_visual(True)

    def update_highlight(self, low, range_update):
        self.require_full_repaint()
        self.update_visual(False)

class ExtBinaryCanvas (extension.ExtBinaryCanvas, _visual_methods):
    def __init__(self, siz, pos):
        self.init()
        super(ExtBinaryCanvas, self).__init__(siz, pos)

    def fill(self, low):
        self.require_full_repaint()
        super(ExtBinaryCanvas, self).fill(low)
        self.update_visual(True)

    def update_highlight(self, low, range_update):
        self.require_full_repaint()
        self.update_visual(False)

class _console (console.Console):
    def init_method(self):
        this = sys.modules[__name__]
        self.add_method(literal.up,              methods, "cursor_up")
        self.add_method(literal.down,            methods, "cursor_down")
        self.add_method(literal.left,            methods, "cursor_left")
        self.add_method(literal.right,           methods, "cursor_right")
        self.add_method(literal.gg,              methods, "cursor_head")
        self.add_method(literal.G,               methods, "cursor_tail")
        self.add_method(literal.zero,            methods, "cursor_lhead")
        self.add_method(literal.doller,          methods, "cursor_ltail")
        self.add_method(literal.H,               methods, "cursor_phead")
        self.add_method(literal.M,               methods, "cursor_pcenter")
        self.add_method(literal.L,               methods, "cursor_ptail")
        self.add_method(literal.w,               methods, "cursor_next_char")
        self.add_method(literal.b,               methods, "cursor_prev_char")
        self.add_method(literal.asterisk,        methods, "cursor_next_current")
        self.add_method(literal.sharp,           methods, "cursor_prev_current")
        self.add_method(literal.parens_end,      methods, "cursor_next_zero")
        self.add_method(literal.parens_beg,      methods, "cursor_prev_zero")
        self.add_method(literal.bracket1_end,    methods, "cursor_next_nonzero")
        self.add_method(literal.bracket1_beg,    methods, "cursor_prev_nonzero")
        self.add_method(literal.bracket2_end,    methods, "end_read_delayed_input")
        self.add_method(literal.bracket2_beg,    methods, "start_read_delayed_input")
        self.add_method(literal.go,              methods, "cursor_to")
        self.add_method(literal.sh,              methods, "cursor_sector_left")
        self.add_method(literal.sl,              methods, "cursor_sector_right")
        self.add_method(literal.szero,           methods, "cursor_sector_shead")
        self.add_method(literal.sdoller,         methods, "cursor_sector_stail")
        self.add_method(literal.sgo,             methods, "cursor_sector_to")
        self.add_method(literal.sz,              methods, "cursor_next_zero_sector")
        self.add_method(literal.snz,             methods, "cursor_next_non_zero_sector")
        self.add_method(literal.sZ,              methods, "cursor_prev_zero_sector")
        self.add_method(literal.snZ,             methods, "cursor_prev_non_zero_sector")
        self.add_method(literal.ctrlb,           methods, "cursor_pprev")
        self.add_method(literal.ctrlu,           methods, "cursor_hpprev")
        self.add_method(literal.ctrlf,           methods, "cursor_pnext")
        self.add_method(literal.ctrld,           methods, "cursor_hpnext")
        self.add_method(literal.mouse,           methods, "handle_mouse_event_visual")
        self.add_method(literal.resize,          methods, "resize_container")
        self.add_method(literal.ctrll,           methods, "refresh_container")
        self.add_method(literal.ctrlw_w,         this,    "_queue_input")
        self.add_method(literal.ctrlw_W,         this,    "_queue_input")
        self.add_method(literal.ctrlw_t,         this,    "_queue_input")
        self.add_method(literal.ctrlw_b,         this,    "_queue_input")
        self.add_method(literal.ctrlw_s,         this,    "_queue_input")
        self.add_method(literal.s_split,         this,    "_queue_input")
        self.add_method(literal.s_vsplit,        this,    "_queue_input")
        self.add_method(literal.ctrlw_plus,      methods, "inc_workspace_height")
        self.add_method(literal.ctrlw_minus,     methods, "dec_workspace_height")
        self.add_method(literal.s_close,         this,    "_queue_input")
        self.add_method(literal.s_only,          this,    "_queue_input")
        self.add_method(literal.s_e,             this,    "_queue_input")
        self.add_method(literal.s_bdelete,       this,    "_queue_input")
        self.add_method(literal.s_bfirst,        this,    "_queue_input")
        self.add_method(literal.s_blast,         this,    "_queue_input")
        self.add_method(literal.s_bnext,         this,    "_queue_input")
        self.add_method(literal.s_bprev,         this,    "_queue_input")
        self.add_method(literal.s_set,           methods, "set_option")
        self.add_method(literal.s_auto,          methods, "set_auto")
        self.add_method(literal.ctrlg,           this,    "_queue_input")
        self.add_method(literal.g_ctrlg,         this,    "_queue_input")
        self.add_method(literal.s_self,          this,    "_queue_input")
        self.add_method(literal.s_pwd,           this,    "_queue_input")
        self.add_method(literal.s_date,          this,    "_queue_input")
        self.add_method(literal.s_kmod,          this,    "_queue_input")
        self.add_method(literal.s_fobj,          this,    "_queue_input")
        self.add_method(literal.s_bufsiz,        this,    "_queue_input")
        self.add_method(literal.s_meminfo,       this,    "_queue_input")
        self.add_method(literal.s_osdep,         this,    "_queue_input")
        self.add_method(literal.s_screen,        this,    "_queue_input")
        self.add_method(literal.s_platform,      this,    "_queue_input")
        self.add_method(literal.s_hostname,      this,    "_queue_input")
        self.add_method(literal.s_term,          this,    "_queue_input")
        self.add_method(literal.s_lang,          this,    "_queue_input")
        self.add_method(literal.s_version,       this,    "_queue_input")
        self.add_method(literal.s_sector,        this,    "_queue_input")
        self.add_method(literal.s_argv,          this,    "_queue_input")
        self.add_method(literal.s_args,          this,    "_queue_input")
        self.add_method(literal.s_md5,           this,    "_show_md5")
        self.add_method(literal.s_sha1,          this,    "_show_sha1")
        self.add_method(literal.s_sha224,        this,    "_show_sha224")
        self.add_method(literal.s_sha256,        this,    "_show_sha256")
        self.add_method(literal.s_sha384,        this,    "_show_sha384")
        self.add_method(literal.s_sha512,        this,    "_show_sha512")
        self.add_method(literal.s_blake2b,       this,    "_show_blake2b")
        self.add_method(literal.s_blake2s,       this,    "_show_blake2s")
        self.add_method(literal.s_sha3_224,      this,    "_show_sha3_224")
        self.add_method(literal.s_sha3_256,      this,    "_show_sha3_256")
        self.add_method(literal.s_sha3_384,      this,    "_show_sha3_384")
        self.add_method(literal.s_sha3_512,      this,    "_show_sha3_512")
        self.add_method(literal.s_cmp,           this,    "_queue_input")
        self.add_method(literal.s_cmpneg,        this,    "_queue_input")
        self.add_method(literal.s_cmpnext,       this,    "_queue_input")
        self.add_method(literal.s_cmpnextneg,    this,    "_queue_input")
        self.add_method(literal.s_cmpr,          this,    "_queue_input")
        self.add_method(literal.s_cmprneg,       this,    "_queue_input")
        self.add_method(literal.s_cmprnext,      this,    "_queue_input")
        self.add_method(literal.s_cmprnextneg,   this,    "_queue_input")
        self.add_method(literal.ctrla,           this,    "_inc_number")
        self.add_method(literal.ctrlx,           this,    "_dec_number")
        self.add_method(literal.period,          this,    "_queue_input")
        self.add_method(literal.toggle,          this,    "_toggle")
        self.add_method(literal.ror,             this,    "_rotate_right")
        self.add_method(literal.rol,             this,    "_rotate_left")
        self.add_method(literal.bswap,           this,    "_swap_bytes")
        self.add_method(literal.delete,          this,    "_delete")
        self.add_method(literal.X,               this,    "_delete")
        self.add_method(literal.D,               this,    "_delete")
        self.add_method(literal.u,               this,    "_queue_input")
        self.add_method(literal.U,               this,    "_queue_input")
        self.add_method(literal.ctrlr,           this,    "_queue_input")
        self.add_method(literal.s_redo_all,      this,    "_queue_input")
        self.add_method(literal.reg_reg,         methods, "start_register")
        self.add_method(literal.m_reg,           this,    "_queue_input")
        self.add_method(literal.backtick_reg,    this,    "_queue_input")
        self.add_method(literal.s_delmarks,      this,    "_queue_input")
        self.add_method(literal.s_delmarksneg,   this,    "_queue_input")
        self.add_method(literal.q_reg,           methods, "start_record")
        self.add_method(literal.atsign_reg,      methods, "replay_record")
        self.add_method(literal.atsign_at,       methods, "replay_record")
        self.add_method(literal.atsign_colon,    methods, "replay_bind")
        self.add_method(literal.s_bind,          this,    "_queue_input")
        self.add_method(literal.bit_and,         this,    "_logical_bit_operation")
        self.add_method(literal.bit_or,          this,    "_logical_bit_operation")
        self.add_method(literal.bit_xor,         this,    "_logical_bit_operation")
        self.add_method(literal.y,               this,    "_yank")
        self.add_method(literal.Y,               this,    "_yank")
        self.add_method(literal.P,               this,    "_put")
        self.add_method(literal.p,               this,    "_put")
        self.add_method(literal.O,               this,    "_put")
        self.add_method(literal.o,               this,    "_put")
        self.add_method(literal.s_w,             this,    "_save_buffer")
        self.add_method(literal.s_wneg,          this,    "_force_save_buffer")
        self.add_method(literal.s_wq,            this,    "_save_buffer_quit")
        #self.add_method(literal.s_x,            None,    None)
        self.add_method(literal.s_q,             this,    "_queue_input")
        self.add_method(literal.s_qneg,          this,    "_queue_input")
        self.add_method(literal.s_qa,            this,    "_queue_input")
        self.add_method(literal.s_qaneg,         this,    "_queue_input")
        self.add_method(literal.s_open_md5,      this,    "_open_md5")
        self.add_method(literal.s_open_sha1,     this,    "_open_sha1")
        self.add_method(literal.s_open_sha224,   this,    "_open_sha224")
        self.add_method(literal.s_open_sha256,   this,    "_open_sha256")
        self.add_method(literal.s_open_sha384,   this,    "_open_sha384")
        self.add_method(literal.s_open_sha512,   this,    "_open_sha512")
        self.add_method(literal.s_open_blake2b,  this,    "_open_blake2b")
        self.add_method(literal.s_open_blake2s,  this,    "_open_blake2s")
        self.add_method(literal.s_open_sha3_224, this,    "_open_sha3_224")
        self.add_method(literal.s_open_sha3_256, this,    "_open_sha3_256")
        self.add_method(literal.s_open_sha3_384, this,    "_open_sha3_384")
        self.add_method(literal.s_open_sha3_512, this,    "_open_sha3_512")
        self.add_method(literal.s_open_b64e,     this,    "_open_base64_encode")
        self.add_method(literal.s_open_b64d,     this,    "_open_base64_decode")
        self.add_method(literal.s_open_b32e,     this,    "_open_base32_encode")
        self.add_method(literal.s_open_b32d,     this,    "_open_base32_decode")
        self.add_method(literal.s_open_b16e,     this,    "_open_base16_encode")
        self.add_method(literal.s_open_b16d,     this,    "_open_base16_decode")
        self.add_method(literal.s_open_b85e,     this,    "_open_base85_encode")
        self.add_method(literal.s_open_b85d,     this,    "_open_base85_decode")
        self.add_method(literal.s_truncate,      this,    "_queue_input")
        self.add_method(literal.s_fsearchw,      methods, "search_word_forward")
        self.add_method(literal.s_rsearchw,      methods, "search_word_backward")
        self.add_method(literal.n,               methods, "search_word_next_forward")
        self.add_method(literal.N,               methods, "search_word_next_backward")
        self.add_method(literal.fsearchc,        methods, "search_char_forward")
        self.add_method(literal.rsearchc,        methods, "search_char_backward")
        self.add_method(literal.fsearchcb,       methods, "search_char_forward_before")
        self.add_method(literal.rsearchcb,       methods, "search_char_backward_before")
        self.add_method(literal.semicolon,       methods, "search_char_next_forward")
        self.add_method(literal.comma,           methods, "search_char_next_backward")
        self.add_method(literal.escape,          this,    "_escape_visual")
        #self.add_method(literal.i,              None,    None)
        #self.add_method(literal.I,              None,    None)
        #self.add_method(literal.a,              None,    None)
        #self.add_method(literal.A,              None,    None)
        self.add_method(literal.R,               this,    "_enter_edit_replace")
        self.add_method(literal.r,               this,    "_do_edit_replace")
        self.add_method(literal.cw,              this,    "_delete_enter_edit_insert")
        self.add_method(literal.v,               this,    "_enter_visual")
        self.add_method(literal.V,               this,    "_enter_line_visual")
        self.add_method(literal.ctrlv,           this,    "_enter_block_visual")
        self.add_method(literal.d,               this,    "_queue_input")
        for li in literal.get_ext_literals():
            self.add_method(li, this, "_queue_input")

    def handle_signal(self):
        _exit_visual(self)
        return kbd.INTERRUPT

    def handle_invalid_literal(self, li):
        self.co.flash("Not a visual command " + li.str)
        return _exit_visual(self)

    def set_banner(self):
        console.set_banner(self.co.get_region_type())

    def assert_method_result(self, retval):
        if retval == methods.QUEUED:
            assert isinstance(self, _console), str(self)

class Console (_console):
    pass

class ExtConsole (_console):
    pass

def _queue_input(self, amp, opc, args, raw):
    if raw[0] in literal.get_slow_ords():
        raw.append(kbd.ENTER)
        # assert opc exists as a slow literal
        if setting.use_debug:
            found = False
            for li in literal.get_slow_literals():
                if li.str == opc:
                    found = True
                    break
            assert found, "{0} is not a slow literal".format(opc)
        # currently only save region for slow commands
        if _in_block_visual(self):
            self.co.save_block_region()
        else:
            self.co.save_range_region()
    self.co.queue_input(raw)
    _exit_visual(self)
    return methods.QUEUED # not methods.RETURN

def _enter_visual(self, amp, opc, args, raw):
    return __enter_visual(self, VISUAL)

def _enter_line_visual(self, amp, opc, args, raw):
    return __enter_visual(self, VISUAL_LINE)

def _enter_block_visual(self, amp, opc, args, raw):
    return __enter_visual(self, VISUAL_BLOCK)

def __enter_visual(self, visual_type):
    if self.co.get_region_type() == visual_type:
        return _exit_visual(self)
    else:
        self.co.set_region_type(visual_type)
        return self.set_console(util.get_class(self))

def _escape_visual(self, amp, opc, args, raw):
    methods.escape(self, amp, opc, args, raw)
    return _exit_visual(self)

def _exit_visual(self, amp=None, opc=None, args=None, raw=None):
    self.co.cleanup_region()
    # Repaint to ensure space between units are cleared before exit.
    # This is not a must since consoles are repainted on dispatch.
    self.co.lrepaint()
    return self.set_console(None)

def _(a, b):
    def _exit(fn):
        def _method(self, amp, opc, args, raw):
            _fn = b if _in_block_visual(self) else a
            ret = _fn(self, amp, opc, args, raw)
            if ret == methods.QUIT:
                return methods.QUIT
            if ret == methods.ERROR:
                return
            assert ret != methods.REWIND
            assert ret != methods.CONTINUE
            return fn(self, amp, opc, args, raw)
        return _method
    return _exit

def _u(a, b):
    def _exit(fn):
        def _method(self, amp, opc, args, raw):
            # the only difference in keeping undo size in args
            und = self.co.get_undo_size()
            assert isinstance(args, list), list
            args.append(und)
            # the rest is same as _
            _fn = b if _in_block_visual(self) else a
            ret = _fn(self, amp, opc, args, raw)
            if ret == methods.QUIT:
                return methods.QUIT
            if ret == methods.ERROR:
                return
            assert ret != methods.REWIND
            assert ret != methods.CONTINUE
            return fn(self, amp, opc, args, raw)
        return _method
    return _exit

def _in_block_visual(self):
    return self.co.get_region_type() == VISUAL_BLOCK

@_(methods.range_show_md5, methods.block_show_md5)
def _show_md5(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_show_sha1, methods.block_show_sha1)
def _show_sha1(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_show_sha224, methods.block_show_sha224)
def _show_sha224(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_show_sha256, methods.block_show_sha256)
def _show_sha256(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_show_sha384, methods.block_show_sha384)
def _show_sha384(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_show_sha512, methods.block_show_sha512)
def _show_sha512(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_show_blake2b, methods.block_show_blake2b)
def _show_blake2b(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_show_blake2s, methods.block_show_blake2s)
def _show_blake2s(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_show_sha3_224, methods.block_show_sha3_224)
def _show_sha3_224(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_show_sha3_256, methods.block_show_sha3_256)
def _show_sha3_256(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_show_sha3_384, methods.block_show_sha3_384)
def _show_sha3_384(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_show_sha3_512, methods.block_show_sha3_512)
def _show_sha3_512(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_inc_number, methods.block_inc_number)
def _inc_number(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_dec_number, methods.block_dec_number)
def _dec_number(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_toggle, methods.block_toggle)
def _toggle(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_rotate_right, methods.block_rotate_right)
def _rotate_right(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_rotate_left, methods.block_rotate_left)
def _rotate_left(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_swap_bytes, methods.block_swap_bytes)
def _swap_bytes(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_delete, methods.block_delete)
def _delete(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_logical_bit_operation, methods.block_logical_bit_operation)
def _logical_bit_operation(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_yank, methods.block_yank)
def _yank(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_put, methods.block_put)
def _put(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_save_buffer, methods.block_save_buffer)
def _save_buffer(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_force_save_buffer, methods.block_force_save_buffer)
def _force_save_buffer(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_save_buffer_quit, methods.block_save_buffer_quit)
def _save_buffer_quit(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_md5, methods.block_open_md5)
def _open_md5(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_sha1, methods.block_open_sha1)
def _open_sha1(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_sha224, methods.block_open_sha224)
def _open_sha224(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_sha256, methods.block_open_sha256)
def _open_sha256(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_sha384, methods.block_open_sha384)
def _open_sha384(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_sha512, methods.block_open_sha512)
def _open_sha512(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_blake2b, methods.block_open_blake2b)
def _open_blake2b(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_blake2s, methods.block_open_blake2s)
def _open_blake2s(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_sha3_224, methods.block_open_sha3_224)
def _open_sha3_224(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_sha3_256, methods.block_open_sha3_256)
def _open_sha3_256(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_sha3_384, methods.block_open_sha3_384)
def _open_sha3_384(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_sha3_512, methods.block_open_sha3_512)
def _open_sha3_512(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_base64_encode, methods.block_open_base64_encode)
def _open_base64_encode(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_base64_decode, methods.block_open_base64_decode)
def _open_base64_decode(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_base32_encode, methods.block_open_base32_encode)
def _open_base32_encode(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_base32_decode, methods.block_open_base32_decode)
def _open_base32_decode(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_base16_encode, methods.block_open_base16_encode)
def _open_base16_encode(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_base16_decode, methods.block_open_base16_decode)
def _open_base16_decode(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_base85_encode, methods.block_open_base85_encode)
def _open_base85_encode(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_open_base85_decode, methods.block_open_base85_decode)
def _open_base85_decode(self, amp, opc, args, raw):
    return _exit_visual(self)

@_(methods.range_delete, methods.block_delete)
def _enter_edit_replace(self, amp, opc, args, raw):
    self.co.cleanup_region()
    arg = edit.Arg(amp=methods.get_int(amp))
    return self.set_console(edit.get_replace_class(), arg)

def _do_edit_replace(self, amp, opc, args, raw):
    if _in_block_visual(self):
        cls = edit.get_block_replace_class()
    else:
        cls = edit.get_range_replace_class()
    arg = edit.Arg(limit=edit.get_input_limit(),
        start=self.co.get_region_range()[0])
    return self.set_console(cls, arg)

@_u(methods.range_delete, methods.block_delete)
def _delete_enter_edit_insert(self, amp, opc, args, raw):
    assert len(args), args
    und = args.pop()
    assert isinstance(und, int), und
    self.co.cleanup_region()
    amp = 1
    arg = edit.Arg(amp=methods.get_int(amp), merge_undo=und)
    return self.set_console(edit.get_insert_class(), arg)
