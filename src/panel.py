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

from . import filebytes
from . import log
from . import screen
from . import setting
from . import terminal
from . import util

# _panel
#     Frame
#         virtual.NullFrame
#         status.StatusFrame
#             status.NullStatusFrame
#     Canvas
#         virtual._canvas
#             virtual.BinaryCanvas
#             virtual.ExtCanvas
#         DisplayCanvas
#             BinaryCanvas
#                 edit.WriteBinaryCanvas
#                 visual.BinaryCanvas
#             TextCanvas
#                 visual.TextCanvas
#             extension.ExtBinaryCanvas
#                 visual.ExtBinaryCanvas
#             extension.ExtTextCanvas
#         status.StatusCanvas
#             status.VerboseStatusCanvas
#             status.SingleStatusCanvas

class _panel (object):
    def __init__(self, siz, pos):
        assert (siz and pos) or (not siz and not pos), (siz, pos)
        if not siz and not pos:
            siz = get_min_size(self)
            pos = get_min_position(self)
        self.scr = screen.alloc(siz[0], siz[1], pos[0], pos[1], self)
        self.__update()
        self.current = True

    def require_full_repaint(self):
        return

    def update(self):
        self.__update()

    def __update(self):
        self.__maxyx = self.scr.getmaxyx()
        self.__begyx = self.scr.getbegyx()

    def get_size_y(self):
        return self.__maxyx[0]

    def get_size_x(self):
        return self.__maxyx[1]

    def get_position_y(self):
        return self.__begyx[0]

    def get_position_x(self):
        return self.__begyx[1]

    def set_current(self, x):
        if x is None:
            return # no change
        assert isinstance(x, bool)
        self.current = x

    def fill(self, low):
        return

    def fill_partial(self, low, num):
        return

    def set_focus(self, *arg):
        self.set_current(arg[0])

    def repaint(self, *arg):
        self.set_current(arg[0])

    def repaint_partial(self, *arg):
        self.set_current(arg[0])

    def noutrefresh(self):
        self.scr.noutrefresh()

    def resize(self, siz, pos):
        if siz:
            self.scr.resize(*siz)
        if pos:
            self.scr.mvwin(*pos)
        self.update()

    def has_geom(self, y, x):
        pos_y = self.get_position_y()
        pos_x = self.get_position_x()
        siz_y = self.get_size_y()
        siz_x = self.get_size_x()
        return (pos_y <= y < pos_y + siz_y) and (pos_x <= x < pos_x + siz_x)

class Frame (_panel):
    def repaint(self, *arg):
        super(Frame, self).repaint(*arg)
        self.box()
        self.noutrefresh()

    def box(self):
        self.scr.box() # need refresh to make it appear

class _attribute (object):
    def get_cell(self):
        util.raise_no_impl("get_cell")

    def get_offset(self):
        util.raise_no_impl("get_offset")

    def get_bufmap(self, bytes_per_line):
        util.raise_no_impl("get_bufmap")

class default_attribute (_attribute):
    def get_cell(self):
        return 1, 0

    def get_offset(self):
        return 0, 0

    def get_bufmap(self, bytes_per_line):
        return self.get_size_y(), self.get_size_x()

class binary_attribute (_attribute):
    def get_cell(self):
        return 3, 1

    def get_offset(self):
        return 1, address_num_width + 1

    def get_bufmap(self, bytes_per_line):
        return self.get_size_y() - self.offset.y, bytes_per_line

class text_attribute (_attribute):
    def get_cell(self):
        return 1, 0

    def get_offset(self):
        return 1, 0

    def get_bufmap(self, bytes_per_line):
        return self.get_size_y() - self.offset.y, bytes_per_line

class Canvas (_panel):
    def __init__(self, siz, pos):
        super(Canvas, self).__init__(siz, pos)
        self.__update()
        self.fileops = None

    def require_full_repaint(self):
        self.need_full_repaint = True

    def update(self):
        super(Canvas, self).update()
        self.__update()

    def __update(self):
        l = list(self.get_cell()) # cell size, space within cell
        l.append(l[0] - l[1]) # [2]: non space within cell
        assert l[2] > 0, l
        self.cell = tuple(l)
        self.offset = util.Pair(*self.get_offset())
        self.bufmap = util.Pair() # need update_capacity()
        self.require_full_repaint()

    def set_buffer(self, fileops):
        self.fileops = fileops

    def get_capacity(self):
        return self.bufmap.y * self.bufmap.x

    def update_capacity(self, bytes_per_line):
        self.bufmap.set(*self.get_bufmap(bytes_per_line))

    def iter_line_buffer(self):
        yield 0, '', screen.A_NONE

    def get_str_single(self, x):
        return x # take str and return str (not bytes)

    def get_str_line(self, buf):
        return buf # take str and return str (not bytes)

    def fill_line(self, y, x, buf, attr, arg):
        self.addstr(y, x, self.get_str_line(buf), attr)

    def repaint(self, *arg):
        super(Canvas, self).repaint(*arg)
        low = arg[1]
        self.fill(low)
        self.noutrefresh()

    def repaint_partial(self, *arg):
        super(Canvas, self).repaint(*arg)
        low = arg[1]
        num = arg[2]
        self.fill_partial(low, num)
        self.noutrefresh()

    def resize(self, siz, pos):
        super(Canvas, self).resize(siz, pos)
        x = self.get_capacity()
        if setting.barrier_size < x:
            log.debug("Change default barrier size {0} -> {1}".format(
                setting.barrier_size, x))
            setting.barrier_size = x

    def chgat(self, y, x, num, attr=screen.A_NONE):
        try:
            # raise on minimizing terminal size (don't remove try/except)
            # may raise on page change for previous pos (???)
            self.scr.chgat(y, x, num, attr | screen.A_COLOR_FB)
        except screen.Error:
            if setting.use_debug:
                raise

    def addstr(self, y, x, s, attr=screen.A_NONE):
        # don't forget to sync with inlined version in __fill_line()
        try:
            # XXX Python 3 is too slow against Python 2.7 (2018-12-14)
            # Python 2.7
            # ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            # 938311    0.436    0.000    0.436    0.000 {built-in method addstr}
            # Python 3.7
            # ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            # 938311    0.978    0.000    0.978    0.000 {method 'addstr' of '_curses.window' objects}
            self.scr.addstr(y, x, s, attr | screen.A_COLOR_FB)
        except screen.Error as e:
            # warning (not error) unless write to lower right corner
            if not ((y == self.get_size_y() - 1) and
                (x + len(s) - 1 == self.get_size_x() - 1)):
                log.warning(self, e, (y, x), s)

    def clrl(self, y, x):
        try:
            # raise on minimizing terminal size (don't remove try/except)
            self.scr.move(y, x)
            self.scr.clrtoeol()
        except screen.Error:
            if setting.use_debug:
                raise

    def get_coordinate(self, pos):
        """Return coordinate of the position within the page"""
        r = pos % self.get_capacity()
        y = self.offset.y + r // self.bufmap.x
        x = self.offset.x + self.get_cell_width(r % self.bufmap.x)
        return y, x

    def get_page_offset(self):
        """Return offset of the current page"""
        pos = self.fileops.get_pos()
        return pos - pos % self.get_capacity()

    def get_next_page_offset(self):
        """Return offset of the next page"""
        return self.get_page_offset() + self.get_capacity()

    def is_page_changed(self):
        return not self.in_same_page(self.fileops.get_pos(),
            self.fileops.get_prev_pos())

    def in_same_page(self, pos1, pos2):
        """Return True if two positions are in the same page"""
        x = self.get_capacity()
        return pos1 // x == pos2 // x

    def get_line_offset(self, pos):
        """Return offset of the current line"""
        return pos - pos % self.bufmap.x

    def read_page(self):
        return self.fileops.read(self.get_page_offset(), self.get_capacity())

    def go_up(self, n):
        return self.sync_cursor()

    def go_down(self, n):
        return self.sync_cursor()

    def go_left(self, n):
        return self.sync_cursor()

    def go_right(self, n):
        return self.sync_cursor()

    def go_pprev(self, n):
        return self.sync_cursor()

    def go_hpprev(self, n):
        return self.sync_cursor()

    def go_pnext(self, n):
        return self.sync_cursor()

    def go_hpnext(self, n):
        return self.sync_cursor()

    def go_head(self, n):
        return self.sync_cursor()

    def go_tail(self, n):
        return self.sync_cursor()

    def go_lhead(self):
        return self.sync_cursor()

    def go_ltail(self, n):
        return self.sync_cursor()

    def go_phead(self, n):
        return self.sync_cursor()

    def go_pcenter(self):
        return self.sync_cursor()

    def go_ptail(self, n):
        return self.sync_cursor()

    def go_to(self, n):
        return self.sync_cursor()

    def sync_cursor(self):
        return

    def get_geom_pos(self, y, x):
        return -1

class DisplayCanvas (Canvas):
    def __init__(self, siz, pos):
        super(DisplayCanvas, self).__init__(siz, pos)
        if screen.use_alt_chgat():
            self.chgat_posstr = self.alt_chgat_posstr
            self.chgat_cursor = self.alt_chgat_cursor
            self.chgat_search = self.alt_chgat_search
        self.attr_posstr = screen.A_BOLD
        self.attr_search = screen.A_BOLD
        self.attr_visual = screen.A_COLOR_VISUAL
        if setting.has_buffer_attr():
            self.fill_line = self.__fill_line
        self.__update()

    def update(self):
        super(DisplayCanvas, self).update()
        self.__update()

    def __update(self):
        self.__unit_width = self.cell[2] * setting.bytes_per_unit + self.cell[1]

    def update_capacity(self, bytes_per_line):
        super(DisplayCanvas, self).update_capacity(bytes_per_line)
        # precalculate after bufmap update
        self.default_units_per_line = self.get_units_per_line(self.bufmap.x)

    def get_units_per_line(self, xlen):
        unitlen = setting.bytes_per_unit
        upl = xlen // unitlen
        xpu = [unitlen] * upl
        r = xlen % unitlen
        if r:
            upl += 1
            xpu.append(r)
        # upl: units per line
        # xpu: buffer size for each unit (last entry may be smaller than bpu)
        return upl, xpu

    def set_focus(self, *arg):
        super(DisplayCanvas, self).set_focus(*arg)
        self.update_highlight(False, True)
        self.noutrefresh()

    # cell distance from beg to end (end inclusive)
    def get_cell_distance(self, beg, end):
        assert end >= beg, (beg, end)
        n = end - beg + 1
        d = (end // setting.bytes_per_unit) - (beg // setting.bytes_per_unit)
        return self.cell[2] * n + self.cell[1] * d

    # e.g. when unit size is 2
    # <>                    x=1
    # <--->                 x=2
    # 0000 0000 0000 0000...
    def get_cell_width(self, x):
        q = x // setting.bytes_per_unit
        return self.cell[2] * x + self.cell[1] * q

    # e.g. when unit size is 2
    # <>                    x=1
    # <-->                  x=2
    # 0000 0000 0000 0000...
    def get_cell_edge(self, x):
        r = 0 if x % setting.bytes_per_unit else 1
        return self.get_cell_width(x) - self.cell[1] * r

    # e.g. when unit size is 2
    # <--->                 x=1
    # <-------->            x=2
    # 0000 0000 0000 0000...
    def get_unit_width(self, x):
        # don't forget to sync with inlined version in __fill_line()
        return self.__unit_width * x

    # e.g. when unit size is 2
    # <-->                  x=1
    # <------->             x=2
    # 0000 0000 0000 0000...
    def get_unit_edge(self, x):
        return self.get_unit_width(x) - self.cell[1]

    # only used by alt chgat
    def read_form_single(self, pos):
        b = self.fileops.read(pos, 1)
        if b:
            return self.get_str_single(filebytes.ord(b))
        else:
            return ' ' * self.cell[2]

    # DisplayCanvas and derived classes must yield bytes (not str),
    # as fill_line() assumes bytes.
    def iter_line_buffer(self):
        b = self.read_page()
        n = 0
        for i in util.get_xrange(self.bufmap.y):
            yield i, b[n : n + self.bufmap.x], screen.A_NONE
            n += self.bufmap.x

    def __fill_pre(self):
        # erase if needed
        # XXX self.clrl() via super's fill() may not work against consecutive
        # lines in final page with some terminals, so clear the screen.
        if self.need_full_repaint:
            self.scr.erase()
        elif _clear_on_fill and \
            self.fileops.get_max_pos() < self.get_next_page_offset():
            self.scr.clear() # not scr.erase()
        # fill posstr if needed
        if self.need_full_repaint or self.is_page_changed():
            self.fill_posstr()

    def __fill_post(self, low):
        self.update_highlight(low, False)
        self.need_full_repaint = False # done in this fill if any

    def fill(self, low):
        self.__fill_pre()
        super(Canvas, self).fill(low)
        x = self.offset.x
        for i, b, a in self.iter_line_buffer():
            y = self.offset.y + i
            if len(b) == self.bufmap.x:
                self.fill_line(y, x, b, a, self.default_units_per_line)
            else:
                self.clrl(y, x)
                if b:
                    self.fill_line(y, x, b, a, self.get_units_per_line(len(b)))
        self.__fill_post(low)

    def fill_partial(self, low, num):
        self.__fill_pre()
        super(Canvas, self).fill_partial(low, num)
        if num == -1:
            num = 1
        pos = self.fileops.get_pos()
        loff = self.get_page_offset()
        lbeg = self.get_line_offset(pos) - self.bufmap.x # one above current
        lend = self.get_line_offset(pos + num - 1)
        x = self.offset.x
        for i, b, a in self.iter_line_buffer():
            if not (lbeg <= loff <= lend):
                loff += self.bufmap.x
                continue
            y = self.offset.y + i
            if len(b) == self.bufmap.x:
                self.fill_line(y, x, b, a, self.default_units_per_line)
            else:
                self.clrl(y, x)
                if b:
                    self.fill_line(y, x, b, a, self.get_units_per_line(len(b)))
            loff += self.bufmap.x
        self.__fill_post(low)

    def fill_line_nth(self, y, x, buf, nth_in_line, attr):
        # fill in unaligned bytes first
        unitlen = setting.bytes_per_unit
        if nth_in_line:
            r = nth_in_line % unitlen
            if r:
                n = unitlen - r
                b = buf[:n]
                buf = buf[n:]
                for _ in filebytes.iter_ords(b):
                    c = self.get_str_single(_)
                    a = attr | screen.buf_attr[_]
                    self.addstr(y, x, c, a)
                    x += len(c)
                x += self.cell[1]
        self.fill_line(y, x, buf, attr, self.get_units_per_line(len(buf)))
        return x # for visual

    # most cpu cycles on repaint are consumed in here
    def __fill_line(self, y, x, buf, attr, arg):
        upl, xpu = arg
        # normally use filebytes.ords(), but this is exception for speed
        if not _bytes_is_int:
            buf = filebytes.ords(buf)
        # precalculate before going into the loop
        c = [self.get_str_single(_) for _ in buf]
        a = [(attr | screen.buf_attr[_] | screen.A_COLOR_FB) for _ in buf]
        # start to fill line
        unitlen = setting.bytes_per_unit
        j = 0
        for i in _xrange(upl):
            # normally use get_unit_width(), but this is exception for speed
            pos = x + self.__unit_width * i
            for k in _xrange(xpu[i]):
                _ = c[j + k]
                xx = pos + len(_) * k
                # normally use Canvas.addstr(), but this is exception for speed
                try:
                    self.scr.addstr(y, xx, _, a[j + k])
                except screen.Error as e:
                    # warning (not error) unless write to lower right corner
                    if not ((y == self.get_size_y() - 1) and
                        (xx + len(_) - 1 == self.get_size_x() - 1)):
                        log.warning(self, e, (y, xx), _)
            j += unitlen

    def update_highlight(self, low, range_update):
        pos = self.fileops.get_pos()
        ppos = self.fileops.get_prev_pos()
        # update previous position first
        self.chgat_posstr(ppos, screen.A_NONE)
        if self.in_same_page(pos, ppos):
            if ppos <= self.fileops.get_max_pos(): # may be invalid after delete
                b = self.fileops.read(ppos, 1)
                attr = screen.buf_attr[filebytes.ord(b)] if b else screen.A_NONE
                self.chgat_cursor(ppos, attr, attr, low)
            else:
                self.chgat_cursor(ppos, screen.A_NONE, screen.A_NONE, low)
        # update search strings before update current position
        if not self.in_same_page(pos, ppos):
            ppos = self.get_page_offset()
        if range_update:
            d = self.range_update_search(pos, ppos, pos)
        else:
            d = self.page_update_search(self.fileops.get_pos())
        # update current position
        attr = screen.A_COLOR_CURRENT if self.current else screen.A_STANDOUT
        if d != -1 and pos in d:
            l = d[pos] # synthesize attrs from search strings
        else:
            l = screen.A_NONE, screen.A_NONE
        self.chgat_posstr(pos, self.attr_posstr)
        self.chgat_cursor(pos, attr | l[0], attr | l[1], low)

    def sync_cursor(self):
        if not self.is_page_changed():
            self.update_highlight(False, True)
            self.noutrefresh()
        else:
            return -1 # need repaint

    def get_geom_pos(self, y, x):
        if not self.has_geom(y, x):
            return -1
        offset_y = self.get_position_y() + self.offset.y
        offset_x = self.get_position_x() + self.offset.x
        if y < offset_y or x < offset_x:
            return -1
        page_pos = 0
        if y > offset_y:
            page_pos += (y - offset_y) * self.bufmap.x
        # XXX do this in O(1)
        line_pos = -1
        for _ in util.get_xrange(1, self.bufmap.x + 1):
            # keep the first x number whose cell width exceeds x distance
            if self.get_cell_width(_) - 1 >= x - offset_x:
                line_pos = _ - 1
                break
        assert line_pos != -1, line_pos
        page_pos += line_pos
        pos = self.get_page_offset() + page_pos
        if pos > self.fileops.get_max_pos():
            pos = self.fileops.get_max_pos()
        return pos

    def chgat_posstr(self, pos, attr):
        return

    def alt_chgat_posstr(self, pos, attr):
        return

    def chgat_cursor(self, pos, attr1, attr2, low):
        return

    def alt_chgat_cursor(self, pos, attr1, attr2, low):
        return

    def chgat_search(self, pos, attr1, attr2, here):
        return

    def alt_chgat_search(self, pos, attr1, attr2, here):
        return

    def fill_posstr(self):
        return

    def page_update_search(self, pos):
        s = self.fileops.get_search_word()
        if not s:
            return -1
        beg = self.get_page_offset()
        end = self.get_next_page_offset()
        return self.__update_search(pos, beg, end, s)

    def range_update_search(self, pos, beg, end):
        s = self.fileops.get_search_word()
        if not s:
            return -1
        if beg > end:
            beg, end = end, beg
        beg -= (len(s) - 1)
        end += len(s)
        return self.__update_search(pos, beg, end, s)

    def __update_search(self, pos, beg, end, s):
        if beg < 0:
            beg = 0
        d = {}
        b = self.fileops.read(beg, end - beg) # end not inclusive
        if not b:
            return d
        found = 0
        while True:
            found = util.find_string(b, s, found)
            if found == -1:
                break
            i = beg + found
            if i < beg or i >= end:
                break
            for j, _ in enumerate(filebytes.iter_ords(s)):
                x = i + j
                d[x] = self.update_search(x, screen.buf_attr[_], x == pos)
            found += 1
        return d # XXX refactor

    def update_search(self, pos, attr_bytes, here):
        if here and self.current:
            attr1 = self.attr_search | screen.A_COLOR_CURRENT
            attr2 = attr1
        else:
            attr1 = self.attr_search
            attr2 = self.attr_search | attr_bytes
        self.chgat_search(pos, attr1, attr2, here)
        return attr1, attr2

def _get_binary_str_single():
    d = {}
    for x in util.get_xrange(0, 256):
        d[x] = "{0:02X}".format(x)
    return d

_binary_str_single = _get_binary_str_single()
_binary_cstr_fmt = {
    16: "{0:02X}",
    10: "{0:02d}",
    8 : "{0:02o}", }

class BinaryCanvas (DisplayCanvas, binary_attribute):
    def __init__(self, siz, pos):
        super(BinaryCanvas, self).__init__(siz, pos)
        self.__update()

    def update(self):
        super(BinaryCanvas, self).update()
        self.__update()

    def __update(self):
        lstr_fmt = {
            16: ":0{0}X".format(address_num_width),
            10: ":{0}d".format(address_num_width),
            8 : ":0{0}o".format(address_num_width), }
        self.__lstr = {
            16: "{{0{0}}}".format(lstr_fmt[16]),
            10: "{{0{0}}}".format(lstr_fmt[10]),
            8: "{{0{0}}}".format(lstr_fmt[8]), }
        self.__lstr_single = self.__lstr
        if address_num_double:
            self.offset.x += (1 + address_num_width) # oooo|oooo
            self.__lstr = {
                16: "{{0{0}}}|{{1{0}}}".format(lstr_fmt[16]),
                10: "{{0{0}}}|{{1{0}}}".format(lstr_fmt[10]),
                8: "{{0{0}}}|{{1{0}}}".format(lstr_fmt[8]), }

    def get_str_single(self, x):
        return _binary_str_single[x] # x is from ord()

    def get_str_line(self, buf):
        if len(buf) == self.bufmap.x:
            upl, xpu = self.default_units_per_line
        else:
            upl, xpu = self.get_units_per_line(len(buf))
        # normally use filebytes.ords(), but this is exception for speed
        if not _bytes_is_int:
            buf = filebytes.ords(buf)
        # start to construct line string
        unitlen = setting.bytes_per_unit
        extra = ' ' * self.cell[1]
        ret = []
        j = 0
        for i in _xrange(upl):
            b = buf[j : j + unitlen]
            s = ''.join([self.get_str_single(_) for _ in b])
            ret.append(s)
            if i != upl - 1:
                ret.append(extra)
            j += unitlen
        return ''.join(ret)

    def chgat_posstr(self, pos, attr):
        y, x = self.get_coordinate(pos)
        self.chgat(0, x, self.get_cell_edge(1), A_UNDERLINE | attr)
        self.chgat(y, 0, self.offset.x - 1, A_UNDERLINE | attr)

    def alt_chgat_posstr(self, pos, attr):
        y, x = self.get_coordinate(pos)
        d = pos % self.bufmap.x
        self.addstr(0, x,
            self.__get_column_posstr(d), A_UNDERLINE | attr)
        s = self.__get_line_posstr(self.get_line_offset(pos))[:-1]
        self.addstr(y, 0, s, A_UNDERLINE | attr)

    def chgat_cursor(self, pos, attr1, attr2, low):
        y, x = self.get_coordinate(pos)
        if low:
            self.chgat(y, x, 1, attr2)
            self.chgat(y, x + 1, 1, attr1)
        else:
            self.chgat(y, x, 1, attr1)
            self.chgat(y, x + 1, 1, attr2)

    def alt_chgat_cursor(self, pos, attr1, attr2, low):
        y, x = self.get_coordinate(pos)
        s = self.read_form_single(pos)
        if low:
            self.addstr(y, x, s[0], attr2)
            self.addstr(y, x + 1, s[1], attr1)
        else:
            self.addstr(y, x, s[0], attr1)
            self.addstr(y, x + 1, s[1], attr2)

    def chgat_search(self, pos, attr1, attr2, here):
        y, x = self.get_coordinate(pos)
        if here:
            self.chgat(y, x, 1, attr1)
            self.chgat(y, x + 1, 1, attr2)
        else:
            self.chgat(y, x, 2, attr2)

    def alt_chgat_search(self, pos, attr1, attr2, here):
        y, x = self.get_coordinate(pos)
        s = self.read_form_single(pos)
        if here:
            self.addstr(y, x, s[0], attr1)
            self.addstr(y, x + 1, s[1], attr2)
        else:
            self.addstr(y, x, s, attr2)

    def fill_posstr(self):
        self.addstr(0, 0, ' ' * self.offset.x) # blank part
        unitlen = setting.bytes_per_unit
        upl, xpu = self.default_units_per_line
        j = 0
        for i in util.get_xrange(upl):
            x = self.offset.x + self.get_unit_width(i)
            bx = ''.join([self.__get_column_posstr(_) for _ in
                util.get_xrange(j, j + unitlen)])
            self.addstr(0, x, bx, A_UNDERLINE)
            j += unitlen
        n = self.get_page_offset()
        for i in util.get_xrange(self.bufmap.y):
            s = self.__get_line_posstr(n)
            self.addstr(self.offset.y + i, 0, s, A_UNDERLINE)
            self.addstr(self.offset.y + i, len(s), ' ')
            n += self.bufmap.x

    def __get_column_posstr(self, n):
        return _binary_cstr_fmt[setting.address_radix].format(n)

    def __get_line_posstr(self, n):
        fmt = self.__lstr[setting.address_radix]
        offset = self.fileops.get_mapping_offset()
        if not address_num_double:
            s = fmt.format(n)
        elif not offset: # other buffer(s) need double space
            fmt_single = self.__lstr_single[setting.address_radix]
            s = "{0} {1}".format(' ' * address_num_width, fmt_single.format(n))
        else:
            s = fmt.format(n + offset, n)
        return s[-(self.offset.x - 1):]

_text_cstr_fmt = {
    16: "{0:X}",
    10: "{0:d}",
    8 : "{0:o}", }

class TextCanvas (DisplayCanvas, text_attribute):
    def get_str_single(self, x):
        return screen.chr_repr[x] # x is from ord()

    def get_str_line(self, buf):
        # normally use filebytes.ords(), but this is exception for speed
        if not _bytes_is_int:
            buf = filebytes.ords(buf)
        return ''.join([self.get_str_single(x) for x in buf])

    def chgat_posstr(self, pos, attr):
        x = pos % self.bufmap.x
        self.chgat(0, self.offset.x + self.get_cell_width(x),
            self.get_cell_edge(1), A_UNDERLINE | attr)

    def alt_chgat_posstr(self, pos, attr):
        x = pos % self.bufmap.x
        self.addstr(0, self.offset.x + self.get_cell_width(x),
            self.__get_column_posstr(x), A_UNDERLINE | attr)

    def chgat_cursor(self, pos, attr1, attr2, low):
        y, x = self.get_coordinate(pos)
        self.chgat(y, x, 1, attr1)

    def alt_chgat_cursor(self, pos, attr1, attr2, low):
        y, x = self.get_coordinate(pos)
        s = self.read_form_single(pos)
        self.addstr(y, x, s, attr1)

    def chgat_search(self, pos, attr1, attr2, here):
        y, x = self.get_coordinate(pos)
        if here:
            self.chgat(y, x, 1, attr1)
        else:
            self.chgat(y, x, 1, attr2)

    def alt_chgat_search(self, pos, attr1, attr2, here):
        y, x = self.get_coordinate(pos)
        s = self.read_form_single(pos)
        if here:
            self.addstr(y, x, s, attr1)
        else:
            self.addstr(y, x, s, attr2)

    def fill_posstr(self):
        s = ''.join([self.__get_column_posstr(x) for x in
            util.get_xrange(self.bufmap.x)])
        self.addstr(0, self.offset.x, s, A_UNDERLINE)

    def __get_column_posstr(self, n):
        return _text_cstr_fmt[setting.address_radix].format(n)[-1]

_clear_on_fill = terminal.in_tmux_tmux() and not terminal.is_screen()
_bytes_is_int = util.is_python3()
_xrange = util.get_xrange

def get_min_address_num_width():
    return 4 # 65536 bytes buffer

# needs to be per workspace for vertical split to support different width
address_num_width = get_min_address_num_width()
address_num_double = False

_MIN_SIZE_Y = 1
_MIN_SIZE_X = 1
_FRAME_MARGIN_Y = 1
_FRAME_MARGIN_X = 1

def get_min_size(cls):
    if not util.is_class(cls):
        cls = util.get_class(cls)
    if util.is_subclass(cls, Frame):
        y = _MIN_SIZE_Y + _FRAME_MARGIN_Y * 2
        x = _MIN_SIZE_X + _FRAME_MARGIN_X * 2
    elif util.is_subclass(cls, Canvas):
        y = _MIN_SIZE_Y
        x = _MIN_SIZE_X
    else:
        assert False, cls
    from . import status
    if not setting.use_status_window_frame and \
        util.is_subclass(cls, status.StatusFrame):
        y -= _FRAME_MARGIN_Y * 2
        x -= _FRAME_MARGIN_X * 2
    return y, x

def get_min_position(cls):
    if not util.is_class(cls):
        cls = util.get_class(cls)
    if util.is_subclass(cls, Frame):
        y = 0
        x = 0
    elif util.is_subclass(cls, Canvas):
        y = _FRAME_MARGIN_Y
        x = _FRAME_MARGIN_X
    else:
        assert False, cls
    from . import status
    if not setting.use_status_window_frame and \
        util.is_subclass(cls, status.StatusCanvas):
        y -= _FRAME_MARGIN_Y
        x -= _FRAME_MARGIN_X
    return y, x

A_UNDERLINE = None
def init():
    global A_UNDERLINE
    assert screen.A_UNDERLINE is not None
    assert screen.A_COLOR_OFFSET is not None
    if screen.A_COLOR_OFFSET != screen.A_NONE or \
        screen.A_UNDERLINE == screen.A_NONE:
        A_UNDERLINE = screen.A_COLOR_OFFSET
    else:
        A_UNDERLINE = screen.A_UNDERLINE
    assert A_UNDERLINE is not None
