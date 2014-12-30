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
from . import package
from . import screen
from . import setting
from . import util
from . import version

def __cleanup(arg):
    if arg.done:
        return -1
    arg.done = True
    console.cleanup(arg.e, arg.tb)
    screen.cleanup()
    literal.cleanup()
    __log_result(arg, log.error)
    __log_result(arg, lambda s: util.printf(s, True))
    log.info("Cleanup")
    log.cleanup()

def __log_result(arg, fn):
    if arg.e:
        fn(arg.e)
    for s in arg.tb:
        fn(s)

def __sigint_handler(sig, frame):
    screen.sti()

def __sigterm_handler(sig, frame):
    sys.exit(1)

def dispatch(optargs=None):
    colors = '|'.join(list(screen.iter_color_name()))
    usage = "Usage: %prog [options] [file paths ...]\n" + \
        "For more information run " + util.get_program_name() + \
        " and type :help<ENTER>"
    parser = optparse.OptionParser(version=version.__version__, usage=usage)

    parser.add_option("-R",
        action="store_true",
        default=False,
        help="Read only mode")
    parser.add_option("-B",
        action="store_true",
        default=False,
        help="Buffer allocation mode")
    parser.add_option("-d",
        action="store_true",
        default=False,
        help="Show buffer address starting from @offset")
    parser.add_option("-x",
        action="store_true",
        default=False,
        help="Show buffer size and current position in hexadecimal")
    parser.add_option("-o",
        type="int",
        default=1,
        metavar="<num>",
        help="Open <num> windows")
    parser.add_option("-O",
        action="store_true",
        default=False,
        help="Open each buffer in different window")
    parser.add_option("--width",
        default=setting.width,
        metavar="<width>",
        help="Set window width [[0-9]+|max|min|auto]")
    parser.add_option("--fg",
        default=setting.color_fg,
        metavar="<color>",
        help="Set foreground color [{0}]".format(colors))
    parser.add_option("--bg",
        default=setting.color_bg,
        metavar="<color>",
        help="Set background color [{0}]".format(colors))
    parser.add_option("--command",
        action="store_true",
        default=False,
        help="Print command list and exit")
    parser.add_option("--sitepkg",
        action="store_true",
        default=False,
        help="Print site package directory and exit")
    parser.add_option("--executable",
        action="store_true",
        default=False,
        help=optparse.SUPPRESS_HELP)
    parser.add_option("--debug",
        action="store_true",
        default=setting.use_debug,
        help=optparse.SUPPRESS_HELP)
    parser.add_option("--env",
        action="store_true",
        default=False,
        help=optparse.SUPPRESS_HELP)
    parser.add_option("--history",
        default=None,
        help=optparse.SUPPRESS_HELP)

    for s in allocator.iter_module_name():
        parser.add_option("--" + s,
            action="store_true",
            default=False,
            help=optparse.SUPPRESS_HELP)

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

    for o in parser.option_list:
        if isinstance(o.dest, str):
            a = getattr(opts, o.dest, None)
            log.debug("Option {0} -> {1}".format(o.dest, a))

    if ret == -1:
        log.error("Failed to make user directory")
    log.debug(sys.argv)
    log.debug("Free ram " +
        util.get_size_repr(kernel.get_free_ram()) + "/" +
        util.get_size_repr(kernel.get_total_ram()))

    signal.signal(signal.SIGINT, __sigint_handler)
    signal.signal(signal.SIGTERM, __sigterm_handler)

    try:
        co = None
        assert literal.init() != -1
        assert screen.init(opts.fg, opts.bg) != -1
        assert console.init() != -1
        co = container.Container()
        if not co.init(args, wspnum, opts.width):
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
