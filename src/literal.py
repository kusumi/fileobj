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
import re
import sys

from . import kbd
from . import setting
from . import util

"""
Literal
    FastLiteral
        RegexLiteral
            StateLiteral
    SlowLiteral
        SearchLiteral
        ExtLiteral
    ArgLiteral
    InvalidLiteral
"""

class Literal (object):
    def __init__(self, str, seq, desc):
        self.str = str
        if not seq:
            seq = [ord(x) for x in self.str]
        self.seq = tuple(seq)
        self.desc = desc
        self.ref = None
        self.children = []

    def __str__(self):
        if setting.use_debug:
            return str(self.seq)
        else:
            return self.str

    def __eq__(self, o):
        return self.seq.__eq__(o.seq)
    def __gt__(self, o):
        return self.seq.__gt__(o.seq)
    def __ge__(self, o):
        return self.seq.__ge__(o.seq)
    def __lt__(self, o):
        return self.seq.__lt__(o.seq)
    def __le__(self, o):
        return self.seq.__le__(o.seq)

    def init(self):
        if self is _tree_root:
            self.refer(None)
        else:
            self.refer(_tree_root)

    def cleanup(self):
        if self.ref and self in self.ref.children:
            self.ref.children.remove(self)
        self.ref = None

    def refer(self, ref):
        self.cleanup()
        self.ref = ref
        if self.ref:
            self.ref.children.append(self)
        return self

    def alias(self, ref):
        assert self.desc == ref.desc
        return self.refer(ref)

    def match(self, l):
        """Return True if self.seq equals sequence l"""
        return self.seq == tuple(l)

    def match_incomplete(self, l):
        """Return True if self.seq starts with sequence l"""
        n = len(l)
        if n > len(self.seq):
            return False
        return self.seq[:n] == tuple(l)

class FastLiteral (Literal):
    pass

class RegexLiteral (FastLiteral):
    def __init__(self, size, body, regex, desc):
        super(RegexLiteral, self).__init__(regex, None, desc)
        self.size = size
        self.body = body
        self.regex = re.compile(regex)

    def match(self, l):
        if len(l) != self.size:
            return False
        if not util.is_graph_sequence(l):
            return False
        if self.regex.match(util.to_string(l)):
            return True
        else:
            return False

    def match_incomplete(self, l):
        if len(l) >= self.size:
            return False
        if not util.is_graph_sequence(l):
            return False
        if util.to_string(l).startswith(self.body):
            return True
        else:
            return False

class StateLiteral (RegexLiteral):
    def __init__(self, size, body, regex, pair, desc):
        super(StateLiteral, self).__init__(size, body, regex, desc)
        self.pair = pair
        self.state = True

    def match(self, l):
        if self.state:
            ret = super(StateLiteral, self).match(l)
        else:
            ret = self.pair.match(l)
        if ret:
            self.state = not self.state
        return ret

    def match_incomplete(self, l):
        if self.state:
            return super(StateLiteral, self).match_incomplete(l)
        else:
            return self.pair.match_incomplete(l)

class SlowLiteral (Literal):
    pass

class SearchLiteral (SlowLiteral):
    def match(self, l):
        return len(l) >= 1 and self.seq[0] == l[0]

    def match_incomplete(self, l):
        return False

class ExtLiteral (SlowLiteral):
    def __init__(self, str, fn, desc):
        super(ExtLiteral, self).__init__(str, None, desc)
        self.fn = fn

class ArgLiteral (Literal):
    def __str__(self):
        return '        ' + super(ArgLiteral, self).__str__()

class InvalidLiteral (Literal):
    pass

_tree_root = Literal('', None, '')

# descriptions are taken from vim help
up            = FastLiteral("<UP>", (kbd.UP,), "Go [count] lines upward")
k             = FastLiteral("k", None, "Go [count] lines upward")
down          = FastLiteral("<DOWN>", (kbd.DOWN,), "Go [count] lines downward")
enter         = FastLiteral("<ENTER>", (kbd.ENTER,), "Go [count] lines downward")
j             = FastLiteral("j", None, "Go [count] lines downward")
left          = FastLiteral("<LEFT>", (kbd.LEFT,), "Go [count] characters to the left")
bspace        = FastLiteral("<BACKSPACE>", (kbd.BACKSPACE,), "Go [count] characters to the left")
h             = FastLiteral("h", None, "Go [count] characters to the left")
right         = FastLiteral("<RIGHT>", (kbd.RIGHT,), "Go [count] characters to the right")
space         = FastLiteral("<SPACE>", (kbd.SPACE,), "Go [count] characters to the right")
l             = FastLiteral("l", None, "Go [count] characters to the right")
gg            = FastLiteral("gg", None, "Go to line [count] where default is first")
G             = FastLiteral("G", None, "Go to line [count] where default is last")
zero          = FastLiteral("0", None, "Go to the first character of the line")
doller        = FastLiteral("$", None, "Go to the end of the line. If a count is given go [count]-1 lines downward")
minus         = FastLiteral("-", None, "Go [count] lines upward, on the first character of the line")
plus          = FastLiteral("+", None, "Go [count] lines downward, on the first character of the line")
H             = FastLiteral("H", None, "Go to line [count] from top of window")
M             = FastLiteral("M", None, "Go to the middle line of window")
L             = FastLiteral("L", None, "Go to line [count] from bottom of window")
w             = FastLiteral("w", None, "Go to the next printable character")
b             = FastLiteral("b", None, "Go to the previous printable character")
parens_end    = FastLiteral(")", None, "Go to the next zero (\\x00)")
parens_beg    = FastLiteral("(", None, "Go to the previous zero (\\x00)")
bracket1_end  = FastLiteral("}", None, "Go to the next non zero character")
bracket1_beg  = FastLiteral("{", None, "Go to the previous non zero character")
bracket2_end  = FastLiteral("]", None, "End reading [count]. e.g. '[-0x10KiB]l' '[-020KiB]l' '[-0b10000KiB]l' are all -16384l")
bracket2_beg  = FastLiteral("[", None, "Get reading [count]. e.g. '[0x10]x' '[020]x' '[0b10000]x' are all 16x")
go            = FastLiteral("go", None, "Go to [count] byte in the buffer where default is start of the buffer")
ctrlb         = FastLiteral("<CTRL>b", (util.ctrl('b'),), "Scroll window [count] pages backward in the buffer")
ctrlu         = FastLiteral("<CTRL>u", (util.ctrl('u'),), "Scroll window [count] half pages backward in the buffer")
ctrlf         = FastLiteral("<CTRL>f", (util.ctrl('f'),), "Scroll window [count] pages forward in the buffer")
ctrld         = FastLiteral("<CTRL>d", (util.ctrl('d'),), "Scroll window [count] half pages forward in the buffer")
ctrll         = FastLiteral("<CTRL>l", (util.ctrl('l'),), "Refresh screen")
ctrlw_w       = FastLiteral("<CTRL>ww", (util.ctrl('w'), ord('w')), "Change to the next window")
ctrlw_ctrlw   = FastLiteral("<CTRL>w<CTRL>w", (util.ctrl('w'), util.ctrl('w')), "Change to the next window")
ctrlw_W       = FastLiteral("<CTRL>wW", (util.ctrl('w'), ord('W')), "Change to the prev window")
ctrlw_t       = FastLiteral("<CTRL>wt", (util.ctrl('w'), ord('t')), "Change to the top window")
ctrlw_ctrlt   = FastLiteral("<CTRL>w<CTRL>t", (util.ctrl('w'), util.ctrl('t')), "Change to the top window")
ctrlw_b       = FastLiteral("<CTRL>wb", (util.ctrl('w'), ord('b')), "Change to the bottom window")
ctrlw_ctrlb   = FastLiteral("<CTRL>w<CTRL>b", (util.ctrl('w'), util.ctrl('b')), "Change to the bottom window")
ctrlw_s       = FastLiteral("<CTRL>ws", (util.ctrl('w'), ord('s')), "Split current window")
ctrlw_ctrls   = FastLiteral("<CTRL>w<CTRL>s", (util.ctrl('w'), util.ctrl('s')), "Split current window")
ctrlw_v       = FastLiteral("<CTRL>wv", (util.ctrl('w'), ord('v')), "Split current window")
ctrlw_ctrlv   = FastLiteral("<CTRL>w<CTRL>v", (util.ctrl('w'), util.ctrl('v')), "Split current window")
ctrlw_plus    = FastLiteral("<CTRL>w+", (util.ctrl('w'), ord('+')), "Increase current window height [count] lines")
ctrlw_minus   = FastLiteral("<CTRL>w-", (util.ctrl('w'), ord('-')), "Decrease current window height [count] lines")
ctrlw_c       = FastLiteral("<CTRL>wc", (util.ctrl('w'), ord('c')), "Close current window")
ctrlw_o       = FastLiteral("<CTRL>wo", (util.ctrl('w'), ord('o')), "Make the current window the only one")
ctrlw_ctrlo   = FastLiteral("<CTRL>w<CTRL>o", (util.ctrl('w'), util.ctrl('o')), "Make the current window the only one")
ctrlw_q       = FastLiteral("<CTRL>wq", (util.ctrl('w'), ord('q')), "Close current window if >1 windows exist else quit program")
tab           = FastLiteral("<TAB>", (kbd.TAB,), "Change buffer to the next")
ctrlg         = FastLiteral("<CTRL>g", (util.ctrl('g'),), "Print current size and position")
g_ctrlg       = FastLiteral("g<CTRL>g", (ord('g'), util.ctrl('g'),), "Print current size and position in sector for block device")
ctrla         = FastLiteral("<CTRL>a", (util.ctrl('a'),), "Add [count] to the number at cursor")
ctrlx         = FastLiteral("<CTRL>x", (util.ctrl('x'),), "Subtract [count] from the number at cursor")
period        = FastLiteral(".", None, "Repeat last change")
toggle        = FastLiteral("~", None, "Switch case of the [count] characters under and after the cursor")
ror           = FastLiteral(">>", None, "Rotate [count] bits to right")
rol           = FastLiteral("<<", None, "Rotate [count] bits to left")
delete        = FastLiteral("<DELETE>", (kbd.DELETE,), "Delete [count] characters under and after the cursor")
x             = FastLiteral("x", None, "Delete [count] characters under and after the cursor")
X             = FastLiteral("X", None, "Delete [count] characters before the cursor")
d             = FastLiteral("d", None, "Delete [count] characters under and after the cursor")
D             = FastLiteral("D", None, "Delete characters under the cursor until the end of buffer")
u             = FastLiteral("u", None, "Undo changes")
U             = FastLiteral("U", None, "Undo all changes")
ctrlr         = FastLiteral("<CTRL>r", (util.ctrl('r'),), "Redo changes")
y             = FastLiteral("y", None, "Yank [count] characters")
Y             = FastLiteral("Y", None, "Yank characters under the cursor until the end of buffer")
P             = FastLiteral("P", None, "Put the text before the cursor [count] times")
p             = FastLiteral("p", None, "Put the text after the cursor [count] times")
O             = FastLiteral("O", None, "Replace the text befor the cursor [count] times")
o             = FastLiteral("o", None, "Replace the text after the cursor [count] times")
ZZ            = FastLiteral("ZZ", None, "Like :wq, but write only when changes have been made")
ZQ            = FastLiteral("ZQ", None, "Close current window if >1 windows exist else quit program without writing")
n             = FastLiteral("n", None, "Repeat the latest search")
N             = FastLiteral("N", None, "Repeat the latest search toward backward")
i             = FastLiteral("i", None, "Start insert edit mode")
I             = FastLiteral("I", None, "Start insert edit mode at the first byte of buffer")
a             = FastLiteral("a", None, "Start append edit mode")
A             = FastLiteral("A", None, "Start append edit mode at the end of buffer")
R             = FastLiteral("R", None, "Start replace edit mode")
r             = FastLiteral("r", None, "Replace [count] characters under the cursor")
v             = FastLiteral("v", None, "Start/End visual mode")
V             = FastLiteral("V", None, "Start/End line visual mode")
ctrlv         = FastLiteral("<CTRL>v", (util.ctrl('v'),), "Start/End block visual mode")
escape        = FastLiteral("<ESCAPE>", (kbd.ESCAPE,), "Clear input or escape from current mode")
resize        = FastLiteral('<RESIZE>', (kbd.RESIZE,), '')

m_reg         = RegexLiteral(2, "m", r"m[0-9a-zA-Z]", "Set mark at cursor position, uppercase marks are valid between buffers")
backtick_reg  = RegexLiteral(2, "`", r"`[0-9a-zA-Z]", "Go to marked position")
q             = FastLiteral("q", None, "Stop recording")
q_reg         = StateLiteral(2, "q", r"q[0-9a-zA-Z]", q, "Record typed characters into register")
atsign_reg    = RegexLiteral(2, "@", r"@[0-9a-zA-Z]", "Execute the contents of register [count] times")
atsign_at     = FastLiteral("@@", None, "Execute the previous @ command [count] times")
bit_and       = RegexLiteral(3, "&", r"&[0-9a-fA-F]{2}", "Write logical and")
bit_or        = RegexLiteral(3, "|", r"\|[0-9a-fA-F]{2}", "Write logical or")
bit_xor       = RegexLiteral(3, "^", r"\^[0-9a-fA-F]{2}", "Write logical xor")

s_e           = SlowLiteral(":e", None, "Open a buffer")
s_bdelete     = SlowLiteral(":bdelete", None, "Close a buffer")
s_bfirst      = SlowLiteral(":bfirst", None, "Go to the first buffer in buffer list")
s_brewind     = SlowLiteral(":brewind", None, "Go to the first buffer in buffer list")
s_blast       = SlowLiteral(":blast", None, "Go to the last buffer in buffer list")
s_bnext       = SlowLiteral(":bnext", None, "Change buffer to the next")
s_bprev       = SlowLiteral(":bprevious", None, "Change buffer to the previous")
s_bNext       = SlowLiteral(":bNext", None, "Change buffer to the previous")
s_set         = SlowLiteral(":set", None, "Set option")
s_self        = SlowLiteral(":self", None, "Print current console instance string")
s_pwd         = SlowLiteral(":pwd", None, "Print the current directory name")
s_date        = SlowLiteral(":date", None, "Print date")
s_platform    = SlowLiteral(":platform", None, "Print platform")
s_hostname    = SlowLiteral(":hostname", None, "Print hostname")
s_term        = SlowLiteral(":term", None, "Print terminal type")
s_sector      = SlowLiteral(":sector", None, "Print sector size for block device")
s_version     = SlowLiteral(":version", None, "Print version")
s_args        = SlowLiteral(":args", None, "Print buffer list with the current buffer in brackets")
s_delmarks    = SlowLiteral(":delmarks", None, "Delete the specified marks")
s_delmarksneg = SlowLiteral(":delmarks!", None, "Delete all marks for the current buffer except for uppercase marks")
s_split       = SlowLiteral(":split", None, "Split current window")
s_close       = SlowLiteral(":close", None, "Close current window")
s_only        = SlowLiteral(":only", None, "Make the current window the only one")
s_w           = SlowLiteral(":w", None, "Write the whole buffer to the file")
s_wneg        = SlowLiteral(":w!", None, "Like :w, but overwrite an existing file")
s_wq          = SlowLiteral(":wq", None, "Write the current file and quit")
s_x           = SlowLiteral(":x", None, "Like :wq, but write only when changes have been made")
s_q           = SlowLiteral(":q", None, "Close current window if >1 windows exist else quit program")
s_qneg        = SlowLiteral(":q!", None, "Close current window if >1 windows exist else quit program without writing")
s_fsearch     = SearchLiteral('/', None, "Search forward. e.g. '/\\x12Python\\x34', '/\\X1234'")
s_rsearch     = SearchLiteral('?', None, "Search backward. e.g. '?\\x12Python\\x34', '?\\X1234'")

s_set_hex     = ArgLiteral("hex", None, "Set output radix to hexadecimal")
s_set_dec     = ArgLiteral("dec", None, "Set output radix to decimal")
s_set_oct     = ArgLiteral("oct", None, "Set output radix to octal")
s_set_binary  = ArgLiteral("binary", None, "Set binary edit mode (unset ascii edit mode)")
s_set_ascii   = ArgLiteral("ascii", None, "Set ascii edit mode (unset binary edit mode)")
s_set_le      = ArgLiteral("le", None, "Set endianness to little (unset big endian if set)")
s_set_be      = ArgLiteral("be", None, "Set endianness to big (unset little endian if set)")
s_set_ws      = ArgLiteral("ws", None, "Set wrapscan mode (search wrap around the end of the buffer)")
s_set_nows    = ArgLiteral("nows", None, "Unset wrapscan mode")
s_set_ic      = ArgLiteral("ic", None, "Set ic mode (ignore the case of alphabets on search)")
s_set_noic    = ArgLiteral("noic", None, "Unset ic mode")
s_set_si      = ArgLiteral("si", None, "Set SI prefix mode (kilo equals 10^3)")
s_set_nosi    = ArgLiteral("nosi", None, "Unset SI prefix mode (kilo equals 2^10)")
s_set_width   = ArgLiteral("width", None, "Set window width to arg [[0-9]+|max|min|auto]")

def get_slow_strings():
    return tuple(":/?")

_slow_ords = tuple(map(ord, get_slow_strings()))
def get_slow_ords():
    return _slow_ords

_literals = {}
def get_literals():
    return _literals.get(Literal, ())

def get_fast_literals():
    return _literals.get(FastLiteral, ())

def get_slow_literals():
    return _literals.get(SlowLiteral, ())

def get_arg_literals():
    return _literals.get(ArgLiteral, ())

def get_ext_literals():
    return _literals.get(ExtLiteral, ())

def get_sorted_literals():
    return _literals.get(None, ())

def find_literal(seq):
    l = get_sorted_literals()
    if not l:
        return None
    beg = 0
    end = len(l) - 1
    if isinstance(seq, str):
        seq = [ord(x) for x in seq]
    seq = tuple(seq)
    while True:
        i = (beg + end) // 2
        if seq == l[i].seq:
            return l[i]
        if seq < l[i].seq:
            end = i - 1
        else:
            beg = i + 1
        if beg > end:
            break

def get_lines(l):
    if not l:
        return []
    n = max([len(str(o)) for o in l])
    f = util.get_string_format("%-${n}s %s", n=n)
    ret = []
    for o in l:
        if o.desc:
            ret.append(f % (o, o.desc))
    return ret

def print_literal():
    init()
    s = get_lines(get_literals())
    util.print_stdout('\n'.join(s).rstrip())
    cleanup()

def init():
    if this._tree_root.children:
        return -1

    for o in util.iter_site_ext_module():
        fn = getattr(o, "get_text", None)
        if fn:
            try:
                desc = o.get_description()
            except Exception:
                desc = ''
            s = o.__name__.rpartition('.')[2]
            setattr(this, "s_" + s, ExtLiteral(':' + s, fn, desc))

    for o in util.iter_dir_values(this):
        if isinstance(o, Literal):
            o.init()

    # alias
    this.k.alias(this.up)
    this.enter.alias(
        this.j.alias(this.down)
    )
    this.bspace.alias(
        this.h.alias(this.left)
    )
    this.space.alias(
        this.l.alias(this.right)
    )
    this.ctrlw_ctrlw.alias(this.ctrlw_w)
    this.ctrlw_ctrlt.alias(this.ctrlw_t)
    this.ctrlw_ctrlb.alias(this.ctrlw_b)
    this.ctrlw_ctrlv.alias(
        this.ctrlw_v.alias(
            this.ctrlw_ctrls.alias(this.ctrlw_s)
        )
    )
    this.ctrlw_c.alias(this.s_close)
    this.ctrlw_ctrlo.alias(
        this.ctrlw_o.alias(this.s_only)
    )
    this.ctrlw_q.alias(this.s_q)
    this.tab.alias(this.s_bnext)
    this.d.alias(
        this.x.alias(this.delete)
    )
    this.ZZ.alias(this.s_x)
    this.ZQ.alias(this.s_qneg)
    this.s_brewind.alias(this.s_bfirst)
    this.s_bNext.alias(this.s_bprev)

    # refer
    this.gg.refer(this.G)
    this.doller.refer(this.zero)
    this.L.refer(
        this.M.refer(H)
    )
    this.b.refer(this.w)
    this.bracket2_beg.refer(
        this.bracket2_end.refer(
            this.bracket1_beg.refer(
                this.bracket1_end.refer(
                    this.parens_beg.refer(this.parens_end)
                )
            )
        )
    )
    this.ctrlu.refer(this.ctrlb)
    this.ctrld.refer(this.ctrlf)
    this.ctrlv.refer(
        this.V.refer(this.v)
    )
    this.g_ctrlg.refer(this.ctrlg)
    this.rol.refer(this.ror)
    this.y.refer(this.Y)
    this.p.refer(this.P)
    this.o.refer(this.O)
    this.n.refer(this.N)
    this.r.refer(
        this.R.refer(
            this.A.refer(
                this.a.refer(
                    this.I.refer(this.i)
                )
            )
        )
    )
    this.backtick_reg.refer(this.m_reg)
    this.q.refer(this.q_reg)
    this.atsign_at.refer(this.atsign_reg)
    this.bit_xor.refer(
        this.bit_or.refer(this.bit_and)
    )
    this.s_bdelete.refer(this.s_e)
    this.s_delmarksneg.refer(this.s_delmarks)
    this.s_rsearch.refer(this.s_fsearch)
    this.s_set_oct.refer(
        this.s_set_dec.refer(
            this.s_set_hex.refer(this.s_set)
        )
    )
    this.s_set_ascii.refer(
        this.s_set_binary.refer(this.s_set)
    )
    this.s_set_be.refer(
        this.s_set_le.refer(this.s_set)
    )
    this.s_set_nows.refer(
        this.s_set_ws.refer(this.s_set)
    )
    this.s_set_noic.refer(
        this.s_set_ic.refer(this.s_set)
    )
    this.s_set_nosi.refer(
        this.s_set_si.refer(this.s_set)
    )
    this.s_set_width.refer(this.s_set)

    def fn(l, o, cls):
        for li in sorted(o.children):
            if isinstance(li, cls):
                l.append(li)
            fn(l, li, cls)
        return tuple(l)

    for cls in Literal, FastLiteral, SlowLiteral, ArgLiteral, ExtLiteral:
        this._literals[cls] = fn([], this._tree_root, cls)
    this._literals[None] = tuple(sorted(get_literals()))

def cleanup():
    for s, o in util.iter_dir(this):
        if isinstance(o, Literal):
            o.cleanup()
        if isinstance(o, ExtLiteral):
            delattr(this, s)
    this._literals.clear()

this = sys.modules[__name__]
