# Copyright (c) 2010, Tomohiro Kusumi
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

from . import ascii
from . import kernel
from . import nodep
from . import setting
from . import terminal
from . import util

CONTINUE  = util.gen_key()
INTERRUPT = util.gen_key()
QUIT      = util.gen_key()

try:
    import curses
    ERROR          = curses.ERR
    _KEY_DOWN      = curses.KEY_DOWN
    _KEY_UP        = curses.KEY_UP
    _KEY_LEFT      = curses.KEY_LEFT
    _KEY_RIGHT     = curses.KEY_RIGHT
    _KEY_BACKSPACE = curses.KEY_BACKSPACE
    _KEY_DC        = curses.KEY_DC
    _KEY_MOUSE     = curses.KEY_MOUSE
    _KEY_RESIZE    = curses.KEY_RESIZE
except ImportError:
    if setting.use_debug:
        raise
    ERROR          = -1
    _KEY_DOWN      = 258
    _KEY_UP        = 259
    _KEY_LEFT      = 260
    _KEY_RIGHT     = 261
    _KEY_BACKSPACE = 263
    _KEY_DC        = 330
    if nodep.is_windows():
        _KEY_MOUSE  = 539
        _KEY_RESIZE = 546
    else:
        _KEY_MOUSE  = 409
        _KEY_RESIZE = 410

# XXX since which 3.x and why ?
if util.is_python2():
    _key_s_x_enter = ascii.LF
else:
    _key_s_x_enter = ascii.CR

#                  *nix            Windows
_keys_stdout = (
    ("TAB",        ascii.HT,       ascii.HT),
    ("ENTER",      _key_s_x_enter, ascii.LF),
    ("ESCAPE",     ascii.ESC,      ascii.ESC),
    ("SPACE",      ascii.SP,       ascii.SP),
    ("DOWN",       util.gen_key(), util.gen_key()),
    ("UP",         util.gen_key(), util.gen_key()),
    ("LEFT",       util.gen_key(), util.gen_key()),
    ("RIGHT",      util.gen_key(), util.gen_key()),
    ("BACKSPACE",  ascii.DEL,      ascii.BS),
    ("BACKSPACE2", util.gen_key(), util.gen_key()),
    ("DELETE",     _KEY_DC,        _KEY_DC),
    ("MOUSE",      util.gen_key(), util.gen_key()),
    ("RESIZE",     util.gen_key(), util.gen_key()),)

#                  *nix/vtxxx      *nix/xterm      Windows
_keys_ncurses = (
    ("TAB",        ascii.HT,       ascii.HT,       ascii.HT),
    ("ENTER",      ascii.LF,       ascii.LF,       ascii.LF),
    ("ESCAPE",     ascii.ESC,      ascii.ESC,      ascii.ESC),
    ("SPACE",      ascii.SP,       ascii.SP,       ascii.SP),
    ("DOWN",       _KEY_DOWN,      _KEY_DOWN,      _KEY_DOWN),
    ("UP",         _KEY_UP,        _KEY_UP,        _KEY_UP),
    ("LEFT",       _KEY_LEFT,      _KEY_LEFT,      _KEY_LEFT),
    ("RIGHT",      _KEY_RIGHT,     _KEY_RIGHT,     _KEY_RIGHT),
    ("BACKSPACE",  ascii.DEL,      _KEY_BACKSPACE, ascii.BS),
    ("BACKSPACE2", util.gen_key(), ascii.DEL,      util.gen_key()),
    ("DELETE",     util.gen_key(), _KEY_DC,        _KEY_DC),
    ("MOUSE",      _KEY_MOUSE,     _KEY_MOUSE,     _KEY_MOUSE),
    ("RESIZE",     _KEY_RESIZE,    _KEY_RESIZE,    _KEY_RESIZE),)

def parse_ansi_sequence(x, s):
    if x == "\x1B": # ESC
        if not s:
            return this.CONTINUE
    elif x == "[": # CSI
        if s == "\x1B": # ESC
            return this.CONTINUE
    elif x == "A":
        if s == "\x1B[": # CSI
            return this.UP
    elif x == "B":
        if s == "\x1B[": # CSI
            return this.DOWN
    elif x == "C":
        if s == "\x1B[": # CSI
            return this.RIGHT
    elif x == "D":
        if s == "\x1B[": # CSI
            return this.LEFT
    elif x == "3":
        if s == "\x1B[": # CSI
            return this.CONTINUE
    elif x == "~":
        if s == "\x1B[3":
            return this.DELETE

def parse_windows_sequence(x, s):
    if ord(x) == 224: # Set Keyboard Strings
        if not s:
            return this.CONTINUE
    elif x == "H":
        if len(s) == 1 and ord(s[0]) == 224:
            return this.UP
    elif x == "P":
        if len(s) == 1 and ord(s[0]) == 224:
            return this.DOWN
    elif x == "M":
        if len(s) == 1 and ord(s[0]) == 224:
            return this.RIGHT
    elif x == "K":
        if len(s) == 1 and ord(s[0]) == 224:
            return this.LEFT
    elif x == "S":
        if len(s) == 1 and ord(s[0]) == 224:
            return this.DELETE

def parse_ncurses_vtxxx_sequence(x, s):
    if x == "\x1B": # ESC
        if not s:
            return this.CONTINUE
    elif x == "[": # CSI
        if s == "\x1B": # ESC
            return this.CONTINUE
    elif x == "3":
        if s == "\x1B[": # CSI
            return this.CONTINUE
    elif x == "~":
        if s == "\x1B[3":
            return this.DELETE

def init():
    if setting.use_stdout:
        keys = _keys_stdout
        if kernel.is_xnix():
            x = 1
            this.parse_sequence = parse_ansi_sequence
        else:
            assert kernel.is_windows(), util.get_os_name()
            x = 2
            this.parse_sequence = parse_windows_sequence
    else:
        keys = _keys_ncurses
        if kernel.is_xnix():
            if terminal.is_vtxxx():
                x = 1
                this.parse_sequence = parse_ncurses_vtxxx_sequence
            else:
                x = 2
                this.parse_sequence = None
        else:
            assert kernel.is_windows(), util.get_os_name()
            x = 3
            this.parse_sequence = None

    l = []
    lb = []
    la = []
    for _ in keys:
        s, v = _[0], _[x]
        l.append((s, v))
        setattr(this, s, v)
        if s.startswith("BACKSPACE"):
            lb.append(v)
        if s in ("DOWN", "UP", "LEFT", "RIGHT"):
            la.append(v)

    this.keys = tuple(l)
    lb = tuple(sorted(lb))
    setattr(this, "get_backspaces", lambda: lb)
    la = tuple(sorted(la))
    setattr(this, "get_arrows", lambda: la)

this = sys.modules[__name__]
init()
