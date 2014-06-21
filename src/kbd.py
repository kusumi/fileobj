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
import curses.ascii
import os

from . import setting

def ctrl(c):
    return curses.ascii.ctrl(c) # return int/str if type is int/str
def isspace(c):
    return curses.ascii.isspace(c)
def isgraph(c):
    return curses.ascii.isgraph(c)

def iter_kbd_name():
    yield "TAB"
    yield "ENTER"
    yield "ESCAPE"
    yield "SPACE"
    yield "DOWN"
    yield "UP"
    yield "LEFT"
    yield "RIGHT"
    yield "BACKSPACE"
    yield "BACKSPACE2"
    yield "DELETE"
    yield "RESIZE"

def _get_code(term):
    if term.startswith("vt"):
        return  curses.ascii.TAB, \
                curses.ascii.LF, \
                curses.ascii.ESC, \
                curses.ascii.SP, \
                curses.KEY_DOWN, \
                curses.KEY_UP, \
                curses.KEY_LEFT, \
                curses.KEY_RIGHT, \
                curses.ascii.BS, \
                None, \
                curses.ascii.DEL, \
                curses.KEY_RESIZE
    else:
        return  curses.ascii.TAB, \
                curses.ascii.LF, \
                curses.ascii.ESC, \
                curses.ascii.SP, \
                curses.KEY_DOWN, \
                curses.KEY_UP, \
                curses.KEY_LEFT, \
                curses.KEY_RIGHT, \
                curses.KEY_BACKSPACE, \
                curses.ascii.DEL, \
                curses.KEY_DC, \
                curses.KEY_RESIZE

def _(default, config):
    if config is None:
        return default
    else:
        return config

_code = _get_code(os.getenv("TERM"))
TAB        = _(_code[0], setting.key_tab)
ENTER      = _(_code[1], setting.key_enter)
ESCAPE     = _(_code[2], setting.key_escape)
SPACE      = _(_code[3], setting.key_space)
DOWN       = _(_code[4], setting.key_down)
UP         = _(_code[5], setting.key_up)
LEFT       = _(_code[6], setting.key_left)
RIGHT      = _(_code[7], setting.key_right)
BACKSPACE  = _(_code[8], setting.key_backspace)
BACKSPACE2 = _(_code[9], setting.key_backspace2) # FIX_ME added for FreeBSD
DELETE     = _(_code[10], setting.key_delete)
RESIZE     = _(_code[11], setting.key_resize)
del _

ERROR     = curses.ERR
DEAD      = 0xDEAD
INTERRUPT = None
ARROWS    = DOWN, UP, LEFT, RIGHT
