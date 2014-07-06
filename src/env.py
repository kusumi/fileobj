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

from __future__ import division
import os
import sys

def iter_env_name():
    yield "FILEOBJ_USE_TEST"
    yield "FILEOBJ_USE_DEBUG"
    yield "FILEOBJ_USE_STDOUT"
    yield "FILEOBJ_USE_STDIN_CBREAK"
    yield "FILEOBJ_USE_FILE_PATH_ATTR"
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
    yield "FILEOBJ_USE_ALLOC_NOENT_RWBUF"
    yield "FILEOBJ_USE_ARRAY_CHUNK"
    yield "FILEOBJ_MMAP_THRESH"
    yield "FILEOBJ_ROBUF_CHUNK_SIZE"
    yield "FILEOBJ_ROBUF_SEARCH_THRESH_RATIO"
    yield "FILEOBJ_RWBUF_CHUNK_BALANCE_INTERVAL"
    yield "FILEOBJ_RWBUF_CHUNK_SIZE_LOW"
    yield "FILEOBJ_RWBUF_CHUNK_SIZE_HIGH"
    yield "FILEOBJ_ROFD_READ_QUEUE_SIZE"
    yield "FILEOBJ_NETBSD_SIZEOF_DISKLABEL"
    yield "FILEOBJ_DRAGONFLYBSD_SIZEOF_PARTINFO"
    yield "FILEOBJ_EXT_STRINGS_RANGE"
    yield "FILEOBJ_EXT_STRINGS_COUNT"
    yield "FILEOBJ_EXT_STRINGS_THRESH"
    yield "FILEOBJ_EXT_CSTRUCT_PATH"
    yield "FILEOBJ_EXT_CSTRUCT_BASE"
    yield "FILEOBJ_EXT_CSTRUCT_DIR"
    yield "FILEOBJ_USE_EXT_CSTRUCT_LIBC"
    yield "FILEOBJ_KEY_TAB"
    yield "FILEOBJ_KEY_ENTER"
    yield "FILEOBJ_KEY_ESCAPE"
    yield "FILEOBJ_KEY_SPACE"
    yield "FILEOBJ_KEY_DOWN"
    yield "FILEOBJ_KEY_UP"
    yield "FILEOBJ_KEY_LEFT"
    yield "FILEOBJ_KEY_RIGHT"
    yield "FILEOBJ_KEY_BACKSPACE"
    yield "FILEOBJ_KEY_BACKSPACE2"
    yield "FILEOBJ_KEY_DELETE"
    yield "FILEOBJ_KEY_RESIZE"

def get_setting(envname):
    if envname in _envs_name:
        funcname = "__get_setting_%s" % \
            env_to_setting_name(envname)
        fn = getattr(this, funcname)
        return fn()
    else:
        assert 0, "Invalid env: %s" % envname

def env_to_setting_name(s):
    return s[len("FILEOBJ_"):].lower()

def __test_bool(envname, default):
    e = __getenv(envname)
    if e is None:
        return default
    else:
        return e.lower() != "false"

def __test_name(envname, default):
    e = __getenv(envname)
    if e is None:
        return default
    else:
        return e

def __test_gt_zero(e):
    try:
        x = int(e)
        if x > 0:
            return x
    except Exception:
        pass

def __test_ge_zero(e):
    try:
        x = int(e)
        if x >= 0:
            return x
    except Exception:
        pass

def __test_ratio(e):
    try:
        x = int(e)
        if 0 <= x <= 100:
            return x / 100
    except Exception:
        pass

def __test_gt_zero_or_default(envname, default):
    e = __getenv(envname)
    if e is None:
        return default
    ret = __test_gt_zero(e)
    if ret is None:
        return default
    else:
        return ret

def __get_setting_use_test():
    return __test_bool("FILEOBJ_USE_TEST", True)

def __get_setting_use_debug():
    return __test_bool("FILEOBJ_USE_DEBUG", False)

def __get_setting_use_stdout():
    return __test_bool("FILEOBJ_USE_STDOUT", False)

def __get_setting_use_stdin_cbreak():
    return __test_bool("FILEOBJ_USE_STDIN_CBREAK", True)

def __get_setting_use_file_path_attr():
    return __test_bool("FILEOBJ_USE_FILE_PATH_ATTR", True)

def __get_setting_use_trace():
    return __test_bool("FILEOBJ_USE_TRACE", False)

def __get_setting_use_trace_symlink():
    return __test_bool("FILEOBJ_USE_TRACE_SYMLINK", False)

def __get_setting_trace_word_size():
    e = __getenv("FILEOBJ_TRACE_WORD_SIZE")
    _ = 2
    if e is None:
        return _
    x = __test_gt_zero(e)
    if x in (2, 4, 8): # no 1
        return x
    else:
        return _

def __get_setting_trace_path():
    return __getenv("FILEOBJ_TRACE_PATH")

def __get_setting_trace_base():
    return __test_name("FILEOBJ_TRACE_BASE", "trace")

def __get_setting_trace_dir():
    return __getenv("FILEOBJ_TRACE_DIR")

def __get_setting_stream_path():
    return __getenv("FILEOBJ_STREAM_PATH")

def __get_setting_stream_base():
    return __getenv("FILEOBJ_STREAM_BASE")

def __get_setting_stream_dir():
    return __getenv("FILEOBJ_STREAM_DIR")

def __get_setting_userdir_path():
    return __getenv("FILEOBJ_USERDIR_PATH")

def __get_setting_userdir_base():
    return __test_name("FILEOBJ_USERDIR_BASE", ".fileobj")

def __get_setting_userdir_dir():
    e = __getenv("FILEOBJ_USERDIR_DIR")
    if e is None:
        return os.getenv("HOME", '')
    else:
        return e

def __get_setting_procfs_mount_dir():
    return __test_name("FILEOBJ_PROCFS_MOUNT_DIR", "/proc")

def __get_setting_use_readonly():
    return __test_bool("FILEOBJ_USE_READONLY", False)

def __get_setting_color_fg():
    e = __getenv("FILEOBJ_COLOR_FG")
    if e is None:
        return None
    else:
        return e.lower()

def __get_setting_color_bg():
    e = __getenv("FILEOBJ_COLOR_BG")
    if e is None:
        return None
    else:
        return e.lower()

def __get_setting_use_log():
    return __test_bool("FILEOBJ_USE_LOG", True)

def __get_setting_use_log_verbose():
    return __test_bool("FILEOBJ_USE_LOG_VERBOSE", True)

def __get_setting_log_level():
    return __test_name("FILEOBJ_LOG_LEVEL", "WARNING")

def __get_setting_log_path():
    return __getenv("FILEOBJ_LOG_PATH")

def __get_setting_log_base():
    return __test_name("FILEOBJ_LOG_BASE", "log")

def __get_setting_log_dir():
    return __getenv("FILEOBJ_LOG_DIR")

def __get_setting_use_history():
    return __test_bool("FILEOBJ_USE_HISTORY", True)

def __get_setting_max_history():
    return __test_gt_zero_or_default("FILEOBJ_MAX_HISTORY", 100)

def __get_setting_history_path():
    return __getenv("FILEOBJ_HISTORY_PATH")

def __get_setting_history_base():
    return __test_name("FILEOBJ_HISTORY_BASE", "history")

def __get_setting_history_dir():
    return __getenv("FILEOBJ_HISTORY_DIR")

def __get_setting_use_barrier():
    return __test_bool("FILEOBJ_USE_BARRIER", True)

def __get_setting_barrier_size():
    return __test_gt_zero_or_default("FILEOBJ_BARRIER_SIZE", 8192)

def __get_setting_barrier_extend():
    return __test_gt_zero_or_default("FILEOBJ_BARRIER_EXTEND", 1024)

def __get_setting_use_alt_chgat():
    return __test_bool("FILEOBJ_USE_ALT_CHGAT", False)

def __get_setting_use_circular_bit_shift():
    return __test_bool("FILEOBJ_USE_CIRCULAR_BIT_SHIFT", True)

def __get_setting_use_single_operation():
    return __test_bool("FILEOBJ_USE_SINGLE_OPERATION", False)

def __get_setting_ram_thresh_ratio():
    e = __getenv("FILEOBJ_RAM_THRESH_RATIO")
    _ = __test_ratio(50)
    if e is None:
        return _
    x = __test_ratio(e)
    if x is None:
        return _
    else:
        return x

def __get_setting_use_even_size_window():
    return __test_bool("FILEOBJ_USE_EVEN_SIZE_WINDOW", False)

def __get_setting_offset_num_width():
    return __test_gt_zero_or_default("FILEOBJ_OFFSET_NUM_WIDTH", 8)

def __get_setting_offset_num_radix():
    e = __getenv("FILEOBJ_OFFSET_NUM_RADIX")
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

def __get_setting_editmode():
    e = __getenv("FILEOBJ_EDITMODE")
    if e is None:
        return 'B'
    elif e[0].upper() == 'A':
        return 'A'
    else:
        return 'B'

def __get_setting_endianness():
    e = __getenv("FILEOBJ_ENDIANNESS")
    if e is None:
        return None
    elif e.lower() == "little":
        return "little"
    elif e.lower() == "big":
        return "big"
    else:
        return None

def __get_setting_use_wrapscan():
    return __test_bool("FILEOBJ_USE_WRAPSCAN", True)

def __get_setting_use_ignorecase():
    return __test_bool("FILEOBJ_USE_IGNORECASE", False)

def __get_setting_use_siprefix():
    return __test_bool("FILEOBJ_USE_SIPREFIX", False)

def __get_setting_width():
    e = __getenv("FILEOBJ_WIDTH")
    if e is None:
        return None
    else:
        return e.lower()

def __get_setting_use_magic_scan():
    return __test_bool("FILEOBJ_USE_MAGIC_SCAN", True)

def __get_setting_use_alloc_retry():
    return __test_bool("FILEOBJ_USE_ALLOC_RETRY", True)

def __get_setting_use_alloc_raise():
    return __test_bool("FILEOBJ_USE_ALLOC_RAISE", False)

def __get_setting_use_alloc_noent_rwbuf():
    return __test_bool("FILEOBJ_USE_ALLOC_NOENT_RWBUF", True)

def __get_setting_use_array_chunk():
    return __test_bool("FILEOBJ_USE_ARRAY_CHUNK", True)

def __get_setting_mmap_thresh():
    e = __getenv("FILEOBJ_MMAP_THRESH")
    try:
        _ = os.sysconf("SC_PAGE_SIZE")
    except Exception:
        _ = 4096
    if e is None:
        return _
    x = __test_ge_zero(e)
    if x is None:
        return _
    else:
        return x

def __get_setting_robuf_chunk_size():
    try:
        default = os.sysconf("SC_PAGE_SIZE")
    except Exception:
        default = 4096
    return __test_gt_zero_or_default("FILEOBJ_ROBUF_CHUNK_SIZE", default)

def __get_setting_robuf_search_thresh_ratio():
    e = __getenv("FILEOBJ_ROBUF_SEARCH_THRESH_RATIO")
    if e is None:
        return None
    else:
        return __test_ratio(e)

def __get_setting_rwbuf_chunk_balance_interval():
    return __test_gt_zero_or_default(
        "FILEOBJ_RWBUF_CHUNK_BALANCE_INTERVAL", 20)

def __get_setting_rwbuf_chunk_size_low():
    e = __getenv("FILEOBJ_RWBUF_CHUNK_SIZE_LOW")
    chunk_size = __get_setting_robuf_chunk_size()
    _ = chunk_size // 5
    if e is None:
        return _
    x = __test_gt_zero(e)
    if x is None or x >= chunk_size:
        return _
    else:
        return x

def __get_setting_rwbuf_chunk_size_high():
    e = __getenv("FILEOBJ_RWBUF_CHUNK_SIZE_HIGH")
    chunk_size = __get_setting_robuf_chunk_size()
    _ = chunk_size * 5
    if e is None:
        return _
    x = __test_gt_zero(e)
    if x is None or x <= chunk_size:
        return _
    else:
        return x

def __get_setting_rofd_read_queue_size():
    return __test_gt_zero_or_default("FILEOBJ_ROFD_READ_QUEUE_SIZE", 1)

def __get_setting_netbsd_sizeof_disklabel():
    return __test_gt_zero_or_default("FILEOBJ_NETBSD_SIZEOF_DISKLABEL", -1)

def __get_setting_dragonflybsd_sizeof_partinfo():
    return __test_gt_zero_or_default(
        "FILEOBJ_DRAGONFLYBSD_SIZEOF_PARTINFO", -1)

def __get_setting_ext_strings_range():
    return __test_gt_zero_or_default("FILEOBJ_EXT_STRINGS_RANGE", 1024)

def __get_setting_ext_strings_count():
    return __test_gt_zero_or_default("FILEOBJ_EXT_STRINGS_COUNT", 1024)

def __get_setting_ext_strings_thresh():
    return __test_gt_zero_or_default("FILEOBJ_EXT_STRINGS_THRESH", 3)

def __get_setting_ext_cstruct_path():
    return __getenv("FILEOBJ_EXT_CSTRUCT_PATH")

def __get_setting_ext_cstruct_base():
    return __test_name("FILEOBJ_EXT_CSTRUCT_BASE", "cstruct")

def __get_setting_ext_cstruct_dir():
    return __getenv("FILEOBJ_EXT_CSTRUCT_DIR")

def __get_setting_use_ext_cstruct_libc():
    return __test_bool("FILEOBJ_USE_EXT_CSTRUCT_LIBC", True)

def __get_setting_key_tab():
    return __get_setting_key("FILEOBJ_KEY_TAB")

def __get_setting_key_enter():
    return __get_setting_key("FILEOBJ_KEY_ENTER")

def __get_setting_key_escape():
    return __get_setting_key("FILEOBJ_KEY_ESCAPE")

def __get_setting_key_space():
    return __get_setting_key("FILEOBJ_KEY_SPACE")

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

def __get_setting_key_backspace2():
    return __get_setting_key("FILEOBJ_KEY_BACKSPACE2")

def __get_setting_key_delete():
    return __get_setting_key("FILEOBJ_KEY_DELETE")

def __get_setting_key_resize():
    return __get_setting_key("FILEOBJ_KEY_RESIZE")

def __get_setting_key(envname):
    e = __getenv(envname)
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
        sys.stdout.write("%s=%s\n" % (x, os.getenv(x)))

def __getenv(envname):
    return getattr(this, envname)

_envs_name = tuple(iter_env_name())
this = sys.modules[__name__]

for _ in _envs_name:
    setattr(this, _, os.getenv(_))
del _
