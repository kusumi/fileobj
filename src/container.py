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
import collections
import sys

from . import allocator
from . import console
from . import extension
from . import fileops
from . import kbd
from . import operand
from . import path
from . import screen
from . import setting
from . import trace
from . import util
from . import void
from . import workspace

class Container (object):
    def __init__(self):
        self.__workspaces = []
        self.__workspace_delta = {}
        self.__fileobjs = []
        self.__consoles = {}
        self.__records = {}
        self.__records_key = ''
        self.__yank_buffer = []
        self.__delayed_input = []
        self.__stream = collections.deque()
        self.__operand = operand.Operand()
        self.__cur_workspace = None
        self.set_prev_context(None)

    def __getattr__(self, name):
        if name == "_Container__cur_workspace":
            raise AttributeError(name)
        return getattr(self.__cur_workspace, name)

    def __len__(self):
        return len(self.__workspaces)

    def init(self, args, wspnum, width):
        assert not self.__fileobjs
        for x in args:
            o = self.__alloc_buffer(x)
            if o:
                self.__fileobjs.append(o)
        if not self.__fileobjs:
            self.__fileobjs.append(self.__alloc_buffer(''))

        s = { 16: "%X",
              10: "%d",
              8 : "%o", }.get(setting.offset_num_radix) % \
                max([o.get_size() for o in self.__fileobjs])
        if len(s) > setting.offset_num_width:
            for x in [2 ** i for i in range(10)]:
                if x > len(s):
                    setting.offset_num_width = x
                    break

        self.__workspaces.append(workspace.Workspace(width))
        wsp = self.__workspaces[0]
        self.__set_workspace(wsp)
        for i, o in enumerate(self.__fileobjs):
            wsp.add_buffer(i, fileops.Fileops(o), self.__get_console())

        for i in range(1, wspnum):
            o = self.clone_workspace()
            o.goto_buffer(i % len(self.__fileobjs))
            self.__workspaces.append(o)
            if self.__build(True):
                self.__remove_workspace(o)
                break
        return self.build()

    def cleanup(self):
        for o in self.__fileobjs:
            o.cleanup()
        self.__operand.cleanup()

    def dispatch(self):
        self.__load_stream()
        while True:
            if self.__cur_workspace.dispatch() == -1:
                return

    def getch(self):
        if len(self.__stream):
            x = self.__read_stream()
        else:
            x = console.getch()
        if self.__records_key:
            x = self.add_record(x)
        if self.__delayed_input:
            x = self.add_delayed_input(x)
        return x

    def flash(self, o=None):
        if o:
            self.show(o)
        screen.flash()

    def show(self, o):
        console.set_message(o)

    def push_banner(self, s):
        console.push_banner(s)
    def pop_banner(self):
        console.pop_banner()

    def set_console(self, cls, arg):
        if cls:
            con = self.__get_console(cls)
        else:
            con = None
        self.__cur_workspace.set_console(con, arg)

    def __get_console(self, cls=workspace.def_console_class):
        if cls not in self.__consoles:
            self.__consoles[cls] = cls(self, self.__operand)
        return self.__consoles[cls]

    def discard_workspace(self):
        for o in self.__workspaces:
            o.discard_window()

    def restore_workspace(self):
        for o in self.__workspaces:
            o.restore_window()

    def __alloc_buffer(self, f):
        if not self.has_buffer(f):
            o = allocator.alloc(f)
            if o:
                return o
            if not self.has_buffer(''):
                return allocator.alloc('') # never fail

    def add_buffer(self, f):
        """Add buffer and make current workspace focus that"""
        if not self.has_buffer(f):
            o = self.__alloc_buffer(f)
            if o:
                return self.__add_buffer(o, self.__get_console())
        else:
            self.__cur_workspace.goto_buffer(
                self.__get_buffer_index(f))

    def add_extension(self, fn, args):
        try:
            args.append(self.get_pos())
            fo = self.__get_buffer(self.get_path())
            ret = fn(self, fileops.Fileops(fo), args)
            if isinstance(ret, (list, tuple)):
                ret = '\n'.join(ret)
        except extension.ExtError:
            e = sys.exc_info()[1]
            ret = util.exc_to_string(e)

        if setting.use_readonly:
            from . import roext as ext
        else:
            from . import rwext as ext
        return self.__add_buffer(ext.Fileobj(ret),
            self.__get_console(void.ExtConsole))

    def __add_buffer(self, o, con):
        if self.__fileobjs:
            i = self.__get_buffer_index(self.get_path())
        else:
            i = 0
        self.__fileobjs.insert(i, o)
        for wsp in self.__workspaces:
            wsp.add_buffer(i, fileops.Fileops(o), con)
        self.__cur_workspace.goto_buffer(i)
        return o.get_path()

    def remove_buffer(self, f, reload=False):
        o = self.__get_buffer(f)
        if o:
            for wsp in self.__workspaces:
                wsp.remove_buffer(self.__fileobjs.index(o))
            o.cleanup()
            self.__fileobjs.remove(o)
            if reload:
                self.add_buffer(f)
            if not self.__fileobjs:
                self.add_buffer('')
        else:
            return -1

    def goto_buffer(self, f):
        i = self.__get_buffer_index(f)
        if i != -1:
            self.__cur_workspace.goto_buffer(i)
        else:
            return -1

    def reload_buffer(self, new):
        return self.__reload_buffer(self.get_path(), new)

    def __reload_buffer(self, old, new):
        """This method has nothing to do with buffer contents"""
        if not self.has_buffer(old):
            return -1
        if old == new:
            self.remove_buffer(old, reload=True)
        else:
            f = self.add_buffer(new)
            if f != new:
                if f is not None:
                    self.remove_buffer(f)
                return -1
            self.remove_buffer(old)
            assert not self.has_buffer(old), old
        assert self.get_path() == new, new

    def __get_buffer(self, f, cond=None):
        i = self.__get_buffer_index(f, cond)
        if i != -1:
            return self.__fileobjs[i]

    def __get_buffer_index(self, f, cond=None):
        f = path.get_path(f)
        for i, x in enumerate(self.get_buffer_paths(cond)):
            if util.is_same_file(f, x) or f == x:
                return i
        return -1

    def has_buffer(self, f, cond=None):
        return self.__get_buffer_index(f, cond) != -1

    def get_buffer_paths(self, cond=None):
        return tuple(o.get_path() for o in self.__fileobjs
            if (cond(o) if cond else True))

    def get_buffer_short_paths(self, cond=None):
        return tuple(o.get_short_path() for o in self.__fileobjs
            if (cond(o) if cond else True))

    def get_buffer_count(self):
        return len(self.__fileobjs)

    def iter_buffer(self):
        for o in self.__cur_workspace.iter_buffer():
            yield o

    def build(self):
        if len(self):
            if self.__build(True):
                self.__clear_workspace_delta()
                ret = self.__build(True) # retry
                if ret:
                    self.flash("Not enough room")
                    return ret
            if setting.use_even_size_window:
                screen.refresh()
            return self.__build(False)

    def __build(self, dry):
        l = console.get_position_y()
        if setting.use_even_size_window:
            h = l // len(self)
            y = 0
            for o in self.__workspaces:
                ret = self.__build_workspace(o, h, y, dry)
                if ret:
                    return ret
                y += h
        else:
            n = len(self)
            q = l // n
            r = l % n
            y = 0
            for o in self.__workspaces:
                h = q
                if r > 0:
                    h += 1
                    r -= 1
                ret = self.__build_workspace(o, h, y, dry)
                if ret:
                    return ret
                y += h

    def __build_workspace(self, wsp, hei, beg, dry):
        if wsp in self.__workspace_delta:
            hei += self.__workspace_delta[wsp][0]
            beg += self.__workspace_delta[wsp][1]
        if dry:
            return wsp.build_dryrun(hei, beg)
        else:
            return wsp.build(hei, beg)

    def adjust_workspace(self, n):
        if len(self) == 1 or not n:
            return -1
        current = self.__cur_workspace
        # assume second adjust won't fail if first adjust doesn't
        if current == self.__workspaces[-1]:
            prev = self.__get_prev_workspace()
            if n > 0:
                if self.__add_workspace_delta(prev, -n, 0) != -1:
                    self.__add_workspace_delta(current, n, -n)
            else:
                if self.__add_workspace_delta(current, n, -n) != -1:
                    self.__add_workspace_delta(prev, -n, 0)
        else:
            next = self.__get_next_workspace()
            if n > 0:
                if self.__add_workspace_delta(next, -n, n) != -1:
                    self.__add_workspace_delta(current, n, 0)
            else:
                if self.__add_workspace_delta(current, n, 0) != -1:
                    self.__add_workspace_delta(next, -n, n)
        self.build()

    def __add_workspace_delta(self, wsp, h, b):
        ret = wsp.build_dryrun_delta(h, b)
        if ret:
            self.flash("Not enough room")
            return ret
        if wsp in self.__workspace_delta:
            self.__workspace_delta[wsp][0] += h
            self.__workspace_delta[wsp][1] += b
        else:
            self.__workspace_delta[wsp] = [h, b]

    def __clear_workspace_delta(self):
        self.__workspace_delta.clear()

    def add_workspace(self):
        i = self.__get_buffer_index(self.get_path())
        cur_workspace = self.__cur_workspace
        new_workspace = self.clone_workspace()
        self.__clear_workspace_delta()
        self.__workspaces.insert(
            self.__workspaces.index(cur_workspace), new_workspace)
        self.__set_workspace(new_workspace)
        if self.build() != -1:
            new_workspace.goto_buffer(i)
            return self.__get_workspace_index()
        else:
            self.__remove_workspace(new_workspace)
            self.__set_workspace(cur_workspace)
            return -1

    def remove_workspace(self):
        if len(self) > 1:
            o = self.__cur_workspace
            if self.__workspaces.index(o) == len(self) - 1:
                self.goto_prev_workspace()
            else:
                self.goto_next_workspace()
            self.__remove_workspace(o)
            self.build()
            return self.__get_workspace_index()
        else:
            self.flash()
            return -1

    def remove_other_workspace(self):
        if len(self) > 1:
            l = [o for o in self.__workspaces
                if o is not self.__cur_workspace]
            for o in l:
                self.__remove_workspace(o)
            assert len(self) == 1
            self.__set_workspace(self.__workspaces[0])
            self.build()
            return self.__get_workspace_index()
        else:
            self.flash()
            return -1

    def __remove_workspace(self, o):
        self.__clear_workspace_delta()
        self.__workspaces.remove(o)

    def goto_next_workspace(self):
        return self.__set_workspace(self.__get_next_workspace())
    def goto_prev_workspace(self):
        return self.__set_workspace(self.__get_prev_workspace())

    def goto_top_workspace(self):
        return self.__set_workspace(self.__workspaces[0])
    def goto_bottom_workspace(self):
        return self.__set_workspace(self.__workspaces[len(self) - 1])

    def __get_workspace_index(self, o=None):
        if not o:
            o = self.__cur_workspace
        return self.__workspaces.index(o)

    def __set_workspace(self, o):
        self.__cur_workspace = o
        return self.__get_workspace_index()

    def __get_next_workspace(self):
        assert len(self)
        i = self.__get_workspace_index()
        if i >= len(self) - 1:
            return self.__workspaces[0]
        else:
            return self.__workspaces[i + 1]

    def __get_prev_workspace(self):
        assert len(self)
        i = self.__get_workspace_index()
        if i <= 0:
            return self.__workspaces[len(self) - 1]
        else:
            return self.__workspaces[i - 1]

    def read(self, x, n):
        return self.__cur_workspace.read(x, n)
    def read_current(self, n):
        return self.__cur_workspace.read_current(n)

    def insert(self, x, s, rec=True):
        self.__cur_workspace.insert(x, s, rec)
    def insert_current(self, s, rec=True):
        self.__cur_workspace.insert_current(s, rec)

    def replace(self, x, s, rec=True):
        self.__cur_workspace.replace(x, s, rec)
    def replace_current(self, s, rec=True):
        self.__cur_workspace.replace_current(s, rec)

    def delete(self, x, n, rec=True):
        self.__cur_workspace.delete(x, n, rec)
    def delete_current(self, n, rec=True):
        self.__cur_workspace.delete_current(n, rec)

    def resize(self):
        x = screen.get_size_x()
        screen.update_size()
        screen.refresh()
        if screen.get_size_x() != x:
            if self.is_gt_max_width():
                self.set_bytes_per_line("max")
            else:
                self.set_bytes_per_line("auto")
        console.resize()
        self.__clear_workspace_delta()
        self.refresh()

    def refresh(self):
        if self.build() == -1 and len(self) > 1:
            self.remove_other_workspace()

    def wbrepaint(self, focus):
        self.__cur_workspace.brepaint(focus)

    def repaint(self, low=False):
        for o in self.__workspaces:
            is_current = self.__cur_workspace is o
            o.repaint(is_current and len(self) > 1)
        if low:
            self.lrepaint(low)

    def lrepaint(self, low=False):
        for o in self.__workspaces:
            is_current = self.__cur_workspace is o
            o.lrepaint(is_current and low)

    def lrepaintf(self, low=False):
        f = self.get_path()
        for o in self.__workspaces:
            if o.get_path() == f:
                is_current = self.__cur_workspace is o
                o.lrepaint(is_current and low)

    def get_prev_context(self):
        return self.__prev_context

    def get_xprev_context(self):
        if self.__xprev_context:
            return self.__xprev_context
        else:
            return self.__prev_context

    def set_prev_context(self, fn, xfn=None):
        self.__prev_context = fn
        self.__xprev_context = xfn

    def buffer_input(self, l):
        self.__stream.extend(l)

    def __load_stream(self):
        f = setting.get_stream_path()
        if path.is_file(f):
            try:
                l = trace.read(f)
                if l:
                    self.buffer_input(l)
                else:
                    self.flash("Failed to read from " + f)
            except Exception:
                e = sys.exc_info()[1]
                self.flash(e)
        elif f:
            self.flash("Can not read from " + f)

    def __read_stream(self):
        if screen.test_signal():
            self.__stream.clear()
            self.flash("Interrupted")
            return kbd.ERROR
        elif len(self.__stream):
            return self.__stream.popleft()
        else:
            return None

    def set_uniq_mark(self, key, pos, f):
        for o in self.__fileobjs:
            if o.get_mark(key) is not None:
                o.delete_mark(key) # delete existing mark if any
        o = self.__get_buffer(f)
        if o:
            o.set_mark(key, pos)

    def get_uniq_mark(self, key):
        for o in self.__fileobjs:
            pos = o.get_mark(key)
            if pos != -1:
                return o.get_path(), pos
        return None, -1

    def get_records(self):
        return dict(self.__records)

    def start_record(self, k):
        assert k != ''
        self.__records_key = k
        self.__records[self.__records_key] = []

    def end_record(self):
        del self.__records[self.__records_key][-1] # remove last q
        self.__records_key = ''

    def add_record(self, x):
        self.__records[self.__records_key].append(x)
        self.show('') # to prevent from hiding banner
        return x

    def replay_record(self, k):
        assert k != ''
        if k in self.__records:
            self.__records['@'] = self.__records[k] # latest
            self.buffer_input(self.__records[k])
        elif k != '@':
            self.flash("'%s' not registered" % k)
        elif k == '@':
            self.flash("No previously used register")

    def start_read_delayed_input(self, x, term):
        assert not self.__delayed_input
        self.__delayed_input_term = term
        self.add_delayed_input(x)

    def end_read_delayed_input(self):
        l = [util.chr2(n) for n in self.__delayed_input[1:-1]]
        self.clear_delayed_input()
        return ''.join(l)

    def add_delayed_input(self, x):
        self.__delayed_input.append(x)
        l = [util.chr2(n) for n in self.__delayed_input]
        self.show(''.join(l))
        if x == self.__delayed_input_term:
            return self.__delayed_input_term
        elif not util.is_graph(x):
            self.clear_delayed_input()
            return x
        else:
            return kbd.ERROR

    def clear_delayed_input(self):
        self.__delayed_input = []
        self.show('')

    def init_yank_buffer(self, buf):
        self.__yank_buffer = [buf]
    def left_add_yank_buffer(self, buf):
        self.__yank_buffer.insert(0, buf)
    def right_add_yank_buffer(self, buf):
        self.__yank_buffer.append(buf)

    def get_yank_buffer_size(self):
        return sum([len(x) for x in self.__yank_buffer])
    def get_yank_buffer(self):
        return ''.join(self.__yank_buffer)

    def set_bytes_per_line(self, arg):
        ret = self.__cur_workspace.find_bytes_per_line(arg)
        if ret == -1:
            return -1
        for o in self.__workspaces:
            o.set_bytes_per_line(ret)
            assert o.get_bytes_per_line() == ret
