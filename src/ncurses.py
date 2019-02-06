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

import collections
import curses

from . import kbd
from . import log
from . import setting
from . import util

Error = curses.error

_has_chgat = True
_use_color = True
_windows = []

A_NONE      = curses.A_NORMAL
A_BOLD      = curses.A_BOLD
A_REVERSE   = curses.A_REVERSE
A_STANDOUT  = curses.A_STANDOUT
A_UNDERLINE = curses.A_UNDERLINE

BUTTON1_CLICKED        = curses.BUTTON1_CLICKED
BUTTON1_PRESSED        = curses.BUTTON1_PRESSED
BUTTON1_RELEASED       = curses.BUTTON1_RELEASED
BUTTON1_DOUBLE_CLICKED = curses.BUTTON1_DOUBLE_CLICKED
BUTTON1_TRIPLE_CLICKED = curses.BUTTON1_TRIPLE_CLICKED
REPORT_MOUSE_POSITION  = curses.REPORT_MOUSE_POSITION

COLOR_INITIALIZED = 1
COLOR_UNSUPPORTED = 2

_default_color = None
_pair_number = 1

def init():
    global _has_chgat, _use_color
    __init_mouse_event_name()
    std = curses.initscr()
    color_fb = A_NONE

    fg, bg = setting.color_fg, setting.color_bg
    arg = setting.color_current, setting.color_zero, setting.color_ff, \
        setting.color_print, setting.color_default, setting.color_visual,
    l = [A_STANDOUT, A_NONE, A_NONE, A_NONE, A_NONE, A_STANDOUT]
    assert len(arg) == len(l), (arg, l)

    if not fg and not bg and not arg:
        log.info("curses color unused")
    else:
        ret = __init_curses_color()
        if ret == COLOR_INITIALIZED:
            ret = __set_curses_color(fg, bg)
            if ret == -1:
                log.error("Failed to set curses color")
                _use_color = False
            elif ret != A_NONE:
                color_fb = ret
            else: # set misc only if fg/bg is unused
                for i, _ in enumerate(arg):
                    x = __set_curses_color_misc(_, l[i] == A_STANDOUT)
                    if _ and x == A_NONE:
                        log.error("Failed to set curses color {0}".format(_))
                    l[i] = x
        elif ret == COLOR_UNSUPPORTED:
            log.info("curses color unsupported")
        elif ret == -1:
            log.error("Failed to init curses color")
            _use_color = False
        else:
            assert False, ret

    if __init_curses_io() == -1:
        log.debug("Failed to init curses io")
    if __test_curses_chgat(std) == -1:
        log.debug("Failed to test curses chgat")
        _has_chgat = False
    return [std, color_fb] + l

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

def cleanup_windows():
    while _windows:
        _windows[0].cleanup()

def __init_curses_io():
    curses.noecho()
    curses.cbreak()
    if setting.use_mouse_events:
        l = curses.mousemask(curses.ALL_MOUSE_EVENTS)
        log.debug("Set mouse mask avail={0} old={1}".format(hex(l[0]),
            hex(l[1])))
    try:
        curses.curs_set(0) # vt100 fails here but just ignore
    except curses.error as e:
        log.debug(e)
        return -1

def __init_curses_color():
    global _default_color
    if not has_color():
        return COLOR_UNSUPPORTED
    try:
        curses.start_color()
        curses.use_default_colors()
        _default_color = -1
        return COLOR_INITIALIZED
    except curses.error as e:
        log.error(e)
        return -1

def __set_curses_color(fg, bg):
    d = dict(list(__iter_color_pair()))
    if fg or bg:
        return __init_curses_pair(d.get(fg), d.get(bg))
    else:
        return A_NONE

def __set_curses_color_misc(s, reverse):
    d = dict(list(__iter_color_pair()))
    if s is None:
        if reverse:
            s = "black,white"
        else:
            s = "white,black"
    l = s.split(",", 1) # either side missing is valid
    if len(l) == 1:
        fg = d.get(l[0])
        bg = None
    elif len(l) == 2:
        fg = d.get(l[0])
        bg = d.get(l[1])
    else:
        assert False, s
    if fg is None and bg is None:
        return A_NONE
    _ = __init_curses_pair(fg, bg)
    if _ == -1:
        return A_NONE
    else:
        return _

def __init_curses_pair(fg, bg):
    global _pair_number
    # https://docs.python.org/3/library/curses.html#curses.init_pair
    assert 1 <= _pair_number <= curses.COLOR_PAIRS-1, _pair_number
    if fg is None:
        fg = _default_color
    if bg is None:
        bg = _default_color
    try:
        curses.init_pair(_pair_number, fg, bg)
        ret = curses.color_pair(_pair_number)
        _pair_number += 1
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
        scr = Window(leny, lenx, begy, begx, ref)
        scr.init()
        return scr
    else:
        return curses.newwin(leny, lenx, begy, begx)

def has_chgat():
    return _has_chgat

def has_color():
    return curses.has_colors() # raise if before initscr()

def use_color():
    return _use_color

def iter_color_name():
    for k, v in __iter_color_pair():
        yield k

def __iter_color_pair():
    for k, v in sorted(util.iter_dir_items(curses)):
        if k.startswith("COLOR_") and isinstance(v, int):
            if k == "COLOR_PAIRS": # not color name
                continue
            s = k[len("COLOR_"):].lower()
            yield s, v

def getmouse():
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
        if s.startswith("BUTTON"):
            k = getattr(curses, s) # should be of int
            if isinstance(k, int):
                _mouse_event_name[k] = s

# APIs must be compatible with
# https://docs.python.org/3/library/curses.html
class Window (object):
    def __init__(self, leny, lenx, begy, begx, ref):
        self.__scr = curses.newwin(leny, lenx, begy, begx)

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

    def _getch(self):
        return self.__scr.getch()

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

        #if l and x == l[-1]: # XXX
        #    l = l[:-1]
        self.__queue_output(l)
        self.__queue_output((x,))
        self.__clear_input()
        return kbd.CONTINUE
