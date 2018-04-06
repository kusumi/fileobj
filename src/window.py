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

from . import panel
from . import screen
from . import util

class Window (object):
    def __init__(self, canvas, frame):
        self.__frame = frame(
            panel.get_min_size(frame),
            panel.get_min_position(frame))
        self.__canvas = canvas(
            panel.get_min_size(canvas),
            panel.get_min_position(canvas))

    def __getattr__(self, name):
        if name == "_Window__canvas":
            raise AttributeError(name)
        return getattr(self.__canvas, name)

    def __get_canvas_size(self):
        lf = panel.get_min_size(self.__frame)
        lc = panel.get_min_size(self.__canvas)
        y = self.get_size_y() - _get_diff_y(lf, lc)
        x = self.get_size_x() - _get_diff_x(lf, lc)
        return y, x

    def __get_canvas_position(self):
        lf = panel.get_min_position(self.__frame)
        lc = panel.get_min_position(self.__canvas)
        y = self.get_position_y() - _get_diff_y(lf, lc)
        x = self.get_position_x() - _get_diff_x(lf, lc)
        return y, x

    def set_buffer(self, fileops):
        self.__canvas.set_buffer(fileops)

    def get_size_y(self):
        return self.__frame.get_size_y()

    def get_size_x(self):
        return self.__frame.get_size_x()

    def get_position_y(self):
        return self.__frame.get_position_y()

    def get_position_x(self):
        return self.__frame.get_position_x()

    def repaint(self, focus):
        self.__frame.repaint(focus)
        self.__canvas.repaint(False)

    def lrepaint(self, low):
        self.__canvas.repaint(low)

    def xrepaint(self):
        self.__frame.repaint(False)

    def resize(self, siz, pos):
        self.__frame.resize(siz, pos)
        self.__canvas.resize(
            self.__get_canvas_size(),
            self.__get_canvas_position())

def _get_diff_y(a, b):
    return a[0] - b[0]

def _get_diff_x(a, b):
    return a[1] - b[1]

def get_min_binary_window_height(lpw=1):
    # need at least 2(lines_per_window==1) lines
    lf = panel.get_min_size(panel.Frame)
    lc = panel.get_min_size(panel.BinaryCanvas)
    return lpw + 1 + _get_diff_y(lf, lc)

def get_min_text_window_height(lpw=1):
    # need at least 2(lines_per_window==1) lines
    lf = panel.get_min_size(panel.Frame)
    lc = panel.get_min_size(panel.TextCanvas)
    return lpw + 1 + _get_diff_y(lf, lc)

def get_status_window_height(scls, fcls):
    assert util.is_subclass(scls, panel.StatusCanvas)
    assert util.is_subclass(fcls, panel.StatusFrame)
    lf = panel.get_min_size(fcls)
    lc = panel.get_min_size(scls)
    if util.is_subclass(scls, panel.VerboseStatusCanvas):
        height = 2
    elif util.is_subclass(scls, panel.SingleStatusCanvas):
        height = 1
    else:
        assert 0, scls
    return height + _get_diff_y(lf, lc)

def get_width(cls, bytes_per_line):
    assert util.is_subclass(cls, panel.Canvas)
    s = cls.__name__
    assert "Binary" in s or "Text" in s
    lf = panel.get_min_size(panel.Frame)
    lc = panel.get_min_size(cls)
    o = cls(None, None)
    ret = o.offset.x
    ret += o.get_cell_edge(bytes_per_line)
    ret += _get_diff_x(lf, lc)
    return ret

def get_max_bytes_per_line(wspnum):
    if not wspnum: # when container creates initial wsp
        wspnum = 1
    width, cell = __get_min_info()
    assert width > 0, width
    assert cell > 0, cell
    max_bpl = screen.get_size_x() - width * wspnum
    max_bpl //= (cell * wspnum)
    return max_bpl

def __get_min_info():
    bc = panel.BinaryCanvas(None, None)
    tc = panel.TextCanvas(None, None)
    lf = panel.get_min_size(panel.Frame)
    width = _get_diff_x(lf, panel.get_min_size(bc))
    width += _get_diff_x(lf, panel.get_min_size(tc))
    width += (bc.offset.x + tc.offset.x)
    cell = bc.get_cell()[0] + tc.get_cell()[0]
    return width, cell
