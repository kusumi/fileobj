# Copyright (c) 2010-2016, Tomohiro Kusumi
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
import string
import sys

from . import console
from . import filebytes
from . import fileobj
from . import kbd
from . import methods
from . import setting
from . import util

EDIT, MOTION, ESCAPE = range(3)

class Console (console.Console):
    def handle_signal(self):
        self.co.flash("Interrupted")
        return kbd.INTERRUPT

    def dispatch(self, arg):
        try:
            self.test()
            self.co.discard_eof()
            self.__listen(arg)
            assert not self.co.is_barrier_active()
        except fileobj.FileobjError as e:
            self.co.flash(e)
        finally:
            self.co.cleanup_region()
            self.co.restore_eof()
            self.co.lrepaintf()
            self.set_console(None)

    def __listen(self, arg):
        if arg.start != -1:
            methods.go_to(self, arg.start)
        self.go_right(arg.delta)
        assert self.co.get_barrier(
            setting.barrier_size) != -1

        l = []
        while True:
            if arg.limit == 0:
                x = kbd.ESCAPE
            else:
                x = self.read_incoming()
            ret = None
            if self.test_write(x):
                ret = self.handle_write(x)
            elif x in (kbd.ESCAPE, kbd.INTERRUPT):
                ret = self.handle_escape()
            elif x == kbd.RESIZE:
                ret = self.handle_resize()
            elif x == kbd.UP:
                ret = self.go_up()
            elif x == kbd.DOWN:
                ret = self.go_down()
            elif x == kbd.LEFT:
                ret = self.go_left()
            elif x == kbd.RIGHT:
                ret = self.go_right()
            elif x != kbd.ERROR:
                self.co.flash()

            if ret == EDIT:
                if arg.limit != -1:
                    arg.limit -= 1
                self.__enqueue(l, ret, x)
            elif ret == MOTION:
                if arg.limit > 0:
                    self.co.put_barrier()
                    break
                self.__enqueue(l, ret, x)
            elif ret == ESCAPE:
                if arg.limit > 0 or not l:
                    self.co.put_barrier()
                    break
                k, v = zip(*l)
                if (MOTION in k) or x == kbd.INTERRUPT:
                    arg.amp = 1
                self.co.set_pos(self.co.put_barrier())
                self.co.test_access()
                if len(l) == 1:
                    self.__sync(arg.amp, k[0], v[0], arg)
                else:
                    self.co.disconnect_workspace()
                    for x in range(arg.amp):
                        for i in range(len(l)):
                            self.__sync(1, k[i], v[i], arg)
                    self.co.reconnect_workspace()
                self.go_left()
                break
            if setting.use_debug:
                console.set_banner(
                    self.co.get_barrier_range())

    def __enqueue(self, l, key, x):
        if key == EDIT:
            value = x
        elif key == MOTION:
            value = self.co.get_pos()
        if l and l[-1][0] == key:
            l[-1][1].append(value)
        else:
            l.append((key, [value]))

    def __sync(self, n, key, seq, arg):
        if key == EDIT:
            if self.write_buffer(n, seq) == -1:
                pfn = self.co.get_prev_context()
            else:
                pfn = None
            def fn(i):
                try:
                    self.co.discard_eof()
                    self.co.add_pos(arg.delta)
                    if pfn:
                        pfn(i)
                    else:
                        self.write_buffer(n, seq)
                    self.co.add_pos(-1)
                finally:
                    self.co.restore_eof()
            self.co.set_prev_context(fn)
        elif key == MOTION:
            self.co.set_pos(seq[-1])

class _insert (object):
    def test(self):
        methods.test_insert_raise(self)
        console.set_banner("insert")

class _replace (object):
    def test(self):
        methods.test_replace_raise(self)
        console.set_banner("replace")

_hexdigits = tuple(ord(x) for x in string.hexdigits)

class _binary (Console):
    def dispatch(self, arg):
        self.low = False
        return super(_binary, self).dispatch(arg)

    def test_write(self, x):
        return x in _hexdigits

    def handle_write(self, x):
        self.write(int(chr(x), 16)) # e.g. pass 10 if x is 0x41
        self.co.lrepaintf(self.low)
        return EDIT

    def handle_escape(self):
        if not self.low:
            self.go_left()
        else:
            self.co.lrepaintf()
            self.low = False
        return ESCAPE

    def handle_resize(self):
        self.co.resize()
        self.co.repaint(self.low)

    def go_up(self):
        methods.go_up(self)
        self.low = False
        return MOTION

    def go_down(self):
        methods.go_down(self)
        self.low = False
        return MOTION

    def go_right(self, n=1):
        methods.go_right(self, n)
        self.low = False
        return MOTION

    def go_left(self):
        methods.go_left(self)
        self.low = False
        return MOTION

    def write(self, x):
        self._do_write(x)
        if self.low:
            self.co.add_pos(1)
        self.low = not self.low

    def write_buffer(self, n, seq):
        seq = seq[:]
        pad = len(seq) % 2
        if pad:
            seq.append(0x30) # '0'
        self.low = False
        ret = self._do_write_buffer(n, seq, pad)
        self.co.add_pos(ret)

class BI (_binary, _insert):
    def _do_write(self, x):
        if not self.low:
            self.co.insert_current((x << 4,))
        else:
            c = self.co.read_current(1)
            self.co.replace_current((filebytes.ord(c) | x,))

    def _do_write_buffer(self, n, seq, pad):
        l = get_ascii_seq(seq) * n
        self.co.insert_current(l)
        return len(l)

class BR (_binary, _replace):
    def _do_write(self, x):
        c = self.co.read_current(1)
        xx = filebytes.ord(c) if c else 0
        if not self.low:
            xx &= 0x0F
            self.co.replace_current(((x << 4) | xx,))
        else:
            xx &= 0xF0
            self.co.replace_current((x | xx,))

    def _do_write_buffer(self, n, seq, pad):
        seq *= n
        if pad:
            siz = len(seq) // n
            for i in range(siz, siz * (n + 1), siz):
                x = self.co.get_pos() + i // 2 - 1
                if x < self.co.get_size():
                    b = self.co.read(x, 1)
                else:
                    b = filebytes.ZERO
                seq[i - 1] = ord(hex(filebytes.ord(b) & 0x0F)[2:])
        l = get_ascii_seq(seq)
        self.co.replace_current(l)
        return len(l)

class RangeBR (BR):
    def write_buffer(self, n, seq):
        methods.range_replace(
            self, None, None, get_ascii(*seq[:2]), None)
        return -1

class BlockBR (BR):
    def write_buffer(self, n, seq):
        methods.block_replace(
            self, None, None, get_ascii(*seq[:2]), None)
        return -1

class _ascii (Console):
    def test_write(self, x):
        # include 9 to 13 -> \t\n\v\f\r
        return kbd.isgraph(x) or kbd.isspace(x)

    def handle_write(self, x):
        self.write(x)
        self.co.lrepaintf()
        return EDIT

    def handle_escape(self):
        self.go_left()
        return ESCAPE

    def handle_resize(self):
        self.co.resize()
        self.co.repaint()

    def go_up(self):
        methods.go_up(self)
        return MOTION

    def go_down(self):
        methods.go_down(self)
        return MOTION

    def go_right(self, n=1):
        methods.go_right(self, n)
        return MOTION

    def go_left(self):
        methods.go_left(self)
        return MOTION

    def write(self, x):
        self._do_write(x)
        self.co.add_pos(1)

    def write_buffer(self, n, seq):
        ret = self._do_write_buffer(n, seq)
        self.co.add_pos(ret)

class AI (_ascii, _insert):
    def _do_write(self, x):
        self.co.insert_current((x,))

    def _do_write_buffer(self, n, seq):
        l = seq * n
        self.co.insert_current(l)
        return len(l)

class AR (_ascii, _replace):
    def _do_write(self, x):
        self.co.replace_current((x,))

    def _do_write_buffer(self, n, seq):
        l = seq * n
        self.co.replace_current(l)
        return len(l)

class RangeAR (AR):
    def write_buffer(self, n, seq):
        methods.range_replace(
            self, None, None, seq[0], None)
        return -1

class BlockAR (AR):
    def write_buffer(self, n, seq):
        methods.block_replace(
            self, None, None, seq[0], None)
        return -1

def get_ascii(upper, lower):
    # e.g. 52,49 ('4','1') -> 0x41
    hex_string = chr(upper) + chr(lower)
    return int(hex_string, 16)

def get_ascii_seq(seq):
    assert len(seq) % 2 == 0
    r = range(0, len(seq), 2)
    return [get_ascii(*seq[i : i + 2]) for i in r]

def get_insert_class():
    return __get_class("{0}I")

def get_replace_class():
    return __get_class("{0}R")

def get_range_replace_class():
    return __get_class("Range{0}R")

def get_block_replace_class():
    return __get_class("Block{0}R")

def __get_class(s):
    return getattr(sys.modules[__name__],
        s.format(setting.editmode))

def get_input_limit():
    if setting.editmode == 'B':
        return 2
    else:
        return 1

class Arg (util.Namespace):
    def __init__(self, **d):
        d.setdefault("amp", 1)
        d.setdefault("start", -1)
        d.setdefault("delta", 0)
        d.setdefault("limit", -1)
        super(Arg, self).__init__(**d)
