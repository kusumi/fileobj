# Copyright (c) 2010-2016, TOMOHIRO KUSUMI
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

import collections
import sys

from . import filebytes
from . import kbd
from . import kernel
from . import log
from . import setting
from . import util

_stdin = sys.stdin
_windows = []

A_DEFAULT   = 0
A_BOLD      = 1
A_STANDOUT  = 2
A_UNDERLINE = 4
A_FOCUS     = 0
A_COLOR     = 0

class _window (object):
    def __init__(self, leny, lenx, begy, begx, ref):
        self.__siz = util.Pair(leny, lenx)
        self.__pos = util.Pair(begy, begx)
        self.__ref = ref

    def init(self):
        if not _windows:
            kernel.get_tc(_stdin)
            log.debug("Save tty attr")
            if setting.use_stdin_cbreak:
                kernel.set_cbreak(_stdin)
                log.debug("Set tty cbreak")
        _windows.append(self)
        self.__ib = collections.deque()
        self.__ob = collections.deque()

    def cleanup(self):
        self.__clear_input()
        self.__clear_output()
        _windows.remove(self)
        if not _windows:
            kernel.set_tc(_stdin)
            log.debug("Restore tty attr")

    def __mkstr(self, y, x, s):
        return "{0} ({1:2}, {2:3}) {3}".format(
            repr(self.__ref), y, x, filebytes.repr(s))

    def keypad(self, yes):
        return

    def idlok(self, yes):
        return

    def scrollok(self, flag):
        return

    def bkgd(self, ch, attr):
        return

    def addstr(self, y, x, s, attr=A_DEFAULT):
        if setting.stdout_verbose > 0:
            util.printf(self.__mkstr(y, x, s))

    def clrtoeol(self):
        return

    def clear(self):
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

    def __clear_input(self):
        self.__ib.clear()

    def __clear_output(self):
        self.__ob.clear()

    def __append_input(self, s):
        self.__ib.extend(s)

    def __append_output(self, s):
        self.__ob.extend(s)

    def __get_output(self):
        try:
            return self.__ob.popleft()
        except IndexError:
            return -1

    def __input_to_string(self):
        return ''.join(self.__ib)

    def getch(self):
        x = self.__get_output()
        if x != -1:
            return ord(x)
        x = _stdin.read(1)
        s = self.__input_to_string()
        self.__append_input(x)
        if x == "\x1B": # ESCAPE
            if not s:
                return kbd.CONTINUE
        elif x == "[":
            if s == "\x1B":
                return kbd.CONTINUE
        elif x == "A":
            if s == "\x1B[":
                self.__clear_input()
                return kbd.UP
        elif x == "B":
            if s == "\x1B[":
                self.__clear_input()
                return kbd.DOWN
        elif x == "C":
            if s == "\x1B[":
                self.__clear_input()
                return kbd.RIGHT
        elif x == "D":
            if s == "\x1B[":
                self.__clear_input()
                return kbd.LEFT
        elif x == "3":
            if s == "\x1B[":
                return kbd.CONTINUE
        elif x == "~":
            if s == "\x1B[3":
                self.__clear_input()
                return kbd.DELETE
        if s and x == s[-1]:
            s = s[:-1]
        self.__append_output(s)
        self.__append_output(x)
        self.__clear_input()
        return kbd.CONTINUE

def init(fg, bg):
    from . import screen
    return newwin(screen.get_size_y(), screen.get_size_x(), 0, 0), \
        A_DEFAULT, \
        A_BOLD, \
        A_STANDOUT, \
        A_UNDERLINE, \
        A_FOCUS, \
        A_COLOR

def cleanup():
    while _windows:
        _windows[0].cleanup()

def flash():
    return

def newwin(leny, lenx, begy, begx, ref=None):
    scr = _window(leny, lenx, begy, begx, ref)
    scr.init()
    return scr

def has_chgat():
    return True

def iter_color_name():
    yield "black"
    yield "white"
