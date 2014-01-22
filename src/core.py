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
from . import screen
from . import setting
from . import util
from . import version

def cleanup(targs):
    console.cleanup(*targs)
    screen.cleanup()
    literal.cleanup()
    e, tb = targs
    if e:
        log.error(e)
        util.print_stderr(e)
    for s in tb:
        log.error(s)
        util.print_stderr(s)
    log.cleanup()

def sigint_handler(sig, frame):
    screen.sti()

def sigterm_handler(sig, frame):
    sys.exit(1)

def dispatch():
    colors = '|'.join(list(screen.iter_color_name()))
    parser = optparse.OptionParser(version=version.__version__,
        usage="Usage: %prog [options] [path1 path2 ...]\n\
For more information, run the program and enter :help<ENTER>")

    parser.add_option("-R",
        action="store_true",
        default=False,
        help="Read only")
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
        help="Set foreground color [%s]" % colors)
    parser.add_option("--bg",
        default=setting.color_bg,
        metavar="<color>",
        help="Set background color [%s]" % colors)
    parser.add_option("--command",
        action="store_true",
        default=False,
        help="Print command list")
    parser.add_option("--sitepkg",
        action="store_true",
        default=False,
        help="Print site package directory")
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
        parser.add_option("--%s" % s,
            action="store_true",
            default=False,
            help=optparse.SUPPRESS_HELP)

    opts, args = parser.parse_args()
    setting.use_debug |= opts.debug

    if opts.command:
        literal.print_literal()
        sys.exit(0)
    if opts.sitepkg:
        print(util.get_package_dir())
        sys.exit(0)
    if opts.env:
        env.print_env()
        sys.exit(0)
    if opts.history:
        history.print_history(opts.history)
        sys.exit(0)

    targs = [None, []]
    atexit.register(cleanup, targs)
    ret = setting.init_user()
    log.init(util.get_program_name())

    for s in allocator.iter_module_name():
        if getattr(opts, s, False):
            allocator.set_default_class(s)
    setting.use_readonly |= opts.R
    wspnum = opts.o
    if opts.O:
        wspnum = len(args)
    if wspnum < 1:
        wspnum = 1

    for o in parser.option_list:
        if isinstance(o.dest, str):
            a = getattr(opts, o.dest, None)
            log.debug("Option %s -> %s" % (o.dest, a))
    if ret == -1:
        log.error("Failed to make user directory")
    log.debug(sys.argv)
    log.debug("Free ram %s/%s" % (
        util.get_byte_string(kernel.get_free_ram()),
        util.get_byte_string(kernel.get_total_ram())))

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    try:
        literal.init()
        screen.init(opts.fg, opts.bg)
        console.init()
        co = None
        co = container.Container()
        if not co.init(args, wspnum, opts.width):
            co.repaint()
            co.dispatch()
    except Exception:
        info = sys.exc_info()
        targs[0] = info[1]
        targs[1] = util.get_traceback(info[2])
        sys.exit(1)
    finally:
        if co:
            co.cleanup()
