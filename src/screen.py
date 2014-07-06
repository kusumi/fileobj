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

import curses
import fcntl
import shutil
import struct
import termios

from . import filebytes
from . import kbd
from . import log
from . import setting
from . import util

_std = None
_size = util.Pair()
_signaled = False
_has_chgat = True

ACS_FOCUS   = 0 # use default
A_NORMAL    = curses.A_NORMAL
A_BOLD      = curses.A_BOLD
A_STANDOUT  = curses.A_STANDOUT
A_UNDERLINE = curses.A_UNDERLINE

def_attr    = A_NORMAL
color_attr  = 0

def init(fg='', bg=''):
    global _std, _has_chgat
    update_size()
    if _std:
        return -1
    if not setting.use_stdout:
        _std = __init_curses(fg, bg)
    else:
        _std = alloc(get_size_y(), get_size_x(), 0, 0)
    _std.keypad(1)
    _std.bkgd(' ', color_attr)
    _std.refresh()
    try:
        # fails on Python 2.5 and some os
        __test_chgat(_std)
        _has_chgat = True
    except Exception as e:
        log.debug(e)
        _has_chgat = False

def cleanup():
    global _std
    clear_size()
    if not _std:
        return -1
    _std.keypad(0)
    _std = None
    if not setting.use_stdout:
        __cleanup_curses()

def __init_curses(fg, bg):
    global ACS_FOCUS
    std = curses.initscr()
    ACS_FOCUS = curses.ACS_CKBOARD
    if fg or bg:
        if __init_curses_color(fg, bg) == -1:
            log.error("Failed to init color")
    curses.noecho()
    curses.cbreak()
    try:
        # vt100 fails here but just ignore
        curses.curs_set(0)
    except Exception as e:
        log.debug(e)
    return std

def __cleanup_curses():
    assert not curses.isendwin()
    curses.echo()
    curses.nocbreak()
    curses.endwin()

def __init_curses_color(fg, bg):
    global color_attr
    if not curses.has_colors():
        return -1
    fg, bg = __get_curses_color_string(fg, bg)
    try:
        pair = 1
        curses.start_color()
        curses.init_pair(pair,
            getattr(curses, fg),
            getattr(curses, bg))
        color_attr = curses.color_pair(pair)
    except Exception as e:
        log.error(e)
        return -1

def __get_curses_color_string(fg, bg):
    d = dict([(s, "COLOR_{0}".format(s.upper()))
        for s in iter_color_name()])
    white = d.get("white")
    black = d.get("black")
    fg = d.get(fg, white)
    bg = d.get(bg, black)
    if fg != bg:
        return fg, bg
    elif fg == white: # white/white -> white/black
        return fg, black
    else: # other/other -> white/other
        return white, bg

def __test_chgat(scr):
    scr.chgat(0, 0, 1, def_attr)
    scr.chgat(0, 0, 1, color_attr)
    scr.chgat(0, 0, 1, def_attr | color_attr)
    scr.chgat(0, 0, get_size_x(), def_attr)
    scr.chgat(0, 0, get_size_x(), color_attr)
    scr.chgat(0, 0, get_size_x(), def_attr | color_attr)
    scr.erase()

def iter_color_name():
    yield "black"
    yield "red"
    yield "green"
    yield "yellow"
    yield "blue"
    yield "magenta"
    yield "cyan"
    yield "white"

def refresh():
    _std.clear()
    _std.refresh()

def flash():
    if not setting.use_stdout:
        curses.flash()

def get_size_y():
    return _size.y

def get_size_x():
    return _size.x

def update_size():
    if util.is_python_version_or_ht(3, 3):
        x, y = shutil.get_terminal_size()
    else:
        b = fcntl.ioctl(0, termios.TIOCGWINSZ, filebytes.pad(8))
        y, x = struct.unpack(util.S2F * 4, b)[:2]
    _size.set(y, x)

def clear_size():
    _size.set(0, 0)

def sti():
    global _signaled
    _signaled = True

def cli():
    global _signaled
    _signaled = False

def test_signal():
    ret = _signaled
    if ret:
        cli()
    return ret

def has_chgat():
    return _has_chgat

def use_alt_chgat():
    return setting.use_alt_chgat or not has_chgat()

class window (object):
    def __init__(self, leny, lenx, begy, begx, ref):
        self.siz = util.Pair(leny, lenx)
        self.pos = util.Pair(begy, begx)
        self.ref = ref
        self.init()

    def init(self):
        return
    def cleanup(self):
        return

    def mkstr(self, y, x, s):
        return "{0} ({1:2}, {2:3}) {3}".format(
            repr(self.ref), y, x, repr(s))

    def keypad(self, yes):
        return
    def idlok(self, yes):
        return
    def scrollok(self, flag):
        return
    def bkgd(self, ch, attr):
        return
    def addstr(self, y, x, s, attr=def_attr):
        return
    def getch(self):
        return kbd.QUIT
    def clrtoeol(self):
        return
    def clear(self):
        return
    def erase(self):
        return
    def refresh(self):
        return
    def move(self, y, x):
        return
    def mvwin(self, y, x):
        self.pos.set(y, x)
    def resize(self, y, x):
        self.siz.set(y, x)
    def box(self):
        return
    def border(self, ls, rs, ts, bs, tl, tr, bl, br):
        return
    def chgat(self, y, x, num, attr):
        return
    def getmaxyx(self):
        return self.siz.y, self.siz.x
    def getbegyx(self):
        return self.pos.y, self.pos.x

def alloc(leny, lenx, begy, begx, ref=None):
    if not setting.use_stdout:
        scr = curses.newwin(leny, lenx, begy, begx)
    else:
        from . import stdout
        scr = stdout.newwin(leny, lenx, begy, begx, ref)
    scr.scrollok(0)
    scr.idlok(0)
    scr.keypad(1)
    scr.bkgd(' ', color_attr)
    return scr
