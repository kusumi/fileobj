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

import logging
import sys

from . import setting
from . import util
from . import version

def init(name, f=None):
    global _logger
    if __get_attr() is None:
        return -1
    if _logger:
        return -1
    try:
        logger = logging.getLogger(name)
        if setting.use_debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(__get_attr(logging.WARNING))
        __add_handler(logger, f)
        _logger = logger
    except Exception:
        return -1

    info('=' * 80)
    info("{0} on {1} {2}".format(
        util.get_python_executable_string(),
        util.get_os_name(),
        util.get_os_release()))
    info("{0} {1}".format(
        util.get_program_path(),
        version.get_tag_string()))
    info("argv {0}".format(sys.argv))

def cleanup():
    global _logger
    if not _logger:
        return -1
    try:
        info("Bye")
        __remove_handler(_logger)
    except Exception:
        return -1
    finally:
        _logger = None

def __get_attr(default=None):
    return getattr(logging, setting.log_level, default)

def __add_handler(logger, f):
    if not logger.handlers:
        if not f:
            f = setting.get_log_path()
        hnd = logging.FileHandler(f)
        hnd.setFormatter(logging.Formatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"))
        logger.addHandler(hnd)

def __remove_handler(logger):
    for hnd in logger.handlers:
        logger.removeHandler(hnd)
        hnd.close()

def debug(*l):
    return __log(l, logging.DEBUG)
def info(*l):
    return __log(l, logging.INFO)
def warning(*l):
    return __log(l, logging.WARNING)
def error(*l):
    return __log(l, logging.ERROR)
def critical(*l):
    return __log(l, logging.CRITICAL)

def __log(l, level):
    assert util.is_seq(l), l
    if len(l) == 1:
        l = l[0]
    s = util.obj_to_string(l)
    if _logger:
        _logger.log(level, s)
    elif setting.log_level.lower() == "stdout":
        util.printf(s)
    else:
        return -1

_logger = None
