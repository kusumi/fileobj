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

from . import ascii
from . import filebytes
from . import kbd
from . import kernel
from . import log
from . import native
from . import screen
from . import setting
from . import util
from . import version

# _panel
#     Frame
#         virtual.NullFrame
#         StatusFrame
#             NullStatusFrame
#     Canvas
#         virtual._canvas
#             virtual.BinaryCanvas
#             virtual.ExtCanvas
#         DisplayCanvas
#             BinaryCanvas
#                 visual.BinaryCanvas
#             TextCanvas
#                 visual.TextCanvas
#             extension.ExtBinaryCanvas
#                 visual.ExtBinaryCanvas
#             extension.ExtTextCanvas
#         StatusCanvas
#             VerboseStatusCanvas
#             SingleStatusCanvas

class _panel (object):
    def __init__(self, siz, pos):
        assert (siz and pos) or (not siz and not pos), (siz, pos)
        if not siz and not pos:
            siz = get_min_size(self)
            pos = get_min_position(self)
        self.scr = screen.alloc(siz[0], siz[1], pos[0], pos[1], self)
        self.current = True

    def update(self):
        return

    def get_size_y(self):
        return self.scr.getmaxyx()[0]

    def get_size_x(self):
        return self.scr.getmaxyx()[1]

    def get_position_y(self):
        return self.scr.getbegyx()[0]

    def get_position_x(self):
        return self.scr.getbegyx()[1]

    def set_current(self, current):
        if isinstance(current, bool): # could be None
            self.current = current

    def fill(self, low):
        return

    def crepaint(self, *arg):
        current = arg[0]
        self.set_current(current)

    def repaint(self, *arg):
        current = arg[0]
        self.set_current(current)

    def refresh(self):
        self.scr.refresh()

    def resize(self, siz, pos):
        if siz:
            self.scr.resize(*siz)
        if pos:
            self.scr.mvwin(*pos)

class Frame (_panel):
    def repaint(self, *arg):
        super(Frame, self).repaint(*arg)
        self.box()
        self.refresh()

    def box(self):
        self.scr.box() # need refresh to make it appear

class StatusFrame (Frame):
    pass

class NullStatusFrame (StatusFrame):
    def box(self):
        return

class default_addon (object):
    def get_cell(self):
        return 1, 0

    def get_offset(self):
        return 0, 0

    def get_bufmap(self, bytes_per_line):
        return self.get_size_y(), self.get_size_x()

class binary_addon (object):
    def get_cell(self):
        return 3, 1

    def get_offset(self):
        return 1, address_num_width + 1

    def get_bufmap(self, bytes_per_line):
        return self.get_size_y() - self.offset.y, bytes_per_line

class text_addon (object):
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

    def update(self):
        super(Canvas, self).update()
        self.__update()

    def __update(self):
        self.cell = self.get_cell() # size, distance
        self.offset = util.Pair(*self.get_offset())
        self.bufmap = util.Pair()

    def set_buffer(self, fileops):
        self.fileops = fileops

    def get_capacity(self):
        return self.bufmap.y * self.bufmap.x

    def update_capacity(self, bytes_per_line):
        self.bufmap.set(*self.get_bufmap(bytes_per_line))

    def iter_buffer(self):
        yield 0, '', screen.A_NONE

    def get_form_single(self, x):
        return x # must be str (not bytes)

    def get_form_line(self, buf):
        return buf # must be str (not bytes)

    def read_form_single(self, pos):
        c = self.fileops.read(pos, 1)
        if c:
            return self.get_form_single(c)
        else:
            d = self.cell[0] - self.cell[1]
            return ' ' * d

    def get_cell_width(self, x):
        return self.cell[0] * x

    def get_cell_edge(self, x):
        return self.get_cell_width(x) - self.cell[1]

    def fill(self, low):
        super(Canvas, self).fill(low)
        x = self.offset.x
        for i, b, a in self.iter_buffer(): # b could be str or bytes
            y = self.offset.y + i
            if len(b) < self.bufmap.x:
                self.clrl(y, x)
            if b:
                self.fill_line(y, x, b, a)

    def fill_line(self, y, x, buf, attr):
        self.printl(y, x, self.get_form_line(buf), attr)

    def repaint(self, *arg):
        super(Canvas, self).repaint(*arg)
        low = arg[1]
        self.fill(low)
        self.refresh()

    def resize(self, siz, pos):
        super(Canvas, self).resize(siz, pos)
        x = self.get_capacity()
        if setting.barrier_size < x:
            log.debug("Change default barrier size {0} -> {1}".format(
                setting.barrier_size, x))
            setting.barrier_size = x

    def chgat(self, y, x, num, attr=screen.A_NONE):
        try:
            # may raise on page change for previous pos
            self.scr.chgat(y, x, num, attr | screen.A_COLOR)
        except Exception:
            pass # log this as error ?

    def printl(self, y, x, s, attr=screen.A_NONE):
        try:
            self.scr.addstr(y, x, s, attr | screen.A_COLOR)
        except Exception as e:
            if (y < self.get_size_y() - 1) or \
                (x + len(s) < self.get_size_x() - 1):
                log.error(e, (y, x), s)

    def clrl(self, y, x):
        try:
            self.scr.move(y, x)
            self.scr.clrtoeol()
        except Exception as e:
            log.error(e)

    def get_coordinate(self, pos):
        """Return coordinate of the position within the page"""
        r = pos - self.get_page_offset()
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

class DisplayCanvas (Canvas):
    def __init__(self, siz, pos):
        super(DisplayCanvas, self).__init__(siz, pos)
        if screen.use_alt_chgat():
            self.chgat_posstr = self.alt_chgat_posstr
            self.chgat_cursor = self.alt_chgat_cursor
            self.chgat_search = self.alt_chgat_search
        self.attr_posstr = screen.parse_attr(screen.A_BOLD)
        self.attr_cursor = screen.parse_attr(screen.A_STANDOUT)
        self.attr_search = screen.parse_attr(screen.A_BOLD)
        self.attr_visual = screen.parse_attr(screen.A_STANDOUT)
        self.__zlc = 0 # zero line count heuristic

    def crepaint(self, *arg):
        super(DisplayCanvas, self).crepaint(*arg)
        self.update_highlight()

    def iter_buffer(self):
        b = self.read_page()
        n = 0
        for i in range(self.bufmap.y):
            yield i, b[n : n + self.bufmap.x], screen.A_NONE
            n += self.bufmap.x

    def fill(self, low):
        # XXX with vt2xx, self.clrl() via super's fill() may not work against
        # consecutive lines in the final page, so clear the entire screen.
        if kernel.is_vt2xx() and \
            self.fileops.get_max_pos() < self.get_next_page_offset():
            self.scr.clear()
        self.fill_posstr()
        super(DisplayCanvas, self).fill(low)
        # update current position
        self.__update_highlight_current(low)
        # update search strings
        self.update_search(self.fileops.get_pos())

    def fill_line(self, y, x, buf, attr=screen.A_NONE):
        if screen.A_COLOR_ZERO == screen.A_NONE:
            super(DisplayCanvas, self).fill_line(y, x, buf, attr)
            return
        if self.__zlc > 5:
            if self.__try_fill_line_zero(y, x, buf, attr) != -1:
                return
        z = 0
        extra = ' ' * self.cell[1]
        for i, b in enumerate(filebytes.iter(buf)):
            if self.test_zero_buffer(b):
                a = attr | screen.A_COLOR_ZERO
                z += 1
            else:
                a = attr
            pos = x + self.get_cell_width(i)
            if setting.use_debug:
                assert pos <= self.offset.x + \
                    self.get_cell_width(self.bufmap.x - 1)
            self.printl(y, pos, self.get_form_single(b), a)
            # clear blank part within cell (XXX need this ?)
            pos = x + self.get_cell_width(i + 1) - len(extra)
            if setting.use_debug:
                assert pos <= self.offset.x + \
                    self.get_cell_width(self.bufmap.x)
            if pos < self.get_size_x():
                self.printl(y, pos, extra)
        if len(buf) == z:
            self.__zlc += 1

    def __try_fill_line_zero(self, y, x, buf, attr):
        if buf == len(buf) * filebytes.ZERO:
            super(DisplayCanvas, self).fill_line(y, x, buf, attr |
                screen.A_COLOR_ZERO)
            self.__zlc += 1
        else:
            self.__zlc = 0
            return -1

    def update_highlight(self):
        # update previous position first
        ppos = self.fileops.get_prev_pos()
        attr = screen.A_COLOR_ZERO if self.test_zero_at(ppos) else screen.A_NONE
        self.chgat_posstr(ppos, screen.A_NONE)
        self.chgat_cursor(ppos, attr, attr, False)
        # update current position
        self.__update_highlight_current(False)
        # update search strings
        pos = self.fileops.get_pos()
        self.range_update_search(pos, ppos, pos)
        self.refresh()

    def __update_highlight_current(self, low):
        pos = self.fileops.get_pos()
        attr1 = screen.A_COLOR_CURRENT if self.current else screen.A_NONE
        attr2 = screen.A_COLOR_ZERO if self.test_zero_at(pos) else screen.A_NONE
        self.chgat_posstr(pos, self.attr_posstr)
        self.chgat_cursor(pos, self.attr_cursor | attr1, attr2, low)

    def sync_cursor(self):
        if self.in_same_page(self.fileops.get_pos(),
            self.fileops.get_prev_pos()):
            self.update_highlight()
        else:
            return -1 # need repaint

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

    def test_zero_buffer(self, b):
        if screen.A_COLOR_ZERO == screen.A_NONE:
            return False
        assert len(b) == 1, b
        return b == filebytes.ZERO

    def test_zero_at(self, pos):
        if screen.A_COLOR_ZERO == screen.A_NONE:
            return False
        return self.fileops.read(pos, 1) == filebytes.ZERO

    def update_search(self, pos):
        s = self.fileops.get_search_word()
        if not s:
            return -1
        beg = self.get_page_offset()
        end = self.get_next_page_offset()
        self.__update_search(pos, beg, end, s)

    def range_update_search(self, pos, beg, end):
        s = self.fileops.get_search_word()
        if not s:
            return -1
        if beg > end:
            beg, end = end, beg
        beg -= (len(s) - 1)
        end += len(s)
        self.__update_search(pos, beg, end, s)

    def __update_search(self, pos, beg, end, s):
        attr_cursor = self.attr_search | self.attr_cursor
        for i in self.__iter_search_word(beg, end, s):
            for j in range(len(s)):
                x = i + j
                here = (x == pos)
                if here and self.current:
                    attr_cursor |= screen.A_COLOR_CURRENT
                self.chgat_search(x, attr_cursor, self.attr_search, here)

    def __iter_search_word(self, beg, end, s):
        if beg < 0:
            beg = 0
        b = self.fileops.read(beg, end - beg) # end not inclusive
        i = 0
        while True:
            i = util.find_string(b, s, i)
            if i == -1:
                break
            pos = beg + i
            if pos < beg or pos >= end:
                break
            yield pos
            i += 1

class BinaryCanvas (DisplayCanvas, binary_addon):
    def __init__(self, siz, pos):
        super(BinaryCanvas, self).__init__(siz, pos)
        self.__update()

    def update(self):
        super(BinaryCanvas, self).update()
        self.__update()

    def __update(self):
        self.__cstr = {
            16: "{0:02X}",
            10: "{0:02d}",
            8 : "{0:02o}", }
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

    def get_form_single(self, x):
        return "{0:02X}".format(filebytes.ord(x) & 0xFF)

    def get_form_line(self, buf):
        return ' '.join([self.get_form_single(x) for x in filebytes.iter(buf)])

    def chgat_posstr(self, pos, attr):
        y, x = self.get_coordinate(pos)
        d = pos % self.bufmap.x
        self.chgat(0, self.offset.x + self.get_cell_width(d),
            self.get_cell_edge(1), screen.A_UNDERLINE | attr)
        self.chgat(y, 0, self.offset.x - 1, screen.A_UNDERLINE | attr)

    def alt_chgat_posstr(self, pos, attr):
        y, x = self.get_coordinate(pos)
        d = pos % self.bufmap.x
        self.printl(0, self.offset.x + self.get_cell_width(d),
            self.__get_column_posstr(d), screen.A_UNDERLINE | attr)
        s = self.__get_line_posstr(self.get_line_offset(pos))[:-1]
        self.printl(y, 0, s, screen.A_UNDERLINE | attr)

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
            self.printl(y, x, s[0], attr2)
            self.printl(y, x + 1, s[1], attr1)
        else:
            self.printl(y, x, s[0], attr1)
            self.printl(y, x + 1, s[1], attr2)

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
            self.printl(y, x, s[0], attr1)
            self.printl(y, x + 1, s[1], attr2)
        else:
            self.printl(y, x, s, attr2)

    def fill_posstr(self):
        self.printl(0, 0, ' ' * self.offset.x) # blank part
        extra = ' ' * self.cell[1]
        for i in range(self.bufmap.x):
            x = self.offset.x + self.get_cell_width(i)
            self.printl(0, x, self.__get_column_posstr(i), screen.A_UNDERLINE)
            # need to clear blank part within cell
            x = self.offset.x + self.get_cell_width(i + 1) - len(extra)
            if x < self.get_size_x():
                self.printl(0, x, extra)

        n = self.get_page_offset()
        for i in range(self.bufmap.y):
            s = self.__get_line_posstr(n)
            self.printl(self.offset.y + i, 0, s, screen.A_UNDERLINE)
            self.printl(self.offset.y + i, len(s), ' ')
            n += self.bufmap.x

    def __get_column_posstr(self, n):
        return self.__cstr[setting.address_radix].format(n)

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

class TextCanvas (DisplayCanvas, text_addon):
    def __init__(self, siz, pos):
        super(TextCanvas, self).__init__(siz, pos)
        self.__cstr = {
            16: "{0:X}",
            10: "{0:d}",
            8 : "{0:o}", }

    def get_form_single(self, x):
        return kbd.to_chr_repr(util.bytes_to_str(x))

    def get_form_line(self, buf):
        return ''.join([self.get_form_single(x) for x in filebytes.iter(buf)])

    def chgat_posstr(self, pos, attr):
        x = pos % self.bufmap.x
        self.chgat(0, self.offset.x + self.get_cell_width(x),
            self.get_cell_edge(1), screen.A_UNDERLINE | attr)

    def alt_chgat_posstr(self, pos, attr):
        x = pos % self.bufmap.x
        self.printl(0, self.offset.x + self.get_cell_width(x),
            self.__get_column_posstr(x), screen.A_UNDERLINE | attr)

    def chgat_cursor(self, pos, attr1, attr2, low):
        y, x = self.get_coordinate(pos)
        self.chgat(y, x, 1, attr1)

    def alt_chgat_cursor(self, pos, attr1, attr2, low):
        y, x = self.get_coordinate(pos)
        s = self.read_form_single(pos)
        self.printl(y, x, s, attr1)

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
            self.printl(y, x, s, attr1)
        else:
            self.printl(y, x, s, attr2)

    def fill_posstr(self):
        s = ''.join([self.__get_column_posstr(x) for x in range(self.bufmap.x)])
        self.printl(0, self.offset.x, s, screen.A_UNDERLINE)

    def __get_column_posstr(self, n):
        return self.__cstr[setting.address_radix].format(n)[-1]

class StatusCanvas (Canvas, default_addon):
    def __init__(self, siz, pos):
        super(StatusCanvas, self).__init__(siz, pos)
        self.__attr_current_status = screen.parse_attr(screen.A_STANDOUT) | \
            screen.A_COLOR_CURRENT
        self.__update()

    def update(self):
        super(StatusCanvas, self).update()
        self.__update()

    def __update(self):
        self.__nstr = {
            16: "0x{0:X}",
            10: "{0:d}",
            8 : "0{0:o}", }
        self.__cur_size = 0
        self.__update_size_format()

    def get_static_info(self):
        s = ''
        if setting.use_debug:
            a = ''
            if screen.use_alt_chgat():
                a += "A"
            if not native.is_enabled():
                a += "N"
            if a:
                s += "{0}|".format(a)
            x = self.fileops.get_type().__module__
            if x.startswith("fileobj."):
                x = x[len("fileobj."):]
            s += "{0}|{1}|{2}|{3} ".format(kernel.get_term_info(),
                util.get_python_string(), version.__version__, x)
        s += self.__get_buffer_name()

        offset = self.fileops.get_mapping_offset()
        length = self.fileops.get_mapping_length()
        fmt = self.__nstr[setting.status_radix] # XXX not static
        if offset or length:
            s += "[@"
            s += fmt.format(offset)
            if length:
                s += "-"
                s += fmt.format(offset + length)
            s += "]"
        if self.fileops.is_readonly():
            s += " [RO]"
        return s

    def __get_buffer_name(self):
        f = self.fileops.get_short_path()
        if f:
            alias = self.fileops.get_alias()
            if alias:
                f += "|{0}".format(alias)
            if self.fileops.is_vm():
                f = "[{0}]".format(f)
            return f
        else:
            return util.NO_NAME

    def get_status_common1(self):
        if self.fileops.is_readonly():
            return ""
        if self.fileops.is_dirty():
            return "[+]"
        else:
            return "   "

    def get_status_common2(self):
        offset = self.fileops.get_mapping_offset()
        fmt = self.__nstr[setting.status_radix]
        siz = fmt.format(self.fileops.get_size())
        pos = fmt.format(self.fileops.get_pos())
        per = "{0:.1f}".format(self.fileops.get_pos_percentage())
        if per.endswith(".0"):
            per = per[:-2]

        # Update the format for e.g. on transition from 99 -> 100.
        # This also means self.__cur_fmt is formatted with the largest
        # file opened in *this* status canvas.
        if len(str(self.fileops.get_size())) > len(str(self.__cur_size)):
            self.__cur_size = self.fileops.get_size()
            self.__update_size_format()

        if not address_num_double:
            return self.__cur_fmt.format(siz, per, pos)
        elif not offset: # other buffer(s) need double space
            return self.__cur_fmt_single.format(siz, per, pos)
        else:
            pos_abs = fmt.format(offset + self.fileops.get_pos())
            return self.__cur_fmt.format(siz, per, pos_abs, pos)

    def get_status_common3(self):
        c = self.fileops.read(self.fileops.get_pos(), 1)
        if not c:
            return ""
        n = filebytes.ord(c)
        return "hex=0x{0:02X} oct=0{1:03o} dec={2:3d} char={3}".format(n, n, n,
            ascii.get_symbol(n))

    def __update_size_format(self):
        n = len(str(self.__cur_size))
        self.__cur_fmt = "{{0:>{0}}}[B] {{1:>5}}% {{2:>{1}}}".format(n, n)
        self.__cur_fmt_single = self.__cur_fmt
        if address_num_double:
            self.__cur_fmt = \
                "{{0:>{0}}}[B] {{1:>5}}% {{2:>{1}}}|{{3:>{2}}}".format(n, n, n)

    def get_format_line(self, s):
        if self.current:
            attr = self.__attr_current_status
            if len(s) < self.get_size_x():
                s += ' ' * (self.get_size_x() - len(s))
        else:
            attr = screen.A_NONE
        return s, attr

class VerboseStatusCanvas (StatusCanvas):
    def set_buffer(self, fileops):
        super(VerboseStatusCanvas, self).set_buffer(fileops)
        if self.fileops is not None:
            a = self.get_static_info()
            b = self.fileops.get_magic()
            def fn():
                yield 0, a
                yield 1, b # may be empty
            self.iter_buffer_template = fn

    def iter_buffer_template(self):
        yield 0, '', screen.A_NONE
        yield 1, '', screen.A_NONE

    def iter_buffer(self):
        g = self.iter_buffer_template()
        i, s = util.iter_next(g)
        x = self.get_status_common1()
        if x:
            if s:
                s += ' '
            s += x
        s, attr = self.get_format_line(s)
        yield i, s, attr

        i, s = util.iter_next(g)
        x = self.get_status_common2()
        if x:
            if s:
                s += ' '
            s += x
        x = self.get_status_common3()
        if x:
            if s:
                s += ' '
            s += x
        s, attr = self.get_format_line(s)
        yield i, s, attr

    def sync_cursor(self):
        self.repaint(None, False)

class SingleStatusCanvas (StatusCanvas):
    def set_buffer(self, fileops):
        super(SingleStatusCanvas, self).set_buffer(fileops)
        if self.fileops is not None:
            a = self.get_static_info()
            s = self.fileops.get_magic()
            if s:
                a += ' '
                a += s
            def fn():
                yield 0, a
            self.iter_buffer_template = fn

    def iter_buffer_template(self):
        yield 0, '', screen.A_NONE

    def iter_buffer(self):
        g = self.iter_buffer_template()
        i, s = util.iter_next(g)
        x = self.get_status_common1()
        if x:
            if s:
                s += ' '
            s += x
        x = self.get_status_common2()
        if x:
            if s:
                s += ' '
            s += x
        x = self.get_status_common3()
        if x and (len(x) < self.get_size_x()/3): # heuristic
            if s:
                s += ' '
            s += x
        s, attr = self.get_format_line(s)
        yield i, s, attr

    def sync_cursor(self):
        self.repaint(None, False)

def get_min_address_num_width():
    return 4 # 65536 bytes buffer

# needs to be per workspace for vertical split to support different width
address_num_width = get_min_address_num_width()
address_num_double = False

def get_status_frame_class():
    if setting.use_status_window_frame:
        return StatusFrame
    else:
        return NullStatusFrame

def get_status_canvas_class():
    if setting.use_status_window_verbose:
        return VerboseStatusCanvas
    else:
        return SingleStatusCanvas

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
    if not setting.use_status_window_frame and \
        util.is_subclass(cls, StatusFrame):
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
    if not setting.use_status_window_frame and \
        util.is_subclass(cls, StatusCanvas):
        y -= _FRAME_MARGIN_Y
        x -= _FRAME_MARGIN_X
    return y, x
