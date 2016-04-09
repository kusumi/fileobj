# Copyright (c) 2010-2016, TOMOHIRO KUSUMI
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

from . import console
from . import edit
from . import kbd
from . import methods
from . import literal
from . import visual

class _console (console.Console):
    def init_method(self):
        this = sys.modules[__name__]
        self.add_method(literal.up           , methods, "cursor_up")
        self.add_method(literal.down         , methods, "cursor_down")
        self.add_method(literal.left         , methods, "cursor_left")
        self.add_method(literal.right        , methods, "cursor_right")
        self.add_method(literal.gg           , methods, "cursor_head")
        self.add_method(literal.G            , methods, "cursor_tail")
        self.add_method(literal.zero         , methods, "cursor_lhead")
        self.add_method(literal.doller       , methods, "cursor_ltail")
        self.add_method(literal.minus        , methods, "cursor_up_lhead")
        self.add_method(literal.plus         , methods, "cursor_down_lhead")
        self.add_method(literal.H            , methods, "cursor_phead")
        self.add_method(literal.M            , methods, "cursor_pcenter")
        self.add_method(literal.L            , methods, "cursor_ptail")
        self.add_method(literal.w            , methods, "cursor_next_char")
        self.add_method(literal.b            , methods, "cursor_prev_char")
        self.add_method(literal.parens_end   , methods, "cursor_next_zero")
        self.add_method(literal.parens_beg   , methods, "cursor_prev_zero")
        self.add_method(literal.bracket1_end , methods, "cursor_next_nonzero")
        self.add_method(literal.bracket1_beg , methods, "cursor_prev_nonzero")
        self.add_method(literal.bracket2_end , methods, "end_read_delayed_input")
        self.add_method(literal.bracket2_beg , methods, "start_read_delayed_input")
        self.add_method(literal.go           , methods, "cursor_to")
        self.add_method(literal.ctrlb        , methods, "cursor_pprev")
        self.add_method(literal.ctrlu        , methods, "cursor_hpprev")
        self.add_method(literal.ctrlf        , methods, "cursor_pnext")
        self.add_method(literal.ctrld        , methods, "cursor_hpnext")
        self.add_method(literal.resize       , methods, "resize_container")
        self.add_method(literal.ctrll        , methods, "refresh_container")
        self.add_method(literal.ctrlw_w      , methods, "switch_to_next_workspace")
        self.add_method(literal.ctrlw_W      , methods, "switch_to_prev_workspace")
        self.add_method(literal.ctrlw_t      , methods, "switch_to_top_workspace")
        self.add_method(literal.ctrlw_b      , methods, "switch_to_bottom_workspace")
        self.add_method(literal.ctrlw_s      , methods, "add_workspace")
        self.add_method(literal.s_split      , methods, "split_workspace")
        self.add_method(literal.ctrlw_plus   , methods, "inc_workspace_height")
        self.add_method(literal.ctrlw_minus  , methods, "dec_workspace_height")
        self.add_method(literal.s_close      , methods, "remove_workspace")
        self.add_method(literal.s_only       , methods, "remove_other_workspace")
        self.add_method(literal.s_e          , methods, "open_buffer")
        self.add_method(literal.s_bdelete    , methods, "close_buffer")
        self.add_method(literal.s_bfirst     , methods, "switch_to_first_buffer")
        self.add_method(literal.s_blast      , methods, "switch_to_last_buffer")
        self.add_method(literal.s_bnext      , methods, "switch_to_next_buffer")
        self.add_method(literal.s_bprev      , methods, "switch_to_prev_buffer")
        self.add_method(literal.s_set        , methods, "set_option")
        self.add_method(literal.ctrlg        , methods, "show_current")
        self.add_method(literal.g_ctrlg      , methods, "show_current_sector")
        self.add_method(literal.s_self       , methods, "show_self")
        self.add_method(literal.s_pwd        , methods, "show_pwd")
        self.add_method(literal.s_date       , methods, "show_date")
        self.add_method(literal.s_kmod       , methods, "show_kernel_module")
        self.add_method(literal.s_fcls       , methods, "show_fileobj_class")
        self.add_method(literal.s_bufsiz     , methods, "show_buffer_size")
        self.add_method(literal.s_platform   , methods, "show_platform")
        self.add_method(literal.s_hostname   , methods, "show_hostname")
        self.add_method(literal.s_term       , methods, "show_term")
        self.add_method(literal.s_lang       , methods, "show_lang")
        self.add_method(literal.s_version    , methods, "show_version")
        self.add_method(literal.s_sector     , methods, "show_sector_size")
        self.add_method(literal.s_argv       , methods, "show_argv")
        self.add_method(literal.s_args       , methods, "show_args")
        self.add_method(literal.s_md5        , methods, "show_md5")
        self.add_method(literal.ctrla        , methods, "inc_number")
        self.add_method(literal.ctrlx        , methods, "dec_number")
        self.add_method(literal.period       , methods, "repeat")
        self.add_method(literal.toggle       , methods, "toggle")
        self.add_method(literal.ror          , methods, "rotate_right")
        self.add_method(literal.rol          , methods, "rotate_left")
        self.add_method(literal.bswap        , methods, "swap_bytes")
        self.add_method(literal.delete       , methods, "delete")
        self.add_method(literal.X            , methods, "backspace")
        self.add_method(literal.D            , methods, "delete_till_end")
        self.add_method(literal.u            , methods, "undo")
        self.add_method(literal.U            , methods, "undo_all")
        self.add_method(literal.ctrlr        , methods, "redo")
        self.add_method(literal.reg_reg      , methods, "start_register")
        self.add_method(literal.m_reg        , methods, "set_mark")
        self.add_method(literal.backtick_reg , methods, "get_mark")
        self.add_method(literal.s_delmarks   , methods, "delete_mark")
        self.add_method(literal.s_delmarksneg, methods, "clear_marks")
        self.add_method(literal.q_reg        , methods, "start_record")
        self.add_method(literal.atsign_reg   , methods, "replay_record")
        self.add_method(literal.atsign_at    , methods, "replay_record")
        self.add_method(literal.bit_and      , methods, "logical_bit_operation")
        self.add_method(literal.bit_or       , methods, "logical_bit_operation")
        self.add_method(literal.bit_xor      , methods, "logical_bit_operation")
        self.add_method(literal.y            , methods, "yank")
        self.add_method(literal.Y            , methods, "yank_till_end")
        self.add_method(literal.P            , methods, "put")
        self.add_method(literal.p            , methods, "put_after")
        self.add_method(literal.O            , methods, "put_over")
        self.add_method(literal.o            , methods, "put_over_after")
        self.add_method(literal.s_w          , methods, "save_buffer")
        self.add_method(literal.s_wneg       , methods, "force_save_buffer")
        self.add_method(literal.s_wq         , methods, "save_buffer_quit")
        self.add_method(literal.s_x          , methods, "xsave_buffer_quit")
        self.add_method(literal.s_q          , methods, "quit")
        self.add_method(literal.s_qneg       , methods, "force_quit")
        self.add_method(literal.s_fsearch    , methods, "search_forward")
        self.add_method(literal.s_rsearch    , methods, "search_backward")
        self.add_method(literal.n            , methods, "search_next_forward")
        self.add_method(literal.N            , methods, "search_next_backward")
        self.add_method(literal.escape       , methods, "escape")
        self.add_method(literal.i            , this,    "_enter_edit_insert")
        self.add_method(literal.I            , this,    "_enter_edit_insert_head")
        self.add_method(literal.a            , this,    "_enter_edit_append")
        self.add_method(literal.A            , this,    "_enter_edit_append_tail")
        self.add_method(literal.R            , this,    "_enter_edit_replace")
        self.add_method(literal.r            , this,    "_do_edit_replace")
        self.add_method(literal.v            , this,    "_enter_visual")
        self.add_method(literal.V            , this,    "_enter_line_visual")
        self.add_method(literal.ctrlv        , this,    "_enter_block_visual")
        for li in literal.get_ext_literals():
            self.add_method(li, methods, "open_extension")

    def handle_signal(self):
        self.co.flash("Type  :q<Enter>  to exit")
        return kbd.ERROR

    def handle_invalid_literal(self, li):
        self.co.flash("Not an editor command " + li.str)
        return methods.HANDLED

class Console (_console):
    pass

class ExtConsole (_console):
    pass

def _enter_edit_insert(self, amp, opc, args, raw):
    arg = edit.Arg(amp=methods.get_int(amp))
    return self.set_console(edit.get_insert_class(), arg)

def _enter_edit_insert_head(self, amp, opc, args, raw):
    arg = edit.Arg(amp=methods.get_int(amp), delta=-self.co.get_pos())
    return self.set_console(edit.get_insert_class(), arg)

def _enter_edit_append(self, amp, opc, args, raw):
    arg = edit.Arg(amp=methods.get_int(amp), delta=1)
    return self.set_console(edit.get_insert_class(), arg)

def _enter_edit_append_tail(self, amp, opc, args, raw):
    delta = self.co.get_max_pos() - self.co.get_pos() + 1
    arg = edit.Arg(amp=methods.get_int(amp), delta=delta)
    return self.set_console(edit.get_insert_class(), arg)

def _enter_edit_replace(self, amp, opc, args, raw):
    arg = edit.Arg(amp=methods.get_int(amp))
    return self.set_console(edit.get_replace_class(), arg)

def _do_edit_replace(self, amp, opc, args, raw):
    arg = edit.Arg(amp=methods.get_int(amp), limit=edit.get_input_limit())
    return self.set_console(edit.get_replace_class(), arg)

def _enter_visual(self, amp, opc, args, raw):
    return __enter_visual(self, visual.VISUAL)

def _enter_line_visual(self, amp, opc, args, raw):
    return __enter_visual(self, visual.VISUAL_LINE)

def _enter_block_visual(self, amp, opc, args, raw):
    return __enter_visual(self, visual.VISUAL_BLOCK)

def __enter_visual(self, visual_type):
    if isinstance(self, ExtConsole):
        cls = visual.ExtConsole
    else:
        cls = visual.Console
    self.co.init_region(self.co.get_pos(), visual_type)
    return self.set_console(cls)
