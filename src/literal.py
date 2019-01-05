# Copyright (c) 2009, Tomohiro Kusumi
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
from . import kernel
from . import setting
from . import util

# Literal
#     FastLiteral
#         RegexLiteral
#             StateLiteral
#     SlowLiteral
#         SearchLiteral
#         ExtLiteral
#     ArgLiteral
#     InvalidLiteral

class Literal (object):
    def __init__(self, str, seq, desc):
        self.str = str
        if not seq:
            seq = [ord(x) for x in self.str]
        self.seq = tuple(seq)
        self.desc = desc
        self.ref = None
        self.ali = None
        self.children = []

        if self.str == "": # root
            assert self.desc == "", self.desc
            self.refer(None)
        else:
            self.refer(this._root)
            assert self.ref, self.ref
            assert self in self.ref.children, self.ref.children

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

    def cleanup(self):
        if self.ref and self in self.ref.children:
            self.ref.children.remove(self)
        self.ref = None

    def is_origin(self):
        return self.ali is None

    def is_alias(self, ref):
        return (self.ali is ref) and ref.desc and ref.desc == self.desc

    def refer(self, ref):
        self.cleanup()
        self.ref = ref
        if self.ref:
            self.ref.children.append(self)
            self.ref.children.sort()
        return ref

    def alias(self, ref):
        assert self.desc == ref.desc
        self.ali = ref # ref is the original of self
        return self.refer(ref)

    def create_alias(self, str, seq):
        cls = util.get_class(self)
        o = cls(str, seq, self.desc) # XXX may raise due to arg mismatch
        assert o.str
        if o.str[0] == ':':
            assert str[0] == ':', (o.str, str)
        else:
            assert str[0] != ':', (o.str, str)
        o.alias(self)
        return o

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
        if not util.isprints(l):
            return False
        s = ''.join([chr(x) for x in l])
        if self.regex.match(s):
            return True
        else:
            return False

    def match_incomplete(self, l):
        if len(l) >= self.size:
            return False
        if not util.isprints(l):
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
        return "    " + super(ArgLiteral, self).__str__()

class InvalidLiteral (Literal):
    pass

def get_slow_strings():
    return tuple(":/?")

_slow_ords = tuple(map(ord, get_slow_strings()))
def get_slow_ords():
    return _slow_ords

_ld = {}
def get_literals():
    return _ld.get(Literal, ())

def get_fast_literals():
    return _ld.get(FastLiteral, ())

def get_slow_literals():
    return _ld.get(SlowLiteral, ())

def get_arg_literals():
    return _ld.get(ArgLiteral, ())

def get_ext_literals():
    return _ld.get(ExtLiteral, ())

def get_sorted_literals():
    return _ld.get(None, ())

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

def get_lines(l=None):
    if not l:
        l = get_literals()
    n = max([len(str(o)) for o in l])
    f = "{{0:<{0}}} {{1}}".format(n)
    return [f.format(str(o), o.desc) for o in l if o.desc]

def print_literal():
    assert init() != -1
    util.printf('\n'.join(get_lines()).rstrip())
    assert cleanup() != -1

# keep this separated from init()
def __alloc_ext_literals(o, fn):
    try:
        desc = o.get_description()
    except Exception:
        desc = ""
    s = o.__name__.rpartition('.')[2]
    li = ExtLiteral(':' + s, fn, desc)
    setattr(this, "s_" + s, li)

# keep this separated from init()
def __register_is_function(cls):
    def fn(li):
        return isinstance(li, cls)
    setattr(this, "is_" + util.get_class_name(cls), fn)

def __register_alias(*args):
    for l, o in args:
        assert isinstance(o, Literal)
        if isinstance(l, Literal):
            l = (l,)
        for _ in l:
            _.alias(o)

def __register_refer(*args):
    for l, o in args:
        assert isinstance(o, Literal)
        if isinstance(l, Literal):
            l = (l,)
        for _ in l:
            _.refer(o)

def init():
    if hasattr(this, "_root"):
        return -1
    setattr(this, "_root", Literal("", None, ""))

    setattr(this, "up", FastLiteral("<UP>", (kbd.UP,), "Go [count] lines upward"))
    setattr(this, "k", this.up.create_alias("k", None))
    setattr(this, "down", FastLiteral("<DOWN>", (kbd.DOWN,), "Go [count] lines downward"))
    setattr(this, "enter", this.down.create_alias("<ENTER>", (kbd.ENTER,)))
    setattr(this, "j", this.down.create_alias("j", None))
    setattr(this, "left", FastLiteral("<LEFT>", (kbd.LEFT,), "Go [count] characters to the left"))
    setattr(this, "bspace", this.left.create_alias("<BACKSPACE>", (kbd.BACKSPACE,)))
    setattr(this, "bspace2", this.left.create_alias("<BACKSPACE2>", (kbd.BACKSPACE2,)))
    setattr(this, "h", this.left.create_alias("h", None))
    setattr(this, "right", FastLiteral("<RIGHT>", (kbd.RIGHT,), "Go [count] characters to the right"))
    setattr(this, "space", this.right.create_alias("<SPACE>", (kbd.SPACE,)))
    setattr(this, "l", this.right.create_alias("l", None))
    setattr(this, "gg", FastLiteral("gg", None, "Go to line [count] (default first line)"))
    setattr(this, "G", FastLiteral("G", None, "Go to line [count] (default last line)"))
    setattr(this, "zero", FastLiteral("0", None, "Go to the first character of the line"))
    setattr(this, "doller", FastLiteral("$", None, "Go to the end of the line. If a count is given go [count]-1 lines downward"))
    setattr(this, "H", FastLiteral("H", None, "Go to line [count] from top of window"))
    setattr(this, "M", FastLiteral("M", None, "Go to the middle line of window"))
    setattr(this, "L", FastLiteral("L", None, "Go to line [count] from bottom of window"))
    setattr(this, "w", FastLiteral("w", None, "Go to the next printable character"))
    setattr(this, "b", FastLiteral("b", None, "Go to the previous printable character"))
    setattr(this, "parens_end", FastLiteral(")", None, "Go to the next zero (\\x00)"))
    setattr(this, "parens_beg", FastLiteral("(", None, "Go to the previous zero (\\x00)"))
    setattr(this, "bracket1_end", FastLiteral("}", None, "Go to the next non zero character"))
    setattr(this, "bracket1_beg", FastLiteral("{", None, "Go to the previous non zero character"))
    setattr(this, "bracket2_end", FastLiteral("]", None, "End reading buffered [count] value"))
    setattr(this, "bracket2_beg", FastLiteral("[", None, "Start reading buffered [count] value"))
    setattr(this, "go", FastLiteral("go", None, "Go to [count] byte in the buffer (default first byte)"))
    setattr(this, "sh", FastLiteral("sh", None, "Go [count] sectors to the left"))
    setattr(this, "sbspace", this.sh.create_alias("s<BACKSPACE>", (ord('s'), kbd.BACKSPACE,)))
    setattr(this, "sbspace2", this.sh.create_alias("s<BACKSPACE2>", (ord('s'), kbd.BACKSPACE2,)))
    setattr(this, "sl", FastLiteral("sl", None, "Go [count] sectors to the right"))
    setattr(this, "sspace", this.sl.create_alias("s<SPACE>", (ord('s'), kbd.SPACE,)))
    setattr(this, "szero", FastLiteral("s0", None, "Go to the first character of the sector"))
    setattr(this, "sdoller", FastLiteral("s$", None, "Go to the end of the sector. If a count is given go [count]-1 sectors downward"))
    setattr(this, "sgo", FastLiteral("sgo", None, "Go to [count] sector in the buffer (default first sector)"))
    setattr(this, "ctrlb", FastLiteral("<CTRL>b", (util.ctrl('b'),), "Scroll window [count] pages backward in the buffer"))
    setattr(this, "ctrlu", FastLiteral("<CTRL>u", (util.ctrl('u'),), "Scroll window [count] half pages backward in the buffer"))
    setattr(this, "ctrlf", FastLiteral("<CTRL>f", (util.ctrl('f'),), "Scroll window [count] pages forward in the buffer"))
    setattr(this, "ctrld", FastLiteral("<CTRL>d", (util.ctrl('d'),), "Scroll window [count] half pages forward in the buffer"))
    setattr(this, "ctrll", FastLiteral("<CTRL>l", (util.ctrl('l'),), "Refresh screen"))
    setattr(this, "ctrlw_w", FastLiteral("<CTRL>ww", (util.ctrl('w'), ord('w')), "Change to the next window"))
    setattr(this, "ctrlw_ctrlw", this.ctrlw_w.create_alias("<CTRL>w<CTRL>w", (util.ctrl('w'), util.ctrl('w'))))
    setattr(this, "ctrlw_W", FastLiteral("<CTRL>wW", (util.ctrl('w'), ord('W')), "Change to the prev window"))
    setattr(this, "ctrlw_t", FastLiteral("<CTRL>wt", (util.ctrl('w'), ord('t')), "Change to the top window"))
    setattr(this, "ctrlw_ctrlt", this.ctrlw_t.create_alias("<CTRL>w<CTRL>t", (util.ctrl('w'), util.ctrl('t'))))
    setattr(this, "ctrlw_b", FastLiteral("<CTRL>wb", (util.ctrl('w'), ord('b')), "Change to the bottom window"))
    setattr(this, "ctrlw_ctrlb", this.ctrlw_b.create_alias("<CTRL>w<CTRL>b", (util.ctrl('w'), util.ctrl('b'))))
    setattr(this, "ctrlw_s", FastLiteral("<CTRL>ws", (util.ctrl('w'), ord('s')), "Split current window"))
    setattr(this, "ctrlw_ctrls", this.ctrlw_s.create_alias("<CTRL>w<CTRL>s", (util.ctrl('w'), util.ctrl('s'))))
    setattr(this, "ctrlw_v", FastLiteral("<CTRL>wv", (util.ctrl('w'), ord('v')), "Split current window vertically"))
    setattr(this, "ctrlw_ctrlv", this.ctrlw_v.create_alias("<CTRL>w<CTRL>v", (util.ctrl('w'), util.ctrl('v'))))
    setattr(this, "ctrlw_plus", FastLiteral("<CTRL>w+", (util.ctrl('w'), ord('+')), "Increase current window height [count] lines"))
    setattr(this, "ctrlw_minus", FastLiteral("<CTRL>w-", (util.ctrl('w'), ord('-')), "Decrease current window height [count] lines"))
    setattr(this, "ctrlw_c", FastLiteral("<CTRL>wc", (util.ctrl('w'), ord('c')), "Close current window"))
    setattr(this, "ctrlw_o", FastLiteral("<CTRL>wo", (util.ctrl('w'), ord('o')), "Make the current window the only one"))
    setattr(this, "ctrlw_ctrlo", this.ctrlw_o.create_alias("<CTRL>w<CTRL>o", (util.ctrl('w'), util.ctrl('o'))))
    setattr(this, "ctrlw_q", FastLiteral("<CTRL>wq", (util.ctrl('w'), ord('q')), "Close current window if more than 1 windows exist else quit program"))
    setattr(this, "tab", FastLiteral("<TAB>", (kbd.TAB,), "Change buffer to the next"))
    setattr(this, "ctrlg", FastLiteral("<CTRL>g", (util.ctrl('g'),), "Print current size and position"))
    setattr(this, "g_ctrlg", FastLiteral("g<CTRL>g", (ord('g'), util.ctrl('g'),), "Print current size and position in sector for block device"))
    setattr(this, "ctrla", FastLiteral("<CTRL>a", (util.ctrl('a'),), "Add [count] to the number at cursor"))
    setattr(this, "ctrlx", FastLiteral("<CTRL>x", (util.ctrl('x'),), "Subtract [count] from the number at cursor"))
    setattr(this, "ctrlc", FastLiteral("<CTRL>c", (util.ctrl('c'),), ""))
    setattr(this, "period", FastLiteral(".", None, "Repeat last change"))
    setattr(this, "toggle", FastLiteral("~", None, "Switch case of the [count] characters under and after the cursor"))
    setattr(this, "ror", FastLiteral(">>", None, "Rotate [count] bits to right"))
    setattr(this, "rol", FastLiteral("<<", None, "Rotate [count] bits to left"))
    setattr(this, "bswap", FastLiteral("sb", None, "Swap byte order of [count] characters"))
    setattr(this, "delete", FastLiteral("<DELETE>", (kbd.DELETE,), "Delete [count] characters under and after the cursor"))
    setattr(this, "x", this.delete.create_alias("x", None))
    setattr(this, "d", this.delete.create_alias("d", None))
    setattr(this, "X", FastLiteral("X", None, "Delete [count] characters before the cursor"))
    setattr(this, "D", FastLiteral("D", None, "Delete characters under the cursor until the end of buffer"))
    setattr(this, "u", FastLiteral("u", None, "Undo changes"))
    setattr(this, "U", FastLiteral("U", None, "Undo all changes"))
    setattr(this, "ctrlr", FastLiteral("<CTRL>r", (util.ctrl('r'),), "Redo changes"))
    setattr(this, "y", FastLiteral("y", None, "Yank [count] characters"))
    setattr(this, "Y", FastLiteral("Y", None, "Yank characters under the cursor until the end of buffer"))
    setattr(this, "P", FastLiteral("P", None, "Put the text before the cursor [count] times"))
    setattr(this, "p", FastLiteral("p", None, "Put the text after the cursor [count] times"))
    setattr(this, "O", FastLiteral("O", None, "Replace the text befor the cursor [count] times"))
    setattr(this, "o", FastLiteral("o", None, "Replace the text after the cursor [count] times"))
    setattr(this, "ZZ", FastLiteral("ZZ", None, "Like :wq, but write only when changes have been made"))
    setattr(this, "ZQ", FastLiteral("ZQ", None, "Close current window if more than 1 windows exist else quit program without writing"))
    setattr(this, "n", FastLiteral("n", None, "Repeat the latest search"))
    setattr(this, "N", FastLiteral("N", None, "Repeat the latest search toward backward"))
    setattr(this, "i", FastLiteral("i", None, "Start insert edit mode"))
    setattr(this, "I", FastLiteral("I", None, "Start insert edit mode at the first byte of buffer"))
    setattr(this, "a", FastLiteral("a", None, "Start append edit mode"))
    setattr(this, "A", FastLiteral("A", None, "Start append edit mode at the end of buffer"))
    setattr(this, "R", FastLiteral("R", None, "Start replace edit mode"))
    setattr(this, "r", FastLiteral("r", None, "Replace [count] characters under the cursor"))
    setattr(this, "v", FastLiteral("v", None, "Start/End visual mode"))
    setattr(this, "V", FastLiteral("V", None, "Start/End line visual mode"))
    setattr(this, "ctrlv", FastLiteral("<CTRL>v", (util.ctrl('v'),), "Start/End block visual mode"))
    setattr(this, "escape", FastLiteral("<ESCAPE>", (kbd.ESCAPE,), "Clear input or escape from current mode"))
    setattr(this, "mouse", FastLiteral("<MOUSE>", (kbd.MOUSE,), ""))
    setattr(this, "resize", FastLiteral("<RESIZE>", (kbd.RESIZE,), ""))

    setattr(this, "_mouse_button1_clicked", FastLiteral("<MOUSE_CLICKED>", (util.MAX_INT, 1), "Move cursor to clicked position in the window"))
    setattr(this, "_mouse_button1_pressed", FastLiteral("<MOUSE_PRESSED>", (util.MAX_INT, 2), "Start visual mode or start visual scroll (if already in visual mode) followed by <MOUSE_RELEASED> event"))
    setattr(this, "_mouse_button1_released", FastLiteral("<MOUSE_RELEASED>", (util.MAX_INT, 3), "Set visual area in the window"))
    setattr(this, "_mouse_button1_double_clicked", FastLiteral("<MOUSE_DOUBLE_CLICKED>", (util.MAX_INT, 4), "Start line visual mode or exit visual mode (if already in visual mode)"))
    setattr(this, "_mouse_button1_triple_clicked", FastLiteral("<MOUSE_TRIPLE_CLICKED>", (util.MAX_INT, 5), "Start block visual mode or exit visual mode (if already in visual mode)"))

    # XXX alternative for block visual mode
    if kernel.is_bsd_derived() or kernel.is_solaris():
        setattr(this, "_ctrlv", FastLiteral("<CTRL>v<CTRL>v", (util.ctrl('v'),), "Start/End block visual mode")) # the first <CTRL>v is ignored

    setattr(this, "reg_reg", RegexLiteral(2, "\"[0-9a-zA-Z\"]", r"^\"[0-9a-zA-Z\"]", "Use register {0-9a-zA-Z\"} for next delete, yank or put (use uppercase character to append with delete and yank)"))
    setattr(this, "m_reg", RegexLiteral(2, "m[0-9a-zA-Z]", r"^m[0-9a-zA-Z]", "Set mark at cursor position, uppercase marks are valid between buffers"))
    setattr(this, "backtick_reg", RegexLiteral(2, "`[0-9a-zA-Z]", r"^`[0-9a-zA-Z]", "Go to marked position"))
    setattr(this, "q", FastLiteral("q", None, "Stop recording"))
    setattr(this, "q_reg", StateLiteral(2, "q[0-9a-zA-Z]", r"^q[0-9a-zA-Z]", this.q, "Record typed characters into register"))
    setattr(this, "atsign_reg", RegexLiteral(2, "@[0-9a-zA-Z]", r"^@[0-9a-zA-Z]", "Execute the contents of register [count] times"))
    setattr(this, "atsign_at", FastLiteral("@@", None, "Execute the previous @ command [count] times"))
    setattr(this, "atsign_colon", FastLiteral("@:", None, "Execute the binded command"))
    setattr(this, "bit_and", RegexLiteral(3, "&[0-9a-fA-F]{2}", r"^&[0-9a-fA-F]{2}", "Replace [count] bytes with bitwise and-ed bytes"))
    setattr(this, "bit_or", RegexLiteral(3, "|[0-9a-fA-F]{2}", r"^\|[0-9a-fA-F]{2}", "Replace [count] bytes with bitwise or-ed bytes"))
    setattr(this, "bit_xor", RegexLiteral(3, "^[0-9a-fA-F]{2}", r"^\^[0-9a-fA-F]{2}", "Replace [count] bytes with bitwise xor-ed bytes"))

    setattr(this, "s_e", SlowLiteral(":e", None, "Open a buffer"))
    setattr(this, "s_bdelete", SlowLiteral(":bdelete", None, "Close a buffer"))
    setattr(this, "s_bfirst", SlowLiteral(":bfirst", None, "Go to the first buffer in buffer list"))
    setattr(this, "s_brewind", this.s_bfirst.create_alias(":brewind", None))
    setattr(this, "s_blast", SlowLiteral(":blast", None, "Go to the last buffer in buffer list"))
    setattr(this, "s_bnext", SlowLiteral(":bnext", None, "Change buffer to the next"))
    setattr(this, "s_bprev", SlowLiteral(":bprevious", None, "Change buffer to the previous"))
    setattr(this, "s_bNext", this.s_bprev.create_alias(":bNext", None))
    setattr(this, "s_set", SlowLiteral(":set", None, "Set option"))
    setattr(this, "s_self", SlowLiteral(":self", None, "Print current console instance string"))
    setattr(this, "s_pwd", SlowLiteral(":pwd", None, "Print the current directory name"))
    setattr(this, "s_date", SlowLiteral(":date", None, "Print date"))
    setattr(this, "s_kmod", SlowLiteral(":kmod", None, "Print Python module name for the platform OS"))
    setattr(this, "s_fobj", SlowLiteral(":fobj", None, "Print Python object name of the current buffer"))
    setattr(this, "s_bufsiz", SlowLiteral(":bufsiz", None, "Print temporary buffer size"))
    setattr(this, "s_meminfo", SlowLiteral(":meminfo", None, "Print free/total physical memory"))
    setattr(this, "s_osdep", SlowLiteral(":osdep", None, "Print OS dependent information"))
    setattr(this, "s_screen", SlowLiteral(":screen", None, "Print screen information"))
    setattr(this, "s_platform", SlowLiteral(":platform", None, "Print platform"))
    setattr(this, "s_hostname", SlowLiteral(":hostname", None, "Print hostname"))
    setattr(this, "s_term", SlowLiteral(":term", None, "Print terminal type"))
    setattr(this, "s_lang", SlowLiteral(":lang", None, "Print locale type"))
    setattr(this, "s_sector", SlowLiteral(":sector", None, "Print sector size for block device"))
    setattr(this, "s_version", SlowLiteral(":version", None, "Print version"))
    setattr(this, "s_argv", SlowLiteral(":argv", None, "Print arguments of this program"))
    setattr(this, "s_args", SlowLiteral(":args", None, "Print buffer list with the current buffer in brackets"))
    setattr(this, "s_md5", SlowLiteral(":md5", None, "Print md5 message digest of the current buffer"))
    setattr(this, "s_sha1", SlowLiteral(":sha1", None, "Print sha1 message digest of the current buffer"))
    setattr(this, "s_sha224", SlowLiteral(":sha224", None, "Print sha224 message digest of the current buffer"))
    setattr(this, "s_sha256", SlowLiteral(":sha256", None, "Print sha256 message digest of the current buffer"))
    setattr(this, "s_sha384", SlowLiteral(":sha384", None, "Print sha384 message digest of the current buffer"))
    setattr(this, "s_sha512", SlowLiteral(":sha512", None, "Print sha512 message digest of the current buffer"))
    setattr(this, "s_sha3_224", SlowLiteral(":sha3_224", None, "Print sha3_224 message digest of the current buffer"))
    setattr(this, "s_sha3_256", SlowLiteral(":sha3_256", None, "Print sha3_256 message digest of the current buffer"))
    setattr(this, "s_sha3_384", SlowLiteral(":sha3_384", None, "Print sha3_384 message digest of the current buffer"))
    setattr(this, "s_sha3_512", SlowLiteral(":sha3_512", None, "Print sha3_512 message digest of the current buffer"))
    setattr(this, "s_cmp", SlowLiteral(":cmp", None, "Compare two buffers and go to the first non matching byte"))
    setattr(this, "s_cmpneg", SlowLiteral(":cmp!", None, "Compare two buffers and go to the first matching byte"))
    setattr(this, "s_cmpnext", SlowLiteral(":cmpnext", None, "Compare two buffers starting from the next byte and go to the first non matching byte"))
    setattr(this, "s_cmpnextneg", SlowLiteral(":cmpnext!", None, "Compare two buffers starting from the next byte and go to the first matching byte"))
    setattr(this, "s_cmpr", SlowLiteral(":cmpr", None, "Compare two buffers from the end and go to the first non matching byte"))
    setattr(this, "s_cmprneg", SlowLiteral(":cmpr!", None, "Compare two buffers from the end and go to the first matching byte"))
    setattr(this, "s_cmprnext", SlowLiteral(":cmprnext", None, "Compare two buffers starting from the previous byte and go to the first non matching byte"))
    setattr(this, "s_cmprnextneg", SlowLiteral(":cmprnext!", None, "Compare two buffers starting from the previous byte and go to the first matching byte"))
    setattr(this, "s_delmarks", SlowLiteral(":delmarks", None, "Delete the specified marks"))
    setattr(this, "s_delmarksneg", SlowLiteral(":delmarks!", None, "Delete all marks for the current buffer except for uppercase marks"))
    setattr(this, "s_split", SlowLiteral(":split", None, "Split current window"))
    setattr(this, "s_vsplit", SlowLiteral(":vsplit", None, "Split current window vertically"))
    setattr(this, "s_close", SlowLiteral(":close", None, "Close current window"))
    setattr(this, "s_only", SlowLiteral(":only", None, "Make the current window the only one"))
    setattr(this, "s_w", SlowLiteral(":w", None, "Write the whole buffer to the file"))
    setattr(this, "s_wneg", SlowLiteral(":w!", None, "Like :w, but overwrite an existing file"))
    setattr(this, "s_wq", SlowLiteral(":wq", None, "Write the current file and quit"))
    setattr(this, "s_x", SlowLiteral(":x", None, "Like :wq, but write only when changes have been made"))
    setattr(this, "s_q", SlowLiteral(":q", None, "Close current window if more than 1 windows exist else quit program"))
    setattr(this, "s_qneg", SlowLiteral(":q!", None, "Close current window if more than 1 windows exist else quit program without writing"))
    setattr(this, "s_qa", SlowLiteral(":qa", None, "Close all windows and quit program"))
    setattr(this, "s_qaneg", SlowLiteral(":qa!", None, "Close all windows and quit program without writing"))
    setattr(this, "s_bind", SlowLiteral(":bind", None, "Run/bind given :command in argument, replayable with {0}".format(this.atsign_colon.str)))
    setattr(this, "s_auto", SlowLiteral(":auto", None, "Optimize editor window size based on the current terminal size"))
    setattr(this, "s_fsearch", SearchLiteral("/", None, "Search forward"))
    setattr(this, "s_rsearch", SearchLiteral("?", None, "Search backward"))

    setattr(this, "s_set_binary", ArgLiteral("binary", None, "Set binary edit mode (unset ascii edit mode)"))
    setattr(this, "s_set_ascii", ArgLiteral("ascii", None, "Set ascii edit mode (unset binary edit mode)"))
    setattr(this, "s_set_le", ArgLiteral("le", None, "Set endianness to little (unset big endian if set)"))
    setattr(this, "s_set_be", ArgLiteral("be", None, "Set endianness to big (unset little endian if set)"))
    setattr(this, "s_set_ws", ArgLiteral("ws", None, "Set wrapscan mode (search wraps around the end of the buffer)"))
    setattr(this, "s_set_nows", ArgLiteral("nows", None, "Unset wrapscan mode"))
    setattr(this, "s_set_ic", ArgLiteral("ic", None, "Set ic mode (ignore the case of alphabets on search)"))
    setattr(this, "s_set_noic", ArgLiteral("noic", None, "Unset ic mode"))
    setattr(this, "s_set_si", ArgLiteral("si", None, "Set SI prefix mode (kilo equals 10^3)"))
    setattr(this, "s_set_nosi", ArgLiteral("nosi", None, "Unset SI prefix mode (kilo equals 2^10)"))
    setattr(this, "s_set_address", ArgLiteral("address", None, "Set address radix to {16,10,8}"))
    setattr(this, "s_set_status", ArgLiteral("status", None, "Set buffer size and current position radix to {16,10,8}"))
    setattr(this, "s_set_bpl", ArgLiteral("bytes_per_line", None, "Set bytes_per_line to {[0-9]+,\"max\",\"min\",\"auto\"}"))
    setattr(this, "s_set_bpl_", this.s_set_bpl.create_alias("bpl", None))
    setattr(this, "s_set_bpw", ArgLiteral("bytes_per_window", None, "Set bytes_per_window to {[0-9]+,\"even\",\"auto\"}"))
    setattr(this, "s_set_bpw_", this.s_set_bpw.create_alias("bpw", None))
    setattr(this, "s_set_bpu", ArgLiteral("bytes_per_unit", None, "Set bytes_per_unit to {\"1\",\"2\",\"4\",\"8\"}"))
    setattr(this, "s_set_bpu_", this.s_set_bpu.create_alias("bpu", None))

    for _ in util.iter_site_ext_module():
        fn = getattr(_, "get_text", None)
        if fn:
            __alloc_ext_literals(_, fn)

    for _ in util.iter_dir_values(this):
        if util.is_subclass(_, Literal):
            __register_is_function(_)

    __register_alias(
        (this.ctrlw_c, this.s_close),
        (this.ctrlw_o, this.s_only),
        (this.ctrlw_q, this.s_q),
        (this.tab, this.s_bnext),
        (this.ZZ, this.s_x),
        (this.ZQ, this.s_qneg),)

    __register_refer(
        (this.gg, this.G),
        (this.doller, this.zero),
        ((this.L, this.M), this.H),
        (this.b, this.w),
        ((this.bracket2_beg, this.bracket2_end, this.bracket1_beg, this.bracket1_end, this.parens_beg), this.parens_end),
        (this.ctrlu, this.ctrlb),
        (this.ctrld, this.ctrlf),
        ((this.ctrlv, this.V), this.v),
        (this.g_ctrlg, this.ctrlg),
        (this.rol, this.ror),
        (this.y, this.Y),
        (this.p, this.P),
        (this.o, this.O),
        (this.n, this.N),
        ((this.r, this.R, this.A, this.a, this.I), this.i),
        (this.backtick_reg, this.m_reg),
        (this.q, this.q_reg),
        (this.atsign_at, this.atsign_reg),
        ((this.bit_xor, this.bit_or), this.bit_and),
        (this.s_bdelete, this.s_e),
        (this.s_cmpneg, this.s_cmp),
        (this.s_delmarksneg, this.s_delmarks),
        (this.s_rsearch, this.s_fsearch),
        ((this.s_set_ascii.refer(this.s_set_binary), this.s_set_be.refer(this.s_set_le), this.s_set_nows.refer(this.s_set_ws), this.s_set_noic.refer(this.s_set_ic), this.s_set_nosi.refer(this.s_set_si), this.s_set_status.refer(this.s_set_address), this.s_set_bpl, this.s_set_bpw, this.s_set_bpu), this.s_set),)

    # edit._deleteconsole currently requires delete variants are of size 1
    assert len(this.delete.seq) == 1, this.delete
    l = [this.delete.seq[0]]
    for o in this.delete.children:
        assert len(o.seq) == 1, o
        l.append(o.seq[0])
    this.delete_cmds = tuple(l)

    def __scan(l, o, cls):
        if setting.use_debug:
            assert tuple(o.children) == tuple(sorted(o.children)), o.children
        for li in o.children: # already sorted (and must be sorted)
            if isinstance(li, cls):
                l.append(li)
            __scan(l, li, cls)

    for cls in Literal, FastLiteral, SlowLiteral, ArgLiteral, ExtLiteral:
        l = []
        __scan(l, this._root, cls)
        _ld[cls] = tuple(l)
    _ld[None] = tuple(sorted(get_literals()))

def cleanup():
    if not hasattr(this, "_root"):
        return -1
    for s, o in util.iter_dir_items(this):
        if this.is_Literal(o):
            o.cleanup()
            delattr(this, s)
    _ld.clear()

this = sys.modules[__name__]
