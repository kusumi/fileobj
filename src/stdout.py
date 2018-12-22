# Copyright (c) 2014, Tomohiro Kusumi
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

from . import filebytes
from . import kbd
from . import kernel
from . import log
from . import ncurses
from . import setting
from . import util

Error = Exception

_stdin = sys.stdin
_count = 0

A_NONE          = 0
A_BOLD          = 1
A_REVERSE       = 2
A_STANDOUT      = 4
A_UNDERLINE     = 8
A_COLOR_FB      = 0
A_COLOR_CURRENT = 0
A_COLOR_ZERO    = 0
A_COLOR_FF      = 0
A_COLOR_PRINT   = 0
A_COLOR_DEFAULT = 0
A_COLOR_VISUAL  = 0

def init():
    from . import screen
    return newwin(screen.get_size_y(), screen.get_size_x(), 0, 0), \
        A_COLOR_FB, A_COLOR_CURRENT, A_COLOR_ZERO, A_COLOR_FF, A_COLOR_PRINT, \
        A_COLOR_DEFAULT, A_COLOR_VISUAL

def cleanup():
    ncurses.cleanup_windows()

def doupdate():
    return

def flash():
    return

def newwin(leny, lenx, begy, begx, ref=None):
    scr = _window(leny, lenx, begy, begx, ref)
    scr.init()
    return scr

def has_chgat():
    return True

def has_color():
    return False

def use_color():
    return False

def iter_color_name():
    yield "black"
    yield "white"

class _window (ncurses.Window):
    def __init__(self, leny, lenx, begy, begx, ref):
        self.__siz = util.Pair(leny, lenx)
        self.__pos = util.Pair(begy, begx)
        self.__ref = ref

    def init(self):
        global _count
        super(_window, self).init()
        if _count == 0:
            kernel.get_tc(_stdin)
            log.debug("Save tty attr")
            kernel.set_cbreak(_stdin)
            log.debug("Set tty cbreak")
        _count += 1

    def cleanup(self):
        global _count
        super(_window, self).cleanup()
        _count -= 1
        if _count == 0:
            kernel.set_tc(_stdin)
            log.debug("Restore tty attr")

    def __mkstr(self, y, x, s):
        return "{0} ({1:2}, {2:3}) {3}".format(repr(self.__ref), y, x,
            filebytes.str(s))

    def keypad(self, yes):
        return

    def idlok(self, yes):
        return

    def scrollok(self, flag):
        return

    def bkgd(self, ch, attr):
        return

    def addstr(self, y, x, s, attr):
        if setting.stdout_verbose > 0:
            util.printf(self.__mkstr(y, x, s))
        if setting.stdout_verbose > 2:
            for x in util.iter_traceback():
                util.printf(x)

    def clrtoeol(self):
        return

    def erase(self):
        return

    def clear(self):
        return

    def noutrefresh(self):
        return

    def refresh(self):
        return

    def move(self, y, x):
        return

    def mvwin(self, y, x):
        self.__pos.set(y, x)

    def resize(self, y, x):
        self.__siz.set(y, x)

    def box(self):
        return

    def border(self, ls, rs, ts, bs, tl, tr, bl, br):
        return

    def chgat(self, y, x, num, attr):
        return

    def getmaxyx(self):
        return self.__siz.y, self.__siz.x

    def getbegyx(self):
        return self.__pos.y, self.__pos.x

    def _getch(self):
        return ord(_stdin.read(1))

    def preprocess(self, x, l):
        if setting.stdout_verbose > 1:
            if kbd.isprint(x):
                util.printf("{0} {1}".format(x, chr(x)))
            else:
                util.printf(x)

    def parse(self, x, l):
        x = chr(x)
        s = ''.join([chr(_) for _ in l])
        if x == "\x1B": # ESC
            if not s:
                return kbd.CONTINUE
        elif x == "[":
            if s == "\x1B": # ESC
                return kbd.CONTINUE # CSI
        elif x == "A":
            if s == "\x1B[": # CSI
                return kbd.UP
        elif x == "B":
            if s == "\x1B[": # CSI
                return kbd.DOWN
        elif x == "C":
            if s == "\x1B[": # CSI
                return kbd.RIGHT
        elif x == "D":
            if s == "\x1B[": # CSI
                return kbd.LEFT
        elif x == "3":
            if s == "\x1B[": # CSI
                return kbd.CONTINUE
        elif x == "~":
            if s == "\x1B[3":
                return self.test_env("delete")
