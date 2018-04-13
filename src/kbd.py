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
from . import setting
from . import util

def _(c):
    if isinstance(c, int):
        return c
    else:
        return ord(c)

def ctrl(c):
    return _(c) & 0x1F

#           isspace(3) isgraph(3) isprint(3)
# 0x09 '\t' True       False      False
# 0x0A '\n' True       False      False
# 0x0B '\v' True       False      False
# 0x0C '\f' True       False      False
# 0x0D '\r' True       False      False
# 0x20 ' '  True       False      True

def isspace(c):
    x = _(c)
    return x in (0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20)

def isgraph(c):
    x = _(c)
    return x >= 0x21 and x <= 0x7E

def isprint(c):
    # return True if isgraph(3) or 0x20
    # this isn't same as isgraph(3) + isspace(3) see above for details
    x = _(c)
    return isgraph(x) or x == 0x20

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

# XXX alternative for block visual mode
use_alt_block_visual = kernel.is_bsd_derived() or kernel.is_solaris()

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
    _KEY_RESIZE    = 410

#                  stdout          VTxxx           xterm/others(XXX)
_keys = [
    ("TAB",        ascii.HT,       ascii.HT,       ascii.HT),
    ("ENTER",      ascii.LF,       ascii.LF,       ascii.LF),
    ("ESCAPE",     ascii.ESC,      ascii.ESC,      ascii.ESC),
    ("SPACE",      ascii.SP,       ascii.SP,       ascii.SP),
    ("DOWN",       util.gen_key(), _KEY_DOWN,      _KEY_DOWN),
    ("UP",         util.gen_key(), _KEY_UP,        _KEY_UP),
    ("LEFT",       util.gen_key(), _KEY_LEFT,      _KEY_LEFT),
    ("RIGHT",      util.gen_key(), _KEY_RIGHT,     _KEY_RIGHT),
    ("BACKSPACE",  ascii.DEL,      ascii.DEL,      _KEY_BACKSPACE),
    ("BACKSPACE2", util.gen_key(), util.gen_key(), ascii.DEL),
    ("DELETE",     _KEY_DC,        util.gen_key(), _KEY_DC),
    ("RESIZE",     util.gen_key(), _KEY_RESIZE,    _KEY_RESIZE),]

def get_code(term):
    if term == "stdout":
        x = 1
    elif term.startswith("vt"):
        x = 2
    else:
        x = 3
    d = {}
    for l in _keys:
        d[l[0]] = l[x]
    return d

def init(term):
    bs = []
    ar = []
    if setting.use_stdout:
        term = "stdout"
    d = get_code(term)

    for s, v in d.items():
        config = getattr(setting, "key_" + s.lower(), None)
        if config is not None:
            v = config
        setattr(this, s, v)
        if s.startswith("BACKSPACE"):
            bs.append(v)
        if s in ("DOWN", "UP", "LEFT", "RIGHT"):
            ar.append(v)

    bs = tuple(sorted(bs))
    setattr(this, "get_backspaces", lambda: bs)
    ar = tuple(sorted(ar))
    setattr(this, "get_arrows", lambda: ar)

this = sys.modules[__name__]
init(kernel.get_term_info())
