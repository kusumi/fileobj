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

def __iter_env():
    yield "FILEOBJ_USE_READONLY", False # -R
    yield "FILEOBJ_USE_BYTES_BUFFER", False # -B
    yield "FILEOBJ_USE_ASCII_EDIT", False # :set binary,ascii
    yield "FILEOBJ_USE_IGNORECASE", False # :set ic
    yield "FILEOBJ_USE_SIPREFIX", False # :set si
    yield "FILEOBJ_USE_WRAPSCAN", True # :set ws
    yield "FILEOBJ_USE_TEXT_WINDOW", True
    yield "FILEOBJ_USE_MOUSE_EVENTS", True
    yield "FILEOBJ_USE_COLOR", True
    yield "FILEOBJ_USE_UNIT_BASED", False
    yield "FILEOBJ_USE_BACKUP", False
    yield "FILEOBJ_USE_TRUNCATE_SHRINK", False
    yield "FILEOBJ_USE_LINE_SCROLL", True
    yield "FILEOBJ_USE_LOWER_CASE_HEX", False
    yield "FILEOBJ_BUFFER_SIZE", 0
    yield "FILEOBJ_LOGICAL_BLOCK_SIZE", 0
    yield "FILEOBJ_ENDIANNESS", None # :set le,be
    yield "FILEOBJ_ADDRESS_RADIX", 16 # :set address
    yield "FILEOBJ_BYTES_PER_LINE", None # --bytes_per_line, :set bytes_per_line
    yield "FILEOBJ_BYTES_PER_WINDOW", None # --bytes_per_window, :set bytes_per_window
    yield "FILEOBJ_BYTES_PER_UNIT", 1 # --bytes_per_unit, :set bytes_per_unit
    yield "FILEOBJ_COLOR_CURRENT", "black,green"
    yield "FILEOBJ_COLOR_ZERO", "green"
    yield "FILEOBJ_COLOR_FF", "magenta"
    yield "FILEOBJ_COLOR_PRINT", "cyan"
    yield "FILEOBJ_COLOR_DEFAULT", "none"
    yield "FILEOBJ_COLOR_VISUAL", "red,yellow"
    yield "FILEOBJ_COLOR_OFFSET", "none"
    yield "FILEOBJ_DISAS_ARCH", "x86"
    yield "FILEOBJ_DISAS_PRIVATE", None

def __iter_env_private():
    yield "__FILEOBJ_USE_DEBUG", False # --debug, unittest (true)
    yield "__FILEOBJ_USE_GETCH", True # unittest (false)
    yield "__FILEOBJ_USE_STDOUT", False # unittest (true)
    yield "__FILEOBJ_USE_CONSOLE_LOG", False # unittest (false)
    yield "__FILEOBJ_USE_SESSION_POSITION", True # unittest (false)
    yield "__FILEOBJ_USE_NATIVE", True
    yield "__FILEOBJ_USE_PATH_ATTR", True
    yield "__FILEOBJ_USE_PID_PATH", True
    yield "__FILEOBJ_USE_TRACE", False
    yield "__FILEOBJ_USE_ALT_CHGAT", False
    yield "__FILEOBJ_USE_CIRCULAR_BIT_SHIFT", True
    yield "__FILEOBJ_USE_SINGLE_OPERATION", False
    yield "__FILEOBJ_USE_DOWNWARD_WINDOW_ADJUST", True
    yield "__FILEOBJ_USE_STATUS_WINDOW_VERBOSE", False
    yield "__FILEOBJ_USE_STATUS_WINDOW_FRAME", False
    yield "__FILEOBJ_USE_AUTO_FILEOPS_ADJUST", True # unittest (false)
    yield "__FILEOBJ_USE_AUTO_FILEOPS_CLEANUP", True # unittest (false)
    yield "__FILEOBJ_USE_FSYNC_CONFIG_FILE", False
    yield "__FILEOBJ_USE_VM_SYNC_ON_EDIT", False
    yield "__FILEOBJ_USE_DELETE_CONSOLE", True # unittest (false)
    yield "__FILEOBJ_USE_ALLOW_PYTHON2", False
    yield "__FILEOBJ_USE_WINDOWS_TERMINAL", False
    yield "__FILEOBJ_USE_TERMINAL_RESIZE", True
    yield "__FILEOBJ_STDOUT_VERBOSE", 1 # unittest (0)
    yield "__FILEOBJ_TRACE_WORD_SIZE", 2
    yield "__FILEOBJ_LOG_LEVEL", "INFO"
    yield "__FILEOBJ_MAX_HISTORY", 1000
    yield "__FILEOBJ_BARRIER_SIZE", 8192
    yield "__FILEOBJ_BARRIER_EXTEND", 1024
    yield "__FILEOBJ_REGFILE_SOFT_LIMIT", ((1 << 20) * 100)
    yield "__FILEOBJ_BUFFER_CHUNK_SIZE", -1
    yield "__FILEOBJ_BUFFER_CHUNK_BALANCE_INTERVAL", 100
    yield "__FILEOBJ_TERMINAL_HEIGHT", -1
    yield "__FILEOBJ_TERMINAL_WIDTH", -1
    yield "__FILEOBJ_PATH_STREAM", None
    yield "__FILEOBJ_COLOR_FB", "none"

_env_default_value = {}

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

def __get_setting_use_color():
    return test_bool("FILEOBJ_USE_COLOR")

def __get_setting_use_unit_based():
    return test_bool("FILEOBJ_USE_UNIT_BASED")

def __get_setting_use_backup():
    return test_bool("FILEOBJ_USE_BACKUP")

def __get_setting_use_truncate_shrink():
    return test_bool("FILEOBJ_USE_TRUNCATE_SHRINK")

def __get_setting_use_line_scroll():
    return test_bool("FILEOBJ_USE_LINE_SCROLL")

def __get_setting_use_lower_case_hex():
    return test_bool("FILEOBJ_USE_LOWER_CASE_HEX")

def __get_setting_buffer_size():
    return test_gt_zero("FILEOBJ_BUFFER_SIZE")

def __get_setting_logical_block_size():
    s = "FILEOBJ_LOGICAL_BLOCK_SIZE"
    ret = test_gt_zero(s)
    if ret % 512 == 0:
        return ret
    else:
        return get_default(s)

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

def __get_setting_color_offset():
    ret = test_name("FILEOBJ_COLOR_OFFSET")
    if not ret or ret.lower() == "none":
        return None
    else:
        return ret

def __get_setting_disas_arch():
    return test_name("FILEOBJ_DISAS_ARCH").lower()

def __get_setting_disas_private():
    return test_name("FILEOBJ_DISAS_PRIVATE")

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

def __get_setting_use_fsync_config_file():
    return test_bool("__FILEOBJ_USE_FSYNC_CONFIG_FILE")

def __get_setting_use_vm_sync_on_edit():
    return test_bool("__FILEOBJ_USE_VM_SYNC_ON_EDIT")

def __get_setting_use_delete_console():
    return test_bool("__FILEOBJ_USE_DELETE_CONSOLE")

def __get_setting_use_allow_python2():
    return test_bool("__FILEOBJ_USE_ALLOW_PYTHON2")

def __get_setting_use_windows_terminal():
    return test_bool("__FILEOBJ_USE_WINDOWS_TERMINAL")

def __get_setting_use_terminal_resize():
    return test_bool("__FILEOBJ_USE_TERMINAL_RESIZE")

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

def __get_setting_path_stream():
    return getenv("__FILEOBJ_PATH_STREAM")

def __get_setting_color_fb():
    ret = test_name("__FILEOBJ_COLOR_FB")
    if not ret or ret.lower() == "none":
        return None
    else:
        return ret

def iter_env_name():
    for l in sorted(__iter_env()):
        yield l[0]

def iter_env_name_private():
    for l in sorted(__iter_env_private()):
        yield l[0]

def iter_defined_env():
    envs = list(iter_env_name()) + list(iter_env_name_private())
    for l in __iter_os_environ():
        if l[0] in envs:
            yield l

def iter_defined_ext_env():
    _ = tuple(iter_ext_env_name())
    for l in __iter_os_environ():
        if l[0] in _:
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

# ext env related are handled separately
_ext_env = {}

def ext_env_add(k, v):
    if v is None:
        del _ext_env[k]
    else:
        assert isinstance(v, str), v
        if k not in _ext_env:
            _ext_env[k] = v

def ext_env_get(k):
    return _ext_env.get(k, "")

def iter_ext_env_name():
    for x in sorted(_ext_env.keys()):
        yield x

# called from setting import, i.e. can't use other fileobj modules
def init(f):
    for k, v in __iter_env():
        _env_default_value[k] = v
    for k, v in __iter_env_private():
        _env_default_value[k] = v

    _config.clear()
    assert f, f
    if os.path.isfile(f):
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

def __write_config(fd, k):
    v = get_default(k)
    if v is None:
        v = ""
    fd.write("#{0}={1}\n".format(k, v))

def cleanup(f, use_debug):
    assert f, f
    if not os.path.isfile(f):
        try:
            d = os.path.dirname(f)
            if not os.path.isdir(d):
                os.makedirs(d)
            with open(f, "w") as fd:
                for x in iter_env_name():
                    __write_config(fd, x)
                for x in iter_ext_env_name():
                    __write_config(fd, x)
                if use_debug:
                    for x in iter_env_name_private():
                        __write_config(fd, x)
        except Exception:
            if use_debug: # ignore unless use_debug
                raise
    _ext_env.clear() # last
