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

import shutil

from . import kernel
from . import setting
from . import util

if not setting.use_stdout:
    from . import ncurses as _screen
else:
    from . import stdout as _screen

_std = None
_size = util.Pair()
_signaled = False

A_DEFAULT   = _screen.A_DEFAULT
A_BOLD      = _screen.A_BOLD
A_STANDOUT  = _screen.A_STANDOUT
A_UNDERLINE = _screen.A_UNDERLINE
A_FOCUS     = _screen.A_FOCUS
A_COLOR     = _screen.A_COLOR

def init(fg='', bg=''):
    global _std, A_FOCUS, A_COLOR
    if update_size() == -1:
        return -1
    if _std:
        return -1
    _std, A_FOCUS, A_COLOR = _screen.init(fg, bg)
    _std.keypad(1)
    _std.bkgd(' ', A_COLOR)
    _std.refresh()

def cleanup():
    global _std
    clear_size()
    if not _std:
        return -1
    _std.keypad(0)
    _std = None
    _screen.cleanup()

def clear():
    _std.clear()
    _std.refresh()

def flash():
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
    if -1 not in (y, x):
        _size.set(y, x)
    else:
        clear_size()
        return -1

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
    return _screen.has_chgat()

def use_alt_chgat():
    return setting.use_alt_chgat or not has_chgat()

def iter_color_name():
    for s in _screen.iter_color_name():
        yield s

def alloc(leny, lenx, begy, begx, ref=None):
    scr = _screen.newwin(leny, lenx, begy, begx, ref)
    scr.scrollok(0)
    scr.idlok(0)
    scr.keypad(1)
    scr.bkgd(' ', A_COLOR)
    return scr
