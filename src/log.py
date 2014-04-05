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

import logging
import sys

from . import setting
from . import util
from . import version

def init(name, f=None):
    if not setting.use_log:
        return -1
    if this._logger:
        return -1
    try:
        logger = logging.getLogger(name)
        if setting.use_debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(getattr(
                logging, setting.log_level, logging.WARNING))
        _add_handler(logger, f)
        this._logger = logger
    except Exception:
        return -1

    verbose('=' * 80)
    verbose("Using Python {0} on {1} {2}".format(
        util.get_python_version_string(),
        util.get_system_string(),
        util.get_release_string()))
    verbose("Running {0} ({1})".format(
        util.get_program_path(), version.__version__))

def cleanup():
    if not setting.use_log:
        return -1
    if not this._logger:
        return -1
    try:
        verbose("Bye")
        _remove_handler(this._logger)
    except Exception:
        return -1
    finally:
        this._logger = None

def _add_handler(logger, f):
    if not logger.handlers:
        if not f:
            f = setting.get_log_path()
        hnd = logging.FileHandler(f)
        hnd.setFormatter(logging.Formatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"))
        logger.addHandler(hnd)

def _remove_handler(logger):
    for hnd in logger.handlers:
        logger.removeHandler(hnd)
        hnd.close()

def debug(o):
    return _log(o, logging.DEBUG)
def info(o):
    return _log(o, logging.INFO)
def warning(o):
    return _log(o, logging.WARNING)
def error(o):
    return _log(o, logging.ERROR)
def critical(o):
    return _log(o, logging.CRITICAL)

def verbose(o, level=logging.INFO):
    if setting.use_log_verbose:
        _log(o, level)

def _log(o, level):
    if this._logger:
        this._logger.log(level, util.object_to_string(o))
    else:
        return -1

_logger = None
this = sys.modules[__name__]
