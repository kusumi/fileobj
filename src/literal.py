# Copyright (c) 2010-2015, TOMOHIRO KUSUMI
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
    def __init__(self, size, str, regex, desc):
        super(RegexLiteral, self).__init__(str, None, desc)
        assert len(str) > 1
        self.size = size
        self.key = self.str[0]
        self.regex = re.compile(regex)

    def match(self, l):
        if len(l) != self.size:
            return False
        if not kbd.isprints(l):
            return False
        s = ''.join([chr(x) for x in l])
        if self.regex.match(s):
            return True
        else:
            return False

    def match_incomplete(self, l):
        if len(l) >= self.size:
            return False
        if not kbd.isprints(l):
            return False
        s = ''.join([chr(x) for x in l])
        if s.startswith(self.key):
            return True
        else:
            return False

class StateLiteral (RegexLiteral):
    def __init__(self, size, str, regex, pair, desc):
        super(StateLiteral, self).__init__(size, str, regex, desc)
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
bracket2_beg  = FastLiteral("[", None, "Start reading [count]. e.g. '[0x10]x' '[020]x' '[0b10000]x' are all 16x")
go            = FastLiteral("go", None, "Go to [count] byte in the buffer where default is start of the buffer")
ctrlb         = FastLiteral("<CTRL>b", (kbd.ctrl('b'),), "Scroll window [count] pages backward in the buffer")
ctrlu         = FastLiteral("<CTRL>u", (kbd.ctrl('u'),), "Scroll window [count] half pages backward in the buffer")
ctrlf         = FastLiteral("<CTRL>f", (kbd.ctrl('f'),), "Scroll window [count] pages forward in the buffer")
ctrld         = FastLiteral("<CTRL>d", (kbd.ctrl('d'),), "Scroll window [count] half pages forward in the buffer")
ctrll         = FastLiteral("<CTRL>l", (kbd.ctrl('l'),), "Refresh screen")
ctrlw_w       = FastLiteral("<CTRL>ww", (kbd.ctrl('w'), ord('w')), "Change to the next window")
ctrlw_ctrlw   = FastLiteral("<CTRL>w<CTRL>w", (kbd.ctrl('w'), kbd.ctrl('w')), "Change to the next window")
ctrlw_W       = FastLiteral("<CTRL>wW", (kbd.ctrl('w'), ord('W')), "Change to the prev window")
ctrlw_t       = FastLiteral("<CTRL>wt", (kbd.ctrl('w'), ord('t')), "Change to the top window")
ctrlw_ctrlt   = FastLiteral("<CTRL>w<CTRL>t", (kbd.ctrl('w'), kbd.ctrl('t')), "Change to the top window")
ctrlw_b       = FastLiteral("<CTRL>wb", (kbd.ctrl('w'), ord('b')), "Change to the bottom window")
ctrlw_ctrlb   = FastLiteral("<CTRL>w<CTRL>b", (kbd.ctrl('w'), kbd.ctrl('b')), "Change to the bottom window")
ctrlw_s       = FastLiteral("<CTRL>ws", (kbd.ctrl('w'), ord('s')), "Split current window")
ctrlw_ctrls   = FastLiteral("<CTRL>w<CTRL>s", (kbd.ctrl('w'), kbd.ctrl('s')), "Split current window")
ctrlw_v       = FastLiteral("<CTRL>wv", (kbd.ctrl('w'), ord('v')), "Split current window")
ctrlw_ctrlv   = FastLiteral("<CTRL>w<CTRL>v", (kbd.ctrl('w'), kbd.ctrl('v')), "Split current window")
ctrlw_plus    = FastLiteral("<CTRL>w+", (kbd.ctrl('w'), ord('+')), "Increase current window height [count] lines")
ctrlw_minus   = FastLiteral("<CTRL>w-", (kbd.ctrl('w'), ord('-')), "Decrease current window height [count] lines")
ctrlw_c       = FastLiteral("<CTRL>wc", (kbd.ctrl('w'), ord('c')), "Close current window")
ctrlw_o       = FastLiteral("<CTRL>wo", (kbd.ctrl('w'), ord('o')), "Make the current window the only one")
ctrlw_ctrlo   = FastLiteral("<CTRL>w<CTRL>o", (kbd.ctrl('w'), kbd.ctrl('o')), "Make the current window the only one")
ctrlw_q       = FastLiteral("<CTRL>wq", (kbd.ctrl('w'), ord('q')), "Close current window if >1 windows exist else quit program")
tab           = FastLiteral("<TAB>", (kbd.TAB,), "Change buffer to the next")
ctrlg         = FastLiteral("<CTRL>g", (kbd.ctrl('g'),), "Print current size and position")
g_ctrlg       = FastLiteral("g<CTRL>g", (ord('g'), kbd.ctrl('g'),), "Print current size and position in sector for block device")
ctrla         = FastLiteral("<CTRL>a", (kbd.ctrl('a'),), "Add [count] to the number at cursor")
ctrlx         = FastLiteral("<CTRL>x", (kbd.ctrl('x'),), "Subtract [count] from the number at cursor")
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
ctrlr         = FastLiteral("<CTRL>r", (kbd.ctrl('r'),), "Redo changes")
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
ctrlv         = FastLiteral("<CTRL>v", (kbd.ctrl('v'),), "Start/End block visual mode")
escape        = FastLiteral("<ESCAPE>", (kbd.ESCAPE,), "Clear input or escape from current mode")
resize        = FastLiteral('<RESIZE>', (kbd.RESIZE,), '')

m_reg         = RegexLiteral(2, "m[0-9a-zA-Z]", r"^m[0-9a-zA-Z]", "Set mark at cursor position, uppercase marks are valid between buffers")
backtick_reg  = RegexLiteral(2, "`[0-9a-zA-Z]", r"^`[0-9a-zA-Z]", "Go to marked position")
q             = FastLiteral("q", None, "Stop recording")
q_reg         = StateLiteral(2, "q[0-9a-zA-Z]", r"^q[0-9a-zA-Z]", q, "Record typed characters into register")
atsign_reg    = RegexLiteral(2, "@[0-9a-zA-Z]", r"^@[0-9a-zA-Z]", "Execute the contents of register [count] times")
atsign_at     = FastLiteral("@@", None, "Execute the previous @ command [count] times")
bit_and       = RegexLiteral(3, "&[0-9a-fA-F]{2}", r"^&[0-9a-fA-F]{2}", "Replace [count] bytes with logical and-ed bytes")
bit_or        = RegexLiteral(3, "|[0-9a-fA-F]{2}", r"^\|[0-9a-fA-F]{2}", "Replace [count] bytes with logical or-ed bytes")
bit_xor       = RegexLiteral(3, "^[0-9a-fA-F]{2}", r"^\^[0-9a-fA-F]{2}", "Replace [count] bytes with logical xor-ed bytes")

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
s_lang        = SlowLiteral(":lang", None, "Print locale type")
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
s_set_address = ArgLiteral("address", None, "Set address radix to arg [16|10|8]")
s_set_status  = ArgLiteral("status", None, "Set buffer size and current position radix to arg [16|10|8]")
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
    util.printf('\n'.join(s).rstrip())
    cleanup()

# keep this separated from init()
def __register_ext_literal(o, fn):
    try:
        desc = o.get_description()
    except Exception:
        desc = ''
    s = o.__name__.rpartition('.')[2]
    li = ExtLiteral(':' + s, fn, desc)
    setattr(this, "s_" + s, li)

# keep this separated from init()
def __register_is_function(cls):
    def fn(li):
        return isinstance(li, cls)
    setattr(this, "is_" + util.get_class_name(cls), fn)

def init():
    if _tree_root.children:
        return -1

    for _ in util.iter_site_ext_module():
        fn = getattr(_, "get_text", None)
        if fn:
            __register_ext_literal(_, fn)

    for _ in util.iter_dir_values(this):
        if isinstance(_, Literal):
            _.init()
        if util.is_subclass(_, Literal):
            __register_is_function(_)

    # alias
    k.alias(up)
    enter.alias(
        j.alias(down)
    )
    bspace.alias(
        h.alias(left)
    )
    space.alias(
        l.alias(right)
    )
    ctrlw_ctrlw.alias(ctrlw_w)
    ctrlw_ctrlt.alias(ctrlw_t)
    ctrlw_ctrlb.alias(ctrlw_b)
    ctrlw_ctrlv.alias(
        ctrlw_v.alias(
            ctrlw_ctrls.alias(ctrlw_s)
        )
    )
    ctrlw_c.alias(s_close)
    ctrlw_ctrlo.alias(
        ctrlw_o.alias(s_only)
    )
    ctrlw_q.alias(s_q)
    tab.alias(s_bnext)
    d.alias(
        x.alias(delete)
    )
    ZZ.alias(s_x)
    ZQ.alias(s_qneg)
    s_brewind.alias(s_bfirst)
    s_bNext.alias(s_bprev)

    # refer
    gg.refer(G)
    doller.refer(zero)
    L.refer(
        M.refer(H)
    )
    b.refer(w)
    bracket2_beg.refer(
        bracket2_end.refer(
            bracket1_beg.refer(
                bracket1_end.refer(
                    parens_beg.refer(parens_end)
                )
            )
        )
    )
    ctrlu.refer(ctrlb)
    ctrld.refer(ctrlf)
    ctrlv.refer(
        V.refer(v)
    )
    g_ctrlg.refer(ctrlg)
    rol.refer(ror)
    y.refer(Y)
    p.refer(P)
    o.refer(O)
    n.refer(N)
    r.refer(
        R.refer(
            A.refer(
                a.refer(
                    I.refer(i)
                )
            )
        )
    )
    backtick_reg.refer(m_reg)
    q.refer(q_reg)
    atsign_at.refer(atsign_reg)
    bit_xor.refer(
        bit_or.refer(bit_and)
    )
    s_bdelete.refer(s_e)
    s_delmarksneg.refer(s_delmarks)
    s_rsearch.refer(s_fsearch)
    s_set_ascii.refer(
        s_set_binary.refer(s_set)
    )
    s_set_be.refer(
        s_set_le.refer(s_set)
    )
    s_set_nows.refer(
        s_set_ws.refer(s_set)
    )
    s_set_noic.refer(
        s_set_ic.refer(s_set)
    )
    s_set_nosi.refer(
        s_set_si.refer(s_set)
    )
    s_set_status.refer(
        s_set_address.refer(s_set)
    )
    s_set_width.refer(s_set)

    def fn(l, o, cls):
        for li in sorted(o.children):
            if isinstance(li, cls):
                l.append(li)
            fn(l, li, cls)
        return tuple(l)

    for cls in Literal, FastLiteral, SlowLiteral, ArgLiteral, ExtLiteral:
        _literals[cls] = fn([], _tree_root, cls)
    _literals[None] = tuple(sorted(get_literals()))

def cleanup():
    for s, o in util.iter_dir_items(this):
        if is_Literal(o):
            o.cleanup()
        if is_ExtLiteral(o):
            delattr(this, s)
    _literals.clear()

this = sys.modules[__name__]
