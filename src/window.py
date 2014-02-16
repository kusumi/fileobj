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

from . import panel
from . import screen

class Window (object):
    def __init__(self, canvas, frame):
        self.__frame = frame(
            panel.get_min_frame_size(),
            panel.get_min_frame_position())
        self.__canvas = canvas(
            self.__get_canvas_size(),
            self.__get_canvas_position())

    def __getattr__(self, name):
        if name == "_Window__canvas":
            raise AttributeError(name)
        return getattr(self.__canvas, name)

    def __get_canvas_size(self):
        y, x = [l[1] - l[0] for l in
            zip(panel.get_min_frame_size(),
                panel.get_min_canvas_size())]
        return self.get_size_y() + y, self.get_size_x() + x

    def __get_canvas_position(self):
        y, x = [l[1] - l[0] for l in
            zip(panel.get_min_frame_position(),
                panel.get_min_canvas_position())]
        return self.get_position_y() + y, self.get_position_x() + x

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

    def resize(self, siz, pos):
        self.__frame.resize(siz, pos)
        self.__canvas.resize(
            self.__get_canvas_size(),
            self.__get_canvas_position())

def get_min_height():
    # need at least two lines for binary/text canvas
    return 2 + panel.get_margin(2) + get_option_window_height()

def get_option_window_height():
    # need two lines for option canvas
    return 2 + panel.get_margin(2)

def get_width(cls, bytes_per_line):
    canvas = cls(None, None)
    return canvas.offset.x + canvas.get_cell_edge(bytes_per_line) + \
        panel.get_margin(2)

def get_max_bytes_per_line():
    bcanvas = panel.BinaryCanvas(None, None)
    tcanvas = panel.TextCanvas(None, None)
    ret = screen.get_size_x() - panel.get_margin(4)
    ret -= (bcanvas.offset.x + tcanvas.offset.x)
    ret //= (bcanvas.get_cell()[0] + tcanvas.get_cell()[0])
    if ret < 1:
        return -1
    else:
        return ret
