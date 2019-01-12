# Copyright (c) 2011, Tomohiro Kusumi
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

from . import kbd
from . import kernel
from . import literal
from . import log
from . import methods
from . import nodep
from . import screen
from . import setting
from . import trace
from . import util

# Console
#     void._console
#         void.Console
#         void.ExtConsole
#     visual._console
#         visual.Console
#         visual.ExtConsole
#     edit.Console
#         edit._writeconsole
#             edit._binary
#                 edit.BI
#                 edit.BR
#                     edit.RangeBR
#                     edit.BlockBR
#             edit._ascii
#                 edit.AI
#                 edit.AR
#                     edit.RangeAR
#                     edit.BlockAR
#         edit._deleteconsole

seqno = 0

class Console (object):
    def __init__(self, co, ope):
        self.co = co
        self.ope = ope
        self.__fd = None
        self.__fn = {}

        if setting.use_console_log:
            self.__fd = open_console_log(util.get_class_repr(self))

        if self.init_method() != -1:
            rl, fl, sl = [], [], []
            for seq in sorted(self.__fn.keys()):
                li = literal.find_literal(seq)
                assert li, seq
                if literal.is_RegexLiteral(li):
                    rl.append(li)
                elif literal.is_FastLiteral(li):
                    fl.append(li)
                elif literal.is_SlowLiteral(li):
                    sl.append(li)
            def fn():
                self.ope.init(rl, fl, sl)
            self.set_operand = fn

    def cleanup(self):
        if self.__fd:
            self.__fd.close()

    def init_method(self):
        return -1

    def add_method(self, li, module, name):
        assert li.is_origin(), (li.str, li.seq)
        self.__add_method(li, module, name)

    def __add_method(self, li, module, name):
        assert li.seq not in self.__fn, (li.str, li.seq)
        if module is not self:
            fn = getattr(module, name)
            util.add_method(self, fn, name)
        self.__fn[li.seq] = getattr(self, name)
        for o in li.children:
            if o.is_alias(li):
                self.__add_method(o, module, name)

    def handle_signal():
        return kbd.ERROR

    def handle_invalid_literal(self, li):
        return methods.HANDLED

    def set_console(self, cls, arg=None):
        self.co.set_console(cls, arg)
        return methods.RETURN

    def queue_input(self, l):
        self.co.queue_input(l)

    def set_banner(self):
        set_banner('')

    def set_operand(self):
        return

    def log(self, *l):
        if setting.use_console_log:
            s = "{0} {1}\n".format(seqno, " ".join([str(_) for _ in l]))
            if self.__fd:
                self.__fd.write(s)
                kernel.fsync(self.__fd)
            if _fd:
                _fd.write(s)
                kernel.fsync(_fd)

    def read_incoming(self):
        global seqno
        refresh()
        seqno += 1
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
            if setting.use_debug:
                if util.test_key(x):
                    assert 0 <= util.decode_key(x) <= 0xFFFF, x
            if x == kbd.ERROR:
                self.ope.clear()
                continue
            elif x == kbd.CONTINUE:
                continue
            elif x == kbd.INTERRUPT:
                return
            elif x == kbd.QUIT:
                self.cleanup()
                return -1

            li, amp, opc, arg, raw, msg, cursor = self.ope.process_incoming(x)
            if li:
                set_message(msg)
            else:
                set_message(msg, cursor)
                continue

            fn = self.__fn.get(li.seq)
            if fn:
                l = amp, opc, arg, raw
                self.log(li.str, l)
                ret = fn(*l)
            else:
                ret = self.handle_invalid_literal(li)
            if ret == methods.HANDLED:
                self.ope.clear()
                self.co.clear_register()
            elif ret == methods.REWIND:
                self.ope.rewind()
            elif ret == methods.CONTINUE:
                continue
            elif ret == methods.RETURN:
                return
            elif ret == methods.QUIT:
                self.cleanup()
                return -1

_scr = None
_log = []
chgat = None
_cursor_attr = None
_fd = None

def init():
    # screen must be initialized
    global _scr, _cursor_attr, chgat, _fd
    if _scr:
        return -1
    _scr = screen.alloc(get_size_y(), get_size_x(), get_position_y(),
        get_position_x(), getch)
    _cursor_attr = screen.A_COLOR_CURRENT
    log.debug(_scr)
    if screen.use_alt_chgat():
        chgat = __alt_chgat
    else:
        chgat = __chgat
    if setting.use_console_log:
        _fd = open_console_log(nodep.get_package_name())

def cleanup(e, tb):
    global _scr
    if not _scr:
        return -1
    _scr = None
    if setting.use_trace:
        l = _log[:]
        # enable below to stop stream before exit (e.g. :q)
        #if l and l[-1] == kbd.ENTER:
        #    del l[-1]
        if trace.write(setting.get_trace_path(), l, e, tb):
            log.error("Failed to write trace")
    if _fd:
        _fd.close()

def cleanup_no_trace():
    cleanup(None, [])

def getch():
    if setting.use_getch:
        return _scr.getch()
    else:
        return kbd.QUIT

def refresh():
    clrl()
    test_flash()
    if _message: # prefer _message to _banner
        addstr(0, _message)
        if _cursor != -1:
            chgat(_cursor, _message, _cursor_attr)
    elif _banner:
        addstr(0, ''.join(_banner))
    _scr.refresh()

def __chgat(x, s, attr):
    _scr.chgat(0, x, 1, attr | screen.A_COLOR_FB)

def __alt_chgat(x, s, attr):
    if x < len(s):
        c = s[x]
    else:
        c = ' '
    addstr(x, c, attr)

def resize():
    try:
        set_message('')
        _scr.resize(get_size_y(), get_size_x())
        _scr.mvwin(get_position_y(), get_position_x())
    except screen.Error as e:
        log.error(resize, e)

def addstr(x, s, attr=screen.A_NONE):
    if len(s) > get_size_x():
        s = s[:get_size_x()-1]
        s += "~"
    try:
        _scr.addstr(0, x, s, attr | screen.A_COLOR_FB)
    except screen.Error as e:
        # error unless attempt to write to lower right corner
        if not ((0 == screen.get_size_y() - 1) and \
            (x + len(s) - 1 == screen.get_size_x() - 1)):
            log.error(addstr, e, x, s)

def clrl():
    _scr.move(0, 0)
    _scr.clrtoeol()

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
    if isinstance(o, AssertionError):
        _message = repr(o) # always show "AssertionError" as s may be ""
        _cursor = -1
    elif isinstance(o, Exception):
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

def get_default_class():
    from . import void
    return void.Console

def open_console_log(prefix):
    s = util.get_timestamp(prefix)
    f = os.path.join(setting.get_user_dir(), s + ".log")
    return kernel.fcreat_text(f)
