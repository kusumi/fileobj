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

from __future__ import division

from . import candidate
from . import history
from . import kbd
from . import literal
from . import screen
from . import util

class Operand (object):
    def __init__(self):
        self.__history = history.History(None)
        self.__prev = util.Namespace(key=kbd.ERROR, ope='', arg='', raw=[])
        self.init([], [], [])

    def init(self, rl, fl, sl):
        # args must be sorted
        self.__regs = rl
        self.__fasts = fl
        self.__slows = sl
        self.__cand = {
            None : candidate.LiteralCandidate(self.__slows),
        }
        l = literal.get_arg_literals()
        a = candidate.LiteralCandidate(l)
        p = candidate.PathCandidate()
        for li in self.__slows:
            if li is literal.s_set:
                self.__cand[li.str] = a
            if li is literal.s_e or \
                li is literal.s_w or \
                li is literal.s_wneg or \
                li is literal.s_wq or \
                li is literal.s_split or \
                li is literal.s_bdelete:
                self.__cand[li.str] = p
        self.clear()

    def cleanup(self):
        self.__history.flush()

    def clear(self):
        self.__cursor = 0
        self.__amp = []
        self.__buf = []
        self.__ope = []
        self.__arg = [] # list of strings

    def get_prev_history(self, c):
        return self.__history.get_latest(c)

    def __add_history(self):
        key = chr(self.__buf[0])
        s = _to_string(self.__buf)
        if s != key:
            if self.__history.get_latest(key) != s:
                self.__history.append(key, s)
            self.__history.reset_cursor(key)

    def __get_older_history(self):
        buf = self.__prev.raw
        assert buf and buf[0] in literal.get_slow_ords()
        x = _to_string(buf)
        s = self.__history.get_older(x[0], x)
        if not s:
            s = self.__history.get_newer(x[0], x)
            if not s:
                s = x
        assert s[0] == x[0]
        self.__set_string(s)

    def __get_newer_history(self):
        buf = self.__prev.raw
        assert buf and buf[0] in literal.get_slow_ords()
        x = _to_string(buf)
        s = self.__history.get_newer(x[0], x)
        if not s:
            s = x
        assert s[0] == x[0]
        self.__set_string(s)

    def __clear_candidate(self):
        self.__cand[None].clear()
        for o in self.__cand.values():
            o.clear()

    def __get_min_cursor(self):
        return 1
    def __at_min_cursor(self):
        return self.__cursor <= self.__get_min_cursor()

    def __get_max_cursor(self):
        return screen.get_size_x() - 2
    def __at_max_cursor(self):
        return self.__cursor >= self.__get_max_cursor()

    def __get_tail_cursor(self):
        return len(self.__buf)
    def __at_tail_cursor(self):
        return self.__cursor == self.__get_tail_cursor()

    def __add_buffer(self, c):
        self.__buf.insert(self.__cursor, c)
        self.__cursor += 1
        self.__parse_buffer()

    def __set_buffer(self, l):
        self.clear()
        self.__buf = list(l)
        self.__cursor = len(self.__buf)
        self.__parse_buffer()

    def __set_string(self, s):
        self.__set_buffer([ord(x) for x in s])

    def __parse_buffer(self):
        self.__arg = []
        if not _is_slow(self.__buf):
            self.__ope = self.__buf
        else:
            l = _to_string(self.__buf).split(' ')
            for i, s in enumerate(l):
                if i == 0:
                    self.__ope = [ord(x) for x in s]
                elif s:
                    self.__arg.append(s)

    def process_incoming(self, x):
        if _is_null(self.__buf) and not self.__scan_amp(x):
            return None, \
                None, None, None, None, \
                None, -1

        a = _get_type(self.__buf)
        if a == _null:
            ret = self.__scan_null(x)
        elif a == _fast:
            ret = self.__scan_fast(x)
        else:
            ret = self.__scan_slow(x)
        if not ret:
            msg = None
            if a != _fast:
                msg = _to_string(self.__buf)
            return None, \
                None, None, None, None, \
                msg, self.__cursor

        a = _get_type(self.__buf)
        if a == _null:
            li = self.__match_null()
        elif a == _fast:
            li = self.__match_fast()
        else:
            li = self.__match_slow()

        amp = None
        if self.__amp:
            amp = int(_to_string(self.__amp))
            if amp > util.MAX_INT:
                amp = util.MAX_INT
            elif amp < util.MIN_INT:
                amp = util.MIN_INT
        ope = ''
        if util.is_graph_sequence(self.__ope):
            ope = _to_string(self.__ope)
        msg = None
        if _is_slow(self.__buf):
            msg = li.str
        return li, \
            amp, ope, self.__arg[:], self.__buf[:], \
            msg, self.__cursor

    def __scan_amp(self, x):
        if self.__amp:
            if not _is_digit(x):
                return True
        elif x == 0x30 or not _is_digit(x): # '0'
            return True # 0 for literal.zero
        self.__amp.append(x)
        return False

    def __scan_null(self, x):
        if x == kbd.ESCAPE:
            self.clear()
            return True
        elif x == kbd.RESIZE:
            self.__set_buffer(literal.resize.seq)
            return True
        else:
            self.__add_buffer(x)
            return not _is_slow(self.__buf)

    def __scan_fast(self, x):
        if x == kbd.ESCAPE:
            self.clear()
            return True
        elif x == kbd.RESIZE:
            self.__set_buffer(literal.resize.seq)
            return True
        else:
            self.__add_buffer(x)
            return True

    def __scan_slow(self, x):
        self.__scan_slow_prev(x)
        if x == kbd.ESCAPE:
            self.__add_history()
            self.__clear_candidate()
            self.clear()
            return True
        elif x == kbd.RESIZE:
            self.__set_buffer(literal.resize.seq)
            return True
        elif x == kbd.TAB:
            return self.__scan_slow_tab()
        elif x in (kbd.UP, util.ctrl('p')):
            self.__get_older_history()
            return False
        elif x in (kbd.DOWN, util.ctrl('n')):
            self.__get_newer_history()
            return False
        elif x == kbd.LEFT:
            if self.__cursor > self.__get_min_cursor():
                self.__cursor -= 1
            return False
        elif x == kbd.RIGHT:
            if self.__cursor < self.__get_tail_cursor():
                self.__cursor += 1
            return False
        elif x == kbd.BACKSPACE:
            self.__backspace_slow()
            return False
        elif x == kbd.DELETE:
            self.__delete_slow()
            return False
        elif x == util.ctrl('a'):
            self.__cursor = self.__get_min_cursor()
            return False
        elif x == util.ctrl('e'):
            self.__cursor = self.__get_tail_cursor()
            return False
        elif x == util.ctrl('k'):
            self.__buf[self.__cursor:] = ''
            self.__parse_buffer()
            return False
        elif x == kbd.ENTER:
            self.__parse_buffer()
            self.__add_history()
            self.__clear_candidate()
            return True
        elif util.is_graph(x):
            if len(self.__ope) < self.__get_max_cursor():
                self.__add_buffer(x)
            return False
        else:
            return False

    def __scan_slow_prev(self, x):
        prev_key = self.__prev.key
        if prev_key != kbd.TAB and x == kbd.TAB:
            self.__parse_buffer()
            self.__prev.ope = _to_string(self.__ope)
            self.__prev.arg = self.__arg[:]
        elif prev_key not in _arrows and x in _arrows:
            self.__parse_buffer()
            self.__prev.raw = self.__buf[:]
        elif prev_key == kbd.TAB and x != kbd.TAB:
            self.__prev.ope = ''
            self.__prev.arg = ''
        elif prev_key in _arrows and x not in _arrows:
            self.__prev.raw = []
        self.__prev.key = x

    def __scan_slow_tab(self):
        if not self.__at_tail_cursor() or \
            self.__buf[self.__get_tail_cursor() - 1] == 0x20: # ' '
            return False
        ope = self.__prev.ope
        arg = self.__prev.arg
        if not arg:
            s = self.__cand[None].get(ope)
            if s:
                self.__set_string(s)
        elif len(arg) == 1 and ope in self.__cand:
            s = self.__cand[ope].get(arg[0])
            if s:
                self.__set_string("%s %s" % (ope, s))
        return False

    def __delete_slow(self):
        key = chr(self.__buf[0])
        if self.__at_tail_cursor():
            self.__backspace_slow()
        else:
            del self.__buf[self.__cursor]
        if not self.__buf:
            self.clear()
            self.__history.reset_cursor(key)
        self.__parse_buffer()

    def __backspace_slow(self):
        key = chr(self.__buf[0])
        if self.__at_min_cursor() and not self.__at_tail_cursor():
            return
        del self.__buf[self.__cursor - 1]
        self.__cursor -= 1
        if not self.__buf:
            self.clear()
            self.__history.reset_cursor(key)
        self.__parse_buffer()

    def __match_null(self):
        return literal.escape

    def __match_fast(self):
        beg = 0
        end = len(self.__fasts) - 1
        seq = tuple(self.__ope)
        while True:
            i = (beg + end) // 2
            o = self.__fasts[i]
            if o.match(seq):
                return o
            elif o.match_incomplete(seq):
                return None
            if seq < o.seq:
                end = i - 1
            else:
                beg = i + 1
            if beg > end:
                break

        for o in self.__regs:
            if o.match(seq):
                return o
            elif o.match_incomplete(seq):
                return None
        self.clear()
        return None

    def __match_slow(self):
        l = []
        for o in self.__slows:
            if o.match(self.__ope):
                return o
            elif o.match_incomplete(self.__ope):
                l.append(o)
        if len(l) == 1:
            s = "%s %s" % (l[0].str, ' '.join(self.__arg))
            self.__set_string(s.rstrip())
            return l[0]
        else:
            s = _to_string(self.__buf)
            return literal.InvalidLiteral(s, None, '')

_arrows = list(kbd.ARROWS)
_arrows.append(util.ctrl('p'))
_arrows.append(util.ctrl('n'))
_null, _fast, _slow = range(3)

def _to_string(l):
    return ''.join([chr(x) for x in l])

def _is_digit(x):
    return 0x30 <= x <= 0x39 # '0' <= x <= '9'

def _is_null(l):
    return _get_type(l) == _null
def _is_slow(l):
    return _get_type(l) == _slow

def _get_type(l):
    if not l:
        return _null
    elif l[0] in literal.get_slow_ords():
        return _slow
    else:
        return _fast
