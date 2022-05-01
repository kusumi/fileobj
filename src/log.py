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

import logging

from . import setting
from . import util

DEBUG    = logging.DEBUG
INFO     = logging.INFO
WARNING  = logging.WARNING
ERROR    = logging.ERROR
CRITICAL = logging.CRITICAL
_levels  = DEBUG, INFO, WARNING, ERROR, CRITICAL

def init(name, f=None):
    global _logger, _logmsg
    assert DEBUG < INFO < WARNING < ERROR < CRITICAL, _levels
    if __get_level() is None:
        return -1
    if _logger:
        return -1
    try:
        logger = logging.getLogger(name)
        if setting.use_debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(__get_level(logging.INFO))
        __add_handler(logger, f)
        _logger = logger
        _logmsg = []
    except Exception:
        return -1

def cleanup():
    global _logger, _logmsg
    if not _logger:
        return -1
    try:
        debug("Bye")
        __remove_handler(_logger)
    except Exception:
        return -1
    finally:
        _logmsg = None
        _logger = None

def __get_level(default=None):
    return getattr(logging, setting.log_level.upper(), default)

def __add_handler(logger, f):
    if not logger.handlers:
        if not f:
            f = setting.get_log_path()
        hnd = logging.FileHandler(f)
        hnd.setFormatter(logging.Formatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"))
        logger.addHandler(hnd)
    assert len(logger.handlers) == 1, logger.handlers

def __remove_handler(logger):
    assert len(logger.handlers) == 1, logger.handlers
    hnd = logger.handlers[0]
    logger.removeHandler(hnd)
    hnd.close()

def debug(*l):
    return __log(l, logging.DEBUG)

def info(*l):
    return __log(l, logging.INFO)

def warning(*l):
    return __log(l, logging.WARNING)

def error(*l):
    ret = __log(l, logging.ERROR)
    if ret == -1:
        return ret
    #for x in util.iter_traceback():
    #    __log((x,), logging.ERROR)
    return ret

def critical(*l):
    ret = __log(l, logging.CRITICAL)
    if ret == -1:
        return ret
    #for x in util.iter_traceback():
    #    __log((x,), logging.CRITICAL)
    return ret

def __log(l, level):
    assert util.is_seq(l), l
    if len(l) == 1:
        l = l[0]
    s = util.obj_to_string(l)
    if _logmsg is None:
        return -1
    _logmsg.append((level, s))
    if _logger:
        _logger.log(level, s)
    elif setting.log_level.lower() == "stdout":
        util.printf(s)
    else:
        return -1

def get_path():
    try:
        return _logger.handlers[0].baseFilename
    except Exception as e:
        error(e)
        return ""

def get_message(level=DEBUG):
    return tuple(iter_message(level))

def iter_message(level=DEBUG):
    if _logmsg is not None:
        for l in _logmsg:
            if l[0] >= level:
                yield l

def has_error():
    for l in _logmsg:
        if l[0] >= logging.ERROR:
            return True
    return False

def debug_traceback(tb=None):
    for x in util.iter_traceback(tb):
        debug(x)

_logger = None
_logmsg = None
