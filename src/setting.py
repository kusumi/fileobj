# Copyright (c) 2010, Tomohiro Kusumi
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

from . import env
from . import nodep

def get_home_dir():
    return _home_dir

def get_user_dir():
    return _user_dir

_windows_suffix = ".txt"

def get_env_path():
    f = os.path.join(get_user_dir(), "env")
    if nodep.is_windows():
        return f + _windows_suffix
    else:
        return f

def _get_suffix():
    from . import kernel
    return _windows_suffix if kernel.is_windows() else ""

def get_trace_path():
    return os.path.join(get_user_dir(), "trace" + _get_suffix())

def get_log_path():
    return os.path.join(get_user_dir(), "log" + _get_suffix())

def get_history_path():
    return os.path.join(get_user_dir(), "history" + _get_suffix())

def get_marks_path():
    return os.path.join(get_user_dir(), "marks" + _get_suffix())

def get_session_path():
    return os.path.join(get_user_dir(), "session" + _get_suffix())

def get_stream_path():
    return __get_path("path_stream")

def get_ext_path(s):
    return __get_path("ext_path_{0}".format(s))

def get_paths():
    d = {}
    for s in ("env", "trace", "log", "history", "marks", "session", "stream"):
        fn = getattr(this, "get_{0}_path".format(s))
        f = fn()
        d[s] = f, os.path.isfile(f)
    return d

# use the setting if already a complete path,
# otherwise consider it as a file name.
def __get_path(s):
    s = getattr(this, s) # e.g. "(ext_)path_xxx"
    if s and os.path.isfile(s):
        return s
    d = get_user_dir()
    if s and d and os.path.isdir(d):
        return os.path.join(d, s + _get_suffix())
    return ''

USER_DIR_NONE         = -1
USER_DIR_NO_READ      = -2
USER_DIR_NO_WRITE     = -3
USER_DIR_MKDIR_FAILED = -4

def init_user():
    d = get_user_dir()
    if not d:
        return USER_DIR_NONE
    elif os.path.isdir(d):
        if not os.access(d, os.R_OK):
            return USER_DIR_NO_READ
        elif not os.access(d, os.R_OK | os.W_OK):
            return USER_DIR_NO_WRITE
        else:
            return # success
    else:
        try:
            os.makedirs(d)
            return # success
        except Exception:
            return USER_DIR_MKDIR_FAILED

def init():
    env.init(get_env_path())
    __init(env.iter_setting())
    assert isinstance(this.use_color, bool)
    if not this.use_color:
        disable_color()

def __init(g):
    for _ in g:
        add(*_)

def cleanup():
    env.cleanup(get_env_path())
    _attr.clear()
    _ext_env.clear()

def add(k, v):
    if k not in _attr:
        setattr(this, k, v)
        _attr[k] = v
    else:
        return -1

def delete(k):
    if k in _attr:
        delattr(this, k)
        del _attr[k]
    else:
        return -1

def update(k, v):
    if delete(k) == -1:
        return -1
    if add(k, v) == -1:
        return -1

def get_snapshot():
    global _snap
    if _attr != _snap:
        _snap = dict(_attr)
    else:
        return -1

def set_snapshot():
    if _attr != _snap:
        cleanup()
        __init(_snap.items())
    else:
        return -1

def iter_setting_name():
    for k in sorted(_attr.keys()):
        yield k

def iter_setting():
    for k in iter_setting_name():
        yield k, getattr(this, k)

def ext_add(k, desc):
    s, e = __ext_get(k, desc)
    return __ext_add(s, env.getenv(e))

def ext_add_bool(k, v, desc):
    s, e = __ext_get(k, desc)
    return __ext_add(s, env.test_bool(e, v))

def ext_add_name(k, v, desc):
    s, e = __ext_get(k, desc)
    return __ext_add(s, env.test_name(e, v))

def ext_add_gt_zero(k, v, desc):
    s, e = __ext_get(k, desc)
    return __ext_add(s, env.test_gt_zero(e, v))

def ext_add_ge_zero(k, v, desc):
    s, e = __ext_get(k, desc)
    return __ext_add(s, env.test_ge_zero(e, v))

def ext_delete(k):
    s, e = __ext_get(k, None) # XXX
    return __ext_delete(s)

def __ext_add(k, v):
    # assert k not in _attr, k
    return add(k, v)

def __ext_delete(k):
    # assert k in _attr, k
    return delete(k)

def __ext_get(k, desc):
    s = "ext_" + k
    e = "FILEOBJ_EXT_" + k.upper()
    if e not in _ext_env:
        _ext_env[e] = desc
    return s, e

def get_ext_env_desc(k):
    return _ext_env.get(k, "")

def iter_ext_env_name():
    for x in sorted(_ext_env.keys()):
        yield x

# non private env + ext env
def iter_env_name():
    for x in env.iter_env_name():
        yield x
    for x in iter_ext_env_name(): # no sorting against above
        yield x

def iter_env_name_private():
    for x in env.iter_env_name_private():
        yield x

def has_buffer_attr():
    return not (this.color_zero is None and this.color_ff is None and
        this.color_print is None and this.color_default is None)

def disable_color():
    # keep color_current and color_visual
    #this.color_current = None
    this.color_zero = None
    this.color_ff = None
    this.color_print = None
    this.color_default = None
    #this.color_visual = None
    this.color_offset = None

_use_unit_based_save = None
_use_unit_based_aux = 0

def discard_unit_based():
    global _use_unit_based_save, _use_unit_based_aux
    _use_unit_based_save = this.use_unit_based
    this.use_unit_based = False
    assert _use_unit_based_aux == 0, _use_unit_based_aux
    _use_unit_based_aux += 1

def restore_unit_based():
    global _use_unit_based_aux
    assert _use_unit_based_aux == 1, _use_unit_based_aux
    _use_unit_based_aux -= 1
    assert _use_unit_based_save is not None, _use_unit_based_save
    this.use_unit_based = _use_unit_based_save

# non env based settings
use_even_size_window = False

_home_dir = os.path.expanduser("~")
_user_dir = os.path.join(_home_dir, ".fileobj")

_attr = {}
_snap = dict(_attr)
_ext_env = {}

this = sys.modules[__name__]
init()
