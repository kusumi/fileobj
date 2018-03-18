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

import os
import sys

from . import env

def get_trace_path():
    return os.path.join(this.user_dir, "trace")

def get_log_path():
    return os.path.join(this.user_dir, "log")

def get_history_path():
    return os.path.join(this.user_dir, "history")

def get_marks_path():
    return os.path.join(this.user_dir, "marks")

def get_stream_path():
    return __get_path("path_stream")

def get_ext_path(s):
    return __get_path("ext_path_{0}".format(s))

# use the setting if already a complete path,
# otherwise consider it as a file name.
def __get_path(s):
    s = getattr(this, s) # e.g. "(ext_)path_xxx"
    if s and os.path.isfile(s):
        return s
    d = this.user_dir
    if s and d and os.path.isdir(d):
        return os.path.join(d, s)
    return ''

USER_DIR_NONE         = -1
USER_DIR_NO_READ      = -2
USER_DIR_NO_WRITE     = -3
USER_DIR_MKDIR_FAILED = -4

def init_user():
    d = this.user_dir
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
    __init(env.iter_setting())

def __init(g):
    for _ in g:
        add(*_)

def cleanup():
    from . import util # util imports setting
    util.clear_dict(_attr)

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

def ext_add(k):
    s, e = __ext_get(k)
    return __ext_add(s, env.getenv(e))

def ext_add_bool(k, v):
    s, e = __ext_get(k)
    return __ext_add(s, env.test_bool(e, v))

def ext_add_name(k, v):
    s, e = __ext_get(k)
    return __ext_add(s, env.test_name(e, v))

def ext_add_gt_zero(k, v):
    s, e = __ext_get(k)
    return __ext_add(s, env.test_gt_zero(e, v))

def ext_add_ge_zero(k, v):
    s, e = __ext_get(k)
    return __ext_add(s, env.test_ge_zero(e, v))

def ext_delete(k):
    s, e = __ext_get(k)
    return __ext_delete(s)

def __ext_add(k, v):
    # assert k not in _attr, k
    return add(k, v)

def __ext_delete(k):
    # assert k in _attr, k
    return delete(k)

def __ext_get(k):
    s = "ext_" + k
    e = "FILEOBJ_EXT_" + k.upper()
    return s, e

_attr = {}
_snap = dict(_attr)
this = sys.modules[__name__]
init()
