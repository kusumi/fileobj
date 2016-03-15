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

import curses

from . import log
from . import util

_has_chgat  = True

def init(fg, bg):
    global _has_chgat
    std = curses.initscr()
    color = __init_curses_color(fg, bg)
    if color == -1:
        log.error("Failed to init curses color")
    if __init_curses_io() == -1:
        log.debug("Failed to init curses io")
    if __test_curses_chgat(std) == -1:
        log.debug("Failed to test curses chgat")
        _has_chgat = False
    return std, \
        curses.A_NORMAL, \
        curses.A_BOLD, \
        curses.A_STANDOUT, \
        curses.A_UNDERLINE, \
        curses.ACS_CKBOARD, \
        color

def cleanup():
    assert not curses.isendwin()
    curses.echo()
    curses.nocbreak()
    curses.endwin()

def __init_curses_io():
    curses.noecho()
    curses.cbreak()
    try:
        # vt100 fails here but just ignore
        curses.curs_set(0)
    except Exception as e:
        log.debug(e)
        return -1

def __init_curses_color(fg, bg):
    if fg is None and bg is None:
        return 0
    if not curses.has_colors():
        return -1
    fg, bg = __find_curses_color(fg, bg)
    try:
        pair = 1
        curses.start_color()
        curses.init_pair(pair, fg, bg)
        return curses.color_pair(pair)
    except Exception as e:
        log.error(e)
        return -1

def __find_curses_color(fg, bg):
    d = dict([l for l in iter_color_pair()])
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

def __test_curses_chgat(std):
    try:
        # fails on Python 2.5 and some os
        std.chgat(0, 0, 1, curses.A_NORMAL)
        std.chgat(0, 0, 1, curses.A_BOLD)
        std.erase()
    except Exception as e:
        log.debug(e)
        return -1

def flash():
    curses.flash()

def newwin(leny, lenx, begy, begx, ref=None):
    return curses.newwin(leny, lenx, begy, begx)

def has_chgat():
    return _has_chgat

_prefix = "COLOR_"

def iter_color_pair():
    for k, v in sorted(util.iter_dir_items(curses)):
        if k.startswith(_prefix) and isinstance(v, int):
            s = k[len(_prefix):].lower()
            yield s, v

def iter_color_name():
    for k, v in iter_color_pair():
        yield k
