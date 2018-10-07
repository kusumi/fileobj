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

import os
import sys

# considered stable interface, officially introduced in version 0.7.74
def __iter_env_name():
    yield "FILEOBJ_USE_READONLY" # -R
    yield "FILEOBJ_USE_BYTES_BUFFER" # -B
    yield "FILEOBJ_USE_ASCII_EDIT" # :set binary,ascii
    yield "FILEOBJ_USE_IGNORECASE" # :set ic
    yield "FILEOBJ_USE_SIPREFIX" # :set si
    yield "FILEOBJ_USE_WRAPSCAN" # :set ws
    yield "FILEOBJ_USE_TEXT_WINDOW"
    yield "FILEOBJ_USE_BACKUP"
    yield "FILEOBJ_ENDIANNESS" # :set le,be
    yield "FILEOBJ_ADDRESS_RADIX" # -x, :set address <arg>
    yield "FILEOBJ_STATUS_RADIX" # -x, :set status <arg>
    yield "FILEOBJ_BYTES_PER_LINE" # --bytes_per_line, :set bytes_per_line
    yield "FILEOBJ_BYTES_PER_WINDOW" # --bytes_per_window, :set bytes_per_window
    yield "FILEOBJ_COLOR_FG" # --fg
    yield "FILEOBJ_COLOR_BG" # --bg
    yield "FILEOBJ_COLOR_CURRENT"
    yield "FILEOBJ_COLOR_ZERO"
    yield "FILEOBJ_COLOR_PRINT"

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
    yield "__FILEOBJ_KEY_BACKSPACE"
    yield "__FILEOBJ_KEY_DELETE"

def getenv(envname):
    return os.getenv(envname)

def test_bool(envname, default):
    e = getenv(envname)
    if e is None:
        return default
    else:
        return e.lower() != "false"

def test_name(envname, default):
    e = getenv(envname)
    if e is None:
        return default
    else:
        return e

def test_gt_zero(envname, default):
    e = getenv(envname)
    if e is None:
        return default
    ret = __env_gt_zero(e)
    if ret is None:
        return default
    else:
        return ret

def test_ge_zero(envname, default):
    e = getenv(envname)
    if e is None:
        return default
    ret = __env_ge_zero(e)
    if ret is None:
        return default
    else:
        return ret

def __env_gt_zero(e):
    try:
        x = int(e)
        if x > 0:
            return x
    except Exception:
        pass

def __env_ge_zero(e):
    try:
        x = int(e)
        if x >= 0:
            return x
    except Exception:
        pass

def __get_setting_use_readonly():
    return test_bool("FILEOBJ_USE_READONLY", False)

def __get_setting_use_bytes_buffer():
    return test_bool("FILEOBJ_USE_BYTES_BUFFER", False)

def __get_setting_use_ascii_edit():
    return test_bool("FILEOBJ_USE_ASCII_EDIT", False)

def __get_setting_use_ignorecase():
    return test_bool("FILEOBJ_USE_IGNORECASE", False)

def __get_setting_use_siprefix():
    return test_bool("FILEOBJ_USE_SIPREFIX", False)

def __get_setting_use_wrapscan():
    return test_bool("FILEOBJ_USE_WRAPSCAN", True)

def __get_setting_use_text_window():
    return test_bool("FILEOBJ_USE_TEXT_WINDOW", True)

def __get_setting_use_backup():
    return test_bool("FILEOBJ_USE_BACKUP", False)

def __get_setting_endianness():
    e = getenv("FILEOBJ_ENDIANNESS")
    if e is None:
        return None
    elif e.lower() == "little":
        return "little"
    elif e.lower() == "big":
        return "big"
    else:
        return None

def __get_setting_address_radix():
    return __get_setting_radix("FILEOBJ_ADDRESS_RADIX", 16)

def __get_setting_status_radix():
    return __get_setting_radix("FILEOBJ_STATUS_RADIX", 10)

def __get_setting_radix(envname, default):
    e = getenv(envname)
    if e is None:
        return default
    try:
        x = int(e)
        if x in (16, 10, 8):
            return x
    except Exception:
        pass
    return default

def __get_setting_bytes_per_line():
    e = getenv("FILEOBJ_BYTES_PER_LINE")
    if e is None:
        return None
    else:
        return e.lower() # return str even if e is \d+

def __get_setting_bytes_per_window():
    e = getenv("FILEOBJ_BYTES_PER_WINDOW")
    if e is None:
        return None
    else:
        return e.lower() # return str even if e is \d+

def __get_setting_color_fg():
    e = getenv("FILEOBJ_COLOR_FG")
    if e is None:
        return None
    else:
        return e.lower()

def __get_setting_color_bg():
    e = getenv("FILEOBJ_COLOR_BG")
    if e is None:
        return None
    else:
        return e.lower()

def __get_setting_color_current():
    ret = test_name("FILEOBJ_COLOR_CURRENT", "green")
    if not ret or ret.lower() == "none": # disable
        return None
    else:
        return ret

def __get_setting_color_zero():
    ret = test_name("FILEOBJ_COLOR_ZERO", "green")
    if not ret or ret.lower() == "none": # disable
        return None
    else:
        return ret

def __get_setting_color_print():
    ret = test_name("FILEOBJ_COLOR_PRINT", "cyan")
    if not ret or ret.lower() == "none": # disable
        return None
    else:
        return ret

def __get_setting_use_debug():
    return test_bool("__FILEOBJ_USE_DEBUG", False)

def __get_setting_use_getch():
    return test_bool("__FILEOBJ_USE_GETCH", True)

def __get_setting_use_stdout():
    return test_bool("__FILEOBJ_USE_STDOUT", False)

def __get_setting_use_console_log():
    return test_bool("__FILEOBJ_USE_CONSOLE_LOG", False)

def __get_setting_use_session_position():
    return test_bool("__FILEOBJ_USE_SESSION_POSITION", True)

def __get_setting_use_native():
    return test_bool("__FILEOBJ_USE_NATIVE", True)

def __get_setting_use_path_attr():
    return test_bool("__FILEOBJ_USE_PATH_ATTR", True)

def __get_setting_use_pid_path():
    return test_bool("__FILEOBJ_USE_PID_PATH", True)

def __get_setting_use_trace():
    return test_bool("__FILEOBJ_USE_TRACE", False)

def __get_setting_use_alt_chgat():
    return test_bool("__FILEOBJ_USE_ALT_CHGAT", False)

def __get_setting_use_circular_bit_shift():
    return test_bool("__FILEOBJ_USE_CIRCULAR_BIT_SHIFT", True)

def __get_setting_use_single_operation():
    return test_bool("__FILEOBJ_USE_SINGLE_OPERATION", False)

def __get_setting_use_downward_window_adjust():
    return test_bool("__FILEOBJ_USE_DOWNWARD_WINDOW_ADJUST", True)

def __get_setting_use_status_window_verbose():
    return test_bool("__FILEOBJ_USE_STATUS_WINDOW_VERBOSE", False)

def __get_setting_use_status_window_frame():
    return test_bool("__FILEOBJ_USE_STATUS_WINDOW_FRAME", False)

def __get_setting_use_auto_fileops_adjust():
    return test_bool("__FILEOBJ_USE_AUTO_FILEOPS_ADJUST", True)

def __get_setting_use_auto_fileops_cleanup():
    return test_bool("__FILEOBJ_USE_AUTO_FILEOPS_CLEANUP", True)

def __get_setting_use_vm_sync_on_edit():
    return test_bool("__FILEOBJ_USE_VM_SYNC_ON_EDIT", False)

def __get_setting_stdout_verbose():
    return test_ge_zero("__FILEOBJ_STDOUT_VERBOSE", 1)

def __get_setting_trace_word_size():
    e = getenv("__FILEOBJ_TRACE_WORD_SIZE")
    _ = 2
    if e is None:
        return _
    x = __env_gt_zero(e)
    if x in (2, 4, 8): # no 1
        return x
    else:
        return _

def __get_setting_log_level():
    return test_name("__FILEOBJ_LOG_LEVEL", "INFO")

def __get_setting_max_history():
    return test_gt_zero("__FILEOBJ_MAX_HISTORY", 1000)

def __get_setting_barrier_size():
    return test_gt_zero("__FILEOBJ_BARRIER_SIZE", 8192)

def __get_setting_barrier_extend():
    return test_gt_zero("__FILEOBJ_BARRIER_EXTEND", 1024)

# default 100 MiB
def __get_setting_regfile_soft_limit():
    return test_ge_zero("__FILEOBJ_REGFILE_SOFT_LIMIT", (1 << 20) * 100)

def __get_setting_buffer_chunk_size():
    return test_gt_zero("__FILEOBJ_BUFFER_CHUNK_SIZE", -1)

def __get_setting_buffer_chunk_balance_interval():
    return test_gt_zero("__FILEOBJ_BUFFER_CHUNK_BALANCE_INTERVAL", 100)

def __get_setting_terminal_height():
    return test_gt_zero("__FILEOBJ_TERMINAL_HEIGHT", -1)

def __get_setting_terminal_width():
    return test_gt_zero("__FILEOBJ_TERMINAL_WIDTH", -1)

def __get_setting_temp_size():
    return test_gt_zero("__FILEOBJ_TEMP_SIZE", -1)

def __get_setting_path_stream():
    return getenv("__FILEOBJ_PATH_STREAM")

def __get_setting_key_backspace():
    return __get_setting_key("__FILEOBJ_KEY_BACKSPACE")

def __get_setting_key_delete():
    return __get_setting_key("__FILEOBJ_KEY_DELETE")

def __get_setting_key(envname):
    e = getenv(envname)
    if e is None:
        return None
    try:
        if e.startswith("0b") and len(e) > 2:
            return int(e[2:], 2)
        elif e.startswith("0x") and len(e) > 2:
            return int(e[2:], 16)
        elif e.startswith("0") and len(e) > 1:
            return int(e[1:], 8)
        else:
            return int(e)
    except Exception:
        return None

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
