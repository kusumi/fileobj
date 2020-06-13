# Copyright (c) 2020, Tomohiro Kusumi
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

from .. import screen
from .. import setting

def get_text(co, fo, args):
    if setting.use_stdout:
        return "Using stdout"
    try:
        import curses
        from .. import ncurses
    except ImportError as e:
        return str(e)

    sl = []
    try:
        sl.append("has_color        {0}".format(screen.has_color()))
        sl.append("can_change_color {0}".format(screen.can_change_color()))
        sl.append("use_color        {0}".format(screen.use_color()))
        sl.append("use_mouse        {0}".format(screen.use_mouse()))
        sl.append("")

        d = {
            ncurses.A_COLOR_FB : "A_COLOR_FB",
            ncurses.A_COLOR_CURRENT : "A_COLOR_CURRENT",
            ncurses.A_COLOR_ZERO : "A_COLOR_ZERO",
            ncurses.A_COLOR_FF : "A_COLOR_FF",
            ncurses.A_COLOR_PRINT : "A_COLOR_PRINT",
            ncurses.A_COLOR_DEFAULT : "A_COLOR_DEFAULT",
            ncurses.A_COLOR_VISUAL : "A_COLOR_VISUAL",
            ncurses.A_COLOR_OFFSET : "A_COLOR_OFFSET", }
        sl.append("pair#")

        # https://docs.python.org/3/library/curses.html#curses.init_pair
        for x in range(1, curses.COLOR_PAIRS-1 + 1):
            if x >= ncurses._pair_number:
                continue
            a = curses.color_pair(x)
            sl.append("{0} {1:x} {2} {3}".format(x, a,
                ncurses._color_pair_number_dict.get(x, None),
                d.get(a, "???")))
        sl.append("")

        d = dict(list(ncurses.__iter_color_pair(True)))
        sl.append("color#")

        # https://docs.python.org/3/library/curses.html#curses.init_color
        for x in range(0, curses.COLORS + 1):
            if x >= ncurses._rgb_number:
                continue
            l = curses.color_content(x)
            sl.append("{0} {1} {2}".format(x, l, d.get(x, "")))
    except curses.error as e:
        return str(e)
    return sl
