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

import atexit
import optparse
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
    log.info("Cleanup")
    log.cleanup()

def __log_error(arg):
    if not arg.e:
        return -1
    log.error(arg.e)
    for s in arg.tb:
        log.error(s)

def __print_error(arg):
    if not arg.e:
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
        suppress_help = "<This is supposed to be suppressed>"
    else:
        suppress_help = optparse.SUPPRESS_HELP
    parser = optparse.OptionParser(version=version.__version__, usage=usage.help)

    parser.add_option("-R", action="store_true", default=False, help=usage.R)
    parser.add_option("-B", action="store_true", default=False, help=usage.B)
    parser.add_option("-d", action="store_true", default=False, help=usage.d)
    parser.add_option("-x", action="store_true", default=False, help=usage.x)
    parser.add_option("-o", action="store_true", default=False, help=usage.o)
    parser.add_option("-O", action="store_true", default=False, help=usage.O)

    parser.add_option("--bytes_per_line", "--bpl", default=setting.bytes_per_line, metavar=usage.bytes_per_line_metavar, help=usage.bytes_per_line)
    parser.add_option("--bytes_per_window", "--bpw", default=setting.bytes_per_window, metavar=usage.bytes_per_window_metavar, help=usage.bytes_per_window)
    parser.add_option("--fg", default=setting.color_fg, metavar=usage.fg_metavar, help=usage.fg)
    parser.add_option("--bg", default=setting.color_bg, metavar=usage.bg_metavar, help=usage.bg)
    parser.add_option("--verbose_window", action="store_true", default=(setting.use_verbose_status_window and setting.use_status_window_frame), help=usage.verbose_window)
    parser.add_option("--backup", action="store_true", default=setting.use_backup, help=usage.backup)
    parser.add_option("--force", action="store_true", default=setting.use_force, help=usage.force)
    parser.add_option("--test_screen", action="store_true", default=False, help=usage.test_screen)
    parser.add_option("--command", action="store_true", default=False, help=usage.command)
    parser.add_option("--sitepkg", action="store_true", default=False, help=usage.sitepkg)

    # hidden options
    parser.add_option("--debug", action="store_true", default=setting.use_debug, help=suppress_help)
    parser.add_option("--terminal_height", type="int", default=-1, metavar="<terminal_height>", help=suppress_help)
    parser.add_option("--terminal_width", type="int", default=-1, metavar="<terminal_width>", help=suppress_help)
    parser.add_option("--wspnum", type="int", default=1, help=suppress_help)

    for s in allocator.iter_module_name():
        parser.add_option("--" + s, action="store_true", default=False, help=suppress_help)

    opts, args = parser.parse_args(optargs)
    if opts.debug:
        setting.use_debug = True

    if opts.command:
        literal.print_literal()
        return
    if opts.sitepkg:
        for x in package.get_paths():
            util.printf(x)
        return

    msg = [None, None, None]
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

    log.info("-" * 50)
    log.info("{0} {1}".format(
        util.get_program_path(),
        version.get_tag_string()))
    log.info("{0} {1}".format(util.get_python_string(), sys.executable))
    log.info("UNAME {0} {1}".format(util.get_os_name(), util.get_os_release()))
    log.info("CPU {0}".format(util.get_cpu_name()))
    log.info("RAM {0}".format(methods.get_meminfo_string()))
    log.info("TERM {0}".format(kernel.get_term_info()))
    log.info("LANG {0}".format(kernel.get_lang_info()))
    log.info(methods.get_osdep_string())
    log.info("argv {0}".format(sys.argv))

    for s in allocator.iter_module_name():
        if getattr(opts, s, False):
            allocator.set_default_class(s)
    if opts.R:
        setting.use_readonly = True
    if opts.B:
        allocator.set_default_buffer_class()
    if opts.d:
        setting.use_address_num_offset = True
    if opts.x:
        setting.status_num_radix = 16
    if opts.o or opts.O:
        wspnum = len(args)
    else:
        wspnum = 1
    if opts.verbose_window:
        setting.use_verbose_status_window = True
        setting.use_status_window_frame = True
    if kernel.is_vtxxx() and (opts.fg or opts.bg):
        msg[2] = "Terminal color unsupported on {0}".format(
            kernel.get_term_info())
        opts.fg = None
        opts.bg = None

    # hidden options
    if opts.terminal_height > 0:
        screen.terminal.height = opts.terminal_height
    if opts.terminal_width > 0:
        screen.terminal.width = opts.terminal_width
    absnum = abs(opts.wspnum)
    if absnum != 1: # force wspnum and split direction
        if absnum > wspnum:
            wspnum = absnum
        if opts.wspnum < 0:
            opts.O = True

    l = []
    for o in parser.option_list:
        if isinstance(o.dest, str):
            a = getattr(opts, o.dest, None)
            l.append("{0}={1}".format(o.dest, a))
    log.debug("options {0}".format(l))

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

    s = "{{0}} caveat enabled on {0}".format(util.get_os_name())
    if not kernel.is_bsd_derived() and setting.use_bsd_caveat:
        msg[1] = s.format("BSD")
    if not kernel.is_illumos() and setting.use_illumos_caveat:
        msg[1] = s.format("illumos")
    if not kernel.is_cygwin() and setting.use_cygwin_caveat:
        msg[1] = s.format("Cygwin")

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
        except Exception as e:
            if setting.use_debug:
                raise
            else:
                __error(str(e))

        if opts.test_screen:
            test_screen()
            return

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

        co = container.Container(targs.baks if opts.backup else None)
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
        __cleanup(targs) # script/profile hits here
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
                l[1] = chr(ret)
            except ValueError:
                l[1] = ""
        if util.test_key(l[0]) and not kbd.isprints(l[1]): # VTxxx
            l[0] = kbd.ERROR

def __update_screen(scr, repaint, l):
    siz = screen.get_size_y() - 2 # frame
    if siz >= 13:
        if repaint:
            scr.addstr(1, 1, "Running {0} on {1}".format(
                util.get_python_string(),
                kernel.get_term_info()))
            scr.addstr(3, 1, "This should look normal.", screen.A_DEFAULT)
            scr.addstr(4, 1, "This should be in bold.", screen.A_BOLD)
            scr.addstr(5, 1, "This should look reversed.", screen.A_REVERSE)
            if kernel.is_screen() and screen.use_color():
                s = "may not"
            else:
                s = "should"
            scr.addstr(6, 1, "This {0} look reversed.".format(s),
                screen.A_STANDOUT)
            if kernel.is_screen() and screen.use_color():
                s = "may not"
            else:
                s = "should"
            scr.addstr(7, 1, "This {0} be underlined.".format(s),
                screen.A_UNDERLINE)
            scr.addstr(8, 1, "This frame should resize if the terminal "
                "emulator is resized.")
            scr.addstr(10, 1, "Check if above appear as they should.")
            scr.addstr(12, 1, "Press {0} to exit.".format(literal.ctrlc.str))
        if l[0] != kbd.ERROR:
            scr.move(13, 1)
            scr.clrtoeol()
            scr.addstr(13, 1, "{0:3} {1}".format(*l))
    elif siz >= 3:
        if repaint:
            scr.addstr(1, 1, "Not enough room.")
            scr.addstr(2, 1, "Press {0} to exit.".format(literal.ctrlc.str))
        if l[0] != kbd.ERROR:
            scr.move(3, 1)
            scr.clrtoeol()
            scr.addstr(3, 1, "{0:3} {1}".format(*l))
