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
from . import setting
from . import status
from . import util

class Window (object):
    def __init__(self, canvas, frame):
        self.__frame = frame(panel.get_min_size(frame),
            panel.get_min_position(frame))
        self.__canvas = canvas(panel.get_min_size(canvas),
            panel.get_min_position(canvas))

    def __getattr__(self, name):
        if name == "_Window__canvas":
            raise AttributeError(name)
        return getattr(self.__canvas, name)

    def __str__(self):
        return "{0},{1}".format(self.__frame, self.__canvas)

    def update(self):
        self.__frame.update()
        self.__canvas.update()

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

    def has_buffer(self):
        return self.__canvas.has_buffer()

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

    def set_focus(self, x):
        self.__frame.set_focus(x)
        self.__canvas.set_focus(x)

    def require_full_repaint(self):
        self.__frame.require_full_repaint()
        self.__canvas.require_full_repaint()

    def repaint(self, is_current):
        self.__frame.repaint(is_current)
        self.__canvas.repaint(is_current, False)

    def lrepaint(self, is_current, low):
        self.__canvas.repaint(is_current, low)

    def prepaint(self, is_current, low, num):
        self.__canvas.repaint_partial(is_current, low, num)

    def xrepaint(self, is_current):
        self.__frame.repaint(is_current)

    def resize(self, siz, pos):
        self.__frame.resize(siz, pos)
        self.__canvas.resize(self.__get_canvas_size(),
            self.__get_canvas_position())

    def has_geom(self, y, x):
        return self.__frame.has_geom(y, x)

    def get_geom_pos(self, y, x):
        return self.__canvas.get_geom_pos(y, x)

    def reset_page_line_state(self, fail_fast=False):
        return self.__canvas.reset_page_line_state(fail_fast)

    def has_page_line_state_machine(self):
        return self.__canvas.has_page_line_state_machine()

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
    if setting.use_text_window:
        # need at least 2(lines_per_window==1) lines
        lf = panel.get_min_size(panel.Frame)
        lc = panel.get_min_size(panel.TextCanvas)
        return lpw + 1 + _get_diff_y(lf, lc)
    else:
        return get_min_binary_window_height(lpw)

def get_status_window_height(scls, fcls):
    assert util.is_subclass(scls, status.StatusCanvas)
    assert util.is_subclass(fcls, status.StatusFrame)
    lf = panel.get_min_size(fcls)
    lc = panel.get_min_size(scls)
    if util.is_subclass(scls, status.VerboseStatusCanvas):
        height = 2
    elif util.is_subclass(scls, status.SingleStatusCanvas):
        height = 1
    else:
        assert False, scls
    return height + _get_diff_y(lf, lc)

def get_width(cls, bytes_per_line):
    assert util.is_subclass(cls, panel.Canvas)
    s = cls.__name__
    assert "Binary" in s or "Text" in s
    lf = panel.get_min_size(panel.Frame)
    lc = panel.get_min_size(cls)
    o = cls(None, None)
    ret = o.offset.x
    unit = bytes_per_line // setting.bytes_per_unit
    if unit < 1:
        unit = 1
    ret += o.get_unit_edge(unit)
    ret += _get_diff_x(lf, lc)
    return ret

# This function must return 0 if no space, don't round up with bpu.
def get_max_bytes_per_line(wspnum):
    if not wspnum: # when container creates initial wsp
        wspnum = 1
    width, cell, edge = __get_min_info()
    assert width > 0, width
    assert cell > 0, cell
    assert edge > 0, edge
    r = screen.get_size_x() - width * wspnum
    r -= edge * wspnum
    if r < 1:
        return 0
    ret = 1
    while True:
        r -= cell * wspnum
        if r < 0: # not "r < 1"
            return util.rounddown(ret, setting.bytes_per_unit)
        ret += 1
    assert False

# Calculation based on cell consumes more space than unit width with bpu > 1,
# so this guarantees get_max_bytes_per_line() works with bpu > 1.
def __get_min_info():
    lf = panel.get_min_size(panel.Frame)
    bc = panel.BinaryCanvas(None, None)
    width = _get_diff_x(lf, panel.get_min_size(bc)) + bc.offset.x
    cell = bc.get_cell()[0]
    edge = bc.get_cell()[0] - bc.get_cell()[1]
    if setting.use_text_window:
        tc = panel.TextCanvas(None, None)
        width += (_get_diff_x(lf, panel.get_min_size(tc)) + tc.offset.x)
        cell += tc.get_cell()[0]
        edge += (tc.get_cell()[0] - tc.get_cell()[1])
    return width, cell, edge
