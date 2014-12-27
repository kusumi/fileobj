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
import sys

from . import kernel
from . import setting

def ctrl(c):
    """Take str/bytes and return int"""
    return curses.ascii.ctrl(ord(c))

#           isspace(3) isgraph(3) isprint(3)
# 0x09 '\t' True       False      False
# 0x0A '\n' True       False      False
# 0x0B '\v' True       False      False
# 0x0C '\f' True       False      False
# 0x0D '\r' True       False      False
# 0x20 ' '  True       False      True

def isspace(c):
    return curses.ascii.isspace(c)

def isgraph(c):
    return curses.ascii.isgraph(c)

def isprint(c):
    # return True if isgraph(3) or 0x20
    # this isn't same as isgraph(3) + isspace(3) see above for details
    return curses.ascii.isprint(c)

def isprints(l):
    return len(l) > 0 and all(isprint(x) for x in l)

def to_chr_repr(c):
    if isprint(c):
        if isinstance(c, int):
            return chr(c)
        else:
            return c
    else:
        return '.'

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
    yield "BACKSPACE2" # FIX_ME added for FreeBSD
    yield "DELETE"
    yield "RESIZE"

def get_code(term, use_stdout):
    if use_stdout:
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
                KEY_DEAD(0x100),
    elif term.startswith("vt"):
        return  curses.ascii.TAB, \
                curses.ascii.LF, \
                curses.ascii.ESC, \
                curses.ascii.SP, \
                curses.KEY_DOWN, \
                curses.KEY_UP, \
                curses.KEY_LEFT, \
                curses.KEY_RIGHT, \
                curses.ascii.BS, \
                KEY_DEAD(0x100), \
                curses.ascii.DEL, \
                curses.KEY_RESIZE,
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
                curses.KEY_RESIZE,

def KEY_DEAD(x):
    return DEAD | (x << 16)

ERROR      = curses.ERR
DEAD       = 0xDEAD
CONTINUE   = KEY_DEAD(0)
INTERRUPT  = KEY_DEAD(1)
QUIT       = KEY_DEAD(2)

TAB        = KEY_DEAD(3)
ENTER      = KEY_DEAD(4)
ESCAPE     = KEY_DEAD(5)
SPACE      = KEY_DEAD(6)
DOWN       = KEY_DEAD(7)
UP         = KEY_DEAD(8)
LEFT       = KEY_DEAD(9)
RIGHT      = KEY_DEAD(10)
BACKSPACE  = KEY_DEAD(11)
BACKSPACE2 = KEY_DEAD(12)
DELETE     = KEY_DEAD(13)
RESIZE     = KEY_DEAD(14)

def get_backspaces():
    return BACKSPACE, BACKSPACE2

def get_arrows():
    return DOWN, UP, LEFT, RIGHT

def init(term):
    l = get_code(term, setting.use_stdout)
    for i, s in enumerate(iter_kbd_name()):
        config = getattr(setting, "key_" + s.lower())
        if config is not None:
            setattr(this, s, config)
        else:
            setattr(this, s, l[i])

this = sys.modules[__name__]
init(kernel.get_term_info())
