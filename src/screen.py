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
import sys
import termios

from . import filebytes
from . import kbd
from . import log
from . import setting
from . import util

_std = None
_std_size = util.Pair()
_signaled = False

ACS_FOCUS   = 0 # use default
A_NORMAL    = curses.A_NORMAL
A_BOLD      = curses.A_BOLD
A_STANDOUT  = curses.A_STANDOUT
A_UNDERLINE = curses.A_UNDERLINE

def_attr    = A_NORMAL
color_attr  = 0

def init(fg='', bg=''):
    update_size()
    if not setting.use_curses:
        return -1
    if not this._std:
        this._std = curses.initscr()
        this.ACS_FOCUS = curses.ACS_CKBOARD
        if fg or bg:
            if _init_color(fg, bg) == -1:
                log.error("Failed to init color")
        this._std.keypad(1)
        this._std.bkgd(' ', this.color_attr)
        this._std.refresh()
        curses.noecho()
        curses.cbreak()
        try:
            curses.curs_set(0) # vt100 fails here but just ignore
        except Exception, e:
            log.debug(e)

def cleanup():
    clear_size()
    if this._std:
        this._std.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        this._std = None

def _init_color(fg, bg):
    if not curses.has_colors():
        return -1
    fg, bg = _parse_color_string(fg, bg)
    try:
        pair = 1
        curses.start_color()
        curses.init_pair(pair,
            getattr(curses, fg), getattr(curses, bg))
        this.color_attr = curses.color_pair(pair)
    except Exception, e:
        log.error(e)
        return -1

def _parse_color_string(fg, bg):
    d = dict([(s, "COLOR_%s" % s.upper())
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
    if this._std:
        this._std.clear()
        this._std.refresh()

def flash():
    if this._std:
        curses.flash()

def get_size_y():
    return this._std_size.y
def get_size_x():
    return this._std_size.x

def update_size():
    if util.is_python_version_or_ht(3, 3):
        x, y = shutil.get_terminal_size()
    else:
        b = fcntl.ioctl(0, termios.TIOCGWINSZ, filebytes.pad(8))
        y, x = struct.unpack(util.S2F * 4, b)[:2]
    this._std_size.set(y, x)

def clear_size():
    this._std_size.set(0, 0)

def sti():
    this._signaled = True
def cli():
    this._signaled = False

def test_signal():
    if this._signaled:
        cli()
        return True
    else:
        return False

class _screen (object):
    def __init__(self, nlines, ncols, begin_y, begin_x):
        self.refer(None)

    def refer(self, ref):
        self.ref = ref

    def get_decorated_string(self, y, x, s):
        ret = "(%2d, %3d) %s" % (y, x, s)
        if setting.use_debug:
            return "%s %s" % (repr(self.ref), ret)
        else:
            return ret

    def addstr(self, y, x, s, attr=def_attr):
        return
    def getch(self):
        return kbd.DEAD
    def clrtoeol(self):
        return
    def refresh(self):
        return
    def move(self, y, x):
        return
    def mvwin(self, y, x):
        return
    def resize(self, nlines, ncols):
        return
    def box(self):
        return
    def border(self, ls, rs, ts, bs, tl, tr, bl, br):
        return
    def chgat(self, y, x, num, attr=def_attr):
        return
    def getmaxyx(self):
        return -1, -1
    def getbegyx(self):
        return -1, -1

class _stdout_screen (_screen):
    def addstr(self, y, x, s, attr=def_attr):
        util.print_stdout(self.get_decorated_string(y, x, s))

class _quiet_screen (_screen):
    def addstr(self, y, x, s, attr=def_attr):
        return

def alloc_screen(nlines, ncols, begin_y, begin_x, ref=None):
    if setting.use_curses:
        scr = curses.newwin(nlines, ncols, begin_y, begin_x)
        scr.scrollok(0)
        scr.idlok(0)
        scr.keypad(1)
        scr.bkgd(' ', this.color_attr)
        return scr
    else:
        scr = _stdout_screen(nlines, ncols, begin_y, begin_x)
        scr.refer(ref)
        return scr

this = sys.modules[__name__]
