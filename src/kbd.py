# Copyright (c) 2010-2016, Tomohiro Kusumi
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
from . import util

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

# XXX alternative for block visual mode
use_alt_block_visual = setting.use_bsd_caveat or \
    setting.use_illumos_caveat

ERROR     = curses.ERR
CONTINUE  = util.gen_key()
INTERRUPT = util.gen_key()
QUIT      = util.gen_key()

#                  stdout            VTxxx              xterm/others(XXX)
_keys = [
    ("TAB",        curses.ascii.TAB, curses.ascii.TAB,  curses.ascii.TAB),
    ("ENTER",      curses.ascii.LF,  curses.ascii.LF,   curses.ascii.LF),
    ("ESCAPE",     curses.ascii.ESC, curses.ascii.ESC,  curses.ascii.ESC),
    ("SPACE",      curses.ascii.SP,  curses.ascii.SP,   curses.ascii.SP),
    ("DOWN",       util.gen_key(),   curses.KEY_DOWN,   curses.KEY_DOWN),
    ("UP",         util.gen_key(),   curses.KEY_UP,     curses.KEY_UP),
    ("LEFT",       util.gen_key(),   curses.KEY_LEFT,   curses.KEY_LEFT),
    ("RIGHT",      util.gen_key(),   curses.KEY_RIGHT,  curses.KEY_RIGHT),
    ("BACKSPACE",  curses.ascii.DEL, curses.ascii.DEL,  curses.KEY_BACKSPACE),
    ("BACKSPACE2", util.gen_key(),   util.gen_key(),    curses.ascii.DEL),
    ("DELETE",     curses.KEY_DC,    util.gen_key(),    curses.KEY_DC),
    ("RESIZE",     util.gen_key(),   curses.KEY_RESIZE, curses.KEY_RESIZE),]

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
