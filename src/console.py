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

import sys

from . import kbd
from . import literal
from . import log
from . import methods
from . import panel
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
            this._log.append(x)
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
            if x == kbd.DEAD:
                return -1
            elif x == kbd.INTERRUPT:
                return
            elif x == kbd.ERROR:
                self.ope.clear()
                continue

            li, amp, ope, arg, raw, msg, cursor = \
                self.ope.process_incoming(x)
            if li:
                if msg is not None:
                    # clear and let fn take care
                    set_message('')
            else:
                if msg is not None:
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
def init():
    this._scr = screen.alloc_screen(get_size_y(), get_size_x(),
        get_position_y(), get_position_x())

def cleanup(e, tb):
    this._scr = None
    if setting.use_trace:
        l = this._log[:]
        if l and l[-1] == kbd.ENTER:
            del l[-1]
        if trace.write(setting.get_trace_path(), l, e, tb):
            log.error("Failed to write trace")

def getch():
    return this._scr.getch()

def refresh():
    clrl()
    if this._message: # prefer _message to _banner
        printl(0, this._message)
        if this._cursor != -1:
            chgat(this._cursor, this._message, screen.A_STANDOUT)
    elif this._banner:
        printl(0, ''.join(this._banner))
    this._scr.refresh()

def __chgat(x, s, attr):
    this._scr.chgat(0, x, 1, attr | screen.color_attr)

def __alt_chgat(x, s, attr):
    if x < len(s):
        c = s[x]
    else:
        c = ' '
    printl(x, c, attr)

if panel.use_alt_chgat_methods():
    chgat = __alt_chgat
else:
    chgat = __chgat

def resize():
    try:
        this._scr.resize(get_size_y(), get_size_x())
        this._scr.mvwin(get_position_y(), get_position_x())
    except Exception as e:
        log.error(e)

def printl(x, s, attr=screen.def_attr):
    try:
        this._scr.addstr(0, x, s, attr | screen.color_attr)
    except Exception as e:
        if len(s) < screen.get_size_x() - 1:
            log.debug((e, x, s))

def clrl():
    try:
        this._scr.move(0, 0)
        this._scr.clrtoeol()
    except Exception as e:
        log.error(e)

_banner = ['']
def set_banner(o):
    if o:
        set_message('')
        this._banner[0] = "-- {0} --".format(str(o).upper())
    else:
        this._banner[0] = ''

def push_banner(s):
    if s:
        set_message('')
    this._banner.append(s)

def pop_banner():
    return this._banner.pop()

_message = ''
_cursor = -1
def set_message(o, cursor=-1):
    s = str(o)
    if isinstance(o, Exception):
        if s:
            this._message = s
        else:
            this._message = repr(o)
        this._cursor = -1
    else:
        if o is not None:
            this._message = s
        else:
            this._message = ''
        this._cursor = cursor

def get_size_y():
    return 1

def get_size_x():
    return screen.get_size_x()

def get_position_y():
    return screen.get_size_y() - get_size_y()

def get_position_x():
    return 0

this = sys.modules[__name__]
