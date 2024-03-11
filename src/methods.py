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

from __future__ import division
from __future__ import with_statement
import base64
import os
import platform
import sys
import time

from . import disas_x86
from . import filebytes
from . import fileobj
from . import kbd
from . import kernel
from . import literal
from . import native
from . import panel
from . import path
from . import screen
from . import setting
from . import terminal
from . import util
from . import version

HANDLED  = None
REWIND   = "REWIND"
CONTINUE = "CONTINUE"
RETURN   = "RETURN"
QUIT     = "QUIT"
ERROR    = "ERROR"
QUEUED   = "QUEUED"

def _cleanup(fn):
    def _(self, amp, opc, args, raw):
        try:
            und = self.co.get_undo_size()
            return fn(self, amp, opc, args, raw)
        except fileobj.Error as e:
            self.co.merge_undo_until(und)
            self.co.lrepaintf()
            self.co.flash(e)
            return ERROR
        except MemoryError as e: # do the same
            self.co.merge_undo_until(und)
            self.co.lrepaintf()
            self.co.flash(e)
            return ERROR
    return _

def __read_chr(self, pos):
    return filebytes.ord(self.co.read(pos, 1))

def test_insert_raise(self):
    __test_permission_raise(self, "insert")

def test_replace_raise(self):
    __test_permission_raise(self, "replace")

def test_delete_raise(self):
    __test_permission_raise(self, "delete")

def test_truncate_raise(self):
    __test_permission_raise(self, "truncate")

def __test_permission_raise(self, s):
    fn = getattr(self.co, "test_" + s)
    if not fn():
        self.co.raise_no_support(s)

def test_empty_raise(self):
    if self.co.is_empty():
        raise fileobj.Error("Empty buffer")

def get_int(amp):
    if amp is None:
        return 1
    else:
        return amp

def __get_range(self):
    beg, end, map = self.co.get_region_range()
    return beg, end - beg + 1

def __get_block(self):
    beg, end, map = self.co.get_region_range()
    siz = end % map.x - beg % map.x + 1
    cnt = (end - beg) // map.x + 1
    return beg, end, map.x, siz, cnt

def __exec_lrepaint(self, fn, i=0):
    __call_context_lrepaint(self, fn, i)
    self.co.set_prev_context(fn)

def __exec_prepaint(self, fn, num, i=0):
    __call_context_prepaint(self, fn, num, i)
    self.co.set_prev_context(fn)

def __call_context_lrepaint(self, fn, i=0):
    fn(i)
    self.co.lrepaintf()

def __call_context_prepaint(self, fn, num, i=0):
    fn(i)
    self.co.prepaintf(num)

def __assert_bpu_aligned(self):
    if not setting.use_unit_based:
        return
    pos = self.co.get_pos()
    if setting.use_debug:
        assert pos % setting.bytes_per_unit == 0, pos
    elif pos % setting.bytes_per_unit:
        self.co.set_unit_pos(pos)

def cursor_up(self, amp, opc, args, raw):
    go_up(self, amp)

def cursor_down(self, amp, opc, args, raw):
    go_down(self, amp)

def cursor_left(self, amp, opc, args, raw):
    go_left(self, amp)

def cursor_right(self, amp, opc, args, raw):
    go_right(self, amp)

def cursor_pprev(self, amp, opc, args, raw):
    go_pprev(self, amp)

def cursor_hpprev(self, amp, opc, args, raw):
    go_hpprev(self, amp)

def cursor_pnext(self, amp, opc, args, raw):
    go_pnext(self, amp)

def cursor_hpnext(self, amp, opc, args, raw):
    go_hpnext(self, amp)

def cursor_head(self, amp, opc, args, raw):
    go_head(self, amp)

def cursor_tail(self, amp, opc, args, raw):
    go_tail(self, amp)

def cursor_lhead(self, amp, opc, args, raw):
    go_lhead(self, amp)

def cursor_ltail(self, amp, opc, args, raw):
    go_ltail(self, amp)

def cursor_up_lhead(self, amp, opc, args, raw):
    go_up_lhead(self, amp)

def cursor_down_lhead(self, amp, opc, args, raw):
    go_down_lhead(self, amp)

def cursor_phead(self, amp, opc, args, raw):
    go_phead(self, amp)

def cursor_pcenter(self, amp, opc, args, raw):
    go_pcenter(self, amp)

def cursor_ptail(self, amp, opc, args, raw):
    go_ptail(self, amp)

def cursor_to(self, amp, opc, args, raw):
    go_to(self, amp)

def __get_logical_block_size(self):
    ret = setting.logical_block_size
    if ret > 0:
        assert ret % 512 == 0, ret
        return ret
    ret = self.co.get_sector_size()
    if ret == -1:
        return 512
    else:
        assert ret % 512 == 0, ret
        return ret

def cursor_sector_left(self, amp, opc, args, raw):
    n = get_int(amp) if amp else 1
    assert n != 0, amp
    if n >= 0:
        __cursor_sector_left(self, n)
    else:
        __cursor_sector_right(self, -n)

def cursor_sector_right(self, amp, opc, args, raw):
    n = get_int(amp) if amp else 1
    assert n != 0, amp
    if n >= 0:
        __cursor_sector_right(self, n)
    else:
        __cursor_sector_left(self, -n)

def __cursor_sector_left(self, n):
    sector_size = __get_logical_block_size(self)
    cur = self.co.get_pos()
    if cur % sector_size == 0:
        pos = cur
        pos -= sector_size * n
    else:
        pos = util.align_head(cur, sector_size)
        assert n > 0, n
        pos -= sector_size * (n - 1)
    go_to(self, pos)

def __cursor_sector_right(self, n):
    sector_size = __get_logical_block_size(self)
    cur = self.co.get_pos()
    if cur % sector_size == 0:
        pos = cur
        pos += sector_size * n
    else:
        pos = util.align_tail(cur, sector_size)
        assert n > 0, n
        pos += sector_size * (n - 1)
    go_to(self, pos)

def cursor_sector_shead(self, amp, opc, args, raw):
    sector_size = __get_logical_block_size(self)
    pos = util.align_head(self.co.get_pos(), sector_size)
    go_to(self, pos)

def cursor_sector_stail(self, amp, opc, args, raw):
    n = get_int(amp) if amp else 1
    sector_size = __get_logical_block_size(self)
    pos = util.align_head(self.co.get_pos(), sector_size)
    pos += (sector_size - 1)
    if n > 1:
        pos += sector_size * (n - 1)
    go_to(self, pos)

def cursor_sector_to(self, amp, opc, args, raw):
    n = get_int(amp) if amp else 0
    sector_size = __get_logical_block_size(self)
    go_to(self, sector_size * n)

def go_up(self, amp=None):
    if self.co.go_up(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_down(self, amp=None):
    if self.co.go_down(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_left(self, amp=None):
    if self.co.go_left(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_right(self, amp=None):
    if self.co.go_right(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_pprev(self, amp=None):
    if self.co.go_pprev(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_hpprev(self, amp=None):
    if self.co.go_hpprev(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_pnext(self, amp=None):
    if self.co.go_pnext(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_hpnext(self, amp=None):
    if self.co.go_hpnext(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_head(self, amp=None):
    if self.co.go_head(get_int(amp) - 1) == -1:
        self.co.lrepaintf()

def go_tail(self, amp=None):
    if self.co.go_tail(get_int(amp) - 1) == -1:
        self.co.lrepaintf()

def go_lhead(self, amp=None):
    if self.co.go_lhead() == -1:
        self.co.lrepaintf()

def go_ltail(self, amp=None):
    if self.co.go_ltail(get_int(amp) - 1) == -1:
        self.co.lrepaintf()

def go_up_lhead(self, amp=None):
    go_up(self, amp)
    go_lhead(self, amp)

def go_down_lhead(self, amp=None):
    go_down(self, amp)
    go_lhead(self, amp)

def go_phead(self, amp=None):
    if self.co.go_phead(get_int(amp) - 1) == -1:
        self.co.lrepaintf()

def go_pcenter(self, amp=None):
    if self.co.go_pcenter() == -1:
        self.co.lrepaintf()

def go_ptail(self, amp=None):
    if self.co.go_ptail(get_int(amp) - 1) == -1:
        self.co.lrepaintf()

def go_to(self, amp=None):
    if amp is None:
        pos = 0
    else:
        pos = get_int(amp)
    if self.co.go_to(pos) == -1:
        self.co.lrepaintf()

def __isprint(b):
    return util.isprint(filebytes.ord(b))

def __is_zero(b):
    return b == filebytes.ZERO

def __is_non_zero(b):
    return b != filebytes.ZERO

def cursor_next_char(self, amp, opc, args, raw):
    __cursor_next_matched(self, get_int(amp), __isprint)

def cursor_next_current(self, amp, opc, args, raw):
    curb = self.co.read(self.co.get_pos(), 1)
    if not curb:
        def __is_current(b):
            return False
    else:
        def __is_current(b):
            return b == curb
    __cursor_next_matched(self, get_int(amp), __is_current)

def cursor_next_zero(self, amp, opc, args, raw):
    __cursor_next_matched(self, get_int(amp), __is_zero)

def cursor_next_nonzero(self, amp, opc, args, raw):
    __cursor_next_matched(self, get_int(amp), __is_non_zero)

def cursor_prev_char(self, amp, opc, args, raw):
    __cursor_prev_matched(self, get_int(amp), __isprint)

def cursor_prev_current(self, amp, opc, args, raw):
    curb = self.co.read(self.co.get_pos(), 1)
    if not curb:
        def __is_current(b):
            return False
    else:
        def __is_current(b):
            return b == curb
    __cursor_prev_matched(self, get_int(amp), __is_current)

def cursor_prev_zero(self, amp, opc, args, raw):
    __cursor_prev_matched(self, get_int(amp), __is_zero)

def cursor_prev_nonzero(self, amp, opc, args, raw):
    __cursor_prev_matched(self, get_int(amp), __is_non_zero)

def __cursor_next_matched(self, cnt, fn):
    pos = self.co.get_pos()
    end = self.co.get_max_pos() # stop if > end
    ret, cnt = __cursor_next_matched_goto(self, pos + 1, end, cnt, fn)
    if ret == -1:
        if not setting.use_wrapscan or \
            __cursor_next_matched_goto(self, 0, pos - 1, cnt, fn)[0] == -1:
            self.co.flash("Search failed")

def __cursor_next_matched_goto(self, pos, end, cnt, fn):
    n = self.co.get_buffer_size()
    while True:
        if pos > end:
            return -1, cnt
        b = self.co.read(pos, n)
        d = 0
        for x in filebytes.iter(b):
            if fn(x):
                cnt -= 1
                if not cnt:
                    go_to(self, pos + d)
                    return None, None
            d += 1
        pos += n
        if len(b) < n:
            return -1, cnt
        if screen.test_signal():
            self.co.flash("Search interrupted")
            return None, None

def __cursor_prev_matched(self, cnt, fn):
    pos = self.co.get_pos()
    end = 0 # stop if <= end
    ret, cnt = __cursor_prev_matched_goto(self, pos, end, cnt, fn)
    if ret == -1:
        beg = self.co.get_max_pos() + 1 # need +1 to start at max pos
        if not setting.use_wrapscan or \
            __cursor_prev_matched_goto(self, beg, pos, cnt, fn)[0] == -1:
            self.co.flash("Search failed")

def __cursor_prev_matched_goto(self, pos, end, cnt, fn):
    n = self.co.get_buffer_size()
    while True:
        if pos < n:
            n = pos
            pos = 0
        else:
            pos -= n
        b = self.co.read(pos, n)
        d = 0
        for x in filebytes.riter(b):
            if fn(x):
                cnt -= 1
                if not cnt:
                    go_to(self, pos + len(b) - 1 - d)
                    return None, None
            d += 1
        if pos <= end:
            return -1, cnt
        if screen.test_signal():
            self.co.flash("Search interrupted")
            return None, None

def cursor_next_zero_sector(self, amp, opc, args, raw):
    n = __get_logical_block_size(self)
    z = filebytes.ZERO * n
    def fn(b):
        return b == z
    __cursor_next_matched_block(self, get_int(amp), fn, n)

def cursor_next_non_zero_sector(self, amp, opc, args, raw):
    n = __get_logical_block_size(self)
    z = filebytes.ZERO * n
    def fn(b):
        return b != z
    __cursor_next_matched_block(self, get_int(amp), fn, n)

def cursor_prev_zero_sector(self, amp, opc, args, raw):
    n = __get_logical_block_size(self)
    z = filebytes.ZERO * n
    def fn(b):
        return b == z
    __cursor_prev_matched_block(self, get_int(amp), fn, n)

def cursor_prev_non_zero_sector(self, amp, opc, args, raw):
    n = __get_logical_block_size(self)
    z = filebytes.ZERO * n
    def fn(b):
        return b != z
    __cursor_prev_matched_block(self, get_int(amp), fn, n)

def __cursor_next_matched_block(self, cnt, fn, n):
    if self.co.get_size() < n:
        self.co.flash("Search failed")
        return
    # both pos / end inclusive
    pos = util.align_tail(self.co.get_pos() + 1, n) # next block head
    end = util.align_head(self.co.get_max_pos(), n) # last block head
    ret, cnt = __cursor_next_matched_block_goto(self, pos, end, cnt, fn, n)
    if ret == -1:
        if not setting.use_wrapscan or __cursor_next_matched_block_goto(self, 0,
            pos - n, cnt, fn, n)[0] == -1:
            self.co.flash("Search failed")

def __cursor_next_matched_block_goto(self, pos, end, cnt, fn, n):
    assert end % n == 0, end
    while True:
        assert pos % n == 0, pos
        if pos > end:
            return -1, cnt
        b = self.co.read(pos, n)
        if len(b) < n:
            return -1, cnt
        if fn(b):
            cnt -= 1
            if not cnt:
                go_to(self, pos)
                return None, None
        pos += len(b)
        if screen.test_signal():
            self.co.flash("Search interrupted")
            return None, None

def __cursor_prev_matched_block(self, cnt, fn, n):
    if self.co.get_size() < n:
        self.co.flash("Search failed")
        return
    # both pos / end inclusive
    pos = util.align_head(self.co.get_pos() - 1, n) # previous block head
    end = 0 # first block head
    ret, cnt = __cursor_prev_matched_block_goto(self, pos, end, cnt, fn, n)
    if ret == -1:
        beg = util.align_head(self.co.get_max_pos(), n) # last block head
        if not setting.use_wrapscan or __cursor_prev_matched_block_goto(self,
            beg, pos + n, cnt, fn, n)[0] == -1:
            self.co.flash("Search failed")

def __cursor_prev_matched_block_goto(self, pos, end, cnt, fn, n):
    assert end % n == 0, end
    while True:
        assert pos % n == 0, pos
        if pos < end:
            return -1, cnt
        b = self.co.read(pos, n)
        # len(b) < n can happen at last page of unaligned size buffer
        if len(b) == n and fn(b):
            cnt -= 1
            if not cnt:
                go_to(self, pos)
                return None, None
        pos -= n # not len(b)
        if screen.test_signal():
            self.co.flash("Search interrupted")
            return None, None

_initial_delayed_input_ignore_duration = 1000
def start_read_delayed_input(self, amp, opc, args, raw):
    # XXX heuristic
    if util.get_elapsed_time() < _initial_delayed_input_ignore_duration:
        return
    self.co.start_read_delayed_input(literal.bracket2_beg.seq[0],
        literal.bracket2_end.seq[0])
    self.co.show(opc[0])

def end_read_delayed_input(self, amp, opc, args, raw):
    s = self.co.end_read_delayed_input()
    self.co.show('')
    self.ope.clear()
    ret = util.eval_size_repr(s, self.co.get_sector_size())
    if ret == 0:
        return
    elif ret is None:
        self.co.flash()
        return
    for s in str(ret):
        if self.ope.process_incoming(ord(s))[0]:
            self.co.flash()
            return
    return CONTINUE

def switch_to_first_buffer(self, amp, opc, args, raw):
    if self.co.get_buffer_count() > 1:
        self.co.switch_to_first_buffer()
        self.co.lrepaintf()
        return RETURN

def switch_to_last_buffer(self, amp, opc, args, raw):
    if self.co.get_buffer_count() > 1:
        self.co.switch_to_last_buffer()
        self.co.lrepaintf()
        return RETURN

def switch_to_next_buffer(self, amp, opc, args, raw):
    if self.co.get_buffer_count() > 1:
        self.co.switch_to_next_buffer()
        self.co.lrepaintf()
        return RETURN

def switch_to_prev_buffer(self, amp, opc, args, raw):
    if self.co.get_buffer_count() > 1:
        self.co.switch_to_prev_buffer()
        self.co.lrepaintf()
        return RETURN

def handle_mouse_event(self, amp, opc, args, raw):
    handled = False
    devid, x, y, z, bstate = screen.getmouse()
    if bstate & screen.BUTTON1_CLICKED:
        __mouse_go_to(self, y, x)
        handled = True
    if bstate & screen.BUTTON1_PRESSED:
        __mouse_enter_visual(self, y, x)
        handled = True
    if bstate & screen.BUTTON1_RELEASED:
        # need to handle, but nothing to do
        handled = True
    if bstate & screen.BUTTON1_DOUBLE_CLICKED:
        __mouse_enter_line_visual(self, y, x)
        handled = True
    if bstate & screen.BUTTON1_TRIPLE_CLICKED: # ignored on Windows
        __mouse_enter_block_visual(self, y, x)
        handled = True
    if bstate & screen.REPORT_MOUSE_POSITION:
        __show_mouse_event(self, devid, x, y, z, bstate)
        handled = True
    if not handled:
        __flash_mouse_event(self, devid, x, y, z, bstate)

# sub functions may change console and immediately return
def handle_mouse_event_visual(self, amp, opc, args, raw):
    handled = False
    devid, x, y, z, bstate = screen.getmouse()
    if bstate & screen.BUTTON1_CLICKED:
        return __mouse_update_visual(self, y, x)
        handled = True
    if bstate & screen.BUTTON1_PRESSED:
        return __mouse_start_scroll_visual(self, devid, y, x)
        handled = True
    if bstate & screen.BUTTON1_RELEASED:
        return __mouse_end_scroll_visual(self, devid, y, x)
        handled = True
    if bstate & screen.BUTTON1_DOUBLE_CLICKED:
        return __mouse_exit_visual(self, y, x)
        handled = True
    if bstate & screen.BUTTON1_TRIPLE_CLICKED: # ignored on Windows
        return __mouse_exit_visual(self, y, x)
        handled = True
    if bstate & screen.REPORT_MOUSE_POSITION:
        __show_mouse_event(self, devid, x, y, z, bstate)
        handled = True
    if not handled:
        __flash_mouse_event(self, devid, x, y, z, bstate)

def __show_mouse_event(self, devid, x, y, z, bstate):
    if setting.use_debug:
        self.co.show((__show_mouse_event, devid, x, y, z,
            screen.get_mouse_event_name(bstate)))

def __flash_mouse_event(self, devid, x, y, z, bstate):
    if setting.use_debug:
        self.co.flash((__flash_mouse_event, devid, x, y, z,
            screen.get_mouse_event_name(bstate)))
    else:
        self.co.flash()

# 1. if (y, x) is not in any workspace -> return -1
# 2. if (y, x) is not in current workspace -> switch workspace
# 3-1. if (y, x) is not in buffer contents -> return -2
# 3-2. else -> change position and return None
def __mouse_go_to(self, y, x):
    assert not self.co.has_region()
    if not self.co.is_geom_valid(y, x):
        self.co.flash("No editor window at {0}".format((y, x)))
        return -1
    if not self.co.has_geom(y, x):
        assert self.co.switch_to_geom_workspace(y, x) != -1
    pos = self.co.get_geom_pos(y, x)
    if pos == -1:
        self.co.lrepaint()
        return -2 # not in buffer contents
    else:
        self.co.go_to(pos)
        self.co.lrepaint()

def __mouse_enter_visual(self, y, x):
    assert not self.co.has_region()
    if __mouse_go_to(self, y, x) is None:
        self.co.queue_input(literal.v.seq)

def __mouse_enter_line_visual(self, y, x):
    assert not self.co.has_region()
    if __mouse_go_to(self, y, x) is None:
        self.co.queue_input(literal.V.seq)

def __mouse_enter_block_visual(self, y, x):
    assert not self.co.has_region()
    if __mouse_go_to(self, y, x) is None:
        self.co.queue_input(literal.ctrlv.seq)

def __mouse_exit_visual(self, y, x):
    assert self.co.has_region()
    if self.co.is_geom_valid(y, x):
        ret = __exit_visual(self)
        assert __mouse_go_to(self, y, x) != -1
        return ret
    else:
        self.co.flash("No editor window at {0}".format((y, x)))

def __mouse_update_visual(self, y, x):
    assert self.co.has_region()
    if self.co.has_geom(y, x): # in current workspace
        pos = self.co.get_geom_pos(y, x)
        if pos != -1: # in buffer contents
            self.co.go_to(pos)
            self.co.lrepaint()
    elif self.co.is_geom_valid(y, x): # in other workspace
        ret = __exit_visual(self)
        assert __mouse_go_to(self, y, x) != -1
        return ret
    else:
        self.co.flash("No editor window at {0}".format((y, x)))

# Note that scroll start/end need to be in current workspace,
# but don't need to be in buffer contents area.
_mouse_event_visual_pressed = None

def __mouse_start_scroll_visual(self, devid, y, x):
    global _mouse_event_visual_pressed
    assert self.co.has_region()
    if self.co.has_geom(y, x):
        _mouse_event_visual_pressed = devid, y, x
    else:
        _mouse_event_visual_pressed = None
        return __mouse_update_visual(self, y, x)

def __mouse_end_scroll_visual(self, devid, y, x):
    global _mouse_event_visual_pressed
    assert self.co.has_region()
    if _mouse_event_visual_pressed is None:
        return __mouse_update_visual(self, y, x)
    if not self.co.has_geom(y, x):
        _mouse_event_visual_pressed = None
        return __mouse_update_visual(self, y, x)
    # in current workspace with valid start position
    assert isinstance(_mouse_event_visual_pressed, tuple)
    start_devid, start_y, start_x = _mouse_event_visual_pressed
    assert devid == start_devid, (devid, start_devid)
    assert self.co.has_geom(start_y, start_x), (start_y, start_x)
    d = y - start_y
    if d > 0:
        go_down(self, d)
    elif d < 0:
        go_up(self, -d)
    # x delta is less trivial
    #d = (x - start_x) // (setting.bytes_per_unit + 1) # XXX
    #if d > 0:
    #    go_right(self, d)
    #elif d < 0:
    #    go_left(self, -d)
    _mouse_event_visual_pressed = None

def __exit_visual(self):
    from . import visual
    return visual._exit_visual(self)

def __raise_if_screen_resize_unsupported(self, amp, opc, args, raw):
    if not screen.is_resize_supported():
        screen.update_size() # must be first call after terminal resize
        if screen.is_size_changed_from_initial():
            # get a list of dirty buffers
            def fn(o):
                return o.is_dirty()
            l = self.co.get_buffer_paths(fn)
            # force quit, but not via QUIT
            ret = force_quit_all(self, amp, opc, args, raw)
            assert ret == QUIT, ret
            # force flash now as there's no next refresh
            screen.flash()
            # ready to bail out
            msg = ["Terminal resize unsupported on {0} {1}".format(
                util.get_os_name(), util.get_os_release())]
            if l:
                msg.append("Unsaved buffer")
                for f in l:
                    msg.append(f)
            raise util.QuietError('\n'.join(msg))

# the common entry point for KEY_RESIZE
def resize_container(self, amp, opc, args, raw):
    __raise_if_screen_resize_unsupported(self, amp, opc, args, raw)
    self.co.resize()
    self.co.repaint()

def refresh_container(self, amp, opc, args, raw):
    # XXX If in tmux, call resize() to possibly recover from a window
    # frame issue which happens after once changing to a different terminal.
    # e.g. Frames disappear on *BSD, and corrupt on Cygwin.
    # Not confirmed on Linux and Solaris.
    __refresh_container(self)

def __refresh_container(self):
    if terminal.is_screen():
        self.co.resize()
    else:
        self.co.refresh()
    self.co.repaint()

def switch_to_next_workspace(self, amp, opc, args, raw):
    if len(self.co) > 1:
        self.co.set_focus(False)
        self.co.switch_to_next_workspace()
        self.co.set_focus(True)
        return RETURN

def switch_to_prev_workspace(self, amp, opc, args, raw):
    if len(self.co) > 1:
        self.co.set_focus(False)
        self.co.switch_to_prev_workspace()
        self.co.set_focus(True)
        return RETURN

def switch_to_top_workspace(self, amp, opc, args, raw):
    if len(self.co) > 1:
        self.co.set_focus(False)
        self.co.switch_to_top_workspace()
        self.co.set_focus(True)
        return RETURN

def switch_to_bottom_workspace(self, amp, opc, args, raw):
    if len(self.co) > 1:
        self.co.set_focus(False)
        self.co.switch_to_bottom_workspace()
        self.co.set_focus(True)
        return RETURN

def add_workspace(self, amp, opc, args, raw):
    for x in util.get_xrange(get_int(amp)):
        if self.co.add_workspace(False) == -1:
            break
    self.co.repaint()

def add_workspace_vertical(self, amp, opc, args, raw):
    for x in util.get_xrange(get_int(amp)):
        if self.co.add_workspace(True) == -1:
            break
    if self.co.test_and_set_max_bytes_per_line() != -1:
        __rebuild(self)
    else:
        self.co.repaint()

def split_workspace(self, amp, opc, args, raw):
    __split_workspace(self, amp, opc, args, raw, False)

def split_workspace_vertical(self, amp, opc, args, raw):
    __split_workspace(self, amp, opc, args, raw, True)

def __split_workspace(self, amp, opc, args, raw, vertical):
    self.co.add_workspace(vertical)
    if args:
        open_buffer(self, amp, opc, args, raw)
    self.co.repaint()

def inc_workspace_height(self, amp, opc, args, raw):
    ret = self.co.adjust_workspace(get_int(amp))
    __parse_adjust_workspace(self, ret)

def dec_workspace_height(self, amp, opc, args, raw):
    ret = self.co.adjust_workspace(-get_int(amp))
    __parse_adjust_workspace(self, ret)

def __parse_adjust_workspace(self, ret):
    if ret is None:
        self.co.repaint()
    elif ret == -1:
        self.co.flash()
    elif ret > 0: # bytes_per_window
        self.co.flash("{0}[B] fixed size window".format(ret))
    else:
        assert False

def remove_workspace(self, amp, opc, args, raw):
    if self.co.remove_workspace() != -1:
        self.co.repaint()
    return RETURN

def remove_other_workspace(self, amp, opc, args, raw):
    if self.co.remove_other_workspace() != -1:
        self.co.repaint()

def __set_binary(self, args):
    setting.use_ascii_edit = False

def __set_ascii(self, args):
    setting.use_ascii_edit = True

def __set_le(self, args):
    setting.endianness = "little"

def __set_be(self, args):
    setting.endianness = "big"

def __set_ws(self, args):
    setting.use_wrapscan = True

def __set_nows(self, args):
    setting.use_wrapscan = False

def __set_ic(self, args):
    setting.use_ignorecase = True

def __set_noic(self, args):
    setting.use_ignorecase = False

def __set_si(self, args):
    setting.use_siprefix = True

def __set_nosi(self, args):
    setting.use_siprefix = False

def __set_address(self, args):
    if __set_radix_arg(self, args, "address_radix") == -1:
        return
    if __try_update_address_num_width(self) == -1:
        __rebuild(self)

def __set_radix_arg(self, args, name):
    if len(args) == 1:
        self.co.show(getattr(setting, name))
        return
    try:
        radix = args[1]
        x = int(radix)
    except Exception:
        self.co.flash("Invalid arg: " + radix)
        return
    if x in (16, 10, 8):
        if getattr(setting, name) == x:
            return -1
        setattr(setting, name, x)
    else:
        self.co.flash("Invalid arg: {0}".format(x))

def __set_bytes_per_line(self, args):
    prev = self.co.get_bytes_per_line()
    if len(args) == 1:
        self.co.show(prev)
    elif self.co.set_bytes_per_line(args[1]) == -1:
        self.co.flash("Invalid arg: " + args[1])
    elif self.co.get_bytes_per_line() != prev:
        __rebuild(self)

def __set_bytes_per_window(self, args):
    prev = self.co.get_bytes_per_window()
    if len(args) == 1:
        self.co.show(self.co.get_capacity())
    elif self.co.set_bytes_per_window(args[1]) == -1:
        try:
            bpw = int(args[1])
            if bpw > prev:
                self.co.flash("Too large arg: {0}".format(bpw))
            else:
                self.co.flash("Invalid arg: {0} ???".format(bpw))
        except ValueError:
            self.co.flash("Invalid arg: {0}".format(args[1]))
    elif self.co.get_bytes_per_window() != prev:
        __rebuild(self)

def __rebuild(self):
    screen.clear_refresh()
    self.co.build()
    self.co.repaint() # repaint regardless of build result

def __set_bytes_per_unit(self, args):
    prev = setting.bytes_per_unit
    if len(args) == 1:
        self.co.show(prev)
        return
    try:
        bpu = int(args[1])
    except ValueError:
        self.co.flash("Invalid arg: {0}".format(args[1]))
        return
    if not bpu:
        self.co.flash("Invalid arg: {0}".format(bpu))
        return

    if bpu != prev:
        setting.bytes_per_unit = bpu
        # update bpl first if not multiple of bpu
        unitlen = setting.bytes_per_unit
        bpl = self.co.get_bytes_per_line()
        if bpl % unitlen:
            nbpl = util.rounddown(bpl, unitlen)
            if self.co.set_bytes_per_line(nbpl) == -1:
                if self.co.set_bytes_per_line("max") == -1:
                    if setting.use_debug:
                        self.co.flash("Failed to set max bpl")
                    else:
                        self.co.flash("Failed to set to {0}".format(bpu))
                    setting.bytes_per_unit = prev
                    assert self.co.set_bytes_per_line(bpl) != -1, bpl
                    return
        assert self.co.get_bytes_per_line() % unitlen == 0
        # ready to build
        screen.clear_refresh()
        # rollback if build failed, or vbuild folded bpl and as a result made
        # inconsistency against setting.bytes_per_unit (updating bpl first
        # should eliminate inconsistency mostly...).
        if self.co.build_quiet() == -1 or \
            self.co.get_bytes_per_line() % unitlen:
            if setting.use_debug:
                self.co.flash("Failed to build")
            else:
                self.co.flash("Failed to set to {0}".format(bpu))
            setting.bytes_per_unit = prev
            self.co.build()
        self.co.repaint()

def __set_scroll_mode(self, args):
    if len(args) == 1:
        if setting.use_line_scroll:
            self.co.show("line")
        else:
            self.co.show("page")
    else:
        s = args[1]
        if s == "line":
            if setting.use_line_scroll:
                return
            setting.use_line_scroll = True
        elif s == "page":
            if not setting.use_line_scroll:
                return
            setting.use_line_scroll = False
        panel.reset()
        __refresh_container(self)

def set_option(self, amp, opc, args, raw):
    _set_methods = {
        literal.s_set_binary.seq:  __set_binary,
        literal.s_set_ascii.seq:   __set_ascii,
        literal.s_set_le.seq:      __set_le,
        literal.s_set_be.seq:      __set_be,
        literal.s_set_ws.seq:      __set_ws,
        literal.s_set_nows.seq:    __set_nows,
        literal.s_set_ic.seq:      __set_ic,
        literal.s_set_noic.seq:    __set_noic,
        literal.s_set_si.seq:      __set_si,
        literal.s_set_nosi.seq:    __set_nosi,
        literal.s_set_address.seq: __set_address,
        literal.s_set_bpl.seq:     __set_bytes_per_line,
        literal.s_set_bpw.seq:     __set_bytes_per_window,
        literal.s_set_bpu.seq:     __set_bytes_per_unit,
        literal.s_set_scroll.seq:  __set_scroll_mode, }

    if not args:
        self.co.flash("Argument required")
        return
    li = None
    argl = literal.get_arg_literals()
    for o in argl:
        if args[0] == o.str:
            li = o
            break
    if not li:
        l = [o for o in argl if o.str.startswith(args[0])]
        if len(l) == 1:
            li = l[0]
    if li:
        fn = _set_methods.get(li.seq)
        if not fn: # li is an alias
            for o in argl:
                if li.is_alias(o):
                    fn = _set_methods.get(o.seq)
                    assert fn, (li.str, o.str)
        fn(self, args)
        self.co.lrepaint()
    else:
        self.co.flash("Unknown option: " + args[0])

def set_auto(self, amp, opc, args, raw):
    if self.co.set_bytes_per_line("auto") == -1:
        self.co.flash("Failed to reset bytes per line")
        return
    if self.co.set_bytes_per_window("auto") == -1:
        __rebuild(self)
        self.co.flash("Failed to reset bytes per window")
        return
    if __try_update_address_num_width(self) == -1:
        __rebuild(self)

def __try_update_address_num_width(self):
    orig = self.co.update_address_num_width()
    if orig == -1:
        return -1 # no change
    screen.clear_refresh()
    if self.co.build_quiet() == -1:
        self.co.set_address_num_width(orig)
        self.co.build()
    self.co.repaint()

def show_current(self, amp, opc, args, raw):
    self.co.show("{0} {1} at {2}".format(self.co.get_short_path(),
        util.get_size_repr(self.co.get_size()),
        util.get_size_repr(self.co.get_pos())))

def show_current_sector(self, amp, opc, args, raw):
    sector_size = self.co.get_sector_size()
    if sector_size == -1:
        show_current(self, amp, opc, args, raw)
    else:
        self.co.show("{0} {1}[sectors] at {2}".format(self.co.get_short_path(),
            self.co.get_size() // sector_size,
            self.co.get_pos() // sector_size))

def show_self(self, amp, opc, args, raw):
    self.co.show(self)

def show_pwd(self, amp, opc, args, raw):
    self.co.show(os.getcwd())

def show_date(self, amp, opc, args, raw):
    self.co.show(time.ctime())

def show_kernel_module(self, amp, opc, args, raw):
    self.co.show(str(kernel.get_kernel_module()))

def show_fileobj_object(self, amp, opc, args, raw):
    self.co.show(self.co.get_repr())

def show_buffer_size(self, amp, opc, args, raw):
    self.co.show(self.co.get_buffer_size())

def show_meminfo(self, amp, opc, args, raw):
    self.co.show(get_meminfo_string())

def get_meminfo_string():
    l = ("total", util.get_size_repr(kernel.get_total_ram())), \
        ("free", util.get_size_repr(kernel.get_free_ram())), \
        ("page", util.get_size_repr(kernel.get_page_size()))
    return util.get_csv_string(l, False)

def show_osdep(self, amp, opc, args, raw):
    self.co.show(get_osdep_string())

def get_osdep_string():
    def _(t):
        return "yes" if t else "no"
    l = ("mmap", _(kernel.has_mmap())), \
        ("mremap", _(kernel.has_mremap())), \
        ("blkdev", _(kernel.is_blkdev_supported())), \
        ("ptrace", _(kernel.has_ptrace())), \
        ("native", _(native.is_enabled())), \
        ("has_chgat", _(screen.has_chgat())), \
        ("use_alt_chgat", _(screen.use_alt_chgat()))
    return util.get_csv_string(l, False)

def show_screen(self, amp, opc, args, raw):
    self.co.show(__get_screen_string(self))

def __get_screen_string(self):
    return "({0},{1}),{2}".format(screen.get_size_y(), screen.get_size_x(),
        self.co.get_build_size())

def show_platform(self, amp, opc, args, raw):
    self.co.show("{0} {1}".format(util.get_os_name(), util.get_os_release()))

def show_hostname(self, amp, opc, args, raw):
    self.co.show(platform.node())

def show_term(self, amp, opc, args, raw):
    self.co.show(terminal.get_type())

def show_lang(self, amp, opc, args, raw):
    self.co.show(terminal.get_lang())

def show_version(self, amp, opc, args, raw):
    self.co.show(version.__version__)

def show_sector_size(self, amp, opc, args, raw):
    x = self.co.get_sector_size()
    if x != -1:
        self.co.show(util.get_size_repr(x))
    else:
        self.co.flash()

def show_argv(self, amp, opc, args, raw):
    self.co.show(str(sys.argv))

def show_args(self, amp, opc, args, raw):
    l = list(self.co.get_buffer_short_paths())
    x = self.co.get_short_path()
    l[l.index(x)] = "[{0}]".format(x)
    self.co.show(' '.join(l))

def __show_hash(self, efn):
    try:
        buf = self.co.readall()
        if not buf:
            self.co.flash("No buffer")
            return
        self.co.show(efn(buf))
    except Exception as e:
        self.co.flash(e)

def __show_hash_partial(self, fn, efn):
    try:
        buf = fn(self)
        if not buf:
            self.co.flash("No buffer selected")
            return
        self.co.show(efn(buf))
    except Exception as e:
        self.co.flash(e)

def __is_equal(a, b):
    return a == b

def __is_not_equal(a, b):
    return a != b

def __cmp_to_find_equal(self, fn):
    return fn(1, 1) is True

# :cmp (compare from offset 0) variants
def cmp_buffer(self, amp, opc, args, raw):
    __cmp_buffer(self, 0, __is_not_equal)

def cmp_buffer_neg(self, amp, opc, args, raw):
    __cmp_buffer(self, 0, __is_equal)

def cmp_buffer_next(self, amp, opc, args, raw):
    __cmp_buffer(self, self.co.get_pos() + 1, __is_not_equal)

def cmp_buffer_next_neg(self, amp, opc, args, raw):
    __cmp_buffer(self, self.co.get_pos() + 1, __is_equal)

# :cmpr (compare from max offset) variants
def cmpr_buffer(self, amp, opc, args, raw):
    __cmpr_buffer(self, self.co.get_max_pos(), __is_not_equal)

def cmpr_buffer_neg(self, amp, opc, args, raw):
    __cmpr_buffer(self, self.co.get_max_pos(), __is_equal)

def cmpr_buffer_next(self, amp, opc, args, raw):
    __cmpr_buffer(self, self.co.get_pos() - 1, __is_not_equal)

def cmpr_buffer_next_neg(self, amp, opc, args, raw):
    __cmpr_buffer(self, self.co.get_pos() - 1, __is_equal)

def __cmp_buffer(self, pos, fn):
    sizes = __cmp_buffer_prep(self)
    if sizes is None:
        return
    max_pos = min(sizes) - 1
    if pos > max_pos:
        self.co.flash("Already at the end of the buffer")
        return

    find_equal = __cmp_to_find_equal(self, fn)
    beg = pos
    siz = kernel.get_buffer_size()

    # XXX too slow
    while True:
        bufs, is_equal = __cmp_buffer_read(self, pos, siz)
        if bufs is None:
            break
        if find_equal and is_equal: # short cut
            __cmp_buffer_goto(self, pos)
            return
        l = [len(b) for b in bufs]
        for x in util.get_xrange(min(l)):
            for i in util.get_xrange(len(bufs)):
                if i == 0:
                    continue
                a = bufs[i - 1]
                b = bufs[i]
                if fn(a[x], b[x]):
                    __cmp_buffer_goto(self, pos + x)
                    return
        if len(set(l)) != 1: # end of either of the buffers
            break
        pos += siz
        if pos > max_pos:
            break
        if screen.test_signal():
            self.co.flash("Forward cmp interrupted")
            return
    if beg == 0: # can only tell if started from offset 0
        if find_equal:
            self.co.show("Buffers have nothing in common")
        else:
            self.co.show("Buffers are the same")
    else:
        self.co.show("Done")

def __cmpr_buffer(self, pos, fn):
    sizes = __cmp_buffer_prep(self)
    if sizes is None:
        return
    if len(set(sizes)) != 1:
        self.co.flash("Buffers need to have the same size")
        return
    max_pos = sizes[0] - 1
    if pos < 0:
        self.co.flash("Already at offset 0 of the buffer")
        return

    find_equal = __cmp_to_find_equal(self, fn)
    beg = pos
    siz = kernel.get_buffer_size()
    pos -= siz
    pos += 1 # max pos is (size - 1), so plus 1
    if pos < 0:
        siz += pos
        pos = 0

    # XXX too slow
    while True:
        bufs, is_equal = __cmp_buffer_read(self, pos, siz)
        if bufs is None:
            break
        if find_equal and is_equal: # short cut
            __cmp_buffer_goto(self, pos + len(bufs[0]) - 1)
            return
        assert len(set([len(b) for b in bufs])) == 1
        n = len(bufs[0])
        for x in util.get_xrange(n):
            for i in util.get_xrange(len(bufs)):
                if i == 0:
                    continue
                a = bufs[i - 1]
                b = bufs[i]
                xx = n - 1 - x
                if fn(a[xx], b[xx]):
                    __cmp_buffer_goto(self, pos + xx)
                    return
        if n <= siz and pos == 0:
            break
        pos -= siz
        if pos < 0:
            pos = 0
        if screen.test_signal():
            self.co.flash("Reverse cmp interrupted")
            return
    if beg == max_pos: # can only tell if started from the end
        if find_equal:
            self.co.show("Buffers have nothing in common")
        else:
            self.co.show("Buffers are the same")
    else:
        self.co.show("Done")

def __cmp_buffer_prep(self):
    if len(self.co) < 2:
        self.co.flash("More than one windows required")
        return
    files = []
    sizes = []
    for x in util.get_xrange(len(self.co)):
        files.append(self.co.get_path())
        sizes.append(self.co.get_size())
        self.co.switch_to_next_workspace()
    assert self.co.get_path() == files[0]
    for i, x in enumerate(sizes):
        if not x:
            self.co.flash(files[i] + " is an empty buffer")
            return
    return sizes

def __cmp_buffer_read(self, pos, siz):
    bufs = []
    is_equal = True
    for x in util.get_xrange(len(self.co)):
        b = self.co.read(pos, siz)
        if not b:
            return None, False
        if bufs and bufs[-1] != b:
            is_equal = False
        bufs.append(b)
        self.co.switch_to_next_workspace()
    return bufs, is_equal

def __cmp_buffer_goto(self, pos):
    # force even sized windows if not set
    if not setting.use_even_size_window:
        self.co.set_bytes_per_window("even")
        self.co.refresh()
        full_repaint = True
    else:
        full_repaint = False
    for x in util.get_xrange(len(self.co)):
        self.co.go_to(pos)
        self.co.switch_to_next_workspace()
    self.co.show(pos)
    if full_repaint:
        self.co.repaint()
    else:
        self.co.lrepaint()

@_cleanup
def inc_number(self, amp, opc, args, raw):
    siz = setting.bytes_per_unit if setting.use_unit_based else 1
    __do_replace_number(self, get_int(amp), self.co.get_unit_pos(), siz)

@_cleanup
def range_inc_number(self, amp, opc, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    __do_replace_number(self, get_int(amp), self.co.get_pos(), siz)

@_cleanup
def block_inc_number(self, amp, opc, args, raw):
    beg, end, mapx, siz, cnt = __get_block(self)
    if cnt == 1:
        self.co.set_pos(beg)
        __do_replace_number(self, get_int(amp), self.co.get_pos(), siz)
    else:
        self.co.flash("Only single line allowed")

@_cleanup
def dec_number(self, amp, opc, args, raw):
    siz = setting.bytes_per_unit if setting.use_unit_based else 1
    __do_replace_number(self, -get_int(amp), self.co.get_unit_pos(), siz)

@_cleanup
def range_dec_number(self, amp, opc, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    __do_replace_number(self, -get_int(amp), self.co.get_pos(), siz)

@_cleanup
def block_dec_number(self, amp, opc, args, raw):
    beg, end, mapx, siz, cnt = __get_block(self)
    if cnt == 1:
        self.co.set_pos(beg)
        __do_replace_number(self, -get_int(amp), self.co.get_pos(), siz)
    else:
        self.co.flash("Only single line allowed")

def __do_replace_number(self, amp, pos, siz):
    def fn(_):
        if siz > 8:
            self.co.flash("Only <= 8 bytes allowed")
            return
        b = self.co.read(pos, siz)
        if not b:
            self.co.flash("Empty buffer")
            return
        x = util.bin_to_int(b) + amp
        if x < 0:
            x += 2 ** (len(b) * 8)
        b = util.int_to_bin(x, len(b))
        if b is None:
            raise fileobj.Error("Failed to convert")
        self.co.replace(pos, filebytes.ords(b))
        self.co.show(util.bin_to_int(b))
    __exec_prepaint(self, fn, siz)

_did_search_word_forward = True
_did_search_char_forward = True

def __get_did_search_forward(k):
    if k in (literal.s_fsearchw.str, literal.s_rsearchw.str):
        return _did_search_word_forward
    elif k in (literal.fsearchc.str[0], literal.rsearchc.str[0]):
        return _did_search_char_forward
    elif k in (literal.fsearchcb.str[0], literal.rsearchcb.str[0]):
        return _did_search_char_forward
    else:
        assert False, k

def __set_did_search_forward(k, v):
    global _did_search_word_forward, _did_search_char_forward
    if k in (literal.s_fsearchw.str, literal.s_rsearchw.str):
        _did_search_word_forward = v
    elif k in (literal.fsearchc.str[0], literal.rsearchc.str[0]):
        _did_search_char_forward = v
    elif k in (literal.fsearchcb.str[0], literal.rsearchcb.str[0]):
        _did_search_char_forward = v
    else:
        assert False, (k, v)

def __get_search_direction_next(k, is_cmd_forward):
    # The direction is set based on the previous regular search.
    # If searched forward (/xxx) and forward next (n), then forward (True).
    # If searched forward (/xxx) and backward next (N), then backward (False).
    # If searched backward (?xxx) and forward next (n), then backward (False).
    # If searched backward (?xxx) and backward next (N), then forward (True).
    return __get_did_search_forward(k) == is_cmd_forward

def __get_search_word_next(self):
    if __get_did_search_forward(literal.s_fsearchw.str):
        k = literal.s_fsearchw.str
    else:
        k = literal.s_rsearchw.str
    s = self.ope.get_prev_history(k)
    if not s:
        self.co.flash("No previous search")
        return -1
    return s

# search
def search_word_forward(self, amp, opc, args, raw):
    # /xxx yyy  zzz
    # is to find "xxx yyy  zzz" but not "xxx".
    # Note that joining args can't handle double space.
    s = util.bytes_to_str(filebytes.input_to_bytes(raw))
    if len(s) == 1:
        s = self.ope.get_prev_history(s[0])
        if not s:
            self.co.flash("No previous search")
            return
    __search(self, s, amp, True) # ignore current position
    __set_did_search_forward(s[0], True)

def search_word_backward(self, amp, opc, args, raw):
    # /xxx yyy  zzz
    # is to find "xxx yyy  zzz" but not "xxx".
    # Note that joining args can't handle double space.
    s = util.bytes_to_str(filebytes.input_to_bytes(raw))
    if len(s) == 1:
        s = self.ope.get_prev_history(s[0])
        if not s:
            self.co.flash("No previous search")
            return
    __search(self, s, amp, False) # ignore current position
    __set_did_search_forward(s[0], False)

_prev_search_char = None
_did_search_char_before = False

def search_char_forward(self, amp, opc, args, raw):
    global _prev_search_char, _did_search_char_before
    s = _prev_search_char = util.bytes_to_str(filebytes.input_to_bytes(raw))
    _did_search_char_before = False
    __search(self, s, amp, True) # ignore current position
    __set_did_search_forward(s[0], True)

def search_char_backward(self, amp, opc, args, raw):
    global _prev_search_char, _did_search_char_before
    s = _prev_search_char = util.bytes_to_str(filebytes.input_to_bytes(raw))
    _did_search_char_before = False
    __search(self, s, amp, False) # ignore current position
    __set_did_search_forward(s[0], False)

def search_char_forward_before(self, amp, opc, args, raw):
    global _prev_search_char, _did_search_char_before
    s = _prev_search_char = util.bytes_to_str(filebytes.input_to_bytes(raw))
    _did_search_char_before = True
    # no need to move +1, no position change on consecutive attempt
    if __search(self, s, amp, True) != -1: # ignore current
        go_left(self, 1) # move -1 if success
    __set_did_search_forward(s[0], True)

def search_char_backward_before(self, amp, opc, args, raw):
    global _prev_search_char, _did_search_char_before
    s = _prev_search_char = util.bytes_to_str(filebytes.input_to_bytes(raw))
    _did_search_char_before = True
    # no need to move -1, no position change on consecutive attempt
    if __search(self, s, amp, False) != -1: # ignore current
        go_right(self, 1) # move +1 if success
    __set_did_search_forward(s[0], False)

# search next
def search_word_next_forward(self, amp, opc, args, raw):
    s = __get_search_word_next(self)
    if s == -1:
        return
    assert s[0] in (literal.s_fsearchw.str, literal.s_rsearchw.str), s
    is_forward = __get_search_direction_next(literal.s_fsearchw.str, True)
    __search(self, s, amp, is_forward)

def search_word_next_backward(self, amp, opc, args, raw):
    s = __get_search_word_next(self)
    if s == -1:
        return
    assert s[0] in (literal.s_fsearchw.str, literal.s_rsearchw.str), s
    is_forward = __get_search_direction_next(literal.s_fsearchw.str, False)
    __search(self, s, amp, is_forward)

def search_char_next_forward(self, amp, opc, args, raw):
    s = _prev_search_char
    if s is None:
        return
    is_forward = __get_search_direction_next(literal.fsearchc.str[0], True)
    if _did_search_char_before:
        go_right(self, 1) # move +1 for consecutive attempt
    __search(self, s, amp, is_forward)
    if _did_search_char_before:
        go_left(self, 1) # move -1, or backout previous +1 on failure

def search_char_next_backward(self, amp, opc, args, raw):
    s = _prev_search_char
    if s is None:
        return
    is_forward = __get_search_direction_next(literal.fsearchc.str[0], False)
    if _did_search_char_before:
        go_left(self, 1) # move -1 for consecutive attempt
    __search(self, s, amp, is_forward)
    if _did_search_char_before:
        go_right(self, 1) # move +1, or backout previous -1 on failure

def __search(self, s, amp, is_forward):
    n = get_int(amp)
    for x in util.get_xrange(n):
        is_last = (x == (n - 1))
        pos = self.co.get_pos()
        if is_forward:
            if pos >= self.co.get_max_pos():
                pos = 0
            else:
                pos += 1
        else:
            if pos <= 0:
                pos = self.co.get_max_pos()
            else:
                pos -= 1
        if __do_search(self, pos, s, is_forward, is_last) == -1:
            return -1

def __do_search(self, pos, s, is_forward, is_last):
    word = util.pack_hex_string(s[1:])
    b = util.str_to_bytes(word)
    if is_forward:
        fn = self.co.search
    else:
        fn = self.co.rsearch
    ret = fn(pos, b, -1)
    if ret == fileobj.NOTFOUND and setting.use_wrapscan:
        if is_forward:
            x = 0
        else:
            x = self.co.get_max_pos()
        ret = fn(x, b, pos)

    # XXX allowing non aligned position after search leads to inconsistency
    #setting.discard_unit_based() # destination may not be aligned with bpu
    retval = None
    if ret == fileobj.NOTFOUND:
        self.co.flash("Search '{0}' failed".format(filebytes.str(word)))
        retval = -1
    elif ret == fileobj.INTERRUPT:
        self.co.flash("Search '{0}' interrupted".format(filebytes.str(word)))
        retval = -1
    elif ret < 0:
        self.co.flash("Search error {0}".format(ret))
        retval = -1
    elif ret != self.co.get_pos():
        self.co.set_pos(ret) # only update position
    # refresh if last or error (e.g. clear old valid search word)
    if is_last or retval == -1:
        self.co.lrepaintf()
    #setting.restore_unit_based()
    return retval

def generic_delete(self, amp, opc, args, raw):
    test_delete_raise(self)
    amp = get_int(amp)
    def fn(_):
        pos = self.co.get_pos()
        buf = self.co.read_current(amp)
        self.co.delete_current(amp)
        if not _:
            self.co.set_delete_buffer(buf)
        else:
            self.co.right_add_delete_buffer(buf)
        # If current position has changed, delete was at end of buffer.
        # XXX Require full repaint for now even though
        # DisplayCanvas.update_highlight() does clear previous position.
        if self.co.get_pos() != pos:
            self.co.require_full_repaint()
    __exec_lrepaint(self, fn)

# generic_delete() without delete buffer modification
def generic_raw_delete(self, amp, opc, args, raw):
    test_delete_raise(self)
    amp = get_int(amp)
    def fn(_):
        pos = self.co.get_pos()
        self.co.delete_current(amp)
        # If current position has changed, delete was at end of buffer.
        # XXX Require full repaint for now even though
        # DisplayCanvas.update_highlight() does clear previous position.
        if self.co.get_pos() != pos:
            self.co.require_full_repaint()
    __exec_lrepaint(self, fn)

def generic_backspace(self, amp, opc, args, raw):
    test_delete_raise(self)
    amp = get_int(amp)
    def fn(_):
        if self.co.get_pos() > 0:
            self.co.add_pos(-amp)
        buf = self.co.read_current(amp)
        self.co.delete_current(amp)
        if not _:
            self.co.set_delete_buffer(buf, False)
        else:
            self.co.left_add_delete_buffer(buf)
    __exec_lrepaint(self, fn)

@_cleanup
def delete_till_end(self, amp, opc, args, raw):
    x = self.co.get_size() - self.co.get_pos()
    if x > 0:
        generic_delete(self, x, opc, args, raw)

@_cleanup
def delete(self, amp, opc, args, raw):
    amp = get_int(amp)
    if setting.use_unit_based:
        amp *= setting.bytes_per_unit
        __assert_bpu_aligned(self)
    generic_delete(self, amp, opc, args, raw)

@_cleanup
def raw_delete(self, amp, opc, args, raw):
    amp = get_int(amp)
    if setting.use_unit_based:
        amp *= setting.bytes_per_unit
        __assert_bpu_aligned(self)
    generic_raw_delete(self, amp, opc, args, raw)

@_cleanup
def backspace(self, amp, opc, args, raw):
    amp = get_int(amp)
    if setting.use_unit_based:
        amp *= setting.bytes_per_unit
        __assert_bpu_aligned(self)
    generic_backspace(self, amp, opc, args, raw)

@_cleanup
def range_delete(self, amp, opc, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    generic_delete(self, siz, opc, [], raw)

@_cleanup
def block_delete(self, amp, opc, args, raw):
    test_delete_raise(self)
    beg, end, mapx, siz, cnt = __get_block(self)
    self.co.set_pos(beg)
    def fn(_):
        und = self.co.get_undo_size()
        pos = self.co.get_pos()
        buf = []
        for i in util.get_xrange(cnt):
            buf.append(self.co.read(pos, siz))
            self.co.delete(pos, siz)
            pos += (mapx - siz)
            if pos > self.co.get_max_pos():
                break
            if screen.test_signal():
                self.co.flash("Delete interrupted ({0}/{1})".format(i, cnt))
                self.co.rollback_restore_until(und)
                return
        buf = filebytes.join(buf)
        if not _:
            self.co.set_delete_buffer(buf)
        else:
            self.co.right_add_delete_buffer(buf)
        self.co.merge_undo(i + 1)
    __exec_lrepaint(self, fn)

def generic_toggle(self, amp, opc, args, raw):
    test_replace_raise(self)
    test_empty_raise(self)
    amp = get_int(amp)
    def fn(_):
        und = self.co.get_undo_size()
        pos = self.co.get_pos()
        if setting.use_single_operation:
            ret = __single_toggle(self, pos, amp)
        else:
            ret = __buffered_toggle(self, pos, amp)
        if ret > 0:
            self.co.merge_undo(ret)
            self.co.add_pos(amp)
        elif ret == -1:
            self.co.rollback_until(und)
    __exec_lrepaint(self, fn)

def __single_toggle(self, pos, amp):
    for x in util.get_xrange(amp):
        b = self.co.read(pos, 1)
        if not b:
            return x
        # no b.isalpha() test here as skipping will have trouble on undo/redo
        if b.islower():
            b = b.upper()
        else:
            b = b.lower()
        self.co.replace(pos, filebytes.ords(b))
        pos += 1
        if screen.test_signal():
            self.co.flash("Toggle interrupted ({0}/{1})".format(x, amp))
            return -1
    return amp

def __buffered_toggle(self, pos, amp):
    l = filebytes.split(self.co.read(pos, amp))
    for i, b in enumerate(l):
        if b.isalpha():
            if b.islower():
                l[i] = b.upper()
            else:
                l[i] = b.lower()
        if screen.test_signal():
            self.co.flash("Toggle interrupted")
            return 0
    self.co.replace(pos, filebytes.seq_to_ords(l))
    return 1

@_cleanup
def toggle(self, amp, opc, args, raw):
    amp = get_int(amp)
    if setting.use_unit_based:
        amp *= setting.bytes_per_unit
        __assert_bpu_aligned(self)
    generic_toggle(self, amp, opc, args, raw)

@_cleanup
def range_toggle(self, amp, opc, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    generic_toggle(self, siz, opc, [], raw)

@_cleanup
def block_toggle(self, amp, opc, args, raw):
    test_replace_raise(self)
    test_empty_raise(self)
    beg, end, mapx, siz, cnt = __get_block(self)
    self.co.set_pos(beg)
    def fn(_):
        und = self.co.get_undo_size()
        pos = self.co.get_pos()
        for i in util.get_xrange(cnt):
            if __buffered_toggle(self, pos, siz) == 0:
                self.co.rollback_restore_until(und)
                return
            pos += mapx
            if pos > self.co.get_max_pos():
                break
        self.co.merge_undo(i + 1)
        self.co.set_pos(pos - mapx + siz)
    __exec_lrepaint(self, fn)

@_cleanup
def range_replace(self, amp, opc, args, raw):
    test_replace_raise(self)
    beg, siz = __get_range(self)
    l = tuple(args for x in util.get_xrange(siz))
    self.co.set_pos(beg)
    def fn(_):
        pos = self.co.get_pos()
        self.co.replace(pos, l)
        self.co.set_pos(pos + siz)
    __exec_lrepaint(self, fn)

@_cleanup
def block_replace(self, amp, opc, args, raw):
    test_replace_raise(self)
    beg, end, mapx, siz, cnt = __get_block(self)
    l = tuple(args for x in util.get_xrange(siz))
    self.co.set_pos(beg)
    def fn(_):
        und = self.co.get_undo_size()
        pos = self.co.get_pos()
        for i in util.get_xrange(cnt):
            self.co.replace(pos, l)
            pos += mapx
            if pos > self.co.get_max_pos():
                break
            if screen.test_signal():
                self.co.flash("Replace interrupted ({0}/{1})".format(i, cnt))
                self.co.rollback_restore_until(und)
                return
        self.co.merge_undo(i + 1)
        self.co.set_pos(pos - mapx + siz)
    __exec_lrepaint(self, fn)

@_cleanup
def rotate_right(self, amp, opc, args, raw):
    test_empty_raise(self)
    __do_rotate_right(self, amp, opc, self.co.get_size() - self.co.get_pos())

def __do_rotate_right(self, amp, opc, siz):
    test_replace_raise(self)
    test_empty_raise(self)
    shift = get_int(amp)
    if shift > 8:
        self.co.flash("Invalid shift: {0}".format(shift))
        return
    def fn(_):
        beg = self.co.get_pos()
        end = beg + siz - 1
        if end > self.co.get_max_pos():
            end = self.co.get_max_pos()
        und = self.co.get_undo_size()
        if setting.use_single_operation:
            ret = __single_rotate_right(self, shift, beg, end)
        else:
            ret = __buffered_rotate_right(self, shift, beg, end)
        if ret > 0:
            self.co.merge_undo(ret)
        elif ret == -1:
            self.co.rollback_until(und)
    __exec_lrepaint(self, fn)

def __single_rotate_right(self, shift, beg, end):
    car = 0
    pos = beg
    car_shift = 8 - shift
    if setting.use_circular_bit_shift:
        car = __read_chr(self, end) << car_shift
    while pos <= end:
        x = __read_chr(self, pos)
        u = (car & 0xFF) | (x >> shift)
        self.co.replace(pos, (u,))
        car = x << car_shift
        pos += 1
        if screen.test_signal():
            self.co.flash("Rotate right interrupted ({0}/{1})".format(pos, end))
            return -1
    return end - beg + 1

def __buffered_rotate_right(self, shift, beg, end):
    car = 0
    siz = end - beg + 1
    buf = filebytes.split(self.co.read(beg, siz))
    assert len(buf) == siz
    if setting.use_circular_bit_shift:
        car = filebytes.ord(buf[-1]) << (8 - shift)
    ret, car = __do_buffered_rotate_right(self, shift, beg, end, buf, car)
    return ret

def __do_buffered_rotate_right(self, shift, beg, end, buf, car):
    assert len(buf) == end - beg + 1
    if shift == 8:
        l = [util.int_to_byte(car)] + buf[:-1]
        car = filebytes.ord(buf[-1])
        buf = l
    else:
        pos = beg
        car_shift = 8 - shift
        while pos <= end:
            x = filebytes.ord(buf[pos - beg])
            u = (car & 0xFF) | (x >> shift)
            buf[pos - beg] = util.int_to_byte(u)
            car = x << car_shift
            pos += 1
            if screen.test_signal():
                self.co.flash("Rotate right interrupted ({0}/{1},{2})".format(
                    pos, end, len(buf)))
                return 0, None
    self.co.replace(beg, filebytes.seq_to_ords(buf))
    return 1, car

@_cleanup
def range_rotate_right(self, amp, opc, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    __do_rotate_right(self, amp, opc, siz)

@_cleanup
def block_rotate_right(self, amp, opc, args, raw):
    test_replace_raise(self)
    test_empty_raise(self)
    shift = get_int(amp)
    if shift > 8:
        self.co.flash("Invalid shift: {0}".format(shift))
        return
    beg, end, mapx, siz, cnt = __get_block(self)
    self.co.set_pos(beg)

    def fn(_):
        und = self.co.get_undo_size()
        pos = self.co.get_pos()
        pos_end = pos + end - beg
        if pos_end > self.co.get_max_pos():
            self.co.flash("Not enough room")
            return
        org = pos
        car = 0
        car_shift = 8 - shift
        if setting.use_circular_bit_shift:
            car = __read_chr(self, pos_end) << car_shift
        for i in util.get_xrange(cnt):
            buf = filebytes.split(self.co.read(pos, siz))
            assert len(buf) == siz
            ret, car = __do_buffered_rotate_right(
                self, shift, pos, pos + siz - 1, buf, car)
            if ret == 0:
                self.co.rollback_restore_until(und)
                return
            pos += mapx
            if pos > self.co.get_max_pos():
                break
        self.co.merge_undo(i + 1)
        self.co.set_pos(org)
    __exec_lrepaint(self, fn)

@_cleanup
def rotate_left(self, amp, opc, args, raw):
    test_empty_raise(self)
    __do_rotate_left(self, amp, opc, self.co.get_pos() + 1)

def __do_rotate_left(self, amp, opc, siz):
    test_replace_raise(self)
    test_empty_raise(self)
    shift = get_int(amp)
    if shift > 8:
        self.co.flash("Invalid shift: {0}".format(shift))
        return
    def fn(_):
        beg = self.co.get_pos()
        end = beg - siz + 1
        if end < 0:
            end = 0
        und = self.co.get_undo_size()
        if setting.use_single_operation:
            ret = __single_rotate_left(self, shift, beg, end)
        else:
            ret = __buffered_rotate_left(self, shift, beg, end)
        if ret > 0:
            self.co.merge_undo(ret)
        elif ret == -1:
            self.co.rollback_until(und)
    __exec_lrepaint(self, fn)

def __single_rotate_left(self, shift, beg, end):
    car = 0
    pos = beg
    car_shift = 8 - shift
    if setting.use_circular_bit_shift:
        car = __read_chr(self, end) >> car_shift
    while pos >= end:
        x = __read_chr(self, pos)
        u = ((x << shift) & 0xFF) | car
        self.co.replace(pos, (u,))
        car = x >> car_shift
        pos -= 1
        if screen.test_signal():
            self.co.flash("Rotate left interrupted ({0}/{1})".format(pos, end))
            return -1
    return beg - end + 1

def __buffered_rotate_left(self, shift, beg, end):
    car = 0
    siz = beg - end + 1
    buf = filebytes.split(self.co.read(end, siz))
    assert len(buf) == siz
    if setting.use_circular_bit_shift:
        car = filebytes.ord(buf[0]) >> (8 - shift)
    ret, car = __do_buffered_rotate_left(self, shift, beg, end, buf, car)
    return ret

def __do_buffered_rotate_left(self, shift, beg, end, buf, car):
    assert len(buf) == beg - end + 1
    if shift == 8:
        l = buf[1:] + [util.int_to_byte(car)]
        car = filebytes.ord(buf[0])
        buf = l
    else:
        pos = beg
        car_shift = 8 - shift
        while pos >= end:
            x = filebytes.ord(buf[pos - end])
            u = ((x << shift) & 0xFF) | car
            buf[pos - end] = util.int_to_byte(u)
            car = x >> car_shift
            pos -= 1
            if screen.test_signal():
                self.co.flash("Rotate left interrupted ({0}/{1},{2})".format(
                    pos, end, len(buf)))
                return 0, None
    self.co.replace(end, filebytes.seq_to_ords(buf))
    return 1, car

@_cleanup
def range_rotate_left(self, amp, opc, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg + siz - 1)
    __do_rotate_left(self, amp, opc, siz)

@_cleanup
def block_rotate_left(self, amp, opc, args, raw):
    test_replace_raise(self)
    test_empty_raise(self)
    shift = get_int(amp)
    if shift > 8:
        self.co.flash("Invalid shift: {0}".format(shift))
        return
    beg, end, mapx, siz, cnt = __get_block(self)
    self.co.set_pos(end)

    def fn(_):
        und = self.co.get_undo_size()
        pos = self.co.get_pos()
        pos_end = pos + beg - end
        if pos_end < 0:
            self.co.flash("Not enough room")
            return
        org = pos
        car = 0
        car_shift = 8 - shift
        if setting.use_circular_bit_shift:
            car = __read_chr(self, pos_end) >> car_shift
        for i in util.get_xrange(cnt):
            buf = filebytes.split(self.co.read(pos - siz + 1, siz))
            assert len(buf) == siz
            ret, car = __do_buffered_rotate_left(
                self, shift, pos, pos - siz + 1, buf, car)
            if ret == 0:
                self.co.rollback_restore_until(und)
                return
            pos -= mapx
            if pos < 0: # probably never hit this
                break
        self.co.merge_undo(i + 1)
        self.co.set_pos(org)
    __exec_lrepaint(self, fn)

@_cleanup
def swap_bytes(self, amp, opc, args, raw):
    siz = get_int(amp)
    if siz == 1:
        siz = 2 # default 2 for no amp
    __swap_bytes(self, siz)

@_cleanup
def range_swap_bytes(self, amp, opc, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    __swap_bytes(self, siz)

def __swap_bytes(self, siz):
    test_replace_raise(self)
    test_empty_raise(self)
    def fn(_):
        buf = self.co.read_current(siz)
        l = __swap_buffer_to_input(self, buf)
        self.co.replace_current(l)
        self.co.add_pos(len(l))
    __exec_lrepaint(self, fn)

def __swap_buffer_to_input(self, buf):
    l = []
    for x in filebytes.riter(buf):
        l.append(filebytes.ord(x))
    return l

@_cleanup
def block_swap_bytes(self, amp, opc, args, raw):
    test_replace_raise(self)
    test_empty_raise(self)
    beg, end, mapx, siz, cnt = __get_block(self)
    self.co.set_pos(beg)

    def fn(_):
        und = self.co.get_undo_size()
        pos = self.co.get_pos()
        pos_end = pos + end - beg
        if pos_end > self.co.get_max_pos():
            self.co.flash("Not enough room")
            return
        ret = __block_read_swap_buffer(self, pos, mapx, siz, cnt)
        if ret == -1:
            self.co.rollback_restore_until(und)
            return
        ret = __block_replace_swap_buffer(self, pos, mapx, siz, cnt, ret)
        if ret == -1:
            self.co.rollback_restore_until(und)
            return
        self.co.merge_undo(ret)
        self.co.set_pos(pos_end + 1)
    __exec_lrepaint(self, fn)

def __block_read_swap_buffer(self, pos, mapx, siz, cnt):
    buf = filebytes.BLANK
    for i in util.get_xrange(cnt):
        b = self.co.read(pos, siz)
        assert len(b) == siz
        buf += b
        pos += mapx
        if pos > self.co.get_max_pos():
            break
        if screen.test_signal():
            self.co.flash("Read swap buffer interrupted ({0}/{1},{2})".format(
                i, cnt, len(buf)))
            return -1
    return __swap_buffer_to_input(self, buf)

def __block_replace_swap_buffer(self, pos, mapx, siz, cnt, l):
    for i in util.get_xrange(cnt):
        self.co.replace(pos, l[:siz])
        l = l[siz:]
        pos += mapx
        if screen.test_signal():
            self.co.flash("Replace swap buffer interrupted "
                "({0}/{1},{2})".format(i, cnt, len(l)))
            return -1
    return cnt

@_cleanup
def repeat(self, amp, opc, args, raw):
    # Repeat action may change position more than once (e.g. write console).
    # When it happens, update highlight can only update the last change,
    # so always force full repaint.
    # XXX write console looks to be the only one with above behavior.
    self.co.require_full_repaint()
    pxfn = self.co.get_xprev_context()
    if not pxfn:
        self.co.flash("No previous command")
    elif amp is None:
        __call_context_lrepaint(self, pxfn)
    else:
        amp = get_int(amp)
        fn = self.co.get_prev_context()
        if amp <= 1:
            __call_context_lrepaint(self, fn)
            self.co.set_prev_context(fn)
        else:
            def xfn(i):
                und = self.co.get_undo_size()
                for j in util.get_xrange(amp):
                    if i == 0 and j == 0:
                        fn(0) # only very first call gets 0 for arg
                    else:
                        fn(1)
                self.co.merge_undo_until(und)
            __call_context_lrepaint(self, xfn)
            self.co.set_prev_context(fn, xfn)

def undo(self, amp, opc, args, raw):
    __undo(self, amp, self.co.undo, "Already at oldest change",
        "Undo interrupted")

def undo_all(self, amp, opc, args, raw):
    siz = self.co.get_undo_size()
    undo(self, siz if siz else 1, opc, args, raw)

def redo(self, amp, opc, args, raw):
    __undo(self, amp, self.co.redo, "Already at newest change",
        "Redo interrupted")

def redo_all(self, amp, opc, args, raw):
    siz = self.co.get_redo_size()
    redo(self, siz if siz else 1, opc, args, raw)

def __undo(self, amp, fn, msg_notfound, msg_interrupt):
    pos = self.co.get_pos()
    ret, msg = fn(get_int(amp))
    if ret == fileobj.ERROR:
        self.co.flash(msg)
    elif ret == fileobj.NOTFOUND:
        self.co.flash(msg_notfound)
    elif ret == fileobj.INTERRUPT:
        self.co.flash(msg_interrupt)
    elif ret >= 0 and ret != self.co.get_pos():
        self.co.set_pos(ret)
    # Require full repaint for potential delete at end of buffer.
    # This is needed even though DisplayCanvas.update_highlight() does clear
    # previous position, because of extra self.co.set_pos() above.
    # (also see methods.generic_delete())
    if self.co.get_pos() != pos:
        self.co.require_full_repaint()
    self.co.lrepaintf()

def set_mark(self, amp, opc, args, raw):
    key = opc[1]
    pos = self.co.get_pos()
    s = "Mark '{0}' at {1}[B]".format(key, pos)
    if key.isupper():
        self.co.set_uniq_mark(key, pos, self.co.get_path())
        self.co.show(s)
    else:
        self.co.set_mark(key, pos)
        self.co.show("{0} for {1}".format(s, self.co.get_path()))

def get_mark(self, amp, opc, args, raw):
    key = opc[1]
    if key.isupper():
        f, pos = self.co.get_uniq_mark(key)
    else:
        f, pos = self.co.get_path(), self.co.get_mark(key)
    if f is not None and pos != -1:
        if self.co.get_path() != f:
            self.co.switch_to_buffer(f)
            self.co.lrepaintf()
        go_to(self, pos)
    else:
        s = "Mark '{0}' not set".format(key)
        if key.isupper():
            self.co.flash(s)
        else:
            self.co.flash("{0} for {1}".format(s, f))

def delete_mark(self, amp, opc, args, raw):
    if not args:
        self.co.flash("Argument required")
        return
    for arg in args:
        for k in arg:
            self.co.delete_mark(k)

def clear_marks(self, amp, opc, args, raw):
    # does not clear uniq marks
    self.co.clear_marks(lambda k: not k.isupper())

def start_record(self, amp, opc, args, raw):
    if opc != literal.q.str:
        self.co.start_record(opc[1])
        self.co.push_banner("recording @{0}".format(opc[1]))
    else:
        self.co.end_record()
        self.co.pop_banner()

def replay_record(self, amp, opc, args, raw):
    assert len(opc) > 1
    for x in util.get_xrange(get_int(amp)):
        self.co.replay_record(opc[1])

def replay_bind(self, amp, opc, args, raw):
    __replay_bind(self)

def __replay_bind(self):
    replay_record(self, None, literal.atsign_colon.str, None, None)

def bind_command(self, amp, opc, args, raw):
    if not args:
        self.co.flash("Argument required")
        return
    s = args[0] # :cmd
    if len(s) < 2 or s[0] != ":":
        self.co.flash("Invalid command {0}".format(s))
        return
    if s == literal.s_bind.str:
        self.co.flash("Can not bind {0} command".format(s))
        return
    self.co.start_record(literal.atsign_colon.str[1])
    for i, s in enumerate(args):
        for x in s: # s is string (not bytes)
            self.co.add_record(ord(x))
        if i != len(args) - 1:
            self.co.add_record(ord(' '))
    self.co.add_record(kbd.ENTER)
    self.co.add_record(ord('q')) # termination
    self.co.end_record()
    __replay_bind(self)

def __get_and_ops(mask):
    return lambda b: filebytes.ord(b) & mask

def __get_or_ops(mask):
    return lambda b: filebytes.ord(b) | mask

def __get_xor_ops(mask):
    return lambda b: filebytes.ord(b) ^ mask

def _get_bit_ops():
    return {
        literal.bit_and.key: __get_and_ops,
        literal.bit_or.key : __get_or_ops,
        literal.bit_xor.key: __get_xor_ops, }

def generic_logical_bit_operation(self, amp, opc, arg, raw):
    test_replace_raise(self)
    test_empty_raise(self)
    amp = get_int(amp)
    mask = (int(opc[1], 16) << 4) | int(opc[2], 16)
    assert 0 <= mask <= 255
    bops = _get_bit_ops().get(opc[0])(mask)
    def fn(_):
        und = self.co.get_undo_size()
        pos = self.co.get_pos()
        if setting.use_single_operation:
            ret = __single_logical_bit_operation(self, pos, amp, bops)
        else:
            ret = __buffered_logical_bit_operation(self, pos, amp, bops)
        if ret > 0:
            self.co.merge_undo(ret)
            self.co.add_pos(amp)
        elif ret == -1:
            self.co.rollback_until(und)
    __exec_lrepaint(self, fn)

def __single_logical_bit_operation(self, pos, amp, fn):
    for x in util.get_xrange(amp):
        b = self.co.read(pos, 1)
        if not b:
            return x
        self.co.replace(pos, (fn(b),))
        pos += 1
        if pos > self.co.get_max_pos():
            break
        if screen.test_signal():
            self.co.flash(
                "Single bitwise operation interrupted ({0}/{1})".format(x, amp))
            return -1
    return amp

def __buffered_logical_bit_operation(self, pos, amp, fn):
    l = []
    for b in filebytes.iter(self.co.read(pos, amp)):
        l.append(fn(b))
        if screen.test_signal():
            self.co.flash("Buffered bitwise operation interrupted")
            return 0
    self.co.replace(pos, l)
    return 1

@_cleanup
def logical_bit_operation(self, amp, opc, arg, raw):
    amp = get_int(amp)
    if setting.use_unit_based:
        amp *= setting.bytes_per_unit
        __assert_bpu_aligned(self)
    generic_logical_bit_operation(self, amp, opc, arg, raw)

@_cleanup
def range_logical_bit_operation(self, amp, opc, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    generic_logical_bit_operation(self, siz, opc, [], raw)

@_cleanup
def block_logical_bit_operation(self, amp, opc, args, raw):
    test_replace_raise(self)
    test_empty_raise(self)
    mask = (int(opc[1], 16) << 4) | int(opc[2], 16)
    assert 0 <= mask <= 255
    bops = _get_bit_ops().get(opc[0])(mask)
    beg, end, mapx, siz, cnt = __get_block(self)
    self.co.set_pos(beg)
    def fn(_):
        und = self.co.get_undo_size()
        pos = self.co.get_pos()
        for i in util.get_xrange(cnt):
            if __buffered_logical_bit_operation(self, pos, siz, bops) == 0:
                self.co.rollback_restore_until(und)
                return
            pos += mapx
            if pos > self.co.get_max_pos():
                break
        self.co.merge_undo(i + 1)
        self.co.set_pos(pos - mapx + siz)
    __exec_lrepaint(self, fn)

def start_register(self, amp, opc, args, raw):
    self.co.start_register(opc[1])
    return REWIND

def generic_yank(self, amp, opc, args, raw):
    try:
        b = self.co.read(self.co.get_pos(), get_int(amp))
    except Exception as e:
        self.co.flash(e)
    else:
        self.co.set_yank_buffer(b)
        s = util.get_size_repr(self.co.get_yank_buffer_size())
        self.co.show(s + " yanked")

def yank(self, amp, opc, arg, raw):
    amp = get_int(amp)
    if setting.use_unit_based:
        amp *= setting.bytes_per_unit
        __assert_bpu_aligned(self)
    generic_yank(self, amp, opc, arg, raw)

def yank_till_end(self, amp, opc, args, raw):
    x = self.co.get_size() - self.co.get_pos()
    if x > 0:
        generic_yank(self, x, opc, args, raw)

def range_yank(self, amp, opc, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    generic_yank(self, siz, opc, [], raw)

def block_yank(self, amp, opc, args, raw):
    beg, end, mapx, siz, cnt = __get_block(self)
    l = []
    try:
        for i in util.get_xrange(cnt):
            l.append(self.co.read(beg, siz))
            beg += mapx
            if beg > self.co.get_max_pos():
                break
            if screen.test_signal():
                self.co.flash("Yank interrupted ({0}/{1})".format(i, cnt))
                return # return without else
    except Exception as e:
        self.co.flash(e)
    else:
        self.co.set_yank_buffer(filebytes.join(l))
        s = util.get_size_repr(self.co.get_yank_buffer_size())
        self.co.show(s + " yanked")

@_cleanup
def put(self, amp, opc, args, raw):
    return __put(self, amp, opc, 0)

@_cleanup
def put_after(self, amp, opc, args, raw):
    return __put(self, amp, opc, 1)

def __put(self, amp, opc, mov):
    test_insert_raise(self)
    if not self.co.get_yank_buffer_size():
        self.co.flash("Nothing to put")
        return
    amp = get_int(amp)
    if setting.use_unit_based:
        mov *= setting.bytes_per_unit
        __assert_bpu_aligned(self)

    def fn(_):
        buf = filebytes.ords(self.co.get_yank_buffer()) * amp
        pos = self.co.get_pos() + mov
        try:
            self.co.open_eof_insert()
            if pos > self.co.get_max_pos():
                pos = self.co.get_max_pos()
            self.co.insert(pos, buf)
            setting.discard_unit_based() # to move specified bytes
            go_right(self, mov + len(buf) - 1 * setting.bytes_per_unit)
            setting.restore_unit_based()
            __assert_bpu_aligned(self)
        finally:
            self.co.close_eof_insert()
    __exec_lrepaint(self, fn)

@_cleanup
def put_over(self, amp, opc, args, raw):
    __put_over(self, amp, opc, 0)

@_cleanup
def put_over_after(self, amp, opc, args, raw):
    __put_over(self, amp, opc, 1)

def __put_over(self, amp, opc, mov):
    test_replace_raise(self)
    if not self.co.get_yank_buffer_size():
        self.co.flash("Nothing to put")
        return
    amp = get_int(amp)
    def fn(_):
        buf = filebytes.ords(self.co.get_yank_buffer()) * amp
        pos = self.co.get_pos() + mov
        if pos > self.co.get_max_pos():
            pos = self.co.get_max_pos()
        self.co.replace(pos, buf)
        go_right(self, len(buf) - 1)
    __exec_lrepaint(self, fn)

@_cleanup
def range_put(self, amp, opc, args, raw):
    test_insert_raise(self)
    test_delete_raise(self)
    try:
        self.co.disconnect_workspace()
        self.co.open_eof_insert()
        buf = filebytes.ords(self.co.get_yank_buffer()) * get_int(amp)
        und = self.co.get_undo_size()
        range_delete(self, amp, opc, args, raw)
        self.co.insert_current(buf)
        self.co.merge_undo_until(und)
    finally:
        self.co.close_eof_insert()
        self.co.reconnect_workspace()
        self.co.lrepaintf()

@_cleanup
def block_put(self, amp, opc, args, raw):
    test_insert_raise(self)
    test_delete_raise(self)
    try:
        self.co.disconnect_workspace()
        self.co.open_eof_insert()
        buf = filebytes.ords(self.co.get_yank_buffer()) * get_int(amp)
        und = self.co.get_undo_size()
        block_delete(self, amp, opc, args, raw)
        self.co.insert_current(buf)
        self.co.merge_undo_until(und)
    finally:
        self.co.close_eof_insert()
        self.co.reconnect_workspace()
        self.co.lrepaintf()

def open_buffer(self, amp, opc, args, raw):
    if len(args) > 1:
        self.co.flash("Only one file name allowed")
    elif not args:
        self.co.show(self.co.get_path())
    else:
        ff = path.get_path(args[0])
        f, offset, length = kernel.parse_file_path(ff)
        ret = path.get_path_failure_message(path.Path(f))
        if ret:
            self.co.flash(ret)
        elif self.co.has_buffer(f):
            self.co.switch_to_buffer(f)
            self.co.lrepaintf()
            if offset or length:
                self.co.flash(f + " exists, can't partially open")
            else:
                offset = self.co.get_mapping_offset()
                length = self.co.get_mapping_length()
                if offset or length:
                    self.co.flash(f + " partially exists, can't open")
                else:
                    show_current(self, amp, opc, args, raw)
                    __try_update_address_num_width(self)
        else:
            self.co.add_buffer(ff)
            if __try_update_address_num_width(self) == -1:
                self.co.lrepaintf()
            return RETURN

def open_extension(self, amp, opc, args, raw):
    for li in literal.get_ext_literals():
        if li.str == opc:
            self.co.add_extension(li.fn, args)
            self.co.lrepaint()
            return RETURN

def close_buffer(self, amp, opc, args, raw):
    if len(args) > 1:
        self.co.flash("Only one file name allowed")
    else:
        if args:
            f = path.get_path(args[0])
        else:
            f = self.co.get_path()
        if not self.co.has_buffer(f):
            self.co.flash("No matching buffer for " + f)
        elif self.co.has_buffer(f, lambda o: o.is_dirty()):
            self.co.flash("No write since last change: " + f)
        else:
            self.co.remove_buffer(f)
            if __try_update_address_num_width(self) == -1:
                self.co.lrepaint()
            return RETURN

def save_buffer(self, amp, opc, args, raw):
    __save_buffer(self, args, False)

def force_save_buffer(self, amp, opc, args, raw):
    __save_buffer(self, args, True)

def __save_buffer(self, args, force):
    # returns -1 if not written
    f, overwrite = __get_save_path(self, args, force)
    if f is None:
        return -1
    try:
        if overwrite:
            buf = self.co.readall()
            msg, new = __overwrite_buffer(self, f, buf)
        else:
            msg, new = self.co.flush(f)
        if msg:
            self.co.show(msg)
        if new and os.path.isfile(new):
            __rename_buffer(self, new)
        if __try_update_address_num_width(self) == -1:
            self.co.lrepaintf()
    except Exception as e:
        self.co.flash(e)
        return -1

def __overwrite_buffer(self, f, buf):
    assert os.path.isfile(f) # existing file
    assert not self.co.has_buffer(f) # external file
    try:
        with util.do_atomic_write(f, fsync=kernel.fsync) as fd:
            fd.write(buf)
        msg = "{0} {1}[B] overwritten".format(f, kernel.get_size(f))
        return msg, None # XXX (msg, f) to be compatible with vi ?
    except Exception as e:
        raise fileobj.Error("Failed to overwrite: " +
            util.e_to_string(e, verbose=False))

def __rename_buffer(self, f):
    pos = self.co.get_pos()
    if self.co.reload_buffer(f) == -1:
        return -1
    # renamed
    go_to(self, pos)
    try:
        assert not self.co.is_dirty()
        self.co.flush() # throw away rollback log
    except fileobj.Error:
        pass

def __get_save_path(self, args, force):
    if len(args) > 1:
        self.co.flash("Only one file name allowed")
    elif not args:
        return self.co.get_path(), False
    else:
        o = path.Path(args[0])
        f = o.path
        ret = path.get_path_failure_message(o, False)
        if ret:
            self.co.flash(ret)
        elif f == self.co.get_path():
            return f, False # write to itself
        elif self.co.has_buffer(f):
            self.co.flash(f + " is loaded in another buffer")
        elif not o.is_noent:
            return f, force # overwrite existing external file if force
        else:
            return f, False # write new external file
    return None, False

def range_save_buffer(self, amp, opc, args, raw):
    __save_partial(self, args, __range_read, False)

def range_force_save_buffer(self, amp, opc, args, raw):
    __save_partial(self, args, __range_read, True)

def __range_read(self):
    beg, siz = __get_range(self)
    return self.co.read(beg, siz)

def block_save_buffer(self, amp, opc, args, raw):
    __save_partial(self, args, __block_read, False)

def block_force_save_buffer(self, amp, opc, args, raw):
    __save_partial(self, args, __block_read, True)

def __block_read(self):
    beg, end, mapx, siz, cnt = __get_block(self)
    l = []
    for i in util.get_xrange(cnt):
        l.append(self.co.read(beg + mapx * i, siz))
        if screen.test_signal():
            self.co.flash("Read interrupted ({0}/{1})".format(i, cnt))
            return None
    return filebytes.join(l)

def __save_partial(self, args, fn, force):
    # returns -1 if not written
    f, overwrite = __get_save_partial_path(self, args, force)
    if f is None:
        return -1
    try:
        buf = fn(self)
        if not buf:
            self.co.flash("No buffer selected")
            return -1
        if overwrite:
            msg, new = __overwrite_buffer(self, f, buf)
        else:
            assert not os.path.exists(f), f
            o = self.co.alloc_fileobj(f) # should not fail
            o.init_buffer(buf)
            msg, new = o.flush()
            assert new, new
        if msg:
            self.co.show(msg)
    except Exception as e:
        self.co.flash(e)
        return -1

def __get_save_partial_path(self, args, force):
    if len(args) > 1:
        self.co.flash("Only one file name allowed")
    elif not args:
        self.co.flash("File name required")
    else:
        o = path.Path(args[0])
        f = o.path
        ret = path.get_path_failure_message(o, False)
        if ret:
            self.co.flash(ret)
        elif f == self.co.get_path():
            self.co.flash("Can not write to this buffer")
        elif self.co.has_buffer(f):
            self.co.flash(f + " is loaded in another buffer")
        elif not o.is_noent:
            if not force:
                self.co.flash(f + " exists")
            else:
                return f, True # overwrite existing external file
        else:
            return f, False # write new external file
    return None, False

def quit(self, amp, opc, args, raw):
    if len(self.co) > 1:
        return remove_workspace(self, amp, opc, args, raw)
    else:
        def fn(o):
            return o.is_dirty()
        l = self.co.get_buffer_paths(fn)
        if not l:
            return QUIT
        f = self.co.get_path()
        if not self.co.has_buffer(f, fn):
            f = l[0]
            self.co.switch_to_buffer(f)
            self.co.lrepaintf()
        self.co.flash("No write since last change: " + f)

def force_quit(self, amp, opc, args, raw):
    if len(self.co) > 1:
        return remove_workspace(self, amp, opc, args, raw)
    else:
        return QUIT

def quit_all(self, amp, opc, args, raw):
    remove_other_workspace(self, amp, opc, args, raw)
    return quit(self, amp, opc, args, raw)

def force_quit_all(self, amp, opc, args, raw):
    remove_other_workspace(self, amp, opc, args, raw) # not must
    return force_quit(self, amp, opc, args, raw)

def save_buffer_quit(self, amp, opc, args, raw):
    if __save_buffer(self, args, False) != -1:
        return quit(self, amp, opc, args, raw)

def xsave_buffer_quit(self, amp, opc, args, raw):
    if self.co.is_dirty():
        return save_buffer_quit(self, amp, opc, [], raw)
    else:
        return quit(self, amp, opc, args, raw)

def range_save_buffer_quit(self, amp, opc, args, raw):
    if __save_partial(self, args, __range_read, False) != -1:
        return quit(self, amp, opc, args, raw)

def block_save_buffer_quit(self, amp, opc, args, raw):
    if __save_partial(self, args, __block_read, False) != -1:
        return quit(self, amp, opc, args, raw)

def escape(self, amp, opc, args, raw):
    self.co.clear_delayed_input()
    self.co.show('')

def __open_inmemory_buffer(self, args, efn):
    # returns -1 if not written
    f = __get_inmemory_buffer_path(self, args, efn)
    if f is None:
        return -1
    assert not os.path.exists(f), f
    try:
        buf = self.co.readall()
        if not buf:
            self.co.flash("No buffer")
            return -1
        buf = efn(buf)
        self.co.add_buffer(f)
        self.co.init_buffer(buf)
        if __try_update_address_num_width(self) == -1:
            self.co.lrepaintf()
        return RETURN
    except Exception as e:
        self.co.flash(e)
        return -1

def __open_inmemory_buffer_partial(self, args, fn, efn):
    # returns -1 if not written
    f = __get_inmemory_buffer_path(self, args, efn)
    if f is None:
        return -1
    assert not os.path.exists(f), f
    try:
        buf = fn(self)
        if not buf:
            self.co.flash("No buffer selected")
            return -1
        buf = efn(buf)
        self.co.add_buffer(f)
        self.co.init_buffer(buf)
        if __try_update_address_num_width(self) == -1:
            self.co.lrepaintf()
        return RETURN
    except Exception as e:
        self.co.flash(e)
        return -1

def __get_inmemory_buffer_path(self, args, efn):
    if len(args) > 1:
        self.co.flash("Only one file name allowed")
        return
    if args:
        f = args[0]
    else:
        f = "{0}_{1}".format(efn, os.path.basename(self.co.get_path()))
    o = path.Path(f)
    f = o.path
    ret = path.get_path_failure_message(o, False)
    if ret:
        self.co.flash(ret)
    elif self.co.has_buffer(f):
        self.co.flash(f + " is already loaded")
    elif not o.is_noent:
        self.co.flash(f + " exists")
    else:
        return f

def disas(self, amp, opc, args, raw):
    arch = setting.disas_arch
    if arch == "x86":
        __disas_x86(self, amp, opc, args, raw)
    else:
        self.co.flash("{0} unsupported".format(arch))

def __disas_x86(self, amp, opc, args, raw):
    if not disas_x86.is_supported():
        self.co.flash("Unsupported, install {0} (e.g. {1})".format(
            disas_x86.get_module_name(), disas_x86.get_module_install_cmd()))
        return

    priv = setting.disas_private
    if priv is not None:
        mode, move = priv.split(",")
        if mode != "":
            try:
                mode = int(mode)
                if mode not in disas_x86.valid_mode:
                    self.co.flash("Invalid mode {0}".format(mode))
                    return
            except ValueError as e:
                self.co.flash("Invalid mode: {0}".format(e))
                return
        else:
            mode = disas_x86.default_mode
        move = move != ""
    else:
        mode = disas_x86.default_mode
        move = False

    pos = self.co.get_pos()
    buf = self.co.read(pos, 15)
    if not buf:
        self.co.flash("Empty buffer")
        return
    try:
        l, _ = disas_x86.decode(pos, buf, mode)
    except Exception as e:
        self.co.flash("Failed to disassemble: {0}".format(e))
        return
    x = l[0]
    s = "0x{0:x} {1}[B] {2} \"{3}\"".format(*x)
    self.co.show(s)
    if move:
        go_right(self, x[1])

@_cleanup
def truncate(self, amp, opc, args, raw):
    test_truncate_raise(self)
    if not args:
        self.co.flash("Argument required")
        return
    tgtsiz = util.parse_size_repr(args[0])
    if not setting.use_truncate_shrink and tgtsiz < self.co.get_size():
        self.co.flash("{0} specified, but shrink disabled by default".format(
            util.get_size_repr(tgtsiz)))
        return

    try:
        self.co.truncate(tgtsiz)
    except Exception as e:
        self.co.flash(e)
        return
    newsiz = self.co.get_size()
    if newsiz == tgtsiz:
        self.co.set_pos(tgtsiz)
    else:
        # this shouldn't happen
        if setting.use_debug:
            assert False, (tgtsiz, newsiz)
        self.co.flash("Failed to truncate {0}, expecting {1}, got {2}".format(
            self.co.get_path(), util.get_size_repr(tgtsiz),
            util.get_size_repr(newsiz)))
    self.co.lrepaintf()

# keep this separated from init()
def __register_hashlib_methods(hash_algo):
    def _s(b):
        try:
            # XXX support hash object update
            return util.get_hash_string(hash_algo, b)
        except AttributeError:
            raise Exception("{0} unsupported by {1}".format(hash_algo,
                util.get_python_string()))

    def fn(self, amp, opc, args, raw):
        __show_hash(self, _s)
    setattr(this, "show_{0}".format(hash_algo), fn)

    def fn(self, amp, opc, args, raw):
        __show_hash_partial(self, __range_read, _s)
    setattr(this, "range_show_{0}".format(hash_algo), fn)

    def fn(self, amp, opc, args, raw):
        __show_hash_partial(self, __block_read, _s)
    setattr(this, "block_show_{0}".format(hash_algo), fn)

    def _b(b):
        try:
            # XXX support hash object update
            return util.get_hash_binary(hash_algo, b)
        except AttributeError:
            raise Exception("{0} unsupported by {1}".format(hash_algo,
                util.get_python_string()))

    def fn(self, amp, opc, args, raw):
        __open_inmemory_buffer(self, args, _b)
    setattr(this, "open_{0}".format(hash_algo), fn)

    def fn(self, amp, opc, args, raw):
        __open_inmemory_buffer_partial(self, args, __range_read, _b)
    setattr(this, "range_open_{0}".format(hash_algo), fn)

    def fn(self, amp, opc, args, raw):
        __open_inmemory_buffer_partial(self, args, __block_read, _b)
    setattr(this, "block_open_{0}".format(hash_algo), fn)

# keep this separated from init()
def __register_base64_methods(n):
    try:
        # base85 supported by Python 3.4+
        _enc = getattr(base64, "b{0}encode".format(n))
    except AttributeError:
        def _enc(b):
            raise Exception("base{0} encode unsupported by {1}".format(n,
                util.get_python_string()))

    def fn(self, amp, opc, args, raw):
        __open_inmemory_buffer(self, args, _enc)
    setattr(this, "open_base{0}_encode".format(n), fn)

    def fn(self, amp, opc, args, raw):
        __open_inmemory_buffer_partial(self, args, __range_read, _enc)
    setattr(this, "range_open_base{0}_encode".format(n), fn)

    def fn(self, amp, opc, args, raw):
        __open_inmemory_buffer_partial(self, args, __block_read, _enc)
    setattr(this, "block_open_base{0}_encode".format(n), fn)

    try:
        # base85 supported by Python 3.4+
        _dec = getattr(base64, "b{0}decode".format(n))
    except AttributeError:
        def _dec(b):
            raise Exception("base{0} decode unsupported by {1}".format(n,
                util.get_python_string()))

    def fn(self, amp, opc, args, raw):
        __open_inmemory_buffer(self, args, _dec)
    setattr(this, "open_base{0}_decode".format(n), fn)

    def fn(self, amp, opc, args, raw):
        __open_inmemory_buffer_partial(self, args, __range_read, _dec)
    setattr(this, "range_open_base{0}_decode".format(n), fn)

    def fn(self, amp, opc, args, raw):
        __open_inmemory_buffer_partial(self, args, __block_read, _dec)
    setattr(this, "block_open_base{0}_decode".format(n), fn)

# see consoles' init_method()
def init():
    # https://docs.python.org//3/library/hashlib.html
    # Python version < 3.6 doesn't have sha3_*, but still must register
    for x in ("md5", "sha1", "sha224", "sha256", "sha384", "sha512",
        "blake2b", "blake2s", "sha3_224", "sha3_256", "sha3_384", "sha3_512"):
        __register_hashlib_methods(x)

    for x in (64, 32, 16, 85):
        __register_base64_methods(x)

this = sys.modules[__name__]
init()
