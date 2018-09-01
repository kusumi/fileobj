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

import argparse
import atexit
import os
import signal
import sys

from . import allocator
from . import console
from . import container
from . import env
from . import kbd
from . import kernel
from . import literal
from . import log
from . import methods
from . import package
from . import path
from . import screen
from . import setting
from . import usage
from . import util
from . import version

def __cleanup(arg):
    if arg.done:
        return -1
    if not arg.e:
        for f in arg.baks.values():
            try:
                os.unlink(f)
            except Exception as e:
                log.error(e)
    arg.done = True
    setting.cleanup()
    kernel.cleanup()
    console.cleanup(arg.e, arg.tb)
    screen.cleanup()
    literal.cleanup()
    __log_error(arg)
    __print_error(arg)
    log.debug("Cleanup")
    log.cleanup()

def __log_error(arg):
    if not arg.e:
        return -1
    log.error(arg.e)
    for s in arg.tb:
        log.error(s)

def __print_error(arg):
    if not arg.e:
        if log.has_error():
            util.printe("*** Found error in log")
        return -1
    util.printe(arg.e)
    if not isinstance(arg.e, util.QuietError):
        for s in arg.tb:
            util.printe(s)

def __sigint_handler(sig, frame):
    screen.sti()

def __sigterm_handler(sig, frame):
    sys.exit(1)

def __error(s):
    raise util.QuietError(s)

def dispatch(optargs=None):
    if setting.use_debug:
        suppress_help = str(None)
    else:
        suppress_help = argparse.SUPPRESS
    parser = argparse.ArgumentParser(usage=usage.help)

    parser.add_argument("-R", action="store_true", default=setting.use_readonly, help=usage.R)
    parser.add_argument("-B", action="store_true", default=setting.use_bytes_buffer, help=usage.B)
    parser.add_argument("-o", nargs="?", type=int, const=-1, metavar=usage.o_metavar, help=usage.o)
    parser.add_argument("-O", nargs="?", type=int, const=-1, metavar=usage.O_metavar, help=usage.O)
    parser.add_argument("--bytes_per_line", "--bpl", default=setting.bytes_per_line, metavar=usage.bytes_per_line_metavar, help=usage.bytes_per_line)
    parser.add_argument("--bytes_per_window", "--bpw", default=setting.bytes_per_window, metavar=usage.bytes_per_window_metavar, help=usage.bytes_per_window)
    parser.add_argument("--fg", default=setting.color_fg, metavar=usage.fg_metavar, help=usage.fg)
    parser.add_argument("--bg", default=setting.color_bg, metavar=usage.bg_metavar, help=usage.bg)
    parser.add_argument("--force", action="store_true", default=False, help=usage.force)
    parser.add_argument("--test_screen", action="store_true", default=False, help=usage.test_screen)
    parser.add_argument("--command", action="store_true", default=False, help=usage.command)
    parser.add_argument("--sitepkg", action="store_true", default=False, help=usage.sitepkg)
    parser.add_argument("--version", action="version", version=version.__version__)
    parser.add_argument("--debug", action="store_true", default=setting.use_debug, help=suppress_help)
    parser.add_argument("args", nargs="*", help=suppress_help) # optargs

    for s in allocator.iter_module_name():
        parser.add_argument("--" + s, action="store_true", default=False, help=suppress_help)

    if util.is_python_version_or_ht(3, 7):
        parse_args = parser.parse_intermixed_args
    else:
        parse_args = parser.parse_args
    opts = parse_args(optargs)
    args = opts.args
    if opts.debug:
        setting.use_debug = True

    if opts.command:
        literal.print_literal()
        return
    if opts.sitepkg:
        for x in package.get_paths():
            util.printf(x)
        return

    msg = [None, None]
    targs = util.Namespace(e=None, tb=[], done=False, baks={})
    atexit.register(__cleanup, targs)

    user_dir = setting.get_user_dir()
    ret = setting.init_user()
    if ret == setting.USER_DIR_NONE:
        msg[0] = "Not using user directory"
    elif ret == setting.USER_DIR_NO_READ:
        msg[0] = "Permission denied (read): {0}".format(user_dir)
    elif ret == setting.USER_DIR_NO_WRITE:
        msg[0] = "Permission denied (write): {0}".format(user_dir)
    elif ret == setting.USER_DIR_MKDIR_FAILED:
        msg[0] = "Failed to create user directory {0}".format(user_dir)

    log.init(util.get_program_name())

    log.debug("-" * 50)
    log.debug("{0} {1}".format(util.get_program_path(),
        version.get_tag_string()))
    log.debug("{0} {1}".format(util.get_python_string(), sys.executable))
    log.debug("UNAME {0} {1}".format(util.get_os_name(), util.get_os_release()))
    log.debug("CPU {0}".format(util.get_cpu_name()))
    log.debug("RAM {0}".format(methods.get_meminfo_string()))
    log.debug("TERM {0}".format(kernel.get_term_info()))
    log.debug("LANG {0}".format(kernel.get_lang_info()))
    log.debug(methods.get_osdep_string())
    log.debug("argv {0}".format(sys.argv))
    log.debug("opts {0}".format(opts))
    log.debug("args {0}".format(args))

    for s in allocator.iter_module_name():
        if getattr(opts, s, False):
            allocator.set_default_class(s)
    if opts.R:
        setting.use_readonly = True
    if opts.B:
        allocator.set_default_buffer_class()
    if opts.o is not None:
        if opts.o == -1:
            wspnum = len(args)
        else:
            wspnum = opts.o
    if opts.O is not None: # must be after opts.o test
        if opts.O == -1:
            wspnum = len(args)
        else:
            wspnum = opts.O
    else:
        wspnum = 1

    l = []
    for _ in env.iter_defined_env():
        l.append("{0}={1}".format(*_))
    for _ in env.iter_defined_ext_env():
        l.append("{0}={1}".format(*_))
    log.debug("envs {0}".format(l))

    l = []
    for _ in setting.iter_setting():
        l.append("{0}={1}".format(*_))
    log.debug("settings {0}".format(l))

    # log all error messages
    for s in msg:
        if s:
            log.error(s)

    signal.signal(signal.SIGINT, __sigint_handler)
    signal.signal(signal.SIGTERM, __sigterm_handler)

    try:
        co = None
        if not kernel.get_kernel_module():
            __error(kernel.get_status_string())

        assert literal.init() != -1

        # don't let go ncurses exception unless in debug
        try:
            if screen.init(opts.fg, opts.bg) == -1:
                __error("Failed to initialize terminal")
            assert console.init() != -1
            if opts.test_screen:
                test_screen()
                return # done
        except Exception as e:
            if setting.use_debug:
                raise
            else:
                __error(str(e))

        if opts.B:
            tot = 0
            for x in args:
                x = kernel.parse_file_path(x)[0] # drop offset/length
                o = path.Path(x)
                if o.is_reg:
                    siz = kernel.get_size(o.path)
                    if siz != -1:
                        tot += siz
            s1 = "Required memory {0}".format(util.get_size_repr(tot))
            s2 = "use --force option to continue"
            log.info(s1)
            free_ram = kernel.get_free_ram()
            if free_ram != -1 and not opts.force and tot > free_ram:
                __error("{0} exceeds free RAM size {1}, {2}".format(
                    s1, util.get_size_repr(free_ram), s2))
            if not opts.force and tot > setting.regfile_soft_limit:
                __error("{0} exceeds soft limit size {1}, {2}".format(
                    s1, util.get_size_repr(setting.regfile_soft_limit), s2))

        co = container.Container(targs.baks if setting.use_backup else None)
        if co.init(args, wspnum, True if opts.O else False,
            opts.bytes_per_line, opts.bytes_per_window) == -1:
            __error("Terminal ({0},{1}) does not have enough room".format(
                screen.get_size_y(), screen.get_size_x()))

        if setting.use_debug:
            d = util.get_import_exceptions()
            assert not d, d
        for s in msg:
            if s:
                co.flash(s)
                break # only the first one (highest priority)
        co.xrepaint()
        co.dispatch()
    except BaseException as e: # not Exception
        tb = sys.exc_info()[2]
        targs.e = e
        targs.tb = util.get_traceback(tb)
    finally:
        if co:
            co.cleanup()

    if not util.is_running_fileobj():
        __cleanup(targs)
    if targs.e:
        return -1

def test_screen():
    scr = screen.alloc_all()
    repaint = True
    l = [kbd.ERROR, ""]

    while True:
        if repaint:
            scr.clear()
            scr.box()
        __update_screen(scr, repaint, l)
        scr.refresh()

        ret = scr.getch()
        if ret == kbd.RESIZE:
            screen.update_size()
            scr.resize(screen.get_size_y(), screen.get_size_x())
            repaint = True
        else:
            repaint = False
        if screen.test_signal():
            break

        li = literal.find_literal((ret,))
        l[0] = ret
        if li:
            l[1] = li.str
        else:
            try:
                l[1] = chr(ret) # may not be printable with Python 3
            except ValueError:
                l[1] = ""
        if util.test_key(l[0]) and not kbd.isprints(l[1]): # VTxxx
            l[0] = kbd.ERROR

def __update_screen(scr, repaint, l):
    siz = screen.get_size_y() - 2 # frame
    if siz >= 16:
        if repaint:
            scr.addstr(1, 1, "Running {0} on {1}.".format(
                util.get_python_string(), kernel.get_term_info()))
            scr.addstr(3, 1, "This should look normal.", screen.A_NONE)
            scr.addstr(4, 1, "This should be in bold.", screen.A_BOLD)
            scr.addstr(5, 1, "This should look reversed.", screen.A_REVERSE)
            if kernel.is_screen() and screen.use_color():
                s = "may or may not"
            else:
                s = "should"
            scr.addstr(6, 1, "This {0} look reversed.".format(s),
                screen.A_STANDOUT)
            if kernel.is_screen() and screen.use_color():
                s = "may or may not"
            else:
                s = "should"
            scr.addstr(7, 1, "This {0} be underlined.".format(s),
                screen.A_UNDERLINE)
            if screen.has_color() and \
                setting.color_current in list(screen.iter_color_name()):
                s = "be in {0}".format(setting.color_current)
            else:
                s = "not have any color"
            scr.addstr(8, 1, "This should {0}.".format(s),
                screen.A_COLOR_CURRENT)
            scr.addstr(9, 1, "This terminal should have a frame.")
            scr.addstr(10, 1, "The frame should resize if the terminal is "
                "resized.")
            scr.addstr(12, 1, "Check if above appear as they should.")
            if kernel.is_xnix():
                s = "with different TERM value"
            else:
                s = "with different terminal environment"
            scr.addstr(13, 1, "If not try {0}.".format(s))
            scr.addstr(15, 1, "Press {0} to exit.".format(literal.ctrlc.str))
        __update_input(scr, 16, l)
    elif siz >= 3:
        if repaint:
            scr.addstr(1, 1, "Not enough room.")
            scr.addstr(2, 1, "Press {0} to exit.".format(literal.ctrlc.str))
        __update_input(scr, 3, l)

def __update_input(scr, y, l):
    if l[0] != kbd.ERROR:
        scr.move(y, 1)
        scr.clrtoeol()
        try:
            scr.addstr(y, 1, "{0:3} {1}".format(*l)) # may raise with Python 3
        except Exception:
            scr.addstr(y, 1, "{0:3}".format(l[0]))
        scr.box() # frame in this line was cleared
