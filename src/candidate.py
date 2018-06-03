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

import os

from . import path
from . import util

class _candidate (object):
    def __init__(self):
        self.clear()

    def clear(self):
        self.__gen = None
        self.__prev = None

    def get(self, arg):
        if not self.__gen or self.__prev != arg:
            self.__update_generator(arg)
            self.__prev = arg
        try:
            return self.__get_next_item()
        except StopIteration:
            self.__update_generator(self.__prev)
            try:
                return self.__get_next_item()
            except StopIteration:
                return None

    def __update_generator(self, arg):
        self.__gen = self._get_generator(arg)

    def _get_generator(self, arg):
        util.raise_no_impl("_get_generator")

    def __get_next_item(self):
        return self._get_item(util.iter_next(self.__gen))

    def _get_item(self, o):
        return o

class LiteralCandidate (_candidate):
    def __init__(self, literals=None):
        super(LiteralCandidate, self).__init__()
        self.__literals = literals

    def init(self, literals):
        self.clear()
        self.__literals = literals

    def _get_generator(self, arg):
        for li in self.__literals:
            if li.str.startswith(arg):
                yield li.str

class PathCandidate (_candidate):
    def _get_generator(self, arg):
        p = path.Path(arg)
        d, b = os.path.split(p.path)
        if util.is_read_ok(d) and (p.is_dir or p.is_reg or p.is_noent):
            l = [x for x in sorted(os.listdir(d)) if x.startswith(b)]
            for s in l:
                f = os.path.join(d, s)
                if os.path.isdir(f) and not f.endswith("/"):
                    f = f + "/"
                yield f, len(l)

    def _get_item(self, o):
        return path.get_short_path(o[0]), o[1]
