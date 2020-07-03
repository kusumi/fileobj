# Copyright (c) 2018, Tomohiro Kusumi
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
import shutil

from . import kernel
from . import util

if kernel.is_xnix():
    import termios
    import tty

    from . import unix as _terminal

    def get_lang():
        return os.getenv("LANG", "")

    def get_type():
        return os.getenv("TERM", "")

    def in_tmux_screen():
        return os.getenv("STY") is not None

    def in_tmux_tmux():
        return os.getenv("TMUX") is not None

    def in_windows_prompt():
        return False

    def getch(fd):
        return ord(fd.read(1))

    def init_getch(fd):
        global _tattr
        if not _tattr:
            _tattr = termios.tcgetattr(fd)
            tty.setcbreak(fd)
        else:
            return -1

    def cleanup_getch(fd):
        global _tattr
        if _tattr:
            termios.tcsetattr(fd, termios.TCSANOW, _tattr)
            _tattr = None
        else:
            return -1

    _tattr = None
else:
    assert kernel.is_windows(), util.get_os_name()
    import msvcrt

    from . import ascii
    from . import windows as _terminal

    def get_lang():
        return ""

    def get_type():
        return ""

    def in_tmux_screen():
        return False

    def in_tmux_tmux():
        return False

    def in_windows_prompt():
        return os.getenv("PROMPT") is not None

    def getch(fd):
        ret = ord(msvcrt.getch())
        if ret == ascii.CR:
            return ascii.LF
        else:
            return ret

    def init_getch(fd):
        return

    def cleanup_getch(fd):
        return

if util.is_python_version_or_ht(3, 3):
    def get_size():
        x, y = shutil.get_terminal_size()
        return y, x
else:
    get_size = _terminal.get_terminal_size

def is_vtxxx():
    return get_type().startswith("vt")

def is_vt1xx():
    return get_type().startswith("vt1")

def is_vt2xx():
    return get_type().startswith("vt2")

def is_xterm():
    return get_type().startswith("xterm")

def is_rxvt():
    return get_type().startswith("rxvt")

def is_gnome():
    return get_type().startswith("gnome")

def is_konsole():
    return get_type().startswith("konsole")

def is_screen():
    return get_type().startswith("screen")

def is_putty():
    return get_type().startswith("putty")

def is_linux():
    return get_type().startswith("linux")

def is_dumb():
    return get_type().startswith("dumb")

# XXX
def is_windows_terminal():
    assert False, "is_windows_terminal"
