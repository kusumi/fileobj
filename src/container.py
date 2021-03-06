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
import collections
import os
import string

from . import allocator
from . import console
from . import extension
from . import fileattr
from . import filebytes
from . import fileops
from . import history
from . import kbd
from . import kernel
from . import literal
from . import log
from . import marks
from . import operand
from . import panel
from . import path
from . import screen
from . import setting
from . import trace
from . import util
from . import void
from . import window
from . import workspace

DEF_REG = '"'
MAX_LOG_N_BPL = 10

class Container (object):
    def __init__(self, backup_files=None):
        self.__getch_count = 0
        self.__baks = backup_files
        self.__bpw = -1
        self.__workspaces = []
        self.__workspace_delta = {}
        self.__fileobjs = []
        self.__consoles = {}
        self.__records = {}
        self.__records_key = ''
        self.__register = DEF_REG
        self.__init_yank_buffer()
        self.__delayed_input_beg_key = None
        self.__delayed_input = []
        self.__prev_delayed_buf = ""
        self.__prev_delayed_key = kbd.ERROR
        self.__stream = collections.deque()
        self.__history = history.History(None,
            literal.get_slow_strings() + (literal.bracket2_beg.str,))
        self.__operand = operand.Operand(self.__history)
        self.__marks = marks.Marks(setting.get_marks_path())
        self.__session = marks.Marks(setting.get_session_path())
        self.__cur_workspace = None
        self.__in_vertical = False
        self.__in_random = False
        self.__is_max_bpl = False
        self.set_prev_context(None)

    def __getattr__(self, name):
        if name == "_Container__cur_workspace":
            raise AttributeError(name)
        return getattr(self.__cur_workspace, name)

    def __len__(self):
        return len(self.__workspaces)

    def init(self, args, wspnum, vertical, optbpl, optbpw):
        assert not self.__fileobjs
        for x in args:
            o = self.__alloc_buffer(x)
            if o:
                self.__fileobjs.append(o)
        if not self.__fileobjs:
            self.__fileobjs.append(self.__alloc_buffer(''))
        assert self.__fileobjs[0] is not None
        self.update_address_num_width() # after fileobj allocation

        bpl = self.__find_bytes_per_line(optbpl)
        if bpl == -1:
            log.debug("Found initial bpl = -1")
            return -1 # no space
        self.__workspaces.append(workspace.Workspace(bpl))
        wsp = self.__workspaces[0]
        self.__set_workspace(wsp)
        for i, o in enumerate(self.__fileobjs):
            self.__workspace_add_buffer(wsp, i, o, self.__get_console())

        # bytes_per_window must be set after the first workspace
        # is registered but before the next one is registered
        if self.set_bytes_per_window(optbpw) == -1:
            self.set_bytes_per_window("auto")

        self.__in_vertical = vertical # True if -O
        for i in util.get_xrange(1, wspnum):
            o = self.__cur_workspace.clone()
            o.switch_to_buffer(i % len(self.__fileobjs))
            self.__workspaces.append(o)
            if self.__build(self.__in_vertical, True) == workspace.BUILD_FAILED:
                self.__remove_workspace(o)
                break
        return self.build()

    def cleanup(self):
        self.__store_session() # must be before fileobj cleanup
        while self.__fileobjs:
            o = self.__fileobjs.pop()
            self.__store_ondisk_marks(o)
            o.cleanup()
        self.__marks.flush()
        self.__session.flush()
        self.__operand.cleanup()
        self.__history.flush()

    def dispatch(self):
        self.__load_stream()
        while True:
            if self.__cur_workspace.dispatch() == -1:
                break

    def getch(self):
        if len(self.__stream):
            x = self.__read_stream()
        else:
            x = console.getch()
        self.__getch_count += 1
        if self.__records_key:
            x = self.add_record(x)
        if self.__delayed_input:
            x = self.add_delayed_input(x)
        return x

    def flash(self, o=None):
        console.queue_flash(o)

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

    def __get_console(self, cls=None):
        if not cls:
            cls = console.get_default_class()
        if cls not in self.__consoles:
            self.__consoles[cls] = cls(self, self.__operand)
        return self.__consoles[cls]

    def disconnect_workspace(self):
        for o in self.__workspaces:
            o.disconnect_window()

    def reconnect_workspace(self):
        for o in self.__workspaces:
            o.reconnect_window()

    def __load_ondisk_marks(self, o):
        d = self.__marks.get(o.get_path())
        if d:
            o.set_marks(d)

    def __store_ondisk_marks(self, o):
        d = o.get_marks()
        self.__marks.set(o.get_path(), d)

    def __load_session(self, o):
        d = self.__session.get(o.get_path())
        if d:
            o.set_session(d)

    def __store_session(self, o=None):
        if not o:
            o = self.__cur_workspace
        if self.__set_session_position(o) != -1: # changed
            self.__session.set(o.get_path(), o.get_session())

    def __get_session_position(self, o):
        if setting.use_session_position:
            ret = o.get_session_value('@')
            if ret == -1:
                return ret
            ret -= o.get_mapping_offset()
            if ret < 0:
                return -1
            return ret
        else:
            return -1

    def __set_session_position(self, o):
        if setting.use_session_position:
            pos = o.get_mapping_offset() + o.get_pos()
            if pos > o.get_max_pos():
                return -1
            return o.set_session_value('@', pos)
        else:
            return -1

    def __alloc_buffer(self, f, reload=False):
        if not self.has_buffer(f):
            o = self.alloc_fileobj(f)
            if o:
                if not reload: # NOT reloading
                    self.__load_ondisk_marks(o)
                return o
            if not self.has_buffer(''):
                return self.alloc_fileobj('') # never fail

    def alloc_fileobj(self, f):
        try:
            o = allocator.alloc(f)
            f = o.get_path()
            if setting.use_debug and os.path.exists(f):
                try:
                    log.debug("{0} {1} {2}".format(repr(o), f, os.stat(f)))
                except Exception as e:
                    log.debug("{0} {1} {2}".format(repr(o), f, repr(e)))
            if self.__baks is not None and f not in self.__baks:
                bak = util.creat_backup(f, util.get_timestamp())
                if bak:
                    self.__baks[f] = bak
            return o
        except allocator.Error as e:
            self.flash(e)

    def add_buffer(self, f, reload=False):
        # add buffer and make current workspace focus that
        if self.__in_random:
            self.__raise_random_stream("Add {0}".format(f))
        if not self.has_buffer(f):
            o = self.__alloc_buffer(f, reload)
            if o:
                return self.__add_buffer(o, self.__get_console())
        else:
            self.__cur_workspace.switch_to_buffer(self.__get_buffer_index(f))

    def add_extension(self, fn, args):
        try:
            args.append(self.get_pos())
            fo = self.__get_buffer(self.get_path())
            ret = fn(self, fileops.Fileops(fo), args)
            if util.is_seq(ret):
                ret = '\n'.join(ret)
        except extension.Error as e:
            ret = util.e_to_string(e)

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
            self.__workspace_add_buffer(wsp, i, o, con)
        self.__cur_workspace.switch_to_buffer(i)
        return o.get_path()

    def __workspace_add_buffer(self, wsp, i, o, con):
        fop = fileops.Fileops(o)
        self.__load_session(o)
        pos = self.__get_session_position(o)
        if pos != -1:
            fop.set_pos(pos)
            cur_pos = fop.get_pos()
            if cur_pos != pos:
                self.flash("Failed to locate at {0}:{1}".format(
                    path.get_short_path(fop.get_path()), pos))
        wsp.add_buffer(i, fop, con)

    def remove_buffer(self, f, reload=False):
        o = self.__get_buffer(f)
        if o:
            self.__store_session()
            for wsp in self.__workspaces:
                wsp.remove_buffer(self.__fileobjs.index(o))
            if reload:
                fileattr.stash_save(f) # before cleanup
            o.cleanup()
            self.__fileobjs.remove(o)
            if reload:
                fileattr.stash_restore(f) # before allocation
                ff = self.add_buffer(f)
                assert ff == f, (ff, f)
            if not self.__fileobjs:
                self.add_buffer('')
        else:
            return -1

    def switch_to_buffer(self, f):
        self.__store_session()
        i = self.__get_buffer_index(f)
        if i != -1:
            self.__cur_workspace.switch_to_buffer(i)
        else:
            return -1

    def switch_to_first_buffer(self):
        self.__store_session()
        self.__cur_workspace.switch_to_first_buffer()

    def switch_to_last_buffer(self):
        self.__store_session()
        self.__cur_workspace.switch_to_last_buffer()

    def switch_to_next_buffer(self):
        self.__store_session()
        self.__cur_workspace.switch_to_next_buffer()

    def switch_to_prev_buffer(self):
        self.__store_session()
        self.__cur_workspace.switch_to_prev_buffer()

    def reload_buffer(self, new):
        return self.__reload_buffer(self.get_path(), new)

    def __reload_buffer(self, old, new):
        if not self.has_buffer(old):
            return -1
        if old == new:
            self.__assert_attr_key(new)
            self.remove_buffer(old, reload=True)
        else:
            self.__assert_attr_key(new)
            f = self.add_buffer(new, reload=True)
            if f != new:
                if f is not None:
                    self.remove_buffer(f)
                return -1
            self.remove_buffer(old)
            assert not self.has_buffer(old), old
        assert self.get_path() == new, new

    def __assert_attr_key(self, f):
        # should have been renamed already or using the same name
        if util.is_running_script_fileobj() or util.is_running_script_perf():
            assert fileattr.has_key(f), fileattr.get_keys()

    def __get_buffer(self, f, cond=None):
        i = self.__get_buffer_index(f, cond)
        if i != -1:
            return self.__fileobjs[i]

    def __get_buffer_index(self, f, cond=None):
        f = kernel.parse_file_path(f)[0] # drop offset/length
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

    def get_build_size(self):
        l = []
        for o in self.__workspaces:
            l.append(o.get_build_size())
        return tuple(l)

    def build(self, vertical=-1):
        return self._build(False, vertical)

    def build_quiet(self, vertical=-1):
        return self._build(True, vertical)

    def _build(self, quiet, vertical):
        if not len(self): # nothing to do
            return
        if vertical == -1:
            vertical = self.__in_vertical
        assert isinstance(vertical, bool)

        if self.__build(vertical, True) == workspace.BUILD_FAILED:
            self.__clear_workspace_delta()
            if self.__build(vertical, True) == workspace.BUILD_FAILED:
                if not quiet:
                    self.flash("Not enough room")
                return -1
        if setting.use_even_size_window or self.__bpw != -1 or vertical:
            screen.clear_refresh()
        if self.__build(vertical, False) == workspace.BUILD_FAILED:
            return -1
        # Update vertical flag after successful build,
        # if explicitly specified or len(self) is 1.
        if len(self) == 1:
            self.__in_vertical = False
        elif vertical:
            self.__in_vertical = True

    def __build(self, vertical, dry):
        if self.__bpw == -1:
            if not vertical:
                return self.__build_workspace(dry)
            else:
                return self.__vbuild_workspace(dry)
        else:
            if not vertical:
                return self.__build_workspace_fixed_size(dry)
            else:
                return self.__vbuild_workspace_fixed_size(dry)

    def __build_workspace(self, dry):
        l = console.get_position_y()
        if setting.use_even_size_window:
            h = l // len(self)
            y = 0
            for o in self.__workspaces:
                ret = self.__do_build_workspace(o, h, y, dry)
                if ret == workspace.BUILD_FAILED:
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
                ret = self.__do_build_workspace(o, h, y, dry)
                if ret == workspace.BUILD_FAILED:
                    return ret
                y += h

    def __do_build_workspace(self, wsp, hei, beg, dry):
        if wsp in self.__workspace_delta:
            hei += self.__workspace_delta[wsp][0]
            beg += self.__workspace_delta[wsp][1]
        if dry:
            return wsp.build_dryrun(hei, beg)
        else:
            return wsp.build(hei, beg)

    def __vbuild_workspace(self, dry):
        while True:
            ret = self.__do_vbuild_workspace(dry)
            if ret == workspace.BUILD_RETRY:
                continue
            else:
                return ret

    def __do_vbuild_workspace(self, dry):
        if dry:
            self.__vbuild_assert_width()
        x = 0
        for o in self.__workspaces:
            if dry:
                ret = o.vbuild_dryrun(x)
            else:
                ret = o.vbuild(x)
            if ret == workspace.BUILD_FAILED:
                # shrink bpl if unable to build with the current bpl
                bpl = self.get_bytes_per_line()
                if bpl < 1:
                    return ret
                else:
                    bpl //= 2 # this is good (not bpu)
                    if bpl < 1:
                        return ret
                    # keep the original value which gets updated in below
                    is_max_bpl = self.__is_max_bpl
                    # window.get_max_bytes_per_line() may fail on resize
                    if self.set_bytes_per_line_in_vertical(bpl, True) == -1:
                        self.__is_max_bpl = is_max_bpl
                        return ret
                    self.__is_max_bpl = is_max_bpl
                    return workspace.BUILD_RETRY
            x += o.guess_width()

    def __build_workspace_fixed_size(self, dry):
        lpw = self.get_lines_per_window()
        y = 0
        for o in self.__workspaces:
            if dry:
                ret = o.build_fixed_size_dryrun(lpw, y)
            else:
                ret = o.build_fixed_size(lpw, y)
            if ret == workspace.BUILD_FAILED:
                return ret
            y += ret

    def __vbuild_workspace_fixed_size(self, dry):
        if dry:
            self.__vbuild_assert_width()
        lpw = self.get_lines_per_window()
        x = 0
        for o in self.__workspaces:
            if dry:
                ret = o.vbuild_fixed_size_dryrun(lpw, x)
            else:
                ret = o.vbuild_fixed_size(lpw, x)
            if ret == workspace.BUILD_FAILED:
                return ret
            x += o.guess_width()

    def __vbuild_assert_width(self):
        prev = -1
        for o in self.__workspaces:
            width = o.guess_width()
            if prev != -1:
                assert width == prev, (width, prev)
            prev = width

    def adjust_workspace(self, n):
        if self.__bpw != -1:
            return self.get_bytes_per_window()
        if len(self) == 1 or not n:
            return -1
        current = self.__cur_workspace
        if current == self.__workspaces[0]: # first
            if self.__adjust_workspace_downward(current, n) == -1:
                return -1
        elif current == self.__workspaces[-1]: # last
            if self.__adjust_workspace_upward(current, n) == -1:
                return -1
        elif setting.use_downward_window_adjust:
            if self.__adjust_workspace_downward(current, n) == -1:
                return -1
        else:
            if self.__adjust_workspace_upward(current, n) == -1:
                return -1
        self.build()

    def __adjust_workspace_downward(self, o, n):
        next = self.__get_next_workspace(o)
        if n > 0:
            while self.__add_workspace_delta(next, -n, n) == -1:
                n -= 1
                if n == 0:
                    return -1
            self.__add_workspace_delta(o, n, 0)
        else:
            while self.__add_workspace_delta(o, n, 0) == -1:
                n += 1
                if n == 0:
                    return -1
            self.__add_workspace_delta(next, -n, n)

    def __adjust_workspace_upward(self, o, n):
        prev = self.__get_prev_workspace(o)
        if n > 0:
            while self.__add_workspace_delta(prev, -n, 0) == -1:
                n -= 1
                if n == 0:
                    return -1
            self.__add_workspace_delta(o, n, -n)
        else:
            while self.__add_workspace_delta(o, n, -n) == -1:
                n += 1
                if n == 0:
                    return -1
            self.__add_workspace_delta(prev, -n, 0)

    def __add_workspace_delta(self, wsp, h, b):
        if self.__in_vertical:
            return -1
        if wsp.build_dryrun_delta(h, b) == workspace.BUILD_FAILED:
            self.flash("Not enough room for delta")
            return -1
        if wsp in self.__workspace_delta:
            self.__workspace_delta[wsp][0] += h
            self.__workspace_delta[wsp][1] += b
        else:
            self.__workspace_delta[wsp] = [h, b]

    def __clear_workspace_delta(self):
        if self.__in_vertical:
            assert not self.__workspace_delta, self.__workspace_delta
        else:
            self.__workspace_delta.clear()

    def add_workspace(self, vertical):
        if len(self) > 1:
            if vertical:
                if not self.__in_vertical:
                    self.flash("Already splitted horizontally, can't mix both")
                    return -1
            else:
                if self.__in_vertical:
                    self.flash("Already splitted vertically, can't mix both")
                    return -1
        i = self.__get_buffer_index(self.get_path())
        cur_workspace = self.__cur_workspace
        new_workspace = self.__cur_workspace.clone()
        self.__clear_workspace_delta()
        self.__workspaces.insert(self.__workspaces.index(cur_workspace),
            new_workspace)
        self.__set_workspace(new_workspace)
        if self.build(vertical) != -1:
            new_workspace.switch_to_buffer(i)
            return self.__get_workspace_index()
        else:
            self.__remove_workspace(new_workspace)
            self.__set_workspace(cur_workspace)
            return -1

    def remove_workspace(self):
        if len(self) > 1:
            self.__store_session()
            o = self.__cur_workspace
            if self.__workspaces.index(o) == len(self) - 1:
                self.switch_to_prev_workspace()
            else:
                self.switch_to_next_workspace()
            self.__remove_workspace(o)
            if self.__in_vertical:
                if self.__is_max_bpl:
                    self.set_bytes_per_line("max")
                else:
                    self.set_bytes_per_line("auto")
            self.build()
            return self.__get_workspace_index()
        else:
            self.flash()
            return -1

    def remove_other_workspace(self):
        if len(self) > 1:
            l = [o for o in self.__workspaces if o is not self.__cur_workspace]
            for o in l:
                self.__store_session(o)
                self.__remove_workspace(o)
            assert len(self) == 1
            self.__set_workspace(self.__workspaces[0])
            if self.__in_vertical:
                if self.__is_max_bpl:
                    self.set_bytes_per_line("max")
                else:
                    self.set_bytes_per_line("auto")
            self.build()
            return self.__get_workspace_index()
        else:
            self.flash()
            return -1

    def __remove_workspace(self, o):
        self.__clear_workspace_delta()
        self.__workspaces.remove(o)

    def switch_to_next_workspace(self):
        return self.__set_workspace(self.__get_next_workspace())

    def switch_to_prev_workspace(self):
        return self.__set_workspace(self.__get_prev_workspace())

    def switch_to_top_workspace(self):
        return self.__set_workspace(self.__workspaces[0])

    def switch_to_bottom_workspace(self):
        return self.__set_workspace(self.__workspaces[len(self) - 1])

    def switch_to_geom_workspace(self, y, x):
        for o in self.__workspaces:
            if o.has_geom(y, x):
                if o is self.__cur_workspace:
                    return # already at the workspace
                else:
                    return self.__set_workspace(o)
        return -1

    def is_geom_valid(self, y, x):
        for o in self.__workspaces:
            if o.has_geom(y, x):
                return True
        return False

    def has_geom(self, y, x):
        return self.__cur_workspace.has_geom(y, x)

    def get_geom_pos(self, y, x):
        return self.__cur_workspace.get_geom_pos(y, x)

    def __get_workspace_index(self, o=None):
        if not o:
            o = self.__cur_workspace
        return self.__workspaces.index(o)

    def __set_workspace(self, o):
        self.__cur_workspace = o
        return self.__get_workspace_index()

    def __get_next_workspace(self, o=None):
        assert len(self)
        i = self.__get_workspace_index(o)
        if i >= len(self) - 1:
            return self.__workspaces[0]
        else:
            return self.__workspaces[i + 1]

    def __get_prev_workspace(self, o=None):
        assert len(self)
        i = self.__get_workspace_index(o)
        if i <= 0:
            return self.__workspaces[len(self) - 1]
        else:
            return self.__workspaces[i - 1]

    def flush(self, f=None):
        if self.__in_random:
            self.__raise_random_stream("Flush {0}".format(f))
        return self.__cur_workspace.flush(f)

    def init_buffer(self, b):
        return self.__cur_workspace.init_buffer(b)

    def read(self, x, n):
        return self.__cur_workspace.read(x, n)

    def read_current(self, n):
        return self.__cur_workspace.read_current(n)

    def insert(self, x, l, rec=True):
        self.__cur_workspace.insert(x, l, rec)

    def insert_current(self, l, rec=True):
        self.__cur_workspace.insert_current(l, rec)

    def replace(self, x, l, rec=True):
        self.__cur_workspace.replace(x, l, rec)

    def replace_current(self, l, rec=True):
        self.__cur_workspace.replace_current(l, rec)

    def delete(self, x, n, rec=True):
        self.__cur_workspace.delete(x, n, rec)

    def delete_current(self, n, rec=True):
        self.__cur_workspace.delete_current(n, rec)

    def resize(self):
        screen.set_soft_resize()
        self.__resize()
        screen.clear_soft_resize()

    def __resize(self):
        x = screen.get_size_x()
        screen.update_size()
        screen.clear_refresh()
        if screen.get_size_x() != x:
            width = self.get_width()
            if self.__in_vertical: # multiply by number of wsp
                width *= len(self)
            if width > screen.get_size_x():
                self.set_bytes_per_line("max")
            else:
                self.set_bytes_per_line("auto")
        console.resize()
        self.__clear_workspace_delta()
        self.refresh()

    def refresh(self):
        if self.build() == -1 and len(self) > 1:
            self.remove_other_workspace()

    # set or unuset focus against current workspace
    def set_focus(self, x):
        assert isinstance(x, bool)
        self.__cur_workspace.set_focus(x)
        screen.doupdate()

    def require_full_repaint(self):
        self.__cur_workspace.require_full_repaint()

    # regular repaint
    # XXX Under certain condition, scr.noutrefresh() seems to actually clear a
    # screen prior to calling screen.doupdate(), and this causes canvas repaint
    # to leave posstr part that was cleared by frame repaint. To avoid this,
    # always require full repaint, or otherwise stop conditional canvas repaint
    # entirely. See DisplayCanvas.__fill_pre().
    # https://docs.python.org/3/library/curses.html#curses.window.noutrefresh
    def repaint(self, low=False):
        for o in self.__workspaces:
            o.require_full_repaint()
            o.repaint(self.__cur_workspace is o)
        if low:
            self.lrepaint(low)
        screen.doupdate()

    # light weight repaint (no frame repaint)
    def lrepaint(self, low=False):
        for o in self.__workspaces:
            is_current = self.__cur_workspace is o
            o.lrepaint(is_current, is_current and low)
        screen.doupdate()

    # lrepaint against workspace with same current buffer
    def lrepaintf(self, low=False):
        f = self.get_path()
        for o in self.__workspaces:
            if o.get_path() == f:
                is_current = self.__cur_workspace is o
                o.lrepaint(is_current, is_current and low)
        screen.doupdate()

    # partial repaint (no frame repaint)
    def prepaint(self, num, low=False):
        for o in self.__workspaces:
            is_current = self.__cur_workspace is o
            o.prepaint(is_current, is_current and low, num)
        screen.doupdate()

    # partial repaint against workspace with same current buffer
    def prepaintf(self, num, low=False):
        f = self.get_path()
        for o in self.__workspaces:
            if o.get_path() == f:
                is_current = self.__cur_workspace is o
                o.prepaint(is_current, is_current and low, num)
        screen.doupdate()

    # frame repaint
    def xrepaint(self):
        for o in self.__workspaces:
            o.xrepaint(self.__cur_workspace is o)
        screen.doupdate()

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

    def queue_input(self, l):
        self.__stream.extend(l)
        log.debug("queue_input: {0} entries".format(len(l)))
        if len(l) <= 1024:
            log.debug(tuple(zip(l, tuple(screen.chr_repr[_] if _ in
                screen.chr_repr else '.' for _ in l))))

    def push_input(self, l):
        self.__stream.extendleft(l)
        log.debug("push_input: {0} entries".format(len(l)))
        if len(l) <= 1024:
            log.debug(tuple(zip(l, tuple(screen.chr_repr[_] if _ in
                screen.chr_repr else '.' for _ in l))))

    def pop_input(self, n):
        for _ in util.get_xrange(n):
            x = self.__stream.popleft()
            log.debug("pop_input {0}".format(x))

    def __raise_random_stream(self, s):
        log.warning(s)
        raise KeyboardInterrupt(s) # not derived from Exception

    def __load_stream(self):
        f = setting.get_stream_path()
        if f.endswith("rand.bin"):
            self.__in_random = True
            log.warning("Random stream {0}".format(f))
        if os.path.isfile(f):
            try:
                l = trace.read(f)
                if l:
                    self.queue_input(l)
                else:
                    self.flash("Failed to read " + f)
            except Exception as e:
                self.flash(e)
        elif f:
            self.flash("Can not read " + f)

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

    def get_registers(self):
        d = {}
        for reg, l in self.__yank_buffer.items():
            d[reg] = filebytes.join(l)
        return d

    def start_register(self, k):
        assert k != ''
        self.__register = k

    def clear_register(self):
        self.__register = DEF_REG

    def get_records(self):
        return dict(self.__records)

    def start_record(self, k):
        assert k != ''
        self.__records_key = k
        self.__records[self.__records_key] = []

    def end_record(self):
        del self.__records[self.__records_key][-1] # remove last q
        if not len(self.__records[self.__records_key]):
            del self.__records[self.__records_key]
        self.__records_key = ''

    def add_record(self, x):
        self.__records[self.__records_key].append(x)
        self.show('') # to prevent from hiding banner
        return x

    def replay_record(self, k):
        assert k != ''
        if k in self.__records:
            self.__records['@'] = self.__records[k] # latest
            self.queue_input(self.__records[k])
        elif k != '@':
            self.flash("'{0}' not registered".format(k))
        elif k == '@':
            self.flash("No previously used register")

    def start_read_delayed_input(self, x, term):
        assert not self.__delayed_input
        assert x is not None, x
        self.__delayed_input_beg_key = x
        self.__delayed_input_beg_str = chr(x)
        self.__delayed_input_end_key = term
        self.__delayed_input_end_str = chr(term)
        self.add_delayed_input(x)

    def end_read_delayed_input(self):
        s = self.__delayed_input_string()
        self.__add_delayed_input_history()
        return s[1:-1] # drop brackets

    def add_delayed_input(self, x):
        # XXX Heuristics to ignore below after certain inputs.
        # Initially pressing a cursor key reads 3 inputs starting "\x1b".
        # Note that there's also heuristic based ignore duration set in
        # methods.start_read_delayed_input() before reaches here.
        if self.__getch_count <= 6:
            # Ignore a subset of ANSI sequences to avoid being stucked
            # initially on pressing a cursor key. These sequences aren't
            # useful for anything.
            s = self.__delayed_input_string()
            if s in ("[A", "[B", "[C", "[D",):
                self.clear_delayed_input()
                self.flash()
                return self.__delayed_input_end_key

        # scan and update prev input first
        if self.__prev_delayed_key not in _arrows and x in _arrows:
            self.__prev_delayed_buf = self.__delayed_input_string()
        elif self.__prev_delayed_key in _arrows and x not in _arrows:
            self.__prev_delayed_buf = ""
        self.__assert_delayed_input(self.__prev_delayed_buf)
        self.__prev_delayed_key = x

        if util.isprint(x):
            self.__delayed_input.append(x)
            self.__reset_delayed_input_cursor()
        elif x == kbd.ESCAPE:
            self.__add_delayed_input_history()
            self.__reset_delayed_input_cursor()
        elif x == kbd.RESIZE:
            self.clear_delayed_input()
            return x # no need to do rest
        elif x == kbd.ENTER:
            x = self.__delayed_input_end_key
            self.__delayed_input.append(x)
            self.__reset_delayed_input_cursor()
        elif x in kbd.get_backspaces():
            if len(self.__delayed_input) > 1:
                self.__delayed_input.pop()
            else:
                self.clear_delayed_input()
            self.__reset_delayed_input_cursor()
        elif x in _up:
            # taken from Operand.__get_older_history()
            b = self.__prev_delayed_buf
            assert b, b
            # XXX this doesn't work properly with TERM=vt*00 ???
            s = self.__history.get_older(b[0], b)
            if not s:
                s = self.__history.get_newer(b[0], b)
                if not s:
                    s = b
            assert s[0] == b[0], (s, b)
            self.__delayed_input = [ord(_) for _ in s]
        elif x in _down:
            # taken from Operand.__get_newer_history()
            b = self.__prev_delayed_buf
            assert b, b
            # XXX this doesn't work properly with TERM=vt*00 ???
            s = self.__history.get_newer(b[0], b)
            if not s:
                s = b
            assert s[0] == b[0], (s, b)
            self.__delayed_input = [ord(_) for _ in s]
        elif x in (kbd.LEFT, kbd.RIGHT):
            self.flash()

        self.show(self.__delayed_input_string())
        if x == self.__delayed_input_end_key:
            return x
        else:
            return kbd.ERROR

    def clear_delayed_input(self):
        self.__delayed_input = []
        self.__prev_delayed_buf = ""
        self.__prev_delayed_key = kbd.ERROR
        self.__reset_delayed_input_cursor()
        self.show('')

    def __delayed_input_string(self):
        return ''.join([chr(i) for i in self.__delayed_input])

    def __add_delayed_input_history(self):
        s = self.__delayed_input_string()
        if not s:
            self.clear_delayed_input()
            return
        key = s[0]
        assert key == self.__delayed_input_beg_str, s
        if s[-1] == self.__delayed_input_end_str:
            value = s[:-1]
        else:
            value = s
        if value != key:
            if self.__history.get_latest(key) != value:
                self.__history.append(key, value)
        self.clear_delayed_input()

    def __reset_delayed_input_cursor(self):
        # methods.escape() may call this without having been in delayed input
        if self.__delayed_input_beg_key is not None:
            self.__history.reset_cursor(self.__delayed_input_beg_str)

    def __assert_delayed_input(self, s):
        assert isinstance(s, str), (s, type(s))
        if s:
            assert s[0] == self.__delayed_input_beg_str, s
            assert s[-1] != self.__delayed_input_end_str, s

    def __init_yank_buffer(self):
        self.__yank_buffer = {}
        self.__yank_buffer[DEF_REG] = []
        for s in string.digits:
            self.__yank_buffer[s] = []
        for s in string.ascii_lowercase:
            self.__yank_buffer[s] = []

    def __rotate_delete_buffer(self):
        for x in util.get_xrange(9, 1, -1): # 9 to 2
            dst = str(x)
            src = str(x - 1)
            self.__yank_buffer[dst] = self.__yank_buffer[src]
        self.__yank_buffer['1'] = []

    def set_yank_buffer(self, buf):
        assert isinstance(buf, filebytes.TYPE)
        l = self.__set_yank_buffer(buf, -1)
        # these two must be in a set
        self.__yank_buffer[DEF_REG] = l
        self.__yank_buffer['0'] = l

    def set_delete_buffer(self, buf, add_right=True):
        assert isinstance(buf, filebytes.TYPE)
        self.__rotate_delete_buffer()
        l = self.__set_yank_buffer(buf, add_right)
        # these two must be in a set
        self.__yank_buffer[DEF_REG] = l
        self.__yank_buffer['1'] = l

    def __set_yank_buffer(self, buf, add_right):
        l = [buf]
        if not self.__register.isupper():
            self.__yank_buffer[self.__register] = l
        else: # append for upper case
            if add_right == -1:
                self.__add_yank_buffer(buf)
            elif add_right is True:
                self.right_add_delete_buffer(buf)
            else:
                self.left_add_delete_buffer(buf)
        return l

    def __add_yank_buffer(self, buf):
        assert isinstance(buf, filebytes.TYPE)
        l = self.__scan_yank_buffer()
        l.append(buf)
        # don't touch register['1']

    def left_add_delete_buffer(self, buf):
        assert isinstance(buf, filebytes.TYPE)
        l = self.__scan_yank_buffer()
        l.insert(0, buf)
        _ = self.__yank_buffer['1']
        if _ != l:
            _.insert(0, buf)

    def right_add_delete_buffer(self, buf):
        assert isinstance(buf, filebytes.TYPE)
        l = self.__scan_yank_buffer()
        l.append(buf)
        _ = self.__yank_buffer['1']
        if _ != l:
            _.append(buf)

    def __scan_yank_buffer(self):
        if not self.__register.isupper():
            l = self.__yank_buffer[self.__register]
        else: # append for upper case
            reg = self.__register.lower()
            if reg in self.__yank_buffer:
                l = [x for x in self.__yank_buffer[reg]]
            else:
                l = []
            self.__yank_buffer[reg] = l
        return l

    def get_yank_buffer_size(self, reg=None):
        if reg is None:
            reg = self.__register
        if reg in self.__yank_buffer:
            return sum(len(x) for x in self.__yank_buffer[reg])
        else:
            return 0

    def get_yank_buffer(self, reg=None):
        if reg is None:
            reg = self.__register
        if reg in self.__yank_buffer:
            return filebytes.join(self.__yank_buffer[reg])
        else:
            return filebytes.BLANK

    def set_address_num_width(self, width):
        assert width >= panel.get_min_address_num_width(), width
        orig = panel.address_num_width
        panel.address_num_width = width
        return orig

    def __set_address_num_double(self):
        # turn on double space if there is a partial buffer
        for o in self.__fileobjs:
            if o.get_mapping_offset():
                panel.address_num_double = True
                break
        else:
            panel.address_num_double = False

    def update_address_num_width(self):
        width = panel.address_num_width
        min_width = panel.get_min_address_num_width()
        assert width >= min_width, width
        self.__set_address_num_double()

        fmt = {
            16: "{0:X}",
            10: "{0:d}",
            8 : "{0:o}",
        }.get(setting.address_radix)
        n = max([o.get_size() for o in self.__fileobjs])
        if n > 0:
            n -= 1
        s = fmt.format(n)

        l = [2 * i for i in util.get_xrange(100)] # max 200 (large enough)
        l = [x for x in l if x >= min_width]

        if len(s) > width:
            for x in l:
                if x > len(s):
                    return self.set_address_num_width(x)
        elif width > len(s) >= min_width:
            l = tuple(reversed(l))
            for x in l:
                if len(s) > x:
                    i = l.index(x)
                    if i:
                        i -= 1
                    x = l[i]
                    return self.set_address_num_width(x)
            return self.set_address_num_width(l[-1])
        elif min_width > len(s):
            return self.set_address_num_width(min_width)
        else:
            assert len(s) == width, (s, len(s), width)
        return -1

    # use this during vbuild, when the flag is potentially false
    def set_bytes_per_line_in_vertical(self, arg, power_of_bpu=False):
        try:
            v = self.__in_vertical
            self.__in_vertical = True # to calculate correct max bpl
            return self.set_bytes_per_line(arg, power_of_bpu)
        finally:
            self.__in_vertical = v

    def set_bytes_per_line(self, arg, power_of_bpu=False):
        ret = self.__find_bytes_per_line(arg)
        if ret == -1:
            return -1
        # adjust down to max power of bpu
        if power_of_bpu:
            unitlen = setting.bytes_per_unit
            if unitlen == 1:
                unitlen = 2
            for bpl in [unitlen ** x for x in util.get_xrange(MAX_LOG_N_BPL)]:
                if ret <= bpl:
                    if ret == bpl: # already power of bpu
                        ret = bpl
                    else:
                        ret = bpl // unitlen
                    if ret < 1:
                        ret = 1
                    break
        # bpl determined by vbuild retry may not be multiple of bpu
        unitlen = setting.bytes_per_unit
        ret = (ret // unitlen) * unitlen
        if not ret:
            return -1
        # update bpl
        for o in self.__workspaces:
            assert o.set_bytes_per_line(ret) != -1
        # assert the result
        prev = -1
        for o in self.__workspaces:
            if prev != -1:
                bpl = o.get_bytes_per_line()
                assert bpl == prev, (bpl, prev)
                prev = bpl

    def __find_bytes_per_line(self, arg):
        ret = self.__do_find_bytes_per_line(arg)
        unitlen = setting.bytes_per_unit
        if ret != -1 and unitlen > ret: # never allow bpu > bpl
            log.warning("bpu > bpl not allowed, using {0}".format(unitlen))
            return unitlen
        else:
            return ret

    def __do_find_bytes_per_line(self, arg):
        self.__is_max_bpl = False # reset
        if self.__in_vertical:
            n = len(self)
        else:
            n = 1
        max_bpl = window.get_max_bytes_per_line(n)
        if setting.bytes_per_unit > max_bpl or max_bpl < 1:
            return -1
        if not arg:
            arg = "auto"
        if arg == "min":
            return 1
        elif arg == "max":
            self.__is_max_bpl = True
            return max_bpl
        elif arg == "auto":
            unitlen = setting.bytes_per_unit
            if unitlen == 1:
                unitlen = 2
            range_max_log_bpl = util.get_xrange(MAX_LOG_N_BPL)
            for ret in reversed([unitlen ** x for x in range_max_log_bpl]):
                if ret <= max_bpl:
                    return ret
            return 1
        else:
            try:
                ret = int(arg)
                if ret >= max_bpl:
                    return max_bpl
                elif ret <= 1:
                    return 1
                else:
                    unitlen = setting.bytes_per_unit
                    ret = (ret // unitlen) * unitlen
                    # redo the test
                    if ret >= max_bpl: # never true
                        return max_bpl
                    elif ret <= 1:
                        return 1
                    return ret
            except ValueError:
                return -1

    def test_and_set_max_bytes_per_line(self):
        if self.__in_vertical and self.__is_max_bpl:
            return self.set_bytes_per_line("max")
        else:
            return -1

    def get_lines_per_window(self):
        if self.__bpw == -1:
            return -1
        bpl = self.get_bytes_per_line()
        return (self.__bpw + bpl - 1) // bpl

    # use Workspace.get_capacity() to get actual capacity
    def get_bytes_per_window(self):
        if self.__bpw == -1:
            return -1
        bpl = self.get_bytes_per_line()
        lpw = self.get_lines_per_window()
        return bpl * lpw

    def set_bytes_per_window(self, arg):
        ret = self.__find_bytes_per_window(arg)
        if ret is None: # auto or even
            return
        if ret == -1:
            return -1
        prev = self.__bpw
        self.__bpw = ret

        # shrink bpl if bpw < bpl
        if self.__bpw < self.__cur_workspace.get_bytes_per_line():
            prev_bpl = self.get_bytes_per_line()
            if self.set_bytes_per_line(self.__bpw) != -1:
                return
            else:
                assert self.set_bytes_per_line(prev_bpl) != -1, prev_bpl
                self.__bpw = prev

        if self.__build(self.__in_vertical, True) == workspace.BUILD_FAILED:
            # expand bpl if possible and retry
            prev_bpl = self.get_bytes_per_line()
            unitlen = setting.bytes_per_unit
            if unitlen == 1:
                unitlen = 2
            bpl_degen = -1
            # path1
            range_max_log_bpl = util.get_xrange(MAX_LOG_N_BPL)
            for bpl in [unitlen ** x for x in range_max_log_bpl]:
                if bpl < prev_bpl:
                    continue
                if self.set_bytes_per_line(bpl) != -1:
                    bpl_degen_enabled = True # XXX
                    if bpl_degen_enabled and self.get_bytes_per_line() < bpl:
                        bpl_degen = bpl
                        break # bpl didn't make unitlen**x, goto path2
                    elif ret <= self.get_bytes_per_window() and \
                        self.__build(self.__in_vertical, True) is None:
                        return
                # could rollback bpl here for extra safety
            # if bpl_degen is set, start path2
            if bpl_degen != -1:
                range_max_log_bpl = util.get_xrange(MAX_LOG_N_BPL)
                for bpl in [unitlen ** x for x in range_max_log_bpl]:
                    if bpl >= bpl_degen:
                        break # bpl_degen or above won't make unitlen**x
                    if self.set_bytes_per_line(bpl) != -1:
                        # this will likely not match given path1 result
                        if self.get_bytes_per_line() == bpl and \
                            ret <= self.get_bytes_per_window() and \
                            self.__build(self.__in_vertical, True) is None:
                            return
                    # could rollback bpl here for extra safety
            # failed, rollback bpl and bpw
            assert self.set_bytes_per_line(prev_bpl) != -1, prev_bpl
            self.__bpw = prev
            return -1

    def __find_bytes_per_window(self, arg):
        if not arg:
            arg = "auto"
        if arg == "auto":
            self.__bpw = -1
            return
        elif arg == "even":
            setting.use_even_size_window = True
            return
        else:
            try:
                return int(arg)
            except ValueError:
                return -1

_arrows = kbd.UP, util.ctrl('p'), kbd.DOWN, util.ctrl('n')
_up = _arrows[:2]
_down = _arrows[2:]
