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

from . import ascii
from . import filebytes
from . import kernel
from . import log
from . import screen
from . import setting
from . import util
from . import version

"""
_panel
    Frame
        virtual.NullFrame
        FocusableFrame
    Canvas
        virtual._canvas
            virtual.BinaryCanvas
            virtual.ExtCanvas
        DisplayCanvas
            BinaryCanvas
                visual.BinaryCanvas
            TextCanvas
                visual.TextCanvas
            extension.ExtBinaryCanvas
                visual.ExtBinaryCanvas
            extension.ExtTextCanvas
        OptionCanvas
"""

class _panel (object):
    def __init__(self, siz, pos):
        self.__size = util.Pair(*siz)
        self.__position = util.Pair(*pos)
        self.scr = screen.alloc_screen(
            self.get_size_y(), self.get_size_x(),
            self.get_position_y(), self.get_position_x(), self)

    def get_size_y(self):
        return self.__size.y

    def get_size_x(self):
        return self.__size.x

    def get_position_y(self):
        return self.__position.y

    def get_position_x(self):
        return self.__position.x

    def fill(self, low):
        return

    def repaint(self, arg):
        util.raise_no_impl("repaint")

    def refresh(self):
        self.scr.refresh()

    def resize(self, siz, pos):
        if siz:
            self.__size.set(*siz)
            self.scr.resize(self.get_size_y(), self.get_size_x())
        if pos:
            self.__position.set(*pos)
            self.scr.mvwin(self.get_position_y(), self.get_position_x())

class Frame (_panel):
    def __init__(self, siz, pos):
        if not siz and not pos:
            siz = get_min_frame_size()
            pos = get_min_frame_position()
        super(Frame, self).__init__(siz, pos)

    def repaint(self, focus):
        self.box(focus)
        self.refresh()

    def box(self, focus):
        """Need refresh to make it appear"""
        self.scr.box()

class FocusableFrame (Frame):
    def box(self, focus):
        if focus:
            self.scr.border(*[screen.ACS_FOCUS for x in range(8)])
        else:
            self.scr.box()

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
        return 1, setting.offset_num_width + 3
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
        if not siz and not pos:
            siz = get_min_canvas_size()
            pos = get_min_canvas_position()
        super(Canvas, self).__init__(siz, pos)
        self.__cell = self.get_cell() # size, distance
        self.offset = util.Pair(*self.get_offset())
        self.bufmap = util.Pair()
        self.fileops = None

    def set_buffer(self, fileops):
        self.fileops = fileops

    def get_capacity(self):
        return self.bufmap.y * self.bufmap.x

    def update_capacity(self, bytes_per_line):
        self.bufmap.set(*self.get_bufmap(bytes_per_line))

    def iter_buffer(self):
        yield 0, ''

    def get_form_single(self, x):
        return x

    def get_form_line(self, buf):
        return buf

    def get_cell_width(self, x):
        return self.__cell[0] * x

    def get_cell_edge(self, x):
        return self.get_cell_width(x) - self.__cell[1]

    def fill(self, low):
        x = self.offset.x
        for i, b in self.iter_buffer():
            y = self.offset.y + i
            if len(b) < self.bufmap.x:
                self.clrl(y, x)
            if b:
                self.printl(y, x, self.get_form_line(b))

    def repaint(self, low):
        self.fill(low)
        self.refresh()

    def resize(self, siz, pos):
        super(Canvas, self).resize(siz, pos)
        x = self.get_capacity()
        if setting.use_barrier and setting.barrier_size < x:
            log.debug("Change default barrier size {0} -> {1}".format(
                setting.barrier_size, x))
            setting.barrier_size = x

    def chgat(self, y, x, num, attr=screen.def_attr):
        """May raise exception on page change for previous pos"""
        try:
            self.scr.chgat(y, x, num, attr | screen.color_attr)
        except Exception:
            pass

    def printl(self, y, x, s, attr=screen.def_attr):
        try:
            self.scr.addstr(y, x, s, attr | screen.color_attr)
        except Exception as e:
            if (y < self.get_size_y() - 1) or \
                (x + len(s) < self.get_size_x() - 1):
                log.debug((e, (y, x), s))

    def clrl(self, y, x):
        try:
            self.scr.move(y, x)
            self.scr.clrtoeol()
        except Exception as e:
            log.error(e)

    def get_coordinate(self, pos):
        """Return coordinate of the position in curses window"""
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

    def in_same_page(self, pos, ppos):
        """Return True if two positions are in the same page"""
        x = self.get_capacity()
        return pos // x == ppos // x

    def get_line_offset(self, pos):
        """Return offset of the current line"""
        return pos - pos % self.bufmap.x

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
        if use_alt_chgat_methods():
            self.chgat_posstr = self.alt_chgat_posstr
            self.chgat_cursor = self.alt_chgat_cursor

    def iter_buffer(self):
        b = self.fileops.read(self.get_page_offset(), self.get_capacity())
        n = 0
        for i in range(self.bufmap.y):
            yield i, b[n : n + self.bufmap.x]
            n += self.bufmap.x

    def fill(self, low):
        self.fill_posstr()
        super(DisplayCanvas, self).fill(low)
        pos = self.fileops.get_pos()
        self.chgat_posstr(pos, screen.A_BOLD)
        self.chgat_cursor(pos, screen.A_STANDOUT, low)

    def update_highlight(self):
        # update prev first since two values may be the same
        ppos = self.fileops.get_prev_pos()
        self.chgat_posstr(ppos, 0)
        self.chgat_cursor(ppos, 0, False)
        pos = self.fileops.get_pos()
        self.chgat_posstr(pos, screen.A_BOLD)
        self.chgat_cursor(pos, screen.A_STANDOUT, False)
        self.refresh()

    def sync_cursor(self):
        if self.in_same_page(
            self.fileops.get_pos(),
            self.fileops.get_prev_pos()):
            self.update_highlight()
        else:
            return -1 # need repaint

    def chgat_posstr(self, pos, attr):
        return
    def alt_chgat_posstr(self, pos, attr):
        return
    def chgat_cursor(self, pos, attr, low):
        return
    def alt_chgat_cursor(self, pos, attr, low):
        return
    def fill_posstr(self):
        return

class BinaryCanvas (DisplayCanvas, binary_addon):
    def __init__(self, siz, pos):
        super(BinaryCanvas, self).__init__(siz, pos)
        self.__cstr = {
            16: "{0:02X}",
            10: "{0:02d}",
            8 : "{0:02o}", }
        self.__lstr = {
            16: "|{0}| ",
            10: " {0}| ",
            8 : "<{0}> ", }
        self.__lstr_fmt = {
            16: "{{0:0{0}X}}".format(setting.offset_num_width),
            10: "{{0:{0}d}}".format(setting.offset_num_width),
            8 : "{{0:0{0}o}}".format(setting.offset_num_width), }

    def get_form_single(self, x):
        return "{0:02X}".format(filebytes.ord(x) & 0xFF)

    def get_form_line(self, buf):
        return ' '.join([self.get_form_single(x) for x in buf])

    def chgat_posstr(self, pos, attr):
        y, x = self.get_coordinate(pos)
        d = pos % self.bufmap.x
        self.chgat(0, self.offset.x + self.get_cell_width(d),
            self.get_cell_edge(1), screen.A_UNDERLINE | attr)
        self.chgat(y, 0, self.offset.x, attr)

    def alt_chgat_posstr(self, pos, attr):
        """Alternative for Python 2.5"""
        y, x = self.get_coordinate(pos)
        d = pos % self.bufmap.x
        self.printl(0, self.offset.x + self.get_cell_width(d),
            self.__get_column_posstr(d), screen.A_UNDERLINE | attr)
        s = self.__get_line_posstr(self.get_line_offset(pos))
        self.printl(y, 0, s, attr)

    def chgat_cursor(self, pos, attr, low):
        y, x = self.get_coordinate(pos)
        if low:
            self.chgat(y, x, 1)
            self.chgat(y, x + 1, 1, attr)
        else:
            self.chgat(y, x, 1, attr)
            self.chgat(y, x + 1, 1)

    def alt_chgat_cursor(self, pos, attr, low):
        """Alternative for Python 2.5"""
        y, x = self.get_coordinate(pos)
        c = self.fileops.read(pos, 1)
        s = self.get_form_single(c) if c else '  '
        if low:
            self.printl(y, x, s[0])
            self.printl(y, x + 1, s[1], attr)
        else:
            self.printl(y, x, s[0], attr)
            self.printl(y, x + 1, s[1])

    def fill_posstr(self):
        self.printl(0, 0, ' ' * self.offset.x) # blank part
        for x in range(self.bufmap.x):
            self.printl(0, self.offset.x + self.get_cell_width(x),
                self.__get_column_posstr(x), screen.A_UNDERLINE)
        n = self.get_page_offset()
        for i in range(self.bufmap.y):
            self.printl(self.offset.y + i, 0, self.__get_line_posstr(n))
            n += self.bufmap.x

    def __get_column_posstr(self, n):
        return self.__cstr[setting.offset_num_radix].format(n)

    def __get_line_posstr(self, n):
        return self.__lstr[setting.offset_num_radix].format(
            self.__lstr_fmt[setting.offset_num_radix].format(
                n)[-setting.offset_num_width:])

class TextCanvas (DisplayCanvas, text_addon):
    def __init__(self, siz, pos):
        super(TextCanvas, self).__init__(siz, pos)
        self.__cstr = {
            16: "{0:X}",
            10: "{0:d}",
            8 : "{0:o}", }

    def get_form_single(self, x):
        return util.chr2(x)

    def get_form_line(self, buf):
        return ''.join([self.get_form_single(x) for x in buf])

    def chgat_posstr(self, pos, attr):
        x = pos % self.bufmap.x
        self.chgat(0, self.offset.x + self.get_cell_width(x),
            self.get_cell_edge(1), screen.A_UNDERLINE | attr)

    def alt_chgat_posstr(self, pos, attr):
        """Alternative for Python 2.5"""
        x = pos % self.bufmap.x
        self.printl(0, self.offset.x + self.get_cell_width(x),
            self.__get_column_posstr(x), screen.A_UNDERLINE | attr)

    def chgat_cursor(self, pos, attr, low):
        y, x = self.get_coordinate(pos)
        self.chgat(y, x, 1, attr)

    def alt_chgat_cursor(self, pos, attr, low):
        """Alternative for Python 2.5"""
        y, x = self.get_coordinate(pos)
        c = self.fileops.read(pos, 1)
        s = self.get_form_single(c) if c else ' '
        self.printl(y, x, s, attr)

    def fill_posstr(self):
        s = ''.join([self.__get_column_posstr(x) for x in
            range(self.bufmap.x)])
        self.printl(0, self.offset.x, s, screen.A_UNDERLINE)

    def __get_column_posstr(self, n):
        return self.__cstr[setting.offset_num_radix].format(n)[-1]

class OptionCanvas (Canvas, default_addon):
    def set_buffer(self, fileops):
        super(OptionCanvas, self).set_buffer(fileops)
        if self.fileops:
            a = ''
            if setting.use_debug:
                a += "<{0}> <{1}> {2} ".format(
                    util.get_python_executable_string(),
                    version.__version__,
                    self.fileops.get_type())
            a += self.fileops.get_short_path()
            if not a:
                a = util.NO_NAME
            offset = self.fileops.get_offset()
            if offset:
                a += " @{0}".format(offset)
            if self.fileops.is_readonly():
                a += " [RO]"
            b = self.fileops.get_magic()
            if b:
                b += ' '
            def fn():
                yield 0, a
                yield 1, b
            self.iter_buffer_template = fn

    def iter_buffer_template(self):
        yield 0, ''
        yield 1, ''

    def iter_buffer(self):
        g = self.iter_buffer_template()
        i, s = util.iter_next(g)
        if self.fileops.is_dirty():
            s += " [+]"
        yield i, s

        i, s = util.iter_next(g)
        per = "{0:.1f}".format(self.fileops.get_pos_percentage())
        if per.endswith(".0"):
            per = per[:-2]
        pos = self.fileops.get_pos()
        s += "{0}[B] {1:>4}% {2}".format(
            self.fileops.get_size(), per, pos)
        x = self.fileops.read(pos, 1)
        if x:
            n = filebytes.ord(x)
            s += " hex=0x{0:02X} oct=0{1:03o} dec={2:3d} char={3}".format(
                n, n, n, ascii.get_symbol(n))
        yield i, s

    def sync_cursor(self):
        self.repaint(False)

def use_alt_chgat_methods():
    return setting.use_alt_chgat or \
        not util.is_python_version_or_ht(2, 6, 0) or \
        not kernel.is_linux() # scr.chgat did not work on NetBSD

def get_min_frame_size():
    return 1 + get_margin(2), 1 + get_margin(2)
def get_min_canvas_size():
    y, x = get_min_frame_size()
    return y - get_margin(2), x - get_margin(2)

def get_min_frame_position():
    return 0, 0
def get_min_canvas_position():
    y, x = get_min_frame_position()
    return y + get_margin(), x + get_margin()

def get_margin(x=1):
    return 1 * x
