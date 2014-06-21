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

import copy

from . import edit
from . import extension
from . import panel
from . import screen
from . import util
from . import virtual
from . import visual
from . import void
from . import window

def_console_class = void.Console

class Workspace (object):
    def __init__(self, width):
        self.__bpl = 1
        if self.set_bytes_per_line(width) == -1:
            self.set_bytes_per_line("auto")
        self.__windows = ()
        self.__fileopss = []
        self.__consoles = []
        self.__vwindows = {}
        self.__bwindows = {}
        self.__twindows = {}
        self.__swindows = {}
        self.__cur_fileops = None
        self.__cur_console = None
        self.__def_vwindow = self.__get_virtual_window()
        self.__def_bwindow = self.__get_binary_window()
        self.__def_twindow = self.__get_text_window()
        self.__def_swindow = self.__get_status_window()

    def __getattr__(self, name):
        if name == "_Workspace__cur_fileops":
            raise AttributeError(name)
        return getattr(self.__cur_fileops, name)

    def __len__(self):
        return len(self.__windows)

    def __set_window(self, con):
        # virtual window comes first
        cls = util.get_class(con)
        self.__windows = \
            self.__get_virtual_window(cls), \
            self.__get_binary_window(cls), \
            self.__get_text_window(cls), \
            self.__get_status_window(cls)

    def __set_buffer(self, o):
        self.__cur_fileops = o
        self.set_console(None, None)
        self.__set_window(self.__cur_console)
        for o in self.__vwindows.values():
            o.set_buffer(self.__cur_fileops)
        for o in self.__bwindows.values():
            o.set_buffer(self.__cur_fileops)
        for o in self.__twindows.values():
            o.set_buffer(self.__cur_fileops)
        for o in self.__swindows.values():
            o.set_buffer(self.__cur_fileops)

    def set_console(self, con, arg):
        if con:
            self.__cur_console = con
        else:
            i = self.__fileopss.index(self.__cur_fileops)
            self.__cur_console = self.__consoles[i]
        self.__set_window(self.__cur_console)
        def dispatch():
            return self.__cur_console.dispatch(arg)
        self.dispatch = dispatch

    def dispatch(self):
        return -1

    def discard_window(self):
        self.__windows = self.__get_virtual_window(
            util.get_class(self.__cur_console)),

    def restore_window(self):
        self.__set_window(self.__cur_console)

    def clone_workspace(self):
        ret = Workspace(self.__bpl)
        for i, o in enumerate(self.__fileopss):
            ret.add_buffer(i, copy.copy(o), self.__consoles[i])
        return ret

    def add_buffer(self, i, fop, con):
        self.__fileopss.insert(i, fop)
        self.__consoles.insert(i, con)
        if len(self.__fileopss) == 1:
            self.__set_buffer(fop)

    def remove_buffer(self, i):
        o = self.__fileopss[i]
        i = self.__fileopss.index(o)
        if self.__cur_fileops == o:
            if i == len(self.__fileopss) - 1:
                self.goto_prev_buffer()
            else:
                self.goto_next_buffer()
        self.__fileopss.remove(self.__fileopss[i])
        self.__consoles.remove(self.__consoles[i])

    def goto_buffer(self, i):
        self.__set_buffer(self.__fileopss[i])

    def goto_first_buffer(self):
        self.__set_buffer(self.__fileopss[0])

    def goto_last_buffer(self):
        self.__set_buffer(self.__fileopss[-1])

    def goto_next_buffer(self):
        if len(self.__fileopss) > 1:
            i = self.__fileopss.index(self.__cur_fileops)
            if i >= len(self.__fileopss) - 1:
                o = self.__fileopss[0]
            else:
                o = self.__fileopss[i + 1]
            self.__set_buffer(o)

    def goto_prev_buffer(self):
        if len(self.__fileopss) > 1:
            i = self.__fileopss.index(self.__cur_fileops)
            if i <= 0:
                o = self.__fileopss[len(self.__fileopss) - 1]
            else:
                o = self.__fileopss[i - 1]
            self.__set_buffer(o)

    def iter_buffer(self):
        for o in self.__fileopss:
            yield o

    def build_dryrun(self, hei, beg):
        min_y = window.get_min_height()
        std_y = screen.get_size_y()
        if min_y > std_y or min_y > hei or hei > std_y:
            return -1
        if self.is_gt_max_width():
            return -2

    def build_dryrun_delta(self, hei_delta, beg_delta):
        return self.build_dryrun(
            self.__def_twindow.get_size_y() +
            self.__def_swindow.get_size_y() + hei_delta,
            self.__def_bwindow.get_position_y() + beg_delta)

    def build(self, hei, beg):
        h = window.get_status_window_height()
        def __build_virtual_window(o):
            siz = hei - h, self.__guess_virtual_window_width()
            pos = beg, 0
            self.__build_window(o, siz, pos)
        def __build_binary_window(o):
            siz = hei - h, self.__guess_binary_window_width()
            pos = beg, 0
            self.__build_window(o, siz, pos)
        def __build_text_window(o):
            siz = hei - h, self.__guess_text_window_width()
            pos = beg, self.__def_bwindow.get_size_x()
            self.__build_window(o, siz, pos)
        def __build_status_window(o):
            siz = h, self.__guess_status_window_width()
            pos = beg + self.__def_bwindow.get_size_y(), 0
            self.__build_window(o, siz, pos)
        self.__build_virtual_window = __build_virtual_window
        self.__build_binary_window = __build_binary_window
        self.__build_text_window = __build_text_window
        self.__build_status_window = __build_status_window
        self.resize()

    def resize(self):
        for o in self.__vwindows.values():
            self.__build_virtual_window(o)
        for o in self.__bwindows.values():
            self.__build_binary_window(o)
        for o in self.__twindows.values():
            self.__build_text_window(o)
        for o in self.__swindows.values():
            self.__build_status_window(o)

    def __build_virtual_window(self, o):
        self.__build_window(o, None, None)
    def __build_binary_window(self, o):
        self.__build_window(o, None, None)
    def __build_text_window(self, o):
        self.__build_window(o, None, None)
    def __build_status_window(self, o):
        self.__build_window(o, None, None)

    def __build_window(self, o, siz, pos):
        o.resize(siz, pos)
        o.update_capacity(self.__bpl)

    def __guess_virtual_window_width(self):
        return window.get_width(virtual.BinaryCanvas, self.__bpl)
    def __guess_binary_window_width(self):
        return window.get_width(panel.BinaryCanvas, self.__bpl)
    def __guess_text_window_width(self):
        return window.get_width(panel.TextCanvas, self.__bpl)
    def __guess_status_window_width(self):
        return self.__guess_binary_window_width() + \
            self.__guess_text_window_width()

    def is_gt_max_width(self):
        return self.__guess_status_window_width() > screen.get_size_x()

    def __get_virtual_window(self, cls=def_console_class):
        if cls not in self.__vwindows:
            if cls is def_console_class:
                o = window.Window(virtual.BinaryCanvas, virtual.NullFrame)
            elif cls is void.ExtConsole:
                o = window.Window(virtual.ExtCanvas, virtual.NullFrame)
            elif cls is visual.Console:
                o = self.__def_vwindow
            elif cls is visual.ExtConsole:
                o = self.__get_virtual_window(void.ExtConsole)
            elif util.is_subclass(cls, edit.Console):
                o = self.__def_vwindow
            o.set_buffer(self.__cur_fileops)
            self.__build_virtual_window(o)
            self.__vwindows[cls] = o
        return self.__vwindows[cls]

    def __get_binary_window(self, cls=def_console_class):
        if cls not in self.__bwindows:
            if cls is def_console_class:
                o = window.Window(panel.BinaryCanvas, panel.FocusableFrame)
            elif cls is void.ExtConsole:
                o = window.Window(
                    extension.ExtBinaryCanvas, panel.FocusableFrame)
            elif cls is visual.Console:
                o = window.Window(visual.BinaryCanvas, panel.FocusableFrame)
            elif cls is visual.ExtConsole:
                o = window.Window(visual.ExtBinaryCanvas, panel.FocusableFrame)
            elif util.is_subclass(cls, edit.Console):
                o = self.__def_bwindow
            o.set_buffer(self.__cur_fileops)
            self.__build_binary_window(o)
            self.__bwindows[cls] = o
        return self.__bwindows[cls]

    def __get_text_window(self, cls=def_console_class):
        if cls not in self.__twindows:
            if cls is def_console_class:
                o = window.Window(panel.TextCanvas, panel.Frame)
            elif cls is void.ExtConsole:
                o = window.Window(extension.ExtTextCanvas, panel.Frame)
            elif cls is visual.Console:
                o = window.Window(visual.TextCanvas, panel.Frame)
            elif cls is visual.ExtConsole:
                o = self.__get_text_window(void.ExtConsole)
            elif util.is_subclass(cls, edit.Console):
                o = self.__def_twindow
            o.set_buffer(self.__cur_fileops)
            self.__build_text_window(o)
            self.__twindows[cls] = o
        return self.__twindows[cls]

    def __get_status_window(self, cls=def_console_class):
        if cls not in self.__swindows:
            if cls is def_console_class:
                o = window.Window(panel.StatusCanvas, panel.Frame)
            elif cls is void.ExtConsole:
                o = self.__def_swindow
            elif cls is visual.Console:
                o = self.__def_swindow
            elif cls is visual.ExtConsole:
                o = self.__def_swindow
            elif util.is_subclass(cls, edit.Console):
                o = self.__def_swindow
            o.set_buffer(self.__cur_fileops)
            self.__build_status_window(o)
            self.__swindows[cls] = o
        return self.__swindows[cls]

    def read(self, x, n):
        return self.__cur_fileops.read(x, n)
    def read_current(self, n):
        return self.__cur_fileops.read(self.get_pos(), n)

    def insert(self, x, l, rec=True):
        self.__cur_fileops.insert(x, l, rec)
    def insert_current(self, l, rec=True):
        self.__cur_fileops.insert(self.get_pos(), l, rec)

    def replace(self, x, l, rec=True):
        self.__cur_fileops.replace(x, l, rec)
    def replace_current(self, l, rec=True):
        self.__cur_fileops.replace(self.get_pos(), l, rec)

    def delete(self, x, n, rec=True):
        self.__cur_fileops.delete(x, n, rec)
    def delete_current(self, n, rec=True):
        self.__cur_fileops.delete(self.get_pos(), n, rec)

    def brepaint(self, focus):
        for o in self.__windows:
            if o in self.__bwindows.values():
                o.repaint(focus)

    def repaint(self, focus):
        for o in self.__windows:
            o.repaint(focus)

    def lrepaint(self, low=False):
        for o in self.__windows:
            o.lrepaint(low)

    def go_up(self, n=1):
        for o in self.__windows:
            if o.go_up(n) == -1:
                return -1

    def go_down(self, n=1):
        for o in self.__windows:
            if o.go_down(n) == -1:
                return -1

    def go_left(self, n=1):
        for o in self.__windows:
            if o.go_left(n) == -1:
                return -1

    def go_right(self, n=1):
        for o in self.__windows:
            if o.go_right(n) == -1:
                return -1

    def go_pprev(self, n):
        for o in self.__windows:
            if o.go_pprev(n) == -1:
                return -1

    def go_hpprev(self, n):
        for o in self.__windows:
            if o.go_hpprev(n) == -1:
                return -1

    def go_pnext(self, n):
        for o in self.__windows:
            if o.go_pnext(n) == -1:
                return -1

    def go_hpnext(self, n):
        for o in self.__windows:
            if o.go_hpnext(n) == -1:
                return -1

    def go_head(self, n):
        for o in self.__windows:
            if o.go_head(n) == -1:
                return -1

    def go_tail(self, n):
        for o in self.__windows:
            if o.go_tail(n) == -1:
                return -1

    def go_lhead(self):
        for o in self.__windows:
            if o.go_lhead() == -1:
                return -1

    def go_ltail(self, n):
        for o in self.__windows:
            if o.go_ltail(n) == -1:
                return -1

    def go_phead(self, n):
        for o in self.__windows:
            if o.go_phead(n) == -1:
                return -1

    def go_pcenter(self):
        for o in self.__windows:
            if o.go_pcenter() == -1:
                return -1

    def go_ptail(self, n):
        for o in self.__windows:
            if o.go_ptail(n) == -1:
                return -1

    def go_to(self, n):
        for o in self.__windows:
            if o.go_to(n) == -1:
                return -1

    def get_bytes_per_line(self):
        return self.__bpl

    def set_bytes_per_line(self, arg):
        ret = self.find_bytes_per_line(arg)
        if ret != -1:
            self.__bpl = ret
        else:
            return -1

    def find_bytes_per_line(self, arg):
        if not arg:
            arg = "auto"
        if arg == "min":
            return 1
        elif arg == "max":
            bpl = window.get_max_bytes_per_line()
            if bpl == -1:
                return -1
            else:
                return bpl
        elif arg == "auto":
            bpl = window.get_max_bytes_per_line()
            if bpl == -1:
                return -1
            for ret in reversed([2 ** x for x in range(10)]):
                if ret <= bpl:
                    return ret
            return 1
        else:
            try:
                ret = int(arg)
                bpl = window.get_max_bytes_per_line()
                if bpl == -1:
                    return -1
                elif ret >= bpl:
                    return bpl
                elif ret <= 1:
                    return 1
                else:
                    return ret
            except ValueError:
                return -1
