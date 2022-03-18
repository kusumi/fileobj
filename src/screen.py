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
import sys

from . import log
from . import setting
from . import terminal
from . import util

if not setting.use_stdout:
    from . import ncurses as _screen
else:
    from . import stdout as _screen

Error = _screen.Error

_std = None
_size = util.Pair()
_initial_size = util.Pair(-1, -1)
_signaled = False
_soft_resize = False

# no .get() wrapper, out of range input is error
chr_repr = {}
buf_attr = {}

A_NONE          = _screen.A_NONE # used by functions' default argument
A_BOLD          = None
A_REVERSE       = None # unused
A_STANDOUT      = None
A_UNDERLINE     = None
A_COLOR_FB      = None
A_COLOR_CURRENT = None
A_COLOR_ZERO    = None
A_COLOR_FF      = None
A_COLOR_PRINT   = None
A_COLOR_DEFAULT = None
A_COLOR_VISUAL  = None
A_COLOR_OFFSET  = None

BUTTON1_CLICKED        = _screen.BUTTON1_CLICKED
BUTTON1_PRESSED        = _screen.BUTTON1_PRESSED
BUTTON1_RELEASED       = _screen.BUTTON1_RELEASED
BUTTON1_DOUBLE_CLICKED = _screen.BUTTON1_DOUBLE_CLICKED
BUTTON1_TRIPLE_CLICKED = _screen.BUTTON1_TRIPLE_CLICKED

BUTTON2_CLICKED        = _screen.BUTTON2_CLICKED
BUTTON2_PRESSED        = _screen.BUTTON2_PRESSED
BUTTON2_RELEASED       = _screen.BUTTON2_RELEASED
BUTTON2_DOUBLE_CLICKED = _screen.BUTTON2_DOUBLE_CLICKED
BUTTON2_TRIPLE_CLICKED = _screen.BUTTON2_TRIPLE_CLICKED

BUTTON3_CLICKED        = _screen.BUTTON3_CLICKED
BUTTON3_PRESSED        = _screen.BUTTON3_PRESSED
BUTTON3_RELEASED       = _screen.BUTTON3_RELEASED
BUTTON3_DOUBLE_CLICKED = _screen.BUTTON3_DOUBLE_CLICKED
BUTTON3_TRIPLE_CLICKED = _screen.BUTTON3_TRIPLE_CLICKED

BUTTON4_CLICKED        = _screen.BUTTON4_CLICKED
BUTTON4_PRESSED        = _screen.BUTTON4_PRESSED
BUTTON4_RELEASED       = _screen.BUTTON4_RELEASED
BUTTON4_DOUBLE_CLICKED = _screen.BUTTON4_DOUBLE_CLICKED
BUTTON4_TRIPLE_CLICKED = _screen.BUTTON4_TRIPLE_CLICKED

REPORT_MOUSE_POSITION  = _screen.REPORT_MOUSE_POSITION

def init():
    global _std, A_NONE, A_BOLD, A_REVERSE, A_STANDOUT, A_UNDERLINE, \
        A_COLOR_FB, A_COLOR_CURRENT, A_COLOR_ZERO, A_COLOR_FF, A_COLOR_PRINT, \
        A_COLOR_DEFAULT, A_COLOR_VISUAL, A_COLOR_OFFSET
    if _std:
        return -1
    _std, A_NONE, A_BOLD, A_REVERSE, A_STANDOUT, A_UNDERLINE, \
        A_COLOR_FB, A_COLOR_CURRENT, A_COLOR_ZERO, A_COLOR_FF, A_COLOR_PRINT, \
        A_COLOR_DEFAULT, A_COLOR_VISUAL, A_COLOR_OFFSET = _screen.init()
    _std.keypad(1)
    _std.bkgd(' ', A_COLOR_FB)
    _std.refresh()
    if update_size() == -1:
        return -1

    chr_repr.clear()
    for x in util.get_xrange(0, 256):
        chr_repr[x] = chr(x) if util.isprint(x) else '.'

    buf_attr.clear()
    for x in util.get_xrange(0, 256):
        if setting.has_buffer_attr():
            if x == 0:
                _ = A_COLOR_ZERO
            elif x == 0xff:
                _ = A_COLOR_FF
            elif util.isprint(x):
                _ = A_COLOR_PRINT
            else:
                _ = A_COLOR_DEFAULT
        else:
            _ = A_NONE
        buf_attr[x] = _
    if setting.use_debug:
        __log_debug()

def __log_debug():
    this = sys.modules[__name__]
    l = []
    for x in ("NONE", "BOLD", "REVERSE", "STANDOUT", "UNDERLINE",
        "COLOR_FB", "COLOR_CURRENT", "COLOR_ZERO", "COLOR_FF", "COLOR_PRINT",
        "COLOR_DEFAULT", "COLOR_VISUAL", "COLOR_OFFSET"):
        s = "A_" + x
        assert hasattr(this, s), s
        a = getattr(this, s)
        assert a is not None, (s, a)
        assert isinstance(a, int), (s, a)
        l.append("{0}=0x{1:X}".format(s, a))

    log.debug("screen: {0}".format(l))
    log.debug("screen: has_color={0} has_extended_color={1} "
        "can_change_color={2} use_color={3} use_mouse={4}".format(
        has_color(), has_extended_color(), can_change_color(), use_color(),
        use_mouse()))
    log.debug("screen: buf_attr {0}".format(set(sorted(buf_attr.values()))))

def cleanup():
    global _std
    __clear_size()
    if _std:
        _std.keypad(0)
        _std = None
    _screen.cleanup() # must always cleanup regardless of _std

def clear_refresh():
    _std.clear() # erase contents
    _std.refresh() # refresh screen

# XXX adhoc way to find if in stream
def __test_stream():
    return os.path.isfile(setting.get_stream_path())

def doupdate():
    _screen.doupdate()

def flash():
    # ignore flash if in stream (too slow depending on stream size)
    if not __test_stream():
        _screen.flash()

def get_size_y():
    return _size.y

def get_size_x():
    return _size.x

def is_size_changed_from_initial():
    return _size.y != _initial_size.y or _size.x != _initial_size.x

def update_size():
    y, x = _screen.get_size()
    if y == -1 and x == -1:
        y, x = terminal.get_size()
    y = __override_size(y, setting.terminal_height)
    x = __override_size(x, setting.terminal_width)
    if y > 0 and x > 0:
        if _initial_size.y == -1 and _initial_size.x == -1:
            _initial_size.set(y, x)
        _size.set(y, x)
    else:
        __clear_size()
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

def __clear_size():
    _initial_size.set(-1, -1)
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

def is_resize_supported():
    return setting.use_terminal_resize and _screen.is_resize_supported()

def has_chgat():
    return _screen.has_chgat()

def use_alt_chgat():
    return setting.use_alt_chgat or not has_chgat()

def has_color():
    return _screen.has_color()

def has_extended_color():
    ret = _screen.has_extended_color()
    assert isinstance(ret, bool) or ret is None
    return ret

def assert_extended_color_supported():
    ret = has_extended_color()
    if isinstance(ret, bool):
        assert ret is True, ret
    else:
        assert ret is None, ret

def assert_extended_color_unsupported():
    ret = has_extended_color()
    if isinstance(ret, bool):
        assert ret is False, ret
    else:
        assert ret is None, ret

def can_change_color():
    return _screen.can_change_color()

def set_color_attr(s):
    return _screen.set_color_attr(s)

def use_color():
    return _screen.use_color()

def use_mouse():
    return _screen.use_mouse()

def iter_color_name():
    for s in _screen.iter_color_name():
        yield s

def getmouse():
    return _screen.getmouse()

def get_mouse_event_name(bstate):
    return _screen.get_mouse_event_name(bstate)

def alloc_all(ref=None):
    return alloc(get_size_y(), get_size_x(), 0, 0, ref)

def alloc(leny, lenx, begy, begx, ref=None):
    scr = _screen.newwin(leny, lenx, begy, begx, ref)
    scr.scrollok(0)
    scr.idlok(0)
    scr.keypad(1)
    scr.bkgd(' ', A_COLOR_FB)
    return scr
