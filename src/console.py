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

from . import kbd
from . import literal
from . import log
from . import methods
from . import screen
from . import setting
from . import trace
from . import util

"""
Console
    void._console
        void.Console
        void.ExtConsole
    visual._console
        visual.Console
        visual.ExtConsole
    edit.Console
        edit._binary
            edit.BI
            edit.BR
                edit.RangeBR
                edit.BlockBR
        edit._ascii
            edit.AI
            edit.AR
                edit.RangeAR
                edit.BlockAR
"""

class Console (object):
    def __init__(self, co, ope):
        self.co = co
        self.ope = ope
        self.__fn = {}
        if self.init_method() != -1:
            rl, fl, sl = [], [], []
            for seq in sorted(self.__fn.keys()):
                li = literal.find_literal(seq)
                assert li, seq
                if isinstance(li, literal.RegexLiteral):
                    rl.append(li)
                elif isinstance(li, literal.FastLiteral):
                    fl.append(li)
                elif isinstance(li, literal.SlowLiteral):
                    sl.append(li)
            def fn():
                self.ope.init(rl, fl, sl)
            self.set_operand = fn

    def init_method(self):
        return -1

    def add_method(self, li, module, name):
        assert li.seq not in self.__fn, li
        if module is not self:
            fn = getattr(module, name)
            util.add_method(self, fn, name)
        self.__fn[li.seq] = getattr(self, name)
        for o in li.children:
            if o.desc and o.desc == li.desc:
                self.add_method(o, module, name)

    def handle_signal():
        return kbd.ERROR

    def handle_invalid_literal(self, li):
        return methods.HANDLED

    def set_console(self, cls, arg=None):
        self.co.set_console(cls, arg)
        return methods.RETURN

    def buffer_input(self, l):
        self.co.buffer_input(l)

    def set_banner(self):
        set_banner('')

    def set_operand(self):
        return

    def read_incoming(self):
        refresh()
        x = self.co.getch()
        if setting.use_trace:
            _log.append(x)
        if screen.test_signal():
            self.ope.clear()
            set_message('')
            return self.handle_signal()
        else:
            return x

    def dispatch(self, arg):
        self.set_banner()
        self.set_operand()
        self.co.lrepaint()
        while True:
            x = self.read_incoming()
            if x == kbd.ERROR:
                self.ope.clear()
                continue
            elif x == kbd.CONTINUE:
                continue
            elif x == kbd.INTERRUPT:
                return
            elif x == kbd.QUIT:
                return -1

            li, amp, ope, arg, raw, msg, cursor = \
                self.ope.process_incoming(x)
            if li:
                set_message(msg)
            else:
                set_message(msg, cursor)
                continue

            fn = self.__fn.get(li.seq)
            if fn:
                ret = fn(amp, ope, arg, raw)
            else:
                ret = self.handle_invalid_literal(li)
            if ret == methods.HANDLED:
                self.ope.clear()
            elif ret == methods.CONTINUE:
                continue
            elif ret == methods.RETURN:
                return
            elif ret == methods.QUIT:
                return -1

_scr = None
_log = []
chgat = None
def init():
    global _scr, chgat
    if _scr:
        return -1
    _scr = screen.alloc(
        get_size_y(), get_size_x(),
        get_position_y(), get_position_x())
    if screen.use_alt_chgat():
        chgat = __alt_chgat
    else:
        chgat = __chgat

def cleanup(e, tb):
    global _scr
    if not _scr:
        return -1
    _scr = None
    if setting.use_trace:
        l = _log[:]
        if l and l[-1] == kbd.ENTER:
            del l[-1]
        if trace.write(setting.get_trace_path(), l, e, tb):
            log.error("Failed to write trace")

def getch():
    return _scr.getch()

def refresh():
    clrl()
    test_flash()
    if _message: # prefer _message to _banner
        printl(0, _message)
        if _cursor != -1:
            chgat(_cursor, _message, screen.A_STANDOUT)
    elif _banner:
        printl(0, ''.join(_banner))
    _scr.refresh()

def __chgat(x, s, attr):
    _scr.chgat(0, x, 1, attr | screen.color_attr)

def __alt_chgat(x, s, attr):
    if x < len(s):
        c = s[x]
    else:
        c = ' '
    printl(x, c, attr)

def resize():
    try:
        set_message('')
        _scr.resize(get_size_y(), get_size_x())
        _scr.mvwin(get_position_y(), get_position_x())
    except Exception as e:
        log.error(e)

def printl(x, s, attr=screen.def_attr):
    try:
        _scr.addstr(0, x, s, attr | screen.color_attr)
    except Exception as e:
        if len(s) < screen.get_size_x() - 1:
            log.debug((e, x, s))

def clrl():
    try:
        _scr.move(0, 0)
        _scr.clrtoeol()
    except Exception as e:
        log.error(e)

_banner = ['']
def set_banner(o):
    if o:
        set_message('')
        _banner[0] = __format_banner(o)
    else:
        _banner[0] = ''

def __format_banner(o):
    return "-- {0} --".format(str(o).upper())

def push_banner(s):
    if s:
        set_message('')
    _banner.append(s)

def pop_banner():
    return _banner.pop()

_message = ''
_cursor = -1
def set_message(o, cursor=-1):
    global _message, _cursor
    if o is None:
        return # ignore None
    s = str(o)
    if isinstance(o, Exception):
        _message = s if s else repr(o)
        _cursor = -1
    else:
        _message = s
        _cursor = cursor

_flashq = []
def queue_flash(o):
    _flashq.append(o)

def test_flash():
    if not _flashq:
        return -1
    o = _flashq.pop()
    if o is not None:
        set_message(o)
    screen.flash()
    while _flashq:
        _flashq.pop()

def get_size_y():
    return 1

def get_size_x():
    return screen.get_size_x()

def get_position_y():
    return screen.get_size_y() - get_size_y()

def get_position_x():
    return 0
