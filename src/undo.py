# Copyright (c) 2011, Tomohiro Kusumi
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

from . import util

ERROR    = -1
NOTFOUND = -2

class Undo (object):
    def __init__(self):
        self.__undoredo = []
        self.__rollback = []
        self.__cursor = 0
        self.__base = 0

    def __len__(self):
        return len(self.__undoredo)

    def add_undo(self, ufn, rfn):
        if self.__cursor < self.__base:
            self.__base = -1
        for x in util.get_xrange(self.get_redo_size()):
            self.__undoredo.pop()
        self.__undoredo.append((ufn, rfn))
        self.__rollback.append((ufn, -1))
        self.__cursor += 1

    def merge_undo(self, n):
        """Return number of merged undos or -1"""
        if self.__cursor != len(self):
            return -1 # can only merge heads
        if self.__cursor <= 1 or n <= 1:
            return -1 # nothing to merge

        if n > self.__cursor:
            n = self.__cursor
        l = [self.__undoredo.pop() for x in util.get_xrange(n)]
        for x in util.get_xrange(len(l)):
            self.__rollback.pop()
        self.__cursor -= n

        undos = [l[i][0] for i in
            util.get_xrange(0, len(l))] # new to old
        redos = [l[i][1] for i in
            util.get_xrange(len(l) - 1, -1, -1)] # old to new
        def ufn(ref):
            return [fn(ref) for fn in undos][-1] # oldest
        def rfn(ref):
            return [fn(ref) for fn in redos][0] # oldest
        self.add_undo(ufn, rfn)
        return len(undos)

    def undo(self, ref):
        if self.__cursor > 0:
            ret, msg, rfn = self.__undo(ref, self.__cursor - 1)
            if ret != ERROR:
                self.__cursor -= 1
                if self.__base != -1 and self.__cursor >= self.__base:
                    self.__rollback.pop()
                else:
                    self.__rollback.append((rfn, +1))
            return ret, self.__cursor == self.__base, msg
        else:
            return NOTFOUND, False, ''

    def __undo(self, ref, index):
        try:
            ufn, rfn = self.__undoredo[index]
            return ufn(ref), '', rfn
        except Exception as e:
            return ERROR, str(e), None

    def redo(self, ref):
        if self.__cursor < len(self):
            ret, msg, ufn = self.__redo(ref, self.__cursor)
            if ret != ERROR:
                self.__cursor += 1
                if self.__base != -1 and self.__cursor <= self.__base:
                    self.__rollback.pop()
                else:
                    self.__rollback.append((ufn, -1))
            return ret, self.__cursor == self.__base, msg
        else:
            return NOTFOUND, False, ''

    def __redo(self, ref, index):
        try:
            ufn, rfn = self.__undoredo[index]
            return rfn(ref), '', ufn
        except Exception as e:
            return ERROR, str(e), None

    def get_undo_size(self):
        return self.__cursor

    def get_redo_size(self):
        return len(self) - self.get_undo_size()

    def get_rollback_log_size(self):
        return len(self.__rollback)

    def sync_base_pointer(self):
        """Throw away log and overwrite base with current"""
        total = 0
        while self.__rollback:
            fn, delta = self.__rollback.pop()
            total += delta
        if self.__base != -1:
            assert self.__cursor + total == self.__base
        self.__base = self.__cursor
        return total

    def restore_rollback_log(self, ref):
        """Restore log and sync current with base"""
        total = 0
        while self.__rollback:
            fn, delta = self.__rollback.pop()
            total += delta
            fn(ref)
        self.__cursor += total
        if self.__base != -1:
            assert self.__cursor == self.__base
        return total
