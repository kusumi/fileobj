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

import collections
import sys
import termios
import tty

from . import kbd
from . import log
from . import screen
from . import setting
from . import util

_stdin = sys.stdin
_attr = None

class _window (screen.window):
    def init(self):
        init()
        self.__ib = collections.deque()
        self.__ob = collections.deque()

    def cleanup(self):
        cleanup()
        self.__clear_input()
        self.__clear_output()

    def __clear_input(self):
        self.__ib.clear()

    def __clear_output(self):
        self.__ob.clear()

    def __append_input(self, s):
        self.__ib.extend(s)

    def __append_output(self, s):
        self.__ob.extend(s)

    def __get_output(self):
        try:
            return self.__ob.popleft()
        except IndexError:
            return -1

    def __input_to_string(self):
        return ''.join(self.__ib)

    def getch(self):
        x = self.__get_output()
        if x != -1:
            return ord(x)
        x = _stdin.read(1)
        s = self.__input_to_string()
        self.__append_input(x)
        if x == "\x1B": # ESCAPE
            if not s:
                return kbd.CONTINUE
        elif x == "[":
            if s == "\x1B":
                return kbd.CONTINUE
        elif x == "A":
            if s == "\x1B[":
                self.__clear_input()
                return kbd.UP
        elif x == "B":
            if s == "\x1B[":
                self.__clear_input()
                return kbd.DOWN
        elif x == "C":
            if s == "\x1B[":
                self.__clear_input()
                return kbd.RIGHT
        elif x == "D":
            if s == "\x1B[":
                self.__clear_input()
                return kbd.LEFT
        elif x == "3":
            if s == "\x1B[":
                return kbd.CONTINUE
        elif x == "~":
            if s == "\x1B[3":
                self.__clear_input()
                return kbd.DELETE
        if s and x == s[-1]:
            s = s[:-1]
        self.__append_output(s)
        self.__append_output(x)
        self.__clear_input()
        return kbd.CONTINUE

    def addstr(self, y, x, s, attr=screen.def_attr):
        util.printf(self.mkstr(y, x, s))

def newwin(leny, lenx, begy, begx, ref=None):
    return _window(leny, lenx, begy, begx, ref)

def init():
    global _attr
    if _attr:
        return -1
    _attr = termios.tcgetattr(_stdin)
    if setting.use_stdin_cbreak:
        tty.setcbreak(_stdin)
        log.debug("Set tty cbreak")

def cleanup():
    global _attr
    if not _attr:
        return -1
    termios.tcsetattr(_stdin, termios.TCSANOW, _attr)
    _attr = None
    log.debug("Restore tty attr")
