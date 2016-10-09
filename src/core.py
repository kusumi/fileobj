# Copyright (c) 2010-2016, Tomohiro Kusumi
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
import signal
import sys

from . import allocator
from . import console
from . import container
from . import env
from . import history
from . import kernel
from . import literal
from . import log
from . import marks
from . import package
from . import screen
from . import setting
from . import usage
from . import util
from . import version

def __cleanup(arg):
    if arg.done:
        return -1
    arg.done = True
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

def dispatch(optargs=None):
    if setting.use_debug: # FILEOBJ_USE_DEBUG=
        suppress_help = "<This is supposed to be suppressed>"
    else:
        suppress_help = optparse.SUPPRESS_HELP
    parser = optparse.OptionParser(version=version.__version__, usage=usage.help)

    parser.add_option("-R", action="store_true", default=False, help=usage.R)
    parser.add_option("-B", action="store_true", default=False, help=usage.B)
    parser.add_option("-d", action="store_true", default=False, help=usage.d)
    parser.add_option("-x", action="store_true", default=False, help=usage.x)
    parser.add_option("-o", type="int", default=1, metavar=usage.o_metavar, help=usage.o)
    parser.add_option("-O", action="store_true", default=False, help=usage.O)

    parser.add_option("--bytes_per_line", default=setting.bytes_per_line, metavar=usage.bytes_per_line_metavar, help=usage.bytes_per_line)
    parser.add_option("--bytes_per_window", default=setting.bytes_per_window, metavar=usage.bytes_per_window_metavar, help=usage.bytes_per_window)
    parser.add_option("--terminal_height", type="int", default=setting.terminal_height, metavar=usage.terminal_height_metavar, help=usage.terminal_height)
    parser.add_option("--terminal_width", type="int", default=setting.terminal_width, metavar=usage.terminal_width_metavar, help=usage.terminal_width)
    parser.add_option("--fg", default=setting.color_fg, metavar=usage.fg_metavar, help=usage.fg)
    parser.add_option("--bg", default=setting.color_bg, metavar=usage.bg_metavar, help=usage.bg)
    parser.add_option("--simple", action="store_true", default=(not setting.use_full_status_window and not setting.use_status_window_frame), help=usage.simple)
    parser.add_option("--command", action="store_true", default=False, help=usage.command)
    parser.add_option("--sitepkg", action="store_true", default=False, help=usage.sitepkg)

    parser.add_option("--executable", action="store_true", default=False, help=suppress_help)
    parser.add_option("--debug", action="store_true", default=setting.use_debug, help=suppress_help)
    parser.add_option("--env", action="store_true", default=False, help=suppress_help)
    parser.add_option("--history", default=None, metavar="<path>", help=suppress_help)
    parser.add_option("--marks", default=None, metavar="<path>", help=suppress_help)

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
    if opts.executable:
        util.printf(util.get_python_executable_string())
        return
    if opts.env:
        env.print_env()
        return
    if opts.history:
        history.print_history(opts.history)
        return
    if opts.marks:
        marks.print_marks(opts.marks)
        return

    targs = util.Namespace(e=None, tb=[], done=False)
    atexit.register(__cleanup, targs)
    ret = setting.init_user()
    log.init(util.get_program_name())

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
    wspnum = opts.o
    if opts.O:
        wspnum = len(args)
    if wspnum < 1:
        wspnum = 1
    if opts.terminal_height > 0:
        setting.terminal_height = opts.terminal_height
    if opts.terminal_width > 0:
        setting.terminal_width = opts.terminal_width
    if opts.simple:
        setting.use_full_status_window = False
        setting.use_status_window_frame = False

    for o in parser.option_list:
        if isinstance(o.dest, str):
            a = getattr(opts, o.dest, None)
            log.debug("Option {0} -> {1}".format(o.dest, a))

    msg = ''
    if not kernel.is_bsd_derived() and setting.use_bsd_caveat:
        msg = "BSD caveat enabled on {0}".format(util.get_os_name())
        log.error(msg)
    if not kernel.is_cygwin() and setting.use_cygwin_caveat:
        msg = "CYGWIN caveat enabled on {0}".format(util.get_os_name())
        log.error(msg)

    if ret == -1:
        msg = "Failed to make user directory {0}".format(setting.user_dir)
        log.error(msg)

    log.debug(sys.argv)
    log.debug("Free ram {0}/{1}".format(
        util.get_size_repr(kernel.get_free_ram()),
        util.get_size_repr(kernel.get_total_ram())))

    signal.signal(signal.SIGINT, __sigint_handler)
    signal.signal(signal.SIGTERM, __sigterm_handler)

    try:
        co = None
        if not kernel.is_detected():
            msg = "{0}, consider setting the following variable e.g.\n" \
                "$ export FILEOBJ_USE_XNIX=\n" \
                "to manually declare running on Unix-like OS".format(
                kernel.get_status_string())
            raise util.QuietError(msg)

        assert literal.init() != -1
        if screen.init(opts.fg, opts.bg) == -1:
            msg = "Unable to retrieve terminal size, consider using " \
                "--terminal_height and --terminal_width options " \
                "to manually specify terminal size"
            raise util.QuietError(msg)
        assert console.init() != -1

        co = container.Container()
        if co.init(args, wspnum,
            opts.bytes_per_line, opts.bytes_per_window, msg) == -1:
            msg = "Terminal ({0},{1}) does not have enough room".format(
                screen.get_size_y(), screen.get_size_x())
            raise util.QuietError(msg)
        if setting.use_debug:
            d = util.get_import_exceptions()
            assert not d, d
        co.repaint()
        co.dispatch()
    except Exception as e:
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
