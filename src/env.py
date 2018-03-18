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

from __future__ import division
import os
import sys

def __iter_env_name():
    """These variables may be renamed or removed without notice."""
    yield "FILEOBJ_USE_DEBUG" # --debug, unittest (true)
    yield "FILEOBJ_USE_FORCE" # --force
    yield "FILEOBJ_USE_GETCH" # unittest (false)
    yield "FILEOBJ_USE_STDOUT" # unittest (true)
    yield "FILEOBJ_STDOUT_VERBOSE" # unittest (0)
    yield "FILEOBJ_USE_PATH_ATTR"
    yield "FILEOBJ_USE_PID_PATH"
    yield "FILEOBJ_USE_SHELL"
    yield "FILEOBJ_USE_TRACE"
    yield "FILEOBJ_TRACE_WORD_SIZE"
    yield "FILEOBJ_USE_READONLY" # -R
    yield "FILEOBJ_USE_BACKUP" # --backup
    yield "FILEOBJ_COLOR_FG" # --fg
    yield "FILEOBJ_COLOR_BG" # --bg
    yield "FILEOBJ_LOG_LEVEL"
    yield "FILEOBJ_MAX_HISTORY"
    yield "FILEOBJ_BARRIER_SIZE"
    yield "FILEOBJ_BARRIER_EXTEND"
    yield "FILEOBJ_USE_CURSOR_FALL_THROUGH"
    yield "FILEOBJ_USE_ALT_CHGAT"
    yield "FILEOBJ_USE_CIRCULAR_BIT_SHIFT"
    yield "FILEOBJ_USE_SINGLE_OPERATION"
    yield "FILEOBJ_USE_EVEN_SIZE_WINDOW"
    yield "FILEOBJ_USE_DOWNWARD_WINDOW_ADJUST"
    yield "FILEOBJ_USE_VERBOSE_STATUS_WINDOW" # --verbose_window
    yield "FILEOBJ_USE_STATUS_WINDOW_FRAME" # --verbose_window
    yield "FILEOBJ_USE_ADDRESS_NUM_OFFSET" # -d
    yield "FILEOBJ_ADDRESS_NUM_RADIX" # :set
    yield "FILEOBJ_STATUS_NUM_RADIX" # -x, :set
    yield "FILEOBJ_EDITMODE" # :set
    yield "FILEOBJ_ENDIANNESS" # :set
    yield "FILEOBJ_USE_WRAPSCAN" # :set
    yield "FILEOBJ_USE_IGNORECASE" # :set
    yield "FILEOBJ_USE_SIPREFIX" # :set
    yield "FILEOBJ_BYTES_PER_LINE" # --bytes_per_line, :set
    yield "FILEOBJ_BYTES_PER_WINDOW" # --bytes_per_window, :set
    yield "FILEOBJ_USE_ALLOC_NOENT_RWBUF"
    yield "FILEOBJ_USE_AUTO_FILEOPS_ADJUST" # unittest (false)
    yield "FILEOBJ_USE_AUTO_FILEOPS_CLEANUP" # unittest (false)
    yield "FILEOBJ_REGFILE_SOFT_LIMIT"
    yield "FILEOBJ_USE_RRVM_SYNC_ON_EDIT"
    yield "FILEOBJ_USE_PS_AUX"
    yield "FILEOBJ_ROBUF_CHUNK_SIZE"
    yield "FILEOBJ_RWBUF_CHUNK_BALANCE_INTERVAL"
    yield "FILEOBJ_RWBUF_CHUNK_SIZE_LOW"
    yield "FILEOBJ_RWBUF_CHUNK_SIZE_HIGH"
    yield "FILEOBJ_USE_NATIVE"
    yield "FILEOBJ_OS_UNAME"
    yield "FILEOBJ_USE_BSD_CAVEAT"
    yield "FILEOBJ_USE_ILLUMOS_CAVEAT"
    yield "FILEOBJ_USE_CYGWIN_CAVEAT"
    yield "FILEOBJ_USE_PUTTY_CAVEAT" # doc/README.notes.md
    yield "FILEOBJ_BUFFER_SIZE"
    yield "FILEOBJ_USER_DIR"
    yield "FILEOBJ_PATH_STREAM"
    yield "FILEOBJ_KEY_DOWN"
    yield "FILEOBJ_KEY_UP"
    yield "FILEOBJ_KEY_LEFT"
    yield "FILEOBJ_KEY_RIGHT"
    yield "FILEOBJ_KEY_BACKSPACE"
    yield "FILEOBJ_KEY_DELETE"
    yield "FILEOBJ_KEY_RESIZE"

# use this instead of os.getenv(),
# since setting expects None for not existing envs
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

def __get_setting_use_debug():
    return test_bool("FILEOBJ_USE_DEBUG", False)

def __get_setting_use_force():
    return test_bool("FILEOBJ_USE_FORCE", False)

def __get_setting_use_getch():
    return test_bool("FILEOBJ_USE_GETCH", True)

def __get_setting_use_stdout():
    return test_bool("FILEOBJ_USE_STDOUT", False)

def __get_setting_stdout_verbose():
    return test_ge_zero("FILEOBJ_STDOUT_VERBOSE", 1)

def __get_setting_use_path_attr():
    return test_bool("FILEOBJ_USE_PATH_ATTR", True)

def __get_setting_use_pid_path():
    return test_bool("FILEOBJ_USE_PID_PATH", True)

def __get_setting_use_shell():
    return test_bool("FILEOBJ_USE_SHELL", False)

def __get_setting_use_trace():
    return test_bool("FILEOBJ_USE_TRACE", False)

def __get_setting_trace_word_size():
    e = getenv("FILEOBJ_TRACE_WORD_SIZE")
    _ = 2
    if e is None:
        return _
    x = __env_gt_zero(e)
    if x in (2, 4, 8): # no 1
        return x
    else:
        return _

def __get_setting_use_readonly():
    return test_bool("FILEOBJ_USE_READONLY", False)

def __get_setting_use_backup():
    return test_bool("FILEOBJ_USE_BACKUP", False)

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

def __get_setting_log_level():
    return test_name("FILEOBJ_LOG_LEVEL", "WARNING")

def __get_setting_max_history():
    return test_gt_zero("FILEOBJ_MAX_HISTORY", 1000)

def __get_setting_barrier_size():
    return test_gt_zero("FILEOBJ_BARRIER_SIZE", 8192)

def __get_setting_barrier_extend():
    return test_gt_zero("FILEOBJ_BARRIER_EXTEND", 1024)

def __get_setting_use_cursor_fall_through():
    return test_bool("FILEOBJ_USE_CURSOR_FALL_THROUGH", False)

def __get_setting_use_alt_chgat():
    return test_bool("FILEOBJ_USE_ALT_CHGAT", False)

def __get_setting_use_circular_bit_shift():
    return test_bool("FILEOBJ_USE_CIRCULAR_BIT_SHIFT", True)

def __get_setting_use_single_operation():
    return test_bool("FILEOBJ_USE_SINGLE_OPERATION", False)

def __get_setting_use_even_size_window():
    return test_bool("FILEOBJ_USE_EVEN_SIZE_WINDOW", False)

def __get_setting_use_downward_window_adjust():
    return test_bool("FILEOBJ_USE_DOWNWARD_WINDOW_ADJUST", True)

def __get_setting_use_verbose_status_window():
    return test_bool("FILEOBJ_USE_VERBOSE_STATUS_WINDOW", False)

def __get_setting_use_status_window_frame():
    return test_bool("FILEOBJ_USE_STATUS_WINDOW_FRAME", False)

def __get_setting_use_address_num_offset():
    return test_bool("FILEOBJ_USE_ADDRESS_NUM_OFFSET", False)

def __get_setting_address_num_radix():
    return __get_setting_radix("FILEOBJ_ADDRESS_NUM_RADIX", 16)

def __get_setting_status_num_radix():
    return __get_setting_radix("FILEOBJ_STATUS_NUM_RADIX", 10)

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

def __get_setting_editmode():
    e = getenv("FILEOBJ_EDITMODE")
    if e is None:
        return 'B'
    elif e[0].upper() == 'A':
        return 'A'
    else:
        return 'B'

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

def __get_setting_use_wrapscan():
    return test_bool("FILEOBJ_USE_WRAPSCAN", True)

def __get_setting_use_ignorecase():
    return test_bool("FILEOBJ_USE_IGNORECASE", False)

def __get_setting_use_siprefix():
    return test_bool("FILEOBJ_USE_SIPREFIX", False)

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

def __get_setting_use_alloc_noent_rwbuf():
    return test_bool("FILEOBJ_USE_ALLOC_NOENT_RWBUF", True)

def __get_setting_use_auto_fileops_adjust():
    return test_bool("FILEOBJ_USE_AUTO_FILEOPS_ADJUST", True)

def __get_setting_use_auto_fileops_cleanup():
    return test_bool("FILEOBJ_USE_AUTO_FILEOPS_CLEANUP", True)

# default 100 MiB
def __get_setting_regfile_soft_limit():
    return test_ge_zero("FILEOBJ_REGFILE_SOFT_LIMIT", (1 << 20) * 100)

def __get_setting_use_rrvm_sync_on_edit():
    return test_bool("FILEOBJ_USE_RRVM_SYNC_ON_EDIT", False)

def __get_setting_use_ps_aux():
    return test_bool("FILEOBJ_USE_PS_AUX", True)

def __get_setting_robuf_chunk_size():
    try:
        siz = os.sysconf("SC_PAGE_SIZE")
    except Exception:
        siz = 4096
    return test_gt_zero("FILEOBJ_ROBUF_CHUNK_SIZE", siz)

def __get_setting_rwbuf_chunk_balance_interval():
    return test_gt_zero("FILEOBJ_RWBUF_CHUNK_BALANCE_INTERVAL", 100)

def __get_setting_rwbuf_chunk_size_low():
    e = getenv("FILEOBJ_RWBUF_CHUNK_SIZE_LOW")
    chunk_size = __get_setting_robuf_chunk_size()
    _ = chunk_size // 5
    if e is None:
        return _
    x = __env_gt_zero(e)
    if x is None or x >= chunk_size:
        return _
    else:
        return x

def __get_setting_rwbuf_chunk_size_high():
    e = getenv("FILEOBJ_RWBUF_CHUNK_SIZE_HIGH")
    chunk_size = __get_setting_robuf_chunk_size()
    _ = chunk_size * 5
    if e is None:
        return _
    x = __env_gt_zero(e)
    if x is None or x <= chunk_size:
        return _
    else:
        return x

def __get_setting_use_native():
    return test_bool("FILEOBJ_USE_NATIVE", True)

def __get_setting_os_uname():
    return getenv("FILEOBJ_OS_UNAME")

def __get_setting_use_bsd_caveat():
    return test_bool("FILEOBJ_USE_BSD_CAVEAT", False)

def __get_setting_use_illumos_caveat():
    return test_bool("FILEOBJ_USE_ILLUMOS_CAVEAT", False)

def __get_setting_use_cygwin_caveat():
    return test_bool("FILEOBJ_USE_CYGWIN_CAVEAT", False)

def __get_setting_use_putty_caveat():
    return test_bool("FILEOBJ_USE_PUTTY_CAVEAT", False)

def __get_setting_buffer_size():
    return test_gt_zero("FILEOBJ_BUFFER_SIZE", -1)

def __get_setting_user_dir():
    d = os.path.join(os.path.expanduser("~"), ".fileobj")
    return test_name("FILEOBJ_USER_DIR", d)

def __get_setting_path_stream():
    return getenv("FILEOBJ_PATH_STREAM")

def __get_setting_key_down():
    return __get_setting_key("FILEOBJ_KEY_DOWN")

def __get_setting_key_up():
    return __get_setting_key("FILEOBJ_KEY_UP")

def __get_setting_key_left():
    return __get_setting_key("FILEOBJ_KEY_LEFT")

def __get_setting_key_right():
    return __get_setting_key("FILEOBJ_KEY_RIGHT")

def __get_setting_key_backspace():
    return __get_setting_key("FILEOBJ_KEY_BACKSPACE")

def __get_setting_key_delete():
    return __get_setting_key("FILEOBJ_KEY_DELETE")

def __get_setting_key_resize():
    return __get_setting_key("FILEOBJ_KEY_RESIZE")

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
        assert not x.startswith("FILEOBJ_EXT_"), x
        yield x

def iter_defined_env():
    envs = list(iter_env_name())
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
    this = sys.modules[__name__]
    for x in iter_env_name():
        name = x[len("FILEOBJ_"):].lower()
        fn = getattr(this, "__get_setting_" + name)
        yield name, fn()
