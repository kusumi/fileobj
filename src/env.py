# Copyright (c) 2012, Tomohiro Kusumi
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

from __future__ import with_statement
import os
import re
import sys

def __iter_env_name():
    yield "FILEOBJ_USE_READONLY" # -R
    yield "FILEOBJ_USE_BYTES_BUFFER" # -B
    yield "FILEOBJ_USE_ASCII_EDIT" # :set binary,ascii
    yield "FILEOBJ_USE_IGNORECASE" # :set ic
    yield "FILEOBJ_USE_SIPREFIX" # :set si
    yield "FILEOBJ_USE_WRAPSCAN" # :set ws
    yield "FILEOBJ_USE_TEXT_WINDOW"
    yield "FILEOBJ_USE_MOUSE_EVENTS"
    yield "FILEOBJ_USE_UNIT_BASED"
    yield "FILEOBJ_USE_BACKUP"
    yield "FILEOBJ_ENDIANNESS" # :set le,be
    yield "FILEOBJ_ADDRESS_RADIX" # :set address
    yield "FILEOBJ_BYTES_PER_LINE" # --bytes_per_line, :set bytes_per_line
    yield "FILEOBJ_BYTES_PER_WINDOW" # --bytes_per_window, :set bytes_per_window
    yield "FILEOBJ_BYTES_PER_UNIT" # --bytes_per_unit, :set bytes_per_unit
    yield "FILEOBJ_COLOR_CURRENT"
    yield "FILEOBJ_COLOR_ZERO"
    yield "FILEOBJ_COLOR_FF"
    yield "FILEOBJ_COLOR_PRINT"
    yield "FILEOBJ_COLOR_DEFAULT"
    yield "FILEOBJ_COLOR_VISUAL"

def __iter_env_name_private():
    yield "__FILEOBJ_USE_DEBUG" # --debug, unittest (true)
    yield "__FILEOBJ_USE_GETCH" # unittest (false)
    yield "__FILEOBJ_USE_STDOUT" # unittest (true)
    yield "__FILEOBJ_USE_CONSOLE_LOG" # unittest (false)
    yield "__FILEOBJ_USE_SESSION_POSITION" # unittest (false)
    yield "__FILEOBJ_USE_NATIVE"
    yield "__FILEOBJ_USE_PATH_ATTR"
    yield "__FILEOBJ_USE_PID_PATH"
    yield "__FILEOBJ_USE_TRACE"
    yield "__FILEOBJ_USE_ALT_CHGAT"
    yield "__FILEOBJ_USE_CIRCULAR_BIT_SHIFT"
    yield "__FILEOBJ_USE_SINGLE_OPERATION"
    yield "__FILEOBJ_USE_DOWNWARD_WINDOW_ADJUST"
    yield "__FILEOBJ_USE_STATUS_WINDOW_VERBOSE"
    yield "__FILEOBJ_USE_STATUS_WINDOW_FRAME"
    yield "__FILEOBJ_USE_AUTO_FILEOPS_ADJUST" # unittest (false)
    yield "__FILEOBJ_USE_AUTO_FILEOPS_CLEANUP" # unittest (false)
    yield "__FILEOBJ_USE_VM_SYNC_ON_EDIT"
    yield "__FILEOBJ_USE_DELETE_CONSOLE" # unittest (false)
    yield "__FILEOBJ_STDOUT_VERBOSE" # unittest (0)
    yield "__FILEOBJ_TRACE_WORD_SIZE"
    yield "__FILEOBJ_LOG_LEVEL"
    yield "__FILEOBJ_MAX_HISTORY"
    yield "__FILEOBJ_BARRIER_SIZE"
    yield "__FILEOBJ_BARRIER_EXTEND"
    yield "__FILEOBJ_REGFILE_SOFT_LIMIT"
    yield "__FILEOBJ_BUFFER_CHUNK_SIZE"
    yield "__FILEOBJ_BUFFER_CHUNK_BALANCE_INTERVAL"
    yield "__FILEOBJ_TERMINAL_HEIGHT"
    yield "__FILEOBJ_TERMINAL_WIDTH"
    yield "__FILEOBJ_TEMP_SIZE"
    yield "__FILEOBJ_PATH_STREAM"
    yield "__FILEOBJ_COLOR_FG"
    yield "__FILEOBJ_COLOR_BG"

_env_default_value = {
    "FILEOBJ_USE_READONLY" : False,
    "FILEOBJ_USE_BYTES_BUFFER" : False,
    "FILEOBJ_USE_ASCII_EDIT" : False,
    "FILEOBJ_USE_IGNORECASE" : False,
    "FILEOBJ_USE_SIPREFIX" : False,
    "FILEOBJ_USE_WRAPSCAN" : True,
    "FILEOBJ_USE_TEXT_WINDOW" : True,
    "FILEOBJ_USE_MOUSE_EVENTS" : True,
    "FILEOBJ_USE_UNIT_BASED" : False,
    "FILEOBJ_USE_BACKUP" : False,
    "FILEOBJ_ENDIANNESS" : None,
    "FILEOBJ_ADDRESS_RADIX" : 16,
    "FILEOBJ_BYTES_PER_LINE" : None,
    "FILEOBJ_BYTES_PER_WINDOW" : None,
    "FILEOBJ_BYTES_PER_UNIT" : 1,
    "FILEOBJ_COLOR_CURRENT" : "black,green",
    "FILEOBJ_COLOR_ZERO" : "green",
    "FILEOBJ_COLOR_FF" : "magenta",
    "FILEOBJ_COLOR_PRINT" : "cyan",
    "FILEOBJ_COLOR_DEFAULT" : "white",
    "FILEOBJ_COLOR_VISUAL" : "red,yellow",

    "__FILEOBJ_USE_DEBUG" : False,
    "__FILEOBJ_USE_GETCH" : True,
    "__FILEOBJ_USE_STDOUT" : False,
    "__FILEOBJ_USE_CONSOLE_LOG" : False,
    "__FILEOBJ_USE_SESSION_POSITION" : True,
    "__FILEOBJ_USE_NATIVE" : True,
    "__FILEOBJ_USE_PATH_ATTR" : True,
    "__FILEOBJ_USE_PID_PATH" : True,
    "__FILEOBJ_USE_TRACE" : False,
    "__FILEOBJ_USE_ALT_CHGAT" : False,
    "__FILEOBJ_USE_CIRCULAR_BIT_SHIFT" : True,
    "__FILEOBJ_USE_SINGLE_OPERATION" : False,
    "__FILEOBJ_USE_DOWNWARD_WINDOW_ADJUST" : True,
    "__FILEOBJ_USE_STATUS_WINDOW_VERBOSE" : False,
    "__FILEOBJ_USE_STATUS_WINDOW_FRAME" : False,
    "__FILEOBJ_USE_AUTO_FILEOPS_ADJUST" : True,
    "__FILEOBJ_USE_AUTO_FILEOPS_CLEANUP" : True,
    "__FILEOBJ_USE_VM_SYNC_ON_EDIT" : False,
    "__FILEOBJ_USE_DELETE_CONSOLE" : True,
    "__FILEOBJ_STDOUT_VERBOSE" : 1,
    "__FILEOBJ_TRACE_WORD_SIZE" : 2,
    "__FILEOBJ_LOG_LEVEL" : "INFO",
    "__FILEOBJ_MAX_HISTORY" : 1000,
    "__FILEOBJ_BARRIER_SIZE" : 8192,
    "__FILEOBJ_BARRIER_EXTEND" : 1024,
    "__FILEOBJ_REGFILE_SOFT_LIMIT" : ((1 << 20) * 100),
    "__FILEOBJ_BUFFER_CHUNK_SIZE" : -1,
    "__FILEOBJ_BUFFER_CHUNK_BALANCE_INTERVAL" : 100,
    "__FILEOBJ_TERMINAL_HEIGHT" : -1,
    "__FILEOBJ_TERMINAL_WIDTH" : -1,
    "__FILEOBJ_TEMP_SIZE" : -1,
    "__FILEOBJ_PATH_STREAM" : None,
    "__FILEOBJ_COLOR_FG" : None,
    "__FILEOBJ_COLOR_BG" : None,
}

def get_default(envname, default=None):
    return _env_default_value.get(envname, default)

def getenv(envname):
    return os.getenv(envname)

def test_bool(envname, default=None):
    e = getenv(envname)
    if e is None:
        return get_default(envname, default)
    else:
        return e.lower() != "false"

def test_name(envname, default=None):
    e = getenv(envname)
    if e is None:
        return get_default(envname, default)
    else:
        return e

def test_gt_zero(envname, default=None):
    e = getenv(envname)
    if e is None:
        return get_default(envname, default)
    else:
        try:
            x = int(e)
            if x > 0:
                return x
        except Exception:
            pass
        return get_default(envname, default)

def test_ge_zero(envname, default=None):
    e = getenv(envname)
    if e is None:
        return get_default(envname, default)
    else:
        try:
            x = int(e)
            if x >= 0:
                return x
        except Exception:
            pass
        return get_default(envname, default)

def __get_setting_use_readonly():
    return test_bool("FILEOBJ_USE_READONLY")

def __get_setting_use_bytes_buffer():
    return test_bool("FILEOBJ_USE_BYTES_BUFFER")

def __get_setting_use_ascii_edit():
    return test_bool("FILEOBJ_USE_ASCII_EDIT")

def __get_setting_use_ignorecase():
    return test_bool("FILEOBJ_USE_IGNORECASE")

def __get_setting_use_siprefix():
    return test_bool("FILEOBJ_USE_SIPREFIX")

def __get_setting_use_wrapscan():
    return test_bool("FILEOBJ_USE_WRAPSCAN")

def __get_setting_use_text_window():
    return test_bool("FILEOBJ_USE_TEXT_WINDOW")

def __get_setting_use_mouse_events():
    return test_bool("FILEOBJ_USE_MOUSE_EVENTS")

def __get_setting_use_unit_based():
    return test_bool("FILEOBJ_USE_UNIT_BASED")

def __get_setting_use_backup():
    return test_bool("FILEOBJ_USE_BACKUP")

def __get_setting_endianness():
    s = "FILEOBJ_ENDIANNESS"
    e = getenv(s)
    if e is None:
        return get_default(s)
    elif e.lower() == "little":
        return "little"
    elif e.lower() == "big":
        return "big"
    else:
        return get_default(s)

def __get_setting_address_radix():
    s = "FILEOBJ_ADDRESS_RADIX"
    e = getenv(s)
    if e is None:
        return get_default(s)
    else:
        try:
            x = int(e)
            if x in (16, 10, 8):
                return x
        except Exception:
            pass
        return get_default(s)

def __get_setting_bytes_per_line():
    s = "FILEOBJ_BYTES_PER_LINE"
    e = getenv(s)
    if e is None:
        return get_default(s)
    else:
        return e.lower() # return str even if e is \d+

def __get_setting_bytes_per_window():
    s = "FILEOBJ_BYTES_PER_WINDOW"
    e = getenv(s)
    if e is None:
        return get_default(s)
    else:
        return e.lower() # return str even if e is \d+

def __get_setting_bytes_per_unit():
    s = "FILEOBJ_BYTES_PER_UNIT"
    e = getenv(s)
    if e is None:
        return get_default(s)
    else:
        try:
            x = int(e)
            if x > 0:
                return x
        except Exception:
            pass
        return get_default(s)

def __get_setting_color_current():
    ret = test_name("FILEOBJ_COLOR_CURRENT")
    if not ret or ret.lower() == "none":
        return None
    else:
        return ret

def __get_setting_color_zero():
    ret = test_name("FILEOBJ_COLOR_ZERO")
    if not ret or ret.lower() == "none":
        return None
    else:
        return ret

def __get_setting_color_ff():
    ret = test_name("FILEOBJ_COLOR_FF")
    if not ret or ret.lower() == "none":
        return None
    else:
        return ret

def __get_setting_color_print():
    ret = test_name("FILEOBJ_COLOR_PRINT")
    if not ret or ret.lower() == "none":
        return None
    else:
        return ret

def __get_setting_color_default():
    ret = test_name("FILEOBJ_COLOR_DEFAULT")
    if not ret or ret.lower() == "none":
        return None
    else:
        return ret

def __get_setting_color_visual():
    ret = test_name("FILEOBJ_COLOR_VISUAL")
    if not ret or ret.lower() == "none":
        return None
    else:
        return ret

def __get_setting_use_debug():
    return test_bool("__FILEOBJ_USE_DEBUG")

def __get_setting_use_getch():
    return test_bool("__FILEOBJ_USE_GETCH")

def __get_setting_use_stdout():
    return test_bool("__FILEOBJ_USE_STDOUT")

def __get_setting_use_console_log():
    return test_bool("__FILEOBJ_USE_CONSOLE_LOG")

def __get_setting_use_session_position():
    return test_bool("__FILEOBJ_USE_SESSION_POSITION")

def __get_setting_use_native():
    return test_bool("__FILEOBJ_USE_NATIVE")

def __get_setting_use_path_attr():
    return test_bool("__FILEOBJ_USE_PATH_ATTR")

def __get_setting_use_pid_path():
    return test_bool("__FILEOBJ_USE_PID_PATH")

def __get_setting_use_trace():
    return test_bool("__FILEOBJ_USE_TRACE")

def __get_setting_use_alt_chgat():
    return test_bool("__FILEOBJ_USE_ALT_CHGAT")

def __get_setting_use_circular_bit_shift():
    return test_bool("__FILEOBJ_USE_CIRCULAR_BIT_SHIFT")

def __get_setting_use_single_operation():
    return test_bool("__FILEOBJ_USE_SINGLE_OPERATION")

def __get_setting_use_downward_window_adjust():
    return test_bool("__FILEOBJ_USE_DOWNWARD_WINDOW_ADJUST")

def __get_setting_use_status_window_verbose():
    return test_bool("__FILEOBJ_USE_STATUS_WINDOW_VERBOSE")

def __get_setting_use_status_window_frame():
    return test_bool("__FILEOBJ_USE_STATUS_WINDOW_FRAME")

def __get_setting_use_auto_fileops_adjust():
    return test_bool("__FILEOBJ_USE_AUTO_FILEOPS_ADJUST")

def __get_setting_use_auto_fileops_cleanup():
    return test_bool("__FILEOBJ_USE_AUTO_FILEOPS_CLEANUP")

def __get_setting_use_vm_sync_on_edit():
    return test_bool("__FILEOBJ_USE_VM_SYNC_ON_EDIT")

def __get_setting_use_delete_console():
    return test_bool("__FILEOBJ_USE_DELETE_CONSOLE")

def __get_setting_stdout_verbose():
    return test_ge_zero("__FILEOBJ_STDOUT_VERBOSE")

def __get_setting_trace_word_size():
    s = "__FILEOBJ_TRACE_WORD_SIZE"
    e = getenv(s)
    if e is None:
        return get_default(s)
    else:
        try:
            x = int(e)
            if x in (2, 4, 8): # no 1
                return x
        except Exception:
            pass
        return get_default(s)

def __get_setting_log_level():
    return test_name("__FILEOBJ_LOG_LEVEL")

def __get_setting_max_history():
    return test_gt_zero("__FILEOBJ_MAX_HISTORY")

def __get_setting_barrier_size():
    return test_gt_zero("__FILEOBJ_BARRIER_SIZE")

def __get_setting_barrier_extend():
    return test_gt_zero("__FILEOBJ_BARRIER_EXTEND")

def __get_setting_regfile_soft_limit():
    return test_ge_zero("__FILEOBJ_REGFILE_SOFT_LIMIT")

def __get_setting_buffer_chunk_size():
    return test_gt_zero("__FILEOBJ_BUFFER_CHUNK_SIZE")

def __get_setting_buffer_chunk_balance_interval():
    return test_gt_zero("__FILEOBJ_BUFFER_CHUNK_BALANCE_INTERVAL")

def __get_setting_terminal_height():
    return test_gt_zero("__FILEOBJ_TERMINAL_HEIGHT")

def __get_setting_terminal_width():
    return test_gt_zero("__FILEOBJ_TERMINAL_WIDTH")

def __get_setting_temp_size():
    return test_gt_zero("__FILEOBJ_TEMP_SIZE")

def __get_setting_path_stream():
    return getenv("__FILEOBJ_PATH_STREAM")

def __get_setting_color_fg():
    s = "__FILEOBJ_COLOR_FG"
    e = getenv(s)
    if e is None:
        return get_default(s)
    else:
        return e.lower()

def __get_setting_color_bg():
    s = "__FILEOBJ_COLOR_BG"
    e = getenv(s)
    if e is None:
        return get_default(s)
    else:
        return e.lower()

def iter_env_name():
    for x in sorted(__iter_env_name()):
        yield x

def iter_env_name_private():
    for x in sorted(__iter_env_name_private()):
        yield x

def iter_defined_env():
    envs = list(iter_env_name()) + list(iter_env_name_private())
    for l in __iter_os_environ():
        if l[0] in envs:
            yield l

def iter_defined_ext_env():
    for l in __iter_os_environ():
        if l[0].startswith("FILEOBJ_EXT_"):
            yield l

def __iter_os_environ():
    for k in sorted(os.environ):
        yield k, os.environ[k]

def iter_setting():
    for x in iter_env_name():
        yield __get_setting(x, "FILEOBJ_")
    for x in iter_env_name_private():
        yield __get_setting(x, "__FILEOBJ_")

def __get_setting(x, prefix):
    this = sys.modules[__name__]
    assert x.startswith(prefix), x
    name = x[len(prefix):].lower()
    fn = getattr(this, "__get_setting_" + name)
    return name, fn()

_regex = re.compile(r"^(.*FILEOBJ_[A-Z_]+)=(\S*)$")
_config = {}

def get_config():
    return _config.copy()

# called from setting import, i.e. can't use other fileobj modules
def init(f):
    assert f, f
    if not os.path.isfile(f):
        try:
            d = os.path.dirname(f)
            if not os.path.isdir(d):
                os.makedirs(d)
            with open(f, "w") as fd:
                # XXX missing FILEOBJ_EXT_XXX
                for x in iter_env_name():
                    fd.write("#{0}={1}\n".format(x, get_default(x)))
                if __get_setting_use_debug():
                    for x in iter_env_name_private():
                        fd.write("#{0}={1}\n".format(x, get_default(x)))
        except Exception:
            pass # ignore
    if not os.path.isfile(f):
        return -1

    _config.clear()
    for l in open(f):
        l = l.strip()
        if l.startswith("#"):
            continue
        if not l.startswith("FILEOBJ_") and not l.startswith("__FILEOBJ_"):
            continue
        m = _regex.match(l)
        if not m:
            continue
        k, v = m.groups()
        if k not in os.environ: # env variables precede config
            os.environ[k] = v
            _config[k] = v
