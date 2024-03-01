# Copyright (c) 2018, Tomohiro Kusumi
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
import os

from . import filebytes
from . import native
from . import nodep
from . import panel
from . import screen
from . import setting
from . import terminal
from . import util
from . import version

class StatusFrame (panel.Frame):
    pass

class NullStatusFrame (StatusFrame):
    def box(self):
        return

_fmt_hex = "0x{0:x}" if setting.use_lower_case_hex else "0x{0:X}"
_fmt_dec = "{0:d}"
_fmt_oct = "0{0:o}"

_pkg_prefix = nodep.get_package_name() + "."

class StatusCanvas (panel.Canvas, panel.default_attribute):
    def __init__(self, siz, pos):
        super(StatusCanvas, self).__init__(siz, pos)
        self.__update()

    def update(self):
        super(StatusCanvas, self).update()
        self.__update()

    def __update(self):
        self.__cur_size = 0
        self.__update_size_format()

    def fill(self, low):
        super(StatusCanvas, self).fill(low)
        x = self.offset.x
        for i, b, a in self.iter_line_buffer():
            y = self.offset.y + i
            if len(b) == self.bufmap.x:
                self.fill_line(y, x, b, screen.A_NONE, None)
            else:
                self.clrl(y, x)
                if b:
                    self.fill_line(y, x, b, screen.A_NONE, None)
            self.chgat(y, x, self.get_size_x(), a)

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
            if x.startswith(_pkg_prefix):
                x = x[len(_pkg_prefix):]
            s += "{0}|{1}|{2}|{3} ".format(terminal.get_type(),
                util.get_python_string(), version.__version__, x)
        s += self.__get_buffer_name()

        offset = self.fileops.get_mapping_offset()
        length = self.fileops.get_mapping_length()
        if offset or length:
            s += "[@"
            s += _fmt_dec.format(offset)
            if length:
                s += "-"
                s += _fmt_dec.format(offset + length)
            s += "]"
        if self.fileops.is_readonly():
            s += " [RO]"
        return s

    def __get_buffer_name(self):
        f = self.fileops.get_short_path()
        if f:
            # XXX self.get_size_x() uninitialized at this point
            if isinstance(self, SingleStatusCanvas) and \
                len(f) > screen.get_size_x() // 4: # heuristic
                f = os.path.basename(self.fileops.get_path())
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
            return ""

    def get_status_common2(self):
        offset = self.fileops.get_mapping_offset()
        siz = self.fileops.get_size()
        siz_str = _fmt_dec.format(siz)
        pos_str = _fmt_dec.format(self.fileops.get_pos())
        per_str = "{0:.1f}".format(self.fileops.get_pos_percentage())
        if per_str.endswith(".0"):
            per_str = per_str[:-2]

        # Update the format for e.g. on transition from 99 -> 100.
        # This also means self.__cur_fmt is formatted with the largest
        # file opened in *this* status canvas.
        if len(str(siz)) > len(str(self.__cur_size)):
            self.__cur_size = siz
            self.__update_size_format()

        if not panel.address_num_double:
            s = self.__cur_fmt.format(pos_str, siz_str, per_str)
        elif not offset: # other buffer(s) need double space
            s = self.__cur_fmt_single.format(pos_str, siz_str, per_str)
        else:
            pos_abs = _fmt_dec.format(offset + self.fileops.get_pos())
            s = self.__cur_fmt.format(pos_abs, pos_str, siz_str, per_str)

        # current unit value
        unitlen = setting.bytes_per_unit
        if unitlen > 8:
            return s
        b = self.fileops.read(self.fileops.get_unit_pos(), unitlen)
        if not b:
            return s
        un = util.bin_to_int(b, False)
        sn = util.bin_to_int(b, True)
        l = [screen.chr_repr[_] for _ in filebytes.iter_ords(b)]
        s += " {0} {1} {2}".format(_fmt_hex.format(un), ''.join(l),
            _fmt_dec.format(un))
        if un != sn:
            s += "/{0}".format(_fmt_dec.format(sn))
        return s

    # width alignment is turned off
    def __update_size_format(self):
        #n = len(str(self.__cur_size))
        #self.__cur_fmt = "{{0:>{0}}}/{{1:>{1}}}[B] {{2:>4}}%".format(n, n)
        self.__cur_fmt = "{0}/{1}[B] {2:>4}%"
        self.__cur_fmt_single = self.__cur_fmt
        if panel.address_num_double:
            #self.__cur_fmt = \
            #    "{{0:>{0}}},{{1:>{1}}}/{{2:>{2}}}[B] {{3:>4}}%".format(n, n, n)
            self.__cur_fmt = "{0},{1}/{2}[B] {3:>4}%"

    def get_format_line(self, s):
        if len(s) > self.get_size_x():
            s = s[:self.get_size_x()-1]
            s += "~"
        return s, screen.A_COLOR_CURRENT if self.current else screen.A_NONE

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
        yield 0, ''
        yield 1, ''

    def iter_line_buffer(self):
        g = self.iter_buffer_template()
        i, s = util.iter_next(g)
        if setting.use_debug and setting.use_line_scroll:
            pls = panel.get_page_line_state(self.fileops)
            x = str(pls)
            if x:
                if s:
                    s += ' '
                s += x
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
        s, attr = self.get_format_line(s)
        yield i, s, attr

    def sync_cursor(self, arg):
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
        yield 0, ''

    def iter_line_buffer(self):
        g = self.iter_buffer_template()
        i, s = util.iter_next(g)
        if setting.use_debug and setting.use_line_scroll:
            pls = panel.get_page_line_state(self.fileops)
            x = str(pls)
            if x:
                if s:
                    s += ' '
                s += x
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
        s, attr = self.get_format_line(s)
        yield i, s, attr

    def sync_cursor(self, arg):
        self.repaint(None, False)

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
