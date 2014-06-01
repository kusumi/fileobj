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
import os
import platform
import time

from . import allocator
from . import filebytes
from . import fileobj
from . import kernel
from . import literal
from . import path
from . import screen
from . import setting
from . import stash
from . import util
from . import version

HANDLED  = None
CONTINUE = "CONTINUE"
RETURN   = "RETURN"
QUIT     = "QUIT"

def _rollback(fn):
    def _(self, amp, ope, args, raw):
        try:
            und = self.co.get_undo_size()
            return fn(self, amp, ope, args, raw)
        except fileobj.FileobjError as e:
            self.co.merge_undo_until(und)
            self.co.lrepaintf()
            self.co.flash(e)
    return _

def __use_single_operation(self, x):
    if x > self.co.get_size():
        x = self.co.get_size()
    if setting.use_single_operation:
        return True
    else:
        ram = kernel.get_free_ram()
        return ram != -1 and x > int(ram * setting.ram_thresh_ratio)

def __read_int(self, pos):
    return filebytes.ord(self.co.read(pos, 1))

def test_insert_raise(self):
    __test_permission_raise(self, "insert")

def test_replace_raise(self):
    __test_permission_raise(self, "replace")

def test_delete_raise(self):
    __test_permission_raise(self, "delete")

def __test_permission_raise(self, s):
    fn = getattr(self.co, "test_" + s)
    if not fn():
        self.co.raise_no_support(s)

def test_empty_raise(self):
    if self.co.is_empty():
        raise fileobj.FileobjError("Empty buffer")

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

def go_up(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_up(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_down(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_down(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_left(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_left(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_right(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_right(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_pprev(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_pprev(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_hpprev(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_hpprev(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_pnext(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_pnext(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_hpnext(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_hpnext(get_int(amp)) == -1:
        self.co.lrepaintf()

def go_head(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_head(get_int(amp) - 1) == -1:
        self.co.lrepaintf()

def go_tail(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_tail(get_int(amp) - 1) == -1:
        self.co.lrepaintf()

def go_lhead(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_lhead() == -1:
        self.co.lrepaintf()

def go_ltail(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_ltail(get_int(amp) - 1) == -1:
        self.co.lrepaintf()

def go_up_lhead(self, amp=None, ope=None, args=None, raw=None):
    go_up(self, amp, ope, args, raw)
    go_lhead(self, amp, ope, args, raw)

def go_down_lhead(self, amp=None, ope=None, args=None, raw=None):
    go_down(self, amp, ope, args, raw)
    go_lhead(self, amp, ope, args, raw)

def go_phead(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_phead(get_int(amp) - 1) == -1:
        self.co.lrepaintf()

def go_pcenter(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_pcenter() == -1:
        self.co.lrepaintf()

def go_ptail(self, amp=None, ope=None, args=None, raw=None):
    if self.co.go_ptail(get_int(amp) - 1) == -1:
        self.co.lrepaintf()

def go_to(self, amp=None, ope=None, args=None, raw=None):
    if amp is None:
        pos = 0
    else:
        pos = get_int(amp)
    if self.co.go_to(pos) == -1:
        self.co.lrepaintf()

def __is_graph(b):
    return util.is_graph(util.bytes_to_str(b))
def __is_zero(b):
    return b == filebytes.ZERO
def __is_non_zero(b):
    return b != filebytes.ZERO

def go_next_char(self, amp, ope, args, raw):
    __go_next_matched(self, get_int(amp), __is_graph)

def go_next_zero(self, amp, ope, args, raw):
    __go_next_matched(self, get_int(amp), __is_zero)

def go_next_nonzero(self, amp, ope, args, raw):
    __go_next_matched(self, get_int(amp), __is_non_zero)

def go_prev_char(self, amp, ope, args, raw):
    __go_prev_matched(self, get_int(amp), __is_graph)

def go_prev_zero(self, amp, ope, args, raw):
    __go_prev_matched(self, get_int(amp), __is_zero)

def go_prev_nonzero(self, amp, ope, args, raw):
    __go_prev_matched(self, get_int(amp), __is_non_zero)

def __go_next_matched(self, cnt, fn):
    n = util.PAGE_SIZE
    pos = self.co.get_pos()
    while True:
        pos += 1
        if pos > self.co.get_max_pos():
            self.co.flash("Search failed")
            return
        b = self.co.read(pos, n)
        d = 0
        for x in filebytes.iter(b):
            if fn(x):
                cnt -= 1
                if not cnt:
                    go_to(self, pos + d)
                    return
            d += 1
        pos += n
        if len(b) < n:
            self.co.flash("Search failed")
            return
        if screen.test_signal():
            self.co.flash("Search interrupted")
            return

def __go_prev_matched(self, cnt, fn):
    n = util.PAGE_SIZE
    pos = self.co.get_pos()
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
                    return
            d += 1
        if not pos:
            self.co.flash("Search failed")
            return
        if screen.test_signal():
            self.co.flash("Search interrupted")
            return

def start_read_delayed_input(self, amp, ope, args, raw):
    self.co.start_read_delayed_input(
        literal.bracket2_beg.seq[0], literal.bracket2_end.seq[0])
    self.co.show(util.to_chr_repr(ope[0]))

def end_read_delayed_input(self, amp, ope, args, raw):
    s = self.co.end_read_delayed_input()
    self.co.show('')
    self.ope.clear()
    ret = util.parse_size_string(s, self.co.get_sector_size())
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

def goto_first_buffer(self, amp, ope, args, raw):
    if self.co.get_buffer_count() > 1:
        self.co.goto_first_buffer()
        self.co.lrepaintf()
        return RETURN

def goto_last_buffer(self, amp, ope, args, raw):
    if self.co.get_buffer_count() > 1:
        self.co.goto_last_buffer()
        self.co.lrepaintf()
        return RETURN

def goto_next_buffer(self, amp, ope, args, raw):
    if self.co.get_buffer_count() > 1:
        self.co.goto_next_buffer()
        self.co.lrepaintf()
        return RETURN

def goto_prev_buffer(self, amp, ope, args, raw):
    if self.co.get_buffer_count() > 1:
        self.co.goto_prev_buffer()
        self.co.lrepaintf()
        return RETURN

def resize_container(self, amp, ope, args, raw):
    self.co.resize()
    self.co.repaint()

def refresh_container(self, amp, ope, args, raw):
    self.co.refresh()
    self.co.repaint()

def goto_next_workspace(self, amp, ope, args, raw):
    if len(self.co) > 1:
        self.co.wbrepaint(False)
        self.co.goto_next_workspace()
        self.co.wbrepaint(True)
        return RETURN

def goto_prev_workspace(self, amp, ope, args, raw):
    if len(self.co) > 1:
        self.co.wbrepaint(False)
        self.co.goto_prev_workspace()
        self.co.wbrepaint(True)
        return RETURN

def goto_top_workspace(self, amp, ope, args, raw):
    if len(self.co) > 1:
        self.co.wbrepaint(False)
        self.co.goto_top_workspace()
        self.co.wbrepaint(True)
        return RETURN

def goto_bottom_workspace(self, amp, ope, args, raw):
    if len(self.co) > 1:
        self.co.wbrepaint(False)
        self.co.goto_bottom_workspace()
        self.co.wbrepaint(True)
        return RETURN

def add_workspace(self, amp, ope, args, raw):
    self.co.add_workspace()
    self.co.repaint()

def split_workspace(self, amp, ope, args, raw):
    self.co.add_workspace()
    if args:
        open_buffer(self, amp, ope, args, raw)
    self.co.repaint()

def inc_workspace_height(self, amp, ope, args, raw):
    if self.co.adjust_workspace(get_int(amp)) != -1:
        self.co.repaint()
    else:
        self.co.flash()

def dec_workspace_height(self, amp, ope, args, raw):
    if self.co.adjust_workspace(-get_int(amp)) != -1:
        self.co.repaint()
    else:
        self.co.flash()

def remove_workspace(self, amp, ope, args, raw):
    if self.co.remove_workspace() != -1:
        self.co.repaint()
    return RETURN

def remove_other_workspace(self, amp, ope, args, raw):
    if self.co.remove_other_workspace() != -1:
        self.co.repaint()

def __set_oct(self, args):
    setting.offset_num_radix = 8
def __set_dec(self, args):
    setting.offset_num_radix = 10
def __set_hex(self, args):
    setting.offset_num_radix = 16

def __set_binary(self, args):
    setting.editmode = 'B'
def __set_ascii(self, args):
    setting.editmode = 'A'

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

def __set_width(self, args):
    prev = self.co.get_bytes_per_line()
    if len(args) == 1:
        self.co.show(prev)
    elif self.co.set_bytes_per_line(args[1]) == -1:
        self.co.flash("Invalid arg: {0}".format(args[1]))
    elif self.co.get_bytes_per_line() != prev:
        screen.refresh()
        self.co.build()
        self.co.repaint()

_set_methods = {
    literal.s_set_oct.seq:    __set_oct,
    literal.s_set_dec.seq:    __set_dec,
    literal.s_set_hex.seq:    __set_hex,
    literal.s_set_binary.seq: __set_binary,
    literal.s_set_ascii.seq:  __set_ascii,
    literal.s_set_le.seq:     __set_le,
    literal.s_set_be.seq:     __set_be,
    literal.s_set_ws.seq:     __set_ws,
    literal.s_set_nows.seq:   __set_nows,
    literal.s_set_ic.seq:     __set_ic,
    literal.s_set_noic.seq:   __set_noic,
    literal.s_set_si.seq:     __set_si,
    literal.s_set_nosi.seq:   __set_nosi,
    literal.s_set_width.seq:  __set_width, }

def set_option(self, amp, ope, args, raw):
    if not args:
        self.co.flash("No arg")
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
        fn(self, args)
        self.co.lrepaint()
    else:
        self.co.flash("Unknown option: {0}".format(args[0]))

def show_current(self, amp, ope, args, raw):
    self.co.show("{0} {1} at {2}".format(
        self.co.get_short_path(),
        util.get_size_string(self.co.get_size()),
        util.get_size_string(self.co.get_pos())))

def show_current_sector(self, amp, ope, args, raw):
    sector_size = self.co.get_sector_size()
    if sector_size == -1:
        show_current(self, amp, ope, args, raw)
    else:
        self.co.show("{0} {1}[sectors] at {2}".format(
            self.co.get_short_path(),
            self.co.get_size() // sector_size,
            self.co.get_pos() // sector_size))

def show_self(self, amp, ope, args, raw):
    self.co.show(self)

def show_pwd(self, amp, ope, args, raw):
    self.co.show(os.getcwd())

def show_date(self, amp, ope, args, raw):
    self.co.show(time.ctime())

def show_platform(self, amp, ope, args, raw):
    self.co.show("{0} {1}".format(
        util.get_system_string(), util.get_release_string()))

def show_hostname(self, amp, ope, args, raw):
    self.co.show(platform.node())

def show_term(self, amp, ope, args, raw):
    self.co.show(os.getenv("TERM"))

def show_lang(self, amp, ope, args, raw):
    self.co.show(os.getenv("LANG"))

def show_version(self, amp, ope, args, raw):
    self.co.show(version.__version__)

def show_sector_size(self, amp, ope, args, raw):
    x = self.co.get_sector_size()
    if x != -1:
        self.co.show(util.get_size_string(x))
    else:
        self.co.flash()

def show_args(self, amp, ope, args, raw):
    l = list(self.co.get_buffer_short_paths())
    x = self.co.get_short_path()
    l[l.index(x)] = "[{0}]".format(x)
    self.co.show(' '.join(l))

@_rollback
def inc_number(self, amp, ope, args, raw):
    __do_replace_number(self, get_int(amp), ope, 1)

@_rollback
def range_inc_number(self, amp, ope, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    __do_replace_number(self, get_int(amp), ope, siz)

@_rollback
def block_inc_number(self, amp, ope, args, raw):
    beg, end, mapx, siz, cnt = __get_block(self)
    if cnt == 1:
        self.co.set_pos(beg)
        __do_replace_number(self, get_int(amp), ope, siz)
    else:
        self.co.flash()

@_rollback
def dec_number(self, amp, ope, args, raw):
    __do_replace_number(self, -get_int(amp), ope, 1)

@_rollback
def range_dec_number(self, amp, ope, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    __do_replace_number(self, -get_int(amp), ope, siz)

@_rollback
def block_dec_number(self, amp, ope, args, raw):
    beg, end, mapx, siz, cnt = __get_block(self)
    if cnt == 1:
        self.co.set_pos(beg)
        __do_replace_number(self, -get_int(amp), ope, siz)
    else:
        self.co.flash()

def __do_replace_number(self, amp, ope, siz):
    def fn(_):
        if siz > 8:
            self.co.flash("Only <= 8 bytes allowed")
            return
        b = self.co.read_current(siz)
        if not b:
            self.co.flash("Empty buffer")
            return
        x = util.bin_to_int(b) + amp
        if x < 0:
            x += 2 ** (len(b) * 8)
        b = util.int_to_bin(x, len(b))
        if b is None:
            raise fileobj.FileobjError("Failed to convert")
        self.co.replace_current(filebytes.ords(b))
        self.co.show(util.bin_to_int(b))
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

_did_search_forward = True
def search_forward(self, amp, ope, args, raw):
    __do_search(self, ope, True)
def search_backward(self, amp, ope, args, raw):
    __do_search(self, ope, False)

def __do_search(self, s, is_forward):
    global _did_search_forward
    if len(s) == 1:
        s = self.ope.get_prev_history(s[0])
        if not s:
            self.co.flash("No previous search")
            return
    _did_search_forward = is_forward
    __search(self, self.co.get_pos(), s, is_forward)

def search_next_forward(self, amp, ope, args, raw):
    __do_search_next(self, '/')
def search_next_backward(self, amp, ope, args, raw):
    __do_search_next(self, '?')

def __do_search_next(self, key):
    if _did_search_forward:
        x = '/'
    else:
        x = '?'
    s = self.ope.get_prev_history(x)
    if not s:
        self.co.flash("No previous search")
        return
    pos = self.co.get_pos()
    is_forward = x == key
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
    __search(self, pos, s, is_forward)

def __search(self, pos, s, is_forward):
    assert s[0] in "/?"
    word = util.pack_hex_string(s[1:])
    if is_forward:
        fn = self.co.search
    else:
        fn = self.co.rsearch
    ret = fn(pos, word, -1)
    if ret == -1 and setting.use_wrapscan:
        if is_forward:
            x = 0
        else:
            x = self.co.get_max_pos()
        ret = fn(x, word, pos)
    if ret == -1:
        self.co.flash("Search {0} failed".format(repr(word)))
    elif ret == -2:
        self.co.flash("Search {0} interrupted".format(repr(word)))
    elif ret < 0:
        self.co.flash("Search error {0}".format(ret))
    elif ret != self.co.get_pos():
        go_to(self, ret)

@_rollback
def delete(self, amp, ope, args, raw):
    test_delete_raise(self)
    amp = get_int(amp)
    def fn(_):
        buf = self.co.read_current(amp)
        self.co.delete_current(amp)
        if not _:
            self.co.init_yank_buffer(buf)
        else:
            self.co.right_add_yank_buffer(buf)
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

@_rollback
def backspace(self, amp, ope, args, raw):
    test_delete_raise(self)
    amp = get_int(amp)
    def fn(_):
        if self.co.get_pos() > 0:
            self.co.add_pos(-amp)
        buf = self.co.read_current(amp)
        self.co.delete_current(amp)
        if not _:
            self.co.init_yank_buffer(buf)
        else:
            self.co.left_add_yank_buffer(buf)
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

def delete_till_end(self, amp, ope, args, raw):
    x = self.co.get_size() - self.co.get_pos()
    if x > 0:
        delete(self, x, ope, args, raw)

@_rollback
def range_delete(self, amp, ope, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    delete(self, siz, ope, [], raw)

@_rollback
def block_delete(self, amp, ope, args, raw):
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
            self.co.init_yank_buffer(buf)
        else:
            self.co.right_add_yank_buffer(buf)
        self.co.merge_undo(i + 1)
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

@_rollback
def toggle(self, amp, ope, args, raw):
    test_replace_raise(self)
    test_empty_raise(self)
    amp = get_int(amp)
    def fn(_):
        und = self.co.get_undo_size()
        pos = self.co.get_pos()
        if __use_single_operation(self, amp):
            ret = __single_toggle(self, pos, amp)
        else:
            ret = __buffered_toggle(self, pos, amp)
        if ret > 0:
            self.co.merge_undo(ret)
            self.co.add_pos(amp)
        elif ret == -1:
            self.co.rollback_until(und)
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

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

@_rollback
def range_toggle(self, amp, ope, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    toggle(self, siz, ope, [], raw)

@_rollback
def block_toggle(self, amp, ope, args, raw):
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
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

@_rollback
def range_replace(self, amp, ope, args, raw):
    test_replace_raise(self)
    beg, siz = __get_range(self)
    l = tuple(args for x in range(siz))
    self.co.set_pos(beg)
    def fn(_):
        pos = self.co.get_pos()
        self.co.replace(pos, l)
        self.co.set_pos(pos + siz)
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

@_rollback
def block_replace(self, amp, ope, args, raw):
    test_replace_raise(self)
    beg, end, mapx, siz, cnt = __get_block(self)
    l = tuple(args for x in range(siz))
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
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

@_rollback
def rotate_right(self, amp, ope, args, raw):
    test_empty_raise(self)
    __do_rotate_right(self, amp, ope, self.co.get_size() - self.co.get_pos())

def __do_rotate_right(self, amp, ope, siz):
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
        if __use_single_operation(self, end - beg):
            ret = __single_rotate_right(self, shift, beg, end)
        else:
            ret = __buffered_rotate_right(self, shift, beg, end)
        if ret > 0:
            self.co.merge_undo(ret)
        elif ret == -1:
            self.co.rollback_until(und)
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

def __single_rotate_right(self, shift, beg, end):
    car = 0
    pos = beg
    car_shift = 8 - shift
    if setting.use_circular_bit_shift:
        car = __read_int(self, end) << car_shift
    while pos <= end:
        x = __read_int(self, pos)
        u = (car & 0xFF) | (x >> shift)
        self.co.replace(pos, (u,))
        car = x << car_shift
        pos += 1
        if screen.test_signal():
            self.co.flash(
                "Rotate right interrupted ({0}/{1})".format(pos, end))
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

@_rollback
def range_rotate_right(self, amp, ope, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    __do_rotate_right(self, amp, ope, siz)

@_rollback
def block_rotate_right(self, amp, ope, args, raw):
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
            car = __read_int(self, pos_end) << car_shift
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
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

@_rollback
def rotate_left(self, amp, ope, args, raw):
    test_empty_raise(self)
    __do_rotate_left(self, amp, ope, self.co.get_pos() + 1)

def __do_rotate_left(self, amp, ope, siz):
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
        if __use_single_operation(self, beg - end):
            ret = __single_rotate_left(self, shift, beg, end)
        else:
            ret = __buffered_rotate_left(self, shift, beg, end)
        if ret > 0:
            self.co.merge_undo(ret)
        elif ret == -1:
            self.co.rollback_until(und)
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

def __single_rotate_left(self, shift, beg, end):
    car = 0
    pos = beg
    car_shift = 8 - shift
    if setting.use_circular_bit_shift:
        car = __read_int(self, end) >> car_shift
    while pos >= end:
        x = __read_int(self, pos)
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

@_rollback
def range_rotate_left(self, amp, ope, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg + siz - 1)
    __do_rotate_left(self, amp, ope, siz)

@_rollback
def block_rotate_left(self, amp, ope, args, raw):
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
            car = __read_int(self, pos_end) >> car_shift
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
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

@_rollback
def repeat(self, amp, ope, args, raw):
    pxfn = self.co.get_xprev_context()
    if not pxfn:
        self.co.flash("No previous command")
    elif amp is None:
        __call_context(self, pxfn, 0)
    else:
        amp = get_int(amp)
        fn = self.co.get_prev_context()
        if amp <= 1:
            __call_context(self, fn, 0)
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
            __call_context(self, xfn, 0)
            self.co.set_prev_context(fn, xfn)

def __call_context(self, fn, i):
    fn(i)
    self.co.lrepaintf()

def undo(self, amp, ope, args, raw):
    ret = self.co.undo(get_int(amp))
    if ret == -1:
        self.co.flash("Already at oldest change")
    elif ret == -2:
        self.co.flash("Undo interrupted")
    elif ret >= 0 and ret != self.co.get_pos():
        self.co.set_pos(ret)
    self.co.lrepaintf()

def undo_all(self, amp, ope, args, raw):
    siz = self.co.get_undo_size()
    undo(self, siz if siz else 1, ope, args, raw)

def redo(self, amp, ope, args, raw):
    ret = self.co.redo(get_int(amp))
    if ret == -1:
        self.co.flash("Already at newest change")
    elif ret == -2:
        self.co.flash("Redo interrupted")
    elif ret >= 0 and ret != self.co.get_pos():
        self.co.set_pos(ret)
    self.co.lrepaintf()

def set_mark(self, amp, ope, args, raw):
    key = ope[1]
    pos = self.co.get_pos()
    s = "Mark '{0}' at {1}[B]".format(key, pos)
    if key.isupper():
        self.co.set_uniq_mark(key, pos, self.co.get_path())
        self.co.show(s)
    else:
        self.co.set_mark(key, pos)
        self.co.show("{0} for {1}".format(s, self.co.get_path()))

def get_mark(self, amp, ope, args, raw):
    key = ope[1]
    if key.isupper():
        f, pos = self.co.get_uniq_mark(key)
    else:
        f, pos = self.co.get_path(), self.co.get_mark(key)
    if f is not None and pos != -1:
        if self.co.get_path() != f:
            self.co.goto_buffer(f)
            self.co.lrepaintf()
        go_to(self, pos)
    else:
        s = "Mark '{0}' not set".format(key)
        if key.isupper():
            self.co.flash(s)
        else:
            self.co.flash("{0} for {1}".format(s, f))

def delete_mark(self, amp, ope, args, raw):
    if not args:
        self.co.flash("Argument required")
        return
    for arg in args:
        for k in arg:
            self.co.delete_mark(k)

def clear_mark(self, amp, ope, args, raw):
    """Does not clear uniq marks"""
    self.co.clear_mark(lambda k: not k.isupper())

def start_record(self, amp, ope, args, raw):
    if ope != literal.q.str:
        self.co.start_record(ope[1])
        self.co.push_banner("recording")
    else:
        self.co.end_record()
        self.co.pop_banner()

def replay_record(self, amp, ope, args, raw):
    assert len(ope) > 1
    for x in util.get_xrange(get_int(amp)):
        self.co.replay_record(ope[1])

def __get_and_ops(mask):
    return lambda b: filebytes.ord(b) & mask
def __get_or_ops(mask):
    return lambda b: filebytes.ord(b) | mask
def __get_xor_ops(mask):
    return lambda b: filebytes.ord(b) ^ mask

_bit_ops = {
    literal.bit_and.key: __get_and_ops,
    literal.bit_or.key : __get_or_ops,
    literal.bit_xor.key: __get_xor_ops, }

@_rollback
def logical_bit_operation(self, amp, ope, arg, raw):
    test_replace_raise(self)
    test_empty_raise(self)
    amp = get_int(amp)
    mask = (int(ope[1], 16) << 4) | int(ope[2], 16)
    assert 0 <= mask <= 255
    bops = _bit_ops.get(ope[0])(mask)
    def fn(_):
        und = self.co.get_undo_size()
        pos = self.co.get_pos()
        if __use_single_operation(self, amp):
            ret = __single_logical_bit_operation(self, pos, amp, bops)
        else:
            ret = __buffered_logical_bit_operation(self, pos, amp, bops)
        if ret > 0:
            self.co.merge_undo(ret)
            self.co.add_pos(amp)
        elif ret == -1:
            self.co.rollback_until(und)
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

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
                "Single logical bit operation interrupted ({0}/{1})".format(
                x, amp))
            return -1
    return amp

def __buffered_logical_bit_operation(self, pos, amp, fn):
    l = []
    for b in filebytes.iter(self.co.read(pos, amp)):
        l.append(fn(b))
        if screen.test_signal():
            self.co.flash("Buffered logical bit operation interrupted")
            return 0
    self.co.replace(pos, l)
    return 1

@_rollback
def range_logical_bit_operation(self, amp, ope, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    logical_bit_operation(self, siz, ope, [], raw)

@_rollback
def block_logical_bit_operation(self, amp, ope, args, raw):
    test_replace_raise(self)
    test_empty_raise(self)
    mask = (int(ope[1], 16) << 4) | int(ope[2], 16)
    assert 0 <= mask <= 255
    bops = _bit_ops.get(ope[0])(mask)
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
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

def yank(self, amp, ope, args, raw):
    try:
        b = self.co.read(self.co.get_pos(), get_int(amp))
    except Exception as e:
        self.co.flash(e)
    else:
        self.co.init_yank_buffer(b)
        self.co.show("{0} yanked".format(
            util.get_size_string(self.co.get_yank_buffer_size())))

def yank_till_end(self, amp, ope, args, raw):
    x = self.co.get_size() - self.co.get_pos()
    if x > 0:
        yank(self, x, ope, args, raw)

def range_yank(self, amp, ope, args, raw):
    beg, siz = __get_range(self)
    self.co.set_pos(beg)
    yank(self, siz, ope, [], raw)

def block_yank(self, amp, ope, args, raw):
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
        self.co.init_yank_buffer(filebytes.join(l))
        self.co.show("{0} yanked".format(
            util.get_size_string(self.co.get_yank_buffer_size())))

@_rollback
def put(self, amp, ope, args, raw):
    return __put(self, amp, ope, 0)
@_rollback
def put_after(self, amp, ope, args, raw):
    return __put(self, amp, ope, 1)

def __put(self, amp, ope, mov):
    test_insert_raise(self)
    if not self.co.get_yank_buffer_size():
        self.co.flash("Nothing to put")
        return
    amp = get_int(amp)
    def fn(_):
        buf = filebytes.ords(self.co.get_yank_buffer()) * amp
        pos = self.co.get_pos() + mov
        try:
            self.co.discard_eof()
            if pos > self.co.get_max_pos():
                pos = self.co.get_max_pos()
            self.co.insert(pos, buf)
            go_right(self, mov + len(buf) - 1)
        finally:
            self.co.restore_eof()
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

@_rollback
def put_over(self, amp, ope, args, raw):
    __put_over(self, amp, ope, 0)
@_rollback
def put_over_after(self, amp, ope, args, raw):
    __put_over(self, amp, ope, 1)

def __put_over(self, amp, ope, mov):
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
    fn(0)
    self.co.lrepaintf()
    self.co.set_prev_context(fn)

@_rollback
def range_put(self, amp, ope, args, raw):
    test_insert_raise(self)
    test_delete_raise(self)
    try:
        self.co.discard_workspace()
        self.co.discard_eof()
        buf = filebytes.ords(self.co.get_yank_buffer()) * get_int(amp)
        und = self.co.get_undo_size()
        range_delete(self, amp, ope, args, raw)
        self.co.insert_current(buf)
        self.co.merge_undo_until(und)
    finally:
        self.co.restore_eof()
        self.co.restore_workspace()
        self.co.lrepaintf()

@_rollback
def block_put(self, amp, ope, args, raw):
    test_insert_raise(self)
    test_delete_raise(self)
    try:
        self.co.discard_workspace()
        self.co.discard_eof()
        buf = filebytes.ords(self.co.get_yank_buffer()) * get_int(amp)
        und = self.co.get_undo_size()
        block_delete(self, amp, ope, args, raw)
        self.co.insert_current(buf)
        self.co.merge_undo_until(und)
    finally:
        self.co.restore_eof()
        self.co.restore_workspace()
        self.co.lrepaintf()

def open_buffer(self, amp, ope, args, raw):
    if len(args) > 1:
        self.co.flash("Only one file name allowed")
    elif not args:
        self.co.show(self.co.get_path())
    else:
        ff = path.get_path(args[0])
        f, offset, length = util.parse_file_path(ff)
        ret = path.get_path_failure_message(path.Path(f))
        if ret:
            self.co.flash(ret)
        elif self.co.has_buffer(f):
            self.co.goto_buffer(f)
            self.co.lrepaintf()
            show_current(self, amp, ope, args, raw)
        else:
            self.co.add_buffer(ff)
            self.co.lrepaintf()
            return RETURN

def open_extension(self, amp, ope, args, raw):
    for li in literal.get_ext_literals():
        if li.str == ope:
            self.co.add_extension(li.fn, args)
            self.co.lrepaint()
            return RETURN

def close_buffer(self, amp, ope, args, raw):
    if len(args) > 1:
        self.co.flash("Only one file name allowed")
    else:
        if args:
            f = path.get_path(args[0])
        else:
            f = self.co.get_path()
        if not self.co.has_buffer(f):
            self.co.flash("No matching buffer for {0}".format(
                path.get_short_path(f)))
        elif self.co.has_buffer(f, lambda o: o.is_dirty()):
            self.co.flash("No write since last change: {0}".format(f))
        else:
            self.co.remove_buffer(f)
            self.co.lrepaint()
            return RETURN

def save_buffer(self, amp, ope, args, raw):
    __save_buffer(self, args, False)

def force_save_buffer(self, amp, ope, args, raw):
    __save_buffer(self, args, True)

def __save_buffer(self, args, force):
    f, overwrite = __get_save_path(self, args, force)
    if f is None:
        return -1
    try:
        if overwrite:
            tmp = stash.TemporaryFile(f, unlink=True)
        else:
            tmp = None
        msg, new = self.co.flush(f)
        if msg:
            self.co.show(msg)
        if new and os.path.isfile(new):
            __rename_buffer(self, new)
        self.co.lrepaintf()
    except Exception as e:
        self.co.flash(e)
        if overwrite and tmp:
            tmp.restore()
    finally:
        if tmp:
            tmp.cleanup()

def __rename_buffer(self, f):
    pos = self.co.get_pos()
    if self.co.reload_buffer(f) == -1:
        return -1
    go_to(self, pos)
    try:
        assert not self.co.is_dirty()
        self.co.flush()
    except fileobj.FileobjError:
        pass

def __get_save_path(self, args, force):
    if len(args) > 1:
        self.co.flash("Only one file name allowed")
    elif not args:
        return self.co.get_path(), False
    else:
        o = path.Path(args[0])
        f = o.path
        ret = path.get_path_failure_message(o)
        if ret:
            self.co.flash(ret)
        elif f != self.co.get_path() and self.co.has_buffer(f):
            self.co.flash(f + " is loaded in another buffer")
        elif f != self.co.get_path() and not o.is_noent:
            return f, force
        else:
            return f, False
    return None, False

def range_save_buffer(self, amp, ope, args, raw):
    __save_partial(self, args, __range_read, False)

def range_force_save_buffer(self, amp, ope, args, raw):
    __save_partial(self, args, __range_read, True)

def __range_read(self):
    beg, siz = __get_range(self)
    return self.co.read(beg, siz)

def block_save_buffer(self, amp, ope, args, raw):
    __save_partial(self, args, __block_read, False)

def block_force_save_buffer(self, amp, ope, args, raw):
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
    f, overwrite = __get_save_partial_path(self, args, force)
    if f is None:
        return -1
    buf = fn(self)
    if not buf:
        return -1
    try:
        if overwrite:
            tmp = stash.TemporaryFile(f, unlink=True)
        else:
            tmp = None
        assert not os.path.exists(f)
        o = allocator.alloc(f)
        o.insert(0, buf)
        msg, new = o.flush()
        if msg:
            self.co.show(msg)
        assert new, new
    except Exception as e:
        self.co.flash(e)
        if overwrite and tmp:
            tmp.restore()
    finally:
        if tmp:
            tmp.cleanup()

def __get_save_partial_path(self, args, force):
    if len(args) > 1:
        self.co.flash("Only one file name allowed")
    elif not args:
        self.co.flash("No file name")
    else:
        o = path.Path(args[0])
        f = o.path
        ret = path.get_path_failure_message(o)
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
                return f, True
        else:
            return f, False
    return None, False

def quit(self, amp, ope, args, raw):
    if len(self.co) > 1:
        if self.co.remove_workspace() != -1:
            self.co.repaint()
        return RETURN
    else:
        def fn(o):
            return o.is_dirty()
        l = self.co.get_buffer_paths(fn)
        if not l:
            return QUIT
        f = self.co.get_path()
        if not self.co.has_buffer(f, fn):
            f = l[0]
            self.co.goto_buffer(f)
            self.co.lrepaintf()
        self.co.flash("No write since last change: {0}".format(f))

def force_quit(self, amp, ope, args, raw):
    if len(self.co) > 1:
        if self.co.remove_workspace() != -1:
            self.co.repaint()
        return RETURN
    else:
        return QUIT

def save_buffer_quit(self, amp, ope, args, raw):
    if __save_buffer(self, args, False) != -1:
        return quit(self, amp, ope, args, raw)

def xsave_buffer_quit(self, amp, ope, args, raw):
    if self.co.is_dirty():
        return save_buffer_quit(self, amp, ope, [], raw)
    else:
        return quit(self, amp, ope, args, raw)

def escape(self, amp, ope, args, raw):
    self.co.clear_delayed_input()
    self.co.show('')
