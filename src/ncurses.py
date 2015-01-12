# Copyright (c) 2010-2015, TOMOHIRO KUSUMI
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

A_DEFAULT   = curses.A_NORMAL
A_BOLD      = curses.A_BOLD
A_STANDOUT  = curses.A_STANDOUT
A_UNDERLINE = curses.A_UNDERLINE
A_FOCUS     = 0 # default
A_COLOR     = 0 # not curses.A_COLOR
_has_chgat  = True

def init(fg, bg):
    global _has_chgat, A_FOCUS
    std = curses.initscr()
    if fg or bg:
        if __init_curses_color(fg, bg) == -1:
            log.error("Failed to init color")
    curses.noecho()
    curses.cbreak()
    try:
        # vt100 fails here but just ignore
        curses.curs_set(0)
    except Exception, e:
        log.debug(e)
    try:
        # fails on Python 2.5 and some os
        std.chgat(0, 0, 1, A_DEFAULT)
        std.chgat(0, 0, 1, A_COLOR)
        std.erase()
    except Exception, e:
        log.debug(e)
        _has_chgat = False
    A_FOCUS = curses.ACS_CKBOARD
    return std, A_FOCUS, A_COLOR

def cleanup():
    assert not curses.isendwin()
    curses.echo()
    curses.nocbreak()
    curses.endwin()

def __init_curses_color(fg, bg):
    global A_COLOR
    if not curses.has_colors():
        return -1
    fg, bg = __get_curses_color_string(fg, bg)
    try:
        pair = 1
        curses.start_color()
        curses.init_pair(pair,
            getattr(curses, fg),
            getattr(curses, bg))
        A_COLOR = curses.color_pair(pair)
    except Exception, e:
        log.error(e)
        return -1

def __get_curses_color_string(fg, bg):
    d = dict([(s, "COLOR_" + s.upper()) for s in iter_color_name()])
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

def flash():
    curses.flash()

def newwin(leny, lenx, begy, begx, ref=None):
    return curses.newwin(leny, lenx, begy, begx)

def has_chgat():
    return _has_chgat

def iter_color_name():
    yield "black"
    yield "red"
    yield "green"
    yield "yellow"
    yield "blue"
    yield "magenta"
    yield "cyan"
    yield "white"
