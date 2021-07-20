# Copyright (c) 2014, Tomohiro Kusumi
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

from __future__ import division

import collections
import curses
import re

from . import kbd
from . import kernel
from . import log
from . import setting
from . import terminal
from . import util

Error = curses.error

_has_chgat = True
_use_color = True
_use_mouse = True
_windows = []

A_NONE          = curses.A_NORMAL
A_BOLD          = curses.A_BOLD
A_REVERSE       = curses.A_REVERSE
A_STANDOUT      = curses.A_STANDOUT
A_UNDERLINE     = curses.A_UNDERLINE
A_COLOR_FB      = None
A_COLOR_CURRENT = None
A_COLOR_ZERO    = None
A_COLOR_FF      = None
A_COLOR_PRINT   = None
A_COLOR_DEFAULT = None
A_COLOR_VISUAL  = None
A_COLOR_OFFSET  = None

try:
    BUTTON1_CLICKED        = curses.BUTTON1_CLICKED
    BUTTON1_PRESSED        = curses.BUTTON1_PRESSED
    BUTTON1_RELEASED       = curses.BUTTON1_RELEASED
    BUTTON1_DOUBLE_CLICKED = curses.BUTTON1_DOUBLE_CLICKED
    BUTTON1_TRIPLE_CLICKED = curses.BUTTON1_TRIPLE_CLICKED

    BUTTON2_CLICKED        = curses.BUTTON2_CLICKED
    BUTTON2_PRESSED        = curses.BUTTON2_PRESSED
    BUTTON2_RELEASED       = curses.BUTTON2_RELEASED
    BUTTON2_DOUBLE_CLICKED = curses.BUTTON2_DOUBLE_CLICKED
    BUTTON2_TRIPLE_CLICKED = curses.BUTTON2_TRIPLE_CLICKED

    BUTTON3_CLICKED        = curses.BUTTON3_CLICKED
    BUTTON3_PRESSED        = curses.BUTTON3_PRESSED
    BUTTON3_RELEASED       = curses.BUTTON3_RELEASED
    BUTTON3_DOUBLE_CLICKED = curses.BUTTON3_DOUBLE_CLICKED
    BUTTON3_TRIPLE_CLICKED = curses.BUTTON3_TRIPLE_CLICKED

    BUTTON4_CLICKED        = curses.BUTTON4_CLICKED
    BUTTON4_PRESSED        = curses.BUTTON4_PRESSED
    BUTTON4_RELEASED       = curses.BUTTON4_RELEASED
    BUTTON4_DOUBLE_CLICKED = curses.BUTTON4_DOUBLE_CLICKED
    BUTTON4_TRIPLE_CLICKED = curses.BUTTON4_TRIPLE_CLICKED

    REPORT_MOUSE_POSITION  = curses.REPORT_MOUSE_POSITION
except AttributeError: # curses via NetBSD pkgsrc
    _use_mouse = False
    BUTTON1_CLICKED        = 0
    BUTTON1_PRESSED        = 0
    BUTTON1_RELEASED       = 0
    BUTTON1_DOUBLE_CLICKED = 0
    BUTTON1_TRIPLE_CLICKED = 0

    BUTTON2_CLICKED        = 0
    BUTTON2_PRESSED        = 0
    BUTTON2_RELEASED       = 0
    BUTTON2_DOUBLE_CLICKED = 0
    BUTTON2_TRIPLE_CLICKED = 0

    BUTTON3_CLICKED        = 0
    BUTTON3_PRESSED        = 0
    BUTTON3_RELEASED       = 0
    BUTTON3_DOUBLE_CLICKED = 0
    BUTTON3_TRIPLE_CLICKED = 0

    BUTTON4_CLICKED        = 0
    BUTTON4_PRESSED        = 0
    BUTTON4_RELEASED       = 0
    BUTTON4_DOUBLE_CLICKED = 0
    BUTTON4_TRIPLE_CLICKED = 0

    REPORT_MOUSE_POSITION  = 0

COLOR_INITIALIZED = 1
COLOR_UNSUPPORTED = 2

_default_color = None
_pair_number = -1
_rgb_number = -1

def init():
    global A_NONE, A_BOLD, A_REVERSE, A_STANDOUT, A_UNDERLINE, \
        A_COLOR_FB, A_COLOR_CURRENT, A_COLOR_ZERO, A_COLOR_FF, A_COLOR_PRINT, \
        A_COLOR_DEFAULT, A_COLOR_VISUAL, A_COLOR_OFFSET
    l = __init()
    A_NONE, A_BOLD, A_REVERSE, A_STANDOUT, A_UNDERLINE, \
        A_COLOR_FB, A_COLOR_CURRENT, A_COLOR_ZERO, A_COLOR_FF, A_COLOR_PRINT, \
        A_COLOR_DEFAULT, A_COLOR_VISUAL, A_COLOR_OFFSET = l[1:]
    return l

def __init():
    global _has_chgat, _use_color, _use_mouse
    __init_mouse_event_name()
    std = curses.initscr()
    color_fb = A_NONE

    fb = setting.color_fb if setting.color_fb else ""
    z = (setting.color_current, A_STANDOUT), \
        (setting.color_zero, A_NONE), \
        (setting.color_ff, A_NONE), \
        (setting.color_print, A_NONE), \
        (setting.color_default, A_NONE), \
        (setting.color_visual, A_STANDOUT), \
        (setting.color_offset, A_NONE)
    arg, l = zip(*z)
    l = list(l)
    assert len(arg) == len(l), (arg, l)

    if __is_curses_color_string_empty(fb) and not arg:
        log.info("curses color unused")
    else:
        ret = __init_curses_color()
        if ret == COLOR_INITIALIZED:
            ret = set_color_attr(fb)
            if ret == -1:
                log.error("Failed to set curses color")
                _use_color = False
            elif ret != A_NONE:
                color_fb = ret
            else: # set other colors if fg/bg unused
                for i, _ in enumerate(arg):
                    x = __set_curses_color_misc(_, l[i] == A_STANDOUT)
                    if x == -1:
                        x = A_NONE
                    if _ is not None and x == A_NONE:
                        log.error("Failed to set curses color {0},{1}".format(
                            i, _))
                    l[i] = x
        elif ret == COLOR_UNSUPPORTED:
            log.info("curses color unsupported")
        elif ret == -1:
            log.error("Failed to init curses color")
            _use_color = False
        else:
            assert False, ret

    if __init_curses() == -1:
        log.debug("Failed to init curses")
    if __init_curses_mouse() == -1:
        log.debug("Failed to init curses mouse")
        _use_mouse = False
    if __test_curses_chgat(std) == -1:
        log.debug("Failed to test curses chgat")
        _has_chgat = False

    # A_UNDERLINE likely unsupported on *nix if color change supported
    if can_change_color() and kernel.is_xnix():
        aul = A_NONE
    else:
        aul = A_UNDERLINE
    ret = [std, A_NONE, A_BOLD, A_REVERSE, A_STANDOUT, aul, color_fb] + l
    return tuple(ret)

def cleanup():
    try:
        curses.isendwin() # raise if initscr() failed
    except curses.error as e:
        log.debug(e)
        log.debug("Failed before curses.initscr()")
        return -1
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    cleanup_windows()

def cleanup_windows():
    while _windows:
        _windows[0].cleanup()

def __init_curses():
    curses.noecho()
    curses.cbreak()
    try:
        curses.curs_set(0) # vt100 fails here but just ignore
    except curses.error as e:
        log.debug(e)
        return -1

# XXX native Windows 10 seems to ignore mouse event
def __init_curses_mouse():
    global _use_mouse
    if not setting.use_mouse_events:
        _use_mouse = False
        return
    # XXX Windows Terminal can't properly receive kbd.MOUSE
    if terminal.is_windows_terminal() or setting.use_windows_terminal:
        _use_mouse = False
        return
    if hasattr(curses, "mousemask"):
        l = curses.mousemask(curses.ALL_MOUSE_EVENTS)
        log.debug("Set mouse mask avail={0} old={1}".format(hex(l[0]),
            hex(l[1])))
    else: # curses via NetBSD pkgsrc
        log.debug("curses mouse mask unsupported")
        return -1

def __init_curses_color():
    global _default_color
    if not has_color():
        return COLOR_UNSUPPORTED
    try:
        curses.start_color()
        curses.use_default_colors()
        assert _default_color is None, _default_color
        _default_color = -1
        assert _pair_number == -1, _pair_number
        __init_curses_color_pair_number()
        assert _rgb_number == -1, _rgb_number
        __init_curses_color_rgb_number()
        log.debug("COLOR_PAIRS={0} COLORS={1}".format(curses.COLOR_PAIRS,
            curses.COLORS))
        return COLOR_INITIALIZED
    except curses.error as e:
        log.error(e)
        return -1

def __test_curses_color_pair_number():
    # https://docs.python.org/3/library/curses.html#curses.init_pair
    return 1 <= _pair_number <= curses.COLOR_PAIRS-1

# curses.COLORS is probably 8 if color change unsupported, but something larger
# (e.g. 256) if color change supported.
def __test_curses_color_rgb_number():
    # https://docs.python.org/3/library/curses.html#curses.init_color
    # XXX curses.init_color() failed on an xterm-256color terminal where COLORS
    # is 256 when it reached color# 256, so use limit of COLORS-1 if COLORS is
    # 256 or above.
    if curses.COLORS >= 256:
        return 0 <= _rgb_number <= curses.COLORS-1
    else:
        return 0 <= _rgb_number <= curses.COLORS

def __init_curses_color_pair_number():
    global _pair_number
    first_call = _pair_number == -1
    _pair_number = 1
    __log_curses_color_number("pair", _pair_number, first_call)
    assert __test_curses_color_pair_number(), _pair_number

def __init_curses_color_rgb_number():
    global _rgb_number
    first_call = _rgb_number == -1
    d = dict(list(__iter_color_pair()))
    assert len(d) > 0, d
    _rgb_number = max(d.values()) + 1 # likely 8
    __log_curses_color_number("rgb", _rgb_number, first_call)
    assert __test_curses_color_rgb_number(), _rgb_number

def __log_curses_color_number(name, value, first_call):
    s = "{0}#={1}".format(name, value)
    if first_call:
        log.debug("Initial " + s)
    else:
        fn = log.error if setting.use_debug else log.info
        fn("Restart " + s)

def __set_curses_color_misc(s, reverse):
    if __is_curses_color_string_empty(s):
        if reverse:
            return A_STANDOUT
        else:
            return A_NONE
    return set_color_attr(s)

def set_color_attr(s):
    assert isinstance(s, str), s
    if not has_color():
        return -1
    l = s.split(",", 1) # either side missing is valid
    if len(l) == 1: # fg only
        fg = __parse_curses_color_string(l[0])
        bg = None
    elif len(l) == 2: # "fg,bg" case including ",bg"
        fg = __parse_curses_color_string(l[0])
        bg = __parse_curses_color_string(l[1])
    else:
        assert False, s
    # A_NONE if both are invalid input
    if fg is None and bg is None:
        return A_NONE
    # failure if either one failed
    if fg == -1 or bg == -1:
        return -1
    # use default color if either is invalid input
    if fg is None:
        fg = _default_color
    if bg is None:
        bg = _default_color
    ret = __add_curses_color_pair_number(fg, bg)
    if ret == -1:
        return -1
    try:
        return curses.color_pair(ret)
    except curses.error as e:
        log.error(e)
        return -1

def __is_curses_color_string_empty(s):
    if not s: # could be either "" or None
        return True
    l = s.split(",", 1)
    for x in l:
        if x != "":
            return False
    return True

# Returns
# 1) color number on success
# 2) -1 on failure
# 3) None for invalid input
def __parse_curses_color_string(s):
    if not s:
        return
    m = re.match(r"^(\d+):(\d+):(\d+)$", s)
    if m:
        l = [int(x) * 1000 // 255 for x in m.groups()]
        assert len(l) == 3, l
        for i, x in enumerate(l):
            if x < 0 or x > 1000: # expect input string within 0-255
                log.error("Invalid color {0} in {1}".format(m.group(i+1), s))
                return
        return __add_curses_color_rgb_number(*l)
    else:
        d = dict(list(__iter_color_pair()))
        return d.get(s)

_color_pair_number_dict = {} # only for debug
def __add_curses_color_pair_number(fg, bg):
    global _pair_number
    assert has_color(), "!has_color"
    assert isinstance(fg, int), fg
    assert isinstance(bg, int), bg
    if not __test_curses_color_pair_number():
        __init_curses_color_pair_number() # the number may not be reusable
    assert __test_curses_color_pair_number(), _pair_number
    try:
        curses.init_pair(_pair_number, fg, bg)
        ret = _pair_number
        if setting.use_debug:
            assert ret not in _color_pair_number_dict, _color_pair_number_dict
        _color_pair_number_dict[ret] = fg, bg
        _pair_number += 1
        return ret
    except curses.error as e:
        log.error(e)
        return -1

def __add_curses_color_rgb_number(r, g, b):
    global _rgb_number
    assert has_color(), "!has_color"
    if not can_change_color():
        log.info("curses color change unsupported")
        return
    if not __test_curses_color_rgb_number():
        __init_curses_color_rgb_number() # the number may not be reusable
    assert __test_curses_color_rgb_number(), _rgb_number
    try:
        curses.init_color(_rgb_number, r, g, b)
        ret = _rgb_number
        _rgb_number += 1
        return ret
    except curses.error as e:
        log.error(e)
        return -1

def __test_curses_chgat(std):
    try:
        # fails on Python 2.5 and some os
        std.chgat(0, 0, 1, A_NONE)
        std.chgat(0, 0, 1, A_BOLD)
        std.erase()
    except Exception as e: # curses.error ?
        log.debug(e)
        return -1

doupdate = curses.doupdate
flash = curses.flash

def newwin(leny, lenx, begy, begx, ref=None):
    if kbd.parse_sequence:
        scr = SeqWindow(leny, lenx, begy, begx, ref)
        scr.init()
        return scr
    elif setting.use_debug:
        scr = GenericWindow(leny, lenx, begy, begx, ref)
        scr.init()
        return scr
    else:
        return curses.newwin(leny, lenx, begy, begx)

def get_size():
    if util.is_python_version_or_ht(3, 5):
        curses.update_lines_cols()
        return curses.LINES, curses.COLS
    else:
        return -1, -1

def is_resize_supported():
    if kernel.is_linux() and util.is_wsl():
        return False
    return True

def has_chgat():
    return _has_chgat

def has_color():
    return curses.has_colors() # raise if before initscr()

def can_change_color():
    return curses.can_change_color() # raise if before initscr()

def use_color():
    return _use_color

def use_mouse():
    return _use_mouse

def iter_color_name():
    for k, v in __iter_color_pair():
        yield k

def __iter_color_pair(reverse=False):
    for k, v in sorted(util.iter_dir_items(curses)):
        if k.startswith("COLOR_") and isinstance(v, int):
            if k == "COLOR_PAIRS": # not color name
                continue
            s = k[len("COLOR_"):].lower()
            yield (v, s) if reverse else (s, v)

def getmouse():
    if not use_mouse():
        return -1, -1, -1, -1, 0
    try:
        return curses.getmouse()
    except curses.error: # for *BSD
        return -1, -1, -1, -1, 0

_mouse_event_name = {}
def get_mouse_event_name(bstate):
    ret = []
    for k, v in _mouse_event_name.items():
        if bstate & k:
            ret.append(v)
    if ret:
        return ",".join(ret)
    else:
        return "?"

def __init_mouse_event_name():
    _mouse_event_name.clear()
    for s in dir(curses):
        if s.startswith("BUTTON") or s == "REPORT_MOUSE_POSITION":
            k = getattr(curses, s) # should be of int
            if isinstance(k, int):
                _mouse_event_name[k] = s

# APIs must be compatible with
# https://docs.python.org/3/library/curses.html
class GenericWindow (object):
    def __init__(self, leny, lenx, begy, begx, ref):
        self.__scr = curses.newwin(leny, lenx, begy, begx)

    def init(self):
        return

    def cleanup(self):
        return

    def keypad(self, yes):
        return self.__scr.keypad(yes)

    def idlok(self, yes):
        return self.__scr.idlok(yes)

    def scrollok(self, flag):
        return self.__scr.scrollok(flag)

    def bkgd(self, ch, attr=A_NONE): # attr must be optional
        return self.__scr.bkgd(ch, attr)

    def addstr(self, y, x, s, attr=A_NONE): # attr must be optional
        return self.__scr.addstr(y, x, s, attr)

    def clrtoeol(self):
        return self.__scr.clrtoeol()

    def erase(self):
        return self.__scr.erase()

    def clear(self):
        return self.__scr.clear()

    def noutrefresh(self):
        return self.__scr.noutrefresh()

    def refresh(self):
        return self.__scr.refresh()

    def move(self, y, x):
        return self.__scr.move(y, x)

    def mvwin(self, y, x):
        return self.__scr.mvwin(y, x)

    def resize(self, y, x):
        return self.__scr.resize(y, x)

    def box(self):
        return self.__scr.box()

    def border(self, ls, rs, ts, bs, tl, tr, bl, br):
        return self.__scr.border(ls, rs, ts, bs, tl, tr, bl, br)

    def chgat(self, y, x, num, attr):
        return self.__scr.chgat(y, x, num, attr)

    def getmaxyx(self):
        return self.__scr.getmaxyx()

    def getbegyx(self):
        return self.__scr.getbegyx()

    def getch(self):
        return self._getch()

    def _getch(self):
        return self.__scr.getch()

class SeqWindow (GenericWindow):
    def __init__(self, leny, lenx, begy, begx, ref):
        super(SeqWindow, self).__init__(leny, lenx, begy, begx, ref)

    def init(self):
        self.__ib = collections.deque()
        self.__ob = collections.deque()
        _windows.append(self)

    def cleanup(self):
        self.__clear_input()
        self.__clear_output()
        _windows.remove(self)

    def __clear_input(self):
        self.__ib.clear()

    def __clear_output(self):
        self.__ob.clear()

    def __queue_input(self, l):
        for x in l:
            assert isinstance(x, int)
        self.__ib.extend(l)

    def __queue_output(self, l):
        for x in l:
            assert isinstance(x, int)
        self.__ob.extend(l)

    def __fetch_output(self):
        try:
            return self.__ob.popleft()
        except IndexError:
            return

    def __input_to_seq(self):
        return tuple(self.__ib)

    def preprocess(self, x, l):
        return

    def getch(self):
        x = self.__fetch_output()
        if x is not None:
            return x
        x = self._getch()
        l = self.__input_to_seq()
        self.__queue_input((x,))
        self.preprocess(x, l)

        ret = None
        if x != kbd.ERROR:
            try:
                ret = kbd.parse_sequence(chr(x), ''.join([chr(_) for _ in l]))
            except ValueError as e:
                # max chr(255) on Python 2
                if not util.is_python2():
                    log.debug(e, x, l)
                    raise
        if ret is not None:
            if ret != kbd.CONTINUE:
                self.__clear_input()
            return ret

        self.__queue_output(l)
        self.__queue_output((x,))
        self.__clear_input()
        return kbd.CONTINUE
