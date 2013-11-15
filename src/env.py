# Copyright (c) 2010-2013, TOMOHIRO KUSUMI
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

def iter_env_name():
    yield "FILEOBJ_USE_DEBUG"
    yield "FILEOBJ_USE_CURSES"
    yield "FILEOBJ_USE_TRACE"
    yield "FILEOBJ_USE_TRACE_SYMLINK"
    yield "FILEOBJ_TRACE_WORD_SIZE"
    yield "FILEOBJ_TRACE_PATH"
    yield "FILEOBJ_TRACE_BASE"
    yield "FILEOBJ_TRACE_DIR"
    yield "FILEOBJ_STREAM_PATH"
    yield "FILEOBJ_STREAM_BASE"
    yield "FILEOBJ_STREAM_DIR"
    yield "FILEOBJ_USERDIR_PATH"
    yield "FILEOBJ_USERDIR_BASE"
    yield "FILEOBJ_USERDIR_DIR"
    yield "FILEOBJ_PROCFS_MOUNT_DIR"
    yield "FILEOBJ_USE_READONLY"
    yield "FILEOBJ_COLOR_FG"
    yield "FILEOBJ_COLOR_BG"
    yield "FILEOBJ_USE_LOG"
    yield "FILEOBJ_USE_LOG_VERBOSE"
    yield "FILEOBJ_LOG_LEVEL"
    yield "FILEOBJ_LOG_PATH"
    yield "FILEOBJ_LOG_BASE"
    yield "FILEOBJ_LOG_DIR"
    yield "FILEOBJ_USE_HISTORY"
    yield "FILEOBJ_MAX_HISTORY"
    yield "FILEOBJ_HISTORY_PATH"
    yield "FILEOBJ_HISTORY_BASE"
    yield "FILEOBJ_HISTORY_DIR"
    yield "FILEOBJ_USE_BARRIER"
    yield "FILEOBJ_BARRIER_SIZE"
    yield "FILEOBJ_BARRIER_EXTEND"
    yield "FILEOBJ_USE_ALT_CHGAT"
    yield "FILEOBJ_USE_CIRCULAR_BIT_SHIFT"
    yield "FILEOBJ_USE_SINGLE_OPERATION"
    yield "FILEOBJ_RAM_THRESH_RATIO"
    yield "FILEOBJ_USE_EVEN_SIZE_WINDOW"
    yield "FILEOBJ_OFFSET_NUM_WIDTH"
    yield "FILEOBJ_OFFSET_NUM_RADIX"
    yield "FILEOBJ_EDITMODE"
    yield "FILEOBJ_ENDIANNESS"
    yield "FILEOBJ_USE_WRAPSCAN"
    yield "FILEOBJ_USE_IGNORECASE"
    yield "FILEOBJ_USE_SIPREFIX"
    yield "FILEOBJ_WIDTH"
    yield "FILEOBJ_USE_MAGIC_SCAN"
    yield "FILEOBJ_USE_ALLOC_RETRY"
    yield "FILEOBJ_USE_ALLOC_RAISE"
    yield "FILEOBJ_USE_ARRAY_CHUNK"
    yield "FILEOBJ_MMAP_THRESH"
    yield "FILEOBJ_ROBUF_CHUNK_SIZE"
    yield "FILEOBJ_ROBUF_SEARCH_THRESH_RATIO"
    yield "FILEOBJ_RWBUF_CHUNK_BALANCE_INTERVAL"
    yield "FILEOBJ_RWBUF_CHUNK_SIZE_LOW"
    yield "FILEOBJ_RWBUF_CHUNK_SIZE_HIGH"
    yield "FILEOBJ_ROFD_READ_QUEUE_SIZE"
    yield "FILEOBJ_EXT_STRINGS_RANGE"
    yield "FILEOBJ_EXT_STRINGS_COUNT"
    yield "FILEOBJ_EXT_STRINGS_THRESH"
    yield "FILEOBJ_EXT_CSTRUCT_PATH"
    yield "FILEOBJ_EXT_CSTRUCT_BASE"
    yield "FILEOBJ_EXT_CSTRUCT_DIR"
    yield "FILEOBJ_KEY_TAB"
    yield "FILEOBJ_KEY_ENTER"
    yield "FILEOBJ_KEY_ESCAPE"
    yield "FILEOBJ_KEY_SPACE"
    yield "FILEOBJ_KEY_DOWN"
    yield "FILEOBJ_KEY_UP"
    yield "FILEOBJ_KEY_LEFT"
    yield "FILEOBJ_KEY_RIGHT"
    yield "FILEOBJ_KEY_BACKSPACE"
    yield "FILEOBJ_KEY_DELETE"
    yield "FILEOBJ_KEY_RESIZE"

def get_setting(s):
    if s == "FILEOBJ_USE_DEBUG":
        return _get_setting_use_debug()
    elif s == "FILEOBJ_USE_CURSES":
        return _get_setting_use_curses()
    elif s == "FILEOBJ_USE_TRACE":
        return _get_setting_use_trace()
    elif s == "FILEOBJ_USE_TRACE_SYMLINK":
        return _get_setting_use_trace_symlink()
    elif s == "FILEOBJ_TRACE_WORD_SIZE":
        return _get_setting_trace_word_size()
    elif s == "FILEOBJ_TRACE_PATH":
        return _get_setting_trace_path()
    elif s == "FILEOBJ_TRACE_BASE":
        return _get_setting_trace_base()
    elif s == "FILEOBJ_TRACE_DIR":
        return _get_setting_trace_dir()
    elif s == "FILEOBJ_STREAM_PATH":
        return _get_setting_stream_path()
    elif s == "FILEOBJ_STREAM_BASE":
        return _get_setting_stream_base()
    elif s == "FILEOBJ_STREAM_DIR":
        return _get_setting_stream_dir()
    elif s == "FILEOBJ_USERDIR_PATH":
        return _get_setting_userdir_path()
    elif s == "FILEOBJ_USERDIR_BASE":
        return _get_setting_userdir_base()
    elif s == "FILEOBJ_USERDIR_DIR":
        return _get_setting_userdir_dir()
    elif s == "FILEOBJ_PROCFS_MOUNT_DIR":
        return _get_setting_procfs_mount_dir()
    elif s == "FILEOBJ_USE_READONLY":
        return _get_setting_use_readonly()
    elif s == "FILEOBJ_COLOR_FG":
        return _get_setting_color_fg()
    elif s == "FILEOBJ_COLOR_BG":
        return _get_setting_color_bg()
    elif s == "FILEOBJ_USE_LOG":
        return _get_setting_use_log()
    elif s == "FILEOBJ_USE_LOG_VERBOSE":
        return _get_setting_use_log_verbose()
    elif s == "FILEOBJ_LOG_LEVEL":
        return _get_setting_log_level()
    elif s == "FILEOBJ_LOG_PATH":
        return _get_setting_log_path()
    elif s == "FILEOBJ_LOG_BASE":
        return _get_setting_log_base()
    elif s == "FILEOBJ_LOG_DIR":
        return _get_setting_log_dir()
    elif s == "FILEOBJ_USE_HISTORY":
        return _get_setting_use_history()
    elif s == "FILEOBJ_MAX_HISTORY":
        return _get_setting_max_history()
    elif s == "FILEOBJ_HISTORY_PATH":
        return _get_setting_history_path()
    elif s == "FILEOBJ_HISTORY_BASE":
        return _get_setting_history_base()
    elif s == "FILEOBJ_HISTORY_DIR":
        return _get_setting_history_dir()
    elif s == "FILEOBJ_USE_BARRIER":
        return _get_setting_use_barrier()
    elif s == "FILEOBJ_BARRIER_SIZE":
        return _get_setting_barrier_size()
    elif s == "FILEOBJ_BARRIER_EXTEND":
        return _get_setting_barrier_extend()
    elif s == "FILEOBJ_USE_ALT_CHGAT":
        return _get_setting_use_alt_chgat()
    elif s == "FILEOBJ_USE_CIRCULAR_BIT_SHIFT":
        return _get_setting_use_circular_bit_shift()
    elif s == "FILEOBJ_USE_SINGLE_OPERATION":
        return _get_setting_use_single_operation()
    elif s == "FILEOBJ_RAM_THRESH_RATIO":
        return _get_setting_ram_thresh_ratio()
    elif s == "FILEOBJ_USE_EVEN_SIZE_WINDOW":
        return _get_setting_use_even_size_window()
    elif s == "FILEOBJ_OFFSET_NUM_WIDTH":
        return _get_setting_offset_num_width()
    elif s == "FILEOBJ_OFFSET_NUM_RADIX":
        return _get_setting_offset_num_radix()
    elif s == "FILEOBJ_EDITMODE":
        return _get_setting_editmode()
    elif s == "FILEOBJ_ENDIANNESS":
        return _get_setting_endianness()
    elif s == "FILEOBJ_USE_WRAPSCAN":
        return _get_setting_use_wrapscan()
    elif s == "FILEOBJ_USE_IGNORECASE":
        return _get_setting_use_ignorecase()
    elif s == "FILEOBJ_USE_SIPREFIX":
        return _get_setting_use_siprefix()
    elif s == "FILEOBJ_WIDTH":
        return _get_setting_width()
    elif s == "FILEOBJ_USE_MAGIC_SCAN":
        return _get_setting_use_magic_scan()
    elif s == "FILEOBJ_USE_ALLOC_RETRY":
        return _get_setting_use_alloc_retry()
    elif s == "FILEOBJ_USE_ALLOC_RAISE":
        return _get_setting_use_alloc_raise()
    elif s == "FILEOBJ_USE_ARRAY_CHUNK":
        return _get_setting_use_array_chunk()
    elif s == "FILEOBJ_MMAP_THRESH":
        return _get_setting_mmap_thresh()
    elif s == "FILEOBJ_ROBUF_CHUNK_SIZE":
        return _get_setting_robuf_chunk_size()
    elif s == "FILEOBJ_ROBUF_SEARCH_THRESH_RATIO":
        return _get_setting_robuf_search_thresh_ratio()
    elif s == "FILEOBJ_RWBUF_CHUNK_BALANCE_INTERVAL":
        return _get_setting_rwbuf_chunk_balance_interval()
    elif s == "FILEOBJ_RWBUF_CHUNK_SIZE_LOW":
        return _get_setting_rwbuf_chunk_size_low()
    elif s == "FILEOBJ_RWBUF_CHUNK_SIZE_HIGH":
        return _get_setting_rwbuf_chunk_size_high()
    elif s == "FILEOBJ_ROFD_READ_QUEUE_SIZE":
        return _get_setting_rofd_read_queue_size()
    elif s == "FILEOBJ_EXT_STRINGS_RANGE":
        return _get_setting_ext_strings_range()
    elif s == "FILEOBJ_EXT_STRINGS_COUNT":
        return _get_setting_ext_strings_count()
    elif s == "FILEOBJ_EXT_STRINGS_THRESH":
        return _get_setting_ext_strings_thresh()
    elif s == "FILEOBJ_EXT_CSTRUCT_PATH":
        return _get_setting_ext_cstruct_path()
    elif s == "FILEOBJ_EXT_CSTRUCT_BASE":
        return _get_setting_ext_cstruct_base()
    elif s == "FILEOBJ_EXT_CSTRUCT_DIR":
        return _get_setting_ext_cstruct_dir()
    elif s == "FILEOBJ_KEY_TAB":
        return _get_setting_key_config(s)
    elif s == "FILEOBJ_KEY_ENTER":
        return _get_setting_key_config(s)
    elif s == "FILEOBJ_KEY_ESCAPE":
        return _get_setting_key_config(s)
    elif s == "FILEOBJ_KEY_SPACE":
        return _get_setting_key_config(s)
    elif s == "FILEOBJ_KEY_DOWN":
        return _get_setting_key_config(s)
    elif s == "FILEOBJ_KEY_UP":
        return _get_setting_key_config(s)
    elif s == "FILEOBJ_KEY_LEFT":
        return _get_setting_key_config(s)
    elif s == "FILEOBJ_KEY_RIGHT":
        return _get_setting_key_config(s)
    elif s == "FILEOBJ_KEY_BACKSPACE":
        return _get_setting_key_config(s)
    elif s == "FILEOBJ_KEY_DELETE":
        return _get_setting_key_config(s)
    elif s == "FILEOBJ_KEY_RESIZE":
        return _get_setting_key_config(s)
    else:
        assert 0, "Invalid env: %s" % s

def _test_bool(e):
    return e.lower() != "false"

def _test_gt_zero(e):
    try:
        x = int(e)
        if x > 0:
            return x
    except Exception:
        pass

def _test_ge_zero(e):
    try:
        x = int(e)
        if x >= 0:
            return x
    except Exception:
        pass

def _test_ratio(e):
    try:
        x = int(e)
        if 0 <= x <= 100:
            return x / 100.0
    except Exception:
        pass

def _get_setting_use_debug():
    e = this.FILEOBJ_USE_DEBUG
    if e is None:
        return False
    else:
        return _test_bool(e)

def _get_setting_use_curses():
    e = this.FILEOBJ_USE_CURSES
    if e is None:
        return True
    else:
        return _test_bool(e)

def _get_setting_use_trace():
    e = this.FILEOBJ_USE_TRACE
    if e is None:
        return False
    else:
        return _test_bool(e)

def _get_setting_use_trace_symlink():
    e = this.FILEOBJ_USE_TRACE_SYMLINK
    if e is None:
        return False
    else:
        return _test_bool(e)

def _get_setting_trace_word_size():
    e = this.FILEOBJ_TRACE_WORD_SIZE
    _ = 2
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x in (2, 4, 8): # no 1
        return x
    else:
        return _

def _get_setting_trace_path():
    return this.FILEOBJ_TRACE_PATH

def _get_setting_trace_base():
    e = this.FILEOBJ_TRACE_BASE
    if e is None:
        return "trace"
    else:
        return e

def _get_setting_trace_dir():
    return this.FILEOBJ_TRACE_DIR

def _get_setting_stream_path():
    return this.FILEOBJ_STREAM_PATH

def _get_setting_stream_base():
    return this.FILEOBJ_STREAM_BASE

def _get_setting_stream_dir():
    return this.FILEOBJ_STREAM_DIR

def _get_setting_userdir_path():
    return this.FILEOBJ_USERDIR_PATH

def _get_setting_userdir_base():
    e = this.FILEOBJ_USERDIR_BASE
    if e is None:
        return ".fileobj"
    else:
        return e

def _get_setting_userdir_dir():
    e = this.FILEOBJ_USERDIR_DIR
    if e is None:
        return os.getenv("HOME", '')
    else:
        return e

def _get_setting_procfs_mount_dir():
    e = this.FILEOBJ_PROCFS_MOUNT_DIR
    if e is None:
        return "/proc"
    else:
        return e

def _get_setting_use_readonly():
    e = this.FILEOBJ_USE_READONLY
    if e is None:
        return False
    else:
        return _test_bool(e)

def _get_setting_color_fg():
    e = this.FILEOBJ_COLOR_FG
    if e is None:
        return None
    else:
        return e.lower()

def _get_setting_color_bg():
    e = this.FILEOBJ_COLOR_BG
    if e is None:
        return None
    else:
        return e.lower()

def _get_setting_use_log():
    e = this.FILEOBJ_USE_LOG
    if e is None:
        return True
    else:
        return _test_bool(e)

def _get_setting_use_log_verbose():
    e = this.FILEOBJ_USE_LOG_VERBOSE
    if e is None:
        return True
    else:
        return _test_bool(e)

def _get_setting_log_level():
    e = this.FILEOBJ_LOG_LEVEL
    if e is None:
        return "WARNING"
    else:
        return e.upper()

def _get_setting_log_path():
    return this.FILEOBJ_LOG_PATH

def _get_setting_log_base():
    e = this.FILEOBJ_LOG_BASE
    if e is None:
        return "log"
    else:
        return e

def _get_setting_log_dir():
    return this.FILEOBJ_LOG_DIR

def _get_setting_use_history():
    e = this.FILEOBJ_USE_HISTORY
    if e is None:
        return True
    else:
        return _test_bool(e)

def _get_setting_max_history():
    e = this.FILEOBJ_MAX_HISTORY
    _ = 100
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_history_path():
    return this.FILEOBJ_HISTORY_PATH

def _get_setting_history_base():
    e = this.FILEOBJ_HISTORY_BASE
    if e is None:
        return "history"
    else:
        return e

def _get_setting_history_dir():
    return this.FILEOBJ_HISTORY_DIR

def _get_setting_use_barrier():
    e = this.FILEOBJ_USE_BARRIER
    if e is None:
        return True
    else:
        return _test_bool(e)

def _get_setting_barrier_size():
    e = this.FILEOBJ_BARRIER_SIZE
    _ = 8192
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_barrier_extend():
    e = this.FILEOBJ_BARRIER_EXTEND
    _ = 1024
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_use_alt_chgat():
    e = this.FILEOBJ_USE_ALT_CHGAT
    if e is None:
        return False
    else:
        return _test_bool(e)

def _get_setting_use_circular_bit_shift():
    e = this.FILEOBJ_USE_CIRCULAR_BIT_SHIFT
    if e is None:
        return True
    else:
        return _test_bool(e)

def _get_setting_use_single_operation():
    e = this.FILEOBJ_USE_SINGLE_OPERATION
    if e is None:
        return False
    else:
        return _test_bool(e)

def _get_setting_ram_thresh_ratio():
    e = this.FILEOBJ_RAM_THRESH_RATIO
    _ = _test_ratio(50)
    if e is None:
        return _
    x = _test_ratio(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_use_even_size_window():
    e = this.FILEOBJ_USE_EVEN_SIZE_WINDOW
    if e is None:
        return False
    else:
        return _test_bool(e)

def _get_setting_offset_num_width():
    e = this.FILEOBJ_OFFSET_NUM_WIDTH
    _ = 8
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_offset_num_radix():
    e = this.FILEOBJ_OFFSET_NUM_RADIX
    _ = 16
    if e is None:
        return _
    try:
        x = int(e)
        if x in (8, 10, 16):
            return x
    except Exception:
        pass
    return _

def _get_setting_editmode():
    e = this.FILEOBJ_EDITMODE
    if e is None:
        return 'B'
    elif e[0].upper() == 'A':
        return 'A'
    else:
        return 'B'

def _get_setting_endianness():
    e = this.FILEOBJ_ENDIANNESS
    if e is None:
        return None
    elif e.lower() == "little":
        return "little"
    elif e.lower() == "big":
        return "big"
    else:
        return None

def _get_setting_use_wrapscan():
    e = this.FILEOBJ_USE_WRAPSCAN
    if e is None:
        return True
    else:
        return _test_bool(e)

def _get_setting_use_ignorecase():
    e = this.FILEOBJ_USE_IGNORECASE
    if e is None:
        return False
    else:
        return _test_bool(e)

def _get_setting_use_siprefix():
    e = this.FILEOBJ_USE_SIPREFIX
    if e is None:
        return False
    else:
        return _test_bool(e)

def _get_setting_width():
    e = this.FILEOBJ_WIDTH
    if e is None:
        return None
    else:
        return e.lower()

def _get_setting_use_magic_scan():
    e = this.FILEOBJ_USE_MAGIC_SCAN
    if e is None:
        return True
    else:
        return _test_bool(e)

def _get_setting_use_alloc_retry():
    e = this.FILEOBJ_USE_ALLOC_RETRY
    if e is None:
        return True
    else:
        return _test_bool(e)

def _get_setting_use_alloc_raise():
    e = this.FILEOBJ_USE_ALLOC_RAISE
    if e is None:
        return False
    else:
        return _test_bool(e)

def _get_setting_use_array_chunk():
    e = this.FILEOBJ_USE_ARRAY_CHUNK
    if e is None:
        return True
    else:
        return _test_bool(e)

def _get_setting_mmap_thresh():
    e = this.FILEOBJ_MMAP_THRESH
    try:
        _ = os.sysconf("SC_PAGE_SIZE")
    except Exception:
        _ = 4096
    if e is None:
        return _
    x = _test_ge_zero(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_robuf_chunk_size():
    e = this.FILEOBJ_ROBUF_CHUNK_SIZE
    try:
        _ = os.sysconf("SC_PAGE_SIZE") / 4
    except Exception:
        _ = 1024
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_robuf_search_thresh_ratio():
    e = this.FILEOBJ_ROBUF_SEARCH_THRESH_RATIO
    if e is None:
        return None
    else:
        return _test_ratio(e)

def _get_setting_rwbuf_chunk_balance_interval():
    e = this.FILEOBJ_RWBUF_CHUNK_BALANCE_INTERVAL
    _ = 20
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_rwbuf_chunk_size_low():
    e = this.FILEOBJ_RWBUF_CHUNK_SIZE_LOW
    chunk_size = _get_setting_robuf_chunk_size()
    _ = chunk_size / 5
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None or x >= chunk_size:
        return _
    else:
        return x

def _get_setting_rwbuf_chunk_size_high():
    e = this.FILEOBJ_RWBUF_CHUNK_SIZE_HIGH
    chunk_size = _get_setting_robuf_chunk_size()
    _ = chunk_size * 2
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None or x <= chunk_size:
        return _
    else:
        return x

def _get_setting_rofd_read_queue_size():
    e = this.FILEOBJ_ROFD_READ_QUEUE_SIZE
    _ = 1
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_ext_strings_range():
    e = this.FILEOBJ_EXT_STRINGS_RANGE
    _ = 1024
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_ext_strings_count():
    e = this.FILEOBJ_EXT_STRINGS_COUNT
    _ = 1024
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_ext_strings_thresh():
    e = this.FILEOBJ_EXT_STRINGS_THRESH
    _ = 3
    if e is None:
        return _
    x = _test_gt_zero(e)
    if x is None:
        return _
    else:
        return x

def _get_setting_ext_cstruct_path():
    return this.FILEOBJ_EXT_CSTRUCT_PATH

def _get_setting_ext_cstruct_base():
    e = this.FILEOBJ_EXT_CSTRUCT_BASE
    if e is None:
        return "cstruct"
    else:
        return e

def _get_setting_ext_cstruct_dir():
    return this.FILEOBJ_EXT_CSTRUCT_DIR

def _get_setting_key_config(s):
    e = getattr(this, s)
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

def print_env():
    for x in iter_env_name():
        print("%s=%s" % (x, os.getenv(x)))

this = sys.modules[__name__]

for _ in iter_env_name():
    setattr(this, _, os.getenv(_))
del _
