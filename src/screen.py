# Copyright (c) 2009, Tomohiro Kusumi
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

import os
import shutil
import sys

from . import kernel
from . import log
from . import setting
from . import util

if not setting.use_stdout:
    from . import ncurses as _screen
else:
    from . import stdout as _screen

_std = None
_size = util.Pair()
_signaled = False
_soft_resize = False

terminal = util.Namespace(height=-1, width=-1)

A_NONE          = _screen.A_NONE
A_BOLD          = _screen.A_BOLD
A_REVERSE       = _screen.A_REVERSE
A_STANDOUT      = _screen.A_STANDOUT
A_UNDERLINE     = _screen.A_UNDERLINE
A_COLOR_FB      = _screen.A_NONE
A_COLOR_CURRENT = _screen.A_NONE
A_COLOR_ZERO    = _screen.A_NONE
A_COLOR_PRINT   = _screen.A_NONE

def init(fg='', bg=''):
    global _std, A_COLOR_FB, A_COLOR_CURRENT, A_COLOR_ZERO, A_COLOR_PRINT
    if update_size() == -1:
        return -1
    if _std:
        return -1
    _std, A_COLOR_FB, A_COLOR_CURRENT, A_COLOR_ZERO, A_COLOR_PRINT = \
        _screen.init(fg, bg)
    _std.keypad(1)
    _std.bkgd(' ', A_COLOR_FB)
    _std.refresh()

    l = []
    l.append("A_NONE=0x{0:X}".format(A_NONE))
    l.append("A_BOLD=0x{0:X}".format(A_BOLD))
    l.append("A_REVERSE=0x{0:X}".format(A_REVERSE))
    l.append("A_STANDOUT=0x{0:X}".format(A_STANDOUT))
    l.append("A_UNDERLINE=0x{0:X}".format(A_UNDERLINE))
    l.append("A_COLOR_FB=0x{0:X}".format(A_COLOR_FB))
    l.append("A_COLOR_CURRENT=0x{0:X}".format(A_COLOR_CURRENT))
    l.append("A_COLOR_ZERO=0x{0:X}".format(A_COLOR_ZERO))
    l.append("A_COLOR_PRINT=0x{0:X}".format(A_COLOR_PRINT))
    log.debug("screen {0}".format(l))

def cleanup():
    global _std
    clear_size()
    if _std:
        _std.keypad(0)
        _std = None
    _screen.cleanup() # must always cleanup regardless of _std

def clear():
    _std.clear()
    _std.refresh()

# XXX adhoc way to find if in stream
def __test_stream():
    return os.path.isfile(setting.get_stream_path())

def flash():
    # ignore flash if in stream (too slow depending on stream size)
    if not __test_stream():
        _screen.flash()

def get_size_y():
    return _size.y

def get_size_x():
    return _size.x

def update_size():
    if util.is_python_version_or_ht(3, 3):
        x, y = shutil.get_terminal_size() # portable ???
    else:
        y, x = kernel.get_terminal_size()
    y = __override_size(y, setting.terminal_height)
    x = __override_size(x, setting.terminal_width)
    if y > 0 and x > 0:
        _size.set(y, x)
    else:
        clear_size()
        return -1

def __override_size(term_size, cfg_size):
    if cfg_size <= 0:
        return term_size
    if term_size == -1:
        return cfg_size
    assert term_size > 0, term_size
    assert cfg_size > 0, cfg_size
    if cfg_size > term_size:
        return term_size
    else:
        return cfg_size

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

def set_soft_resize():
    global _soft_resize
    _soft_resize = True

def clear_soft_resize():
    global _soft_resize
    _soft_resize = False

def test_soft_resize():
    return _soft_resize

def has_chgat():
    return _screen.has_chgat()

def use_alt_chgat():
    return setting.use_alt_chgat or not has_chgat()

def has_color():
    return _screen.has_color()

def use_color():
    return _screen.use_color()

def iter_color_name():
    for s in _screen.iter_color_name():
        yield s

def alloc_all(ref=None):
    return alloc(get_size_y(), get_size_x(), 0, 0, ref)

def alloc(leny, lenx, begy, begx, ref=None):
    scr = _screen.newwin(leny, lenx, begy, begx, ref)
    scr.scrollok(0)
    scr.idlok(0)
    scr.keypad(1)
    scr.bkgd(' ', A_COLOR_FB)
    return scr

def parse_attr(default, extra=None):
    if extra is None:
        extra = []
    assert util.is_seq(extra)
    this = sys.modules[__name__]
    attr = zero = A_NONE
    for s in extra:
        name = "A_" + s.upper()
        if hasattr(this, name): # valid extra
            attr |= getattr(this, name)

    # handle special case
    if kernel.is_screen() and use_color():
        if default == A_STANDOUT: # will not standout
            attr |= A_REVERSE

    # return default if extra empty or invalid
    if attr == zero:
        return default
    else:
        return attr
