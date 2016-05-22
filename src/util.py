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
from __future__ import print_function
from __future__ import with_statement
import contextlib
import hashlib
import inspect
import os
import platform
import re
import string
import struct
import subprocess
import sys
import tempfile
import time
import traceback

from . import package
from . import setting
from . import version

NO_NAME = "[No Name]"
UNKNOWN = "Unknown"

class GenericError (Exception):
    """Exception -> BaseException -> object in Python 2.5 or >"""
    pass

class QuietError (GenericError):
    pass

class Namespace (object):
    def __init__(self, **kwd):
        self.set(**kwd)

    def set(self, **kwd):
        for l in kwd.items():
            setattr(self, *l)

class Pair (object):
    def __init__(self, y=0, x=0):
        self.set(y, x)

    def __str__(self):
        return "({0},{1})".format(self.y, self.x)

    def set(self, y, x):
        self.y = y
        self.x = x

_python_version = tuple(sys.version_info[:3])
def get_python_version():
    return _python_version

def get_python_version_string():
    return '.'.join([str(x) for x in get_python_version()])

def get_python_executable_string():
    return "python{0}.{1}".format(*get_python_version()[:2])

def is_python2():
    return get_python_version()[0] == 2

def is_python3():
    return get_python_version()[0] == 3

def is_python_version_or_ht(*l):
    v = get_python_version()
    l = tuple(l)
    d = len(v) - len(l)
    if d > 0:
        l = list(l) + [0 for x in range(d)]
        return v >= tuple(l)
    elif d < 0:
        v = list(v) + [0 for x in range(-d)]
        return tuple(v) >= l
    else:
        return v >= l

def is_python2_version_or_ht(*l):
    return is_python2() and is_python_version_or_ht(*l)

def is_python3_version_or_ht(*l):
    return is_python3() and is_python_version_or_ht(*l)

def is_python3_supported():
    return version.get_version() >= (0, 7, 0)

def get_home():
    return os.path.expanduser("~")

def get_program_path():
    return sys.argv[0]

def get_program_name():
    return os.path.basename(get_program_path())

def is_running_script(name=None):
    f = get_program_path()
    s = get_program_name()
    if name:
        return os.path.isfile(f) and s == name
    else:
        return os.path.isfile(f)

def is_running_fileobj():
    return is_running_script("fileobj")

def is_running_profile():
    return is_running_script("profile")

def is_running_inbox():
    return is_running_fileobj() or is_running_profile()

def is_running_outbox():
    return not is_running_inbox()

def is_in_screen():
    return "STY" in os.environ

def is_in_tmux():
    return "TMUX" in os.environ

def is_in_terminal_multiplexer():
    return \
        is_in_screen() or \
        is_in_tmux() # or ...

_Xregex = re.compile(r"\\X[{0}]{{1,}}$".format(string.hexdigits))
_xregex = re.compile(r"\\x([{0}]{{1,2}})".format(string.hexdigits))

# \X1234 -> \x12\x34
# \X123  -> \x12\x30
# \x41\x42\x43 -> ABC
# \x41\x42C -> ABC
def pack_hex_string(s):
    if _Xregex.match(s):
        s = s[len("\\X"):]
        if len(s) % 2:
            s += '0'
        l = []
        for i in range(0, len(s), 2):
            l.append("\\x" + s[i : i + 2])
        s = ''.join(l)
    pos = 0
    while True:
        m = _xregex.search(s, pos)
        if m:
            pos = m.end() - 3
            t = m.group()
            n = len(t) - 2
            assert n in (1, 2)
            l = [int(c, 16) for c in t[2:]]
            if n == 1:
                u = l[0]
            else:
                u = (l[0] << 4) + l[1]
            b = struct.pack(U1F, u)
            s = s.replace(t, bytes_to_str(b), 1)
        else:
            return s

def escape_regex_pattern(s):
    l = list(s)
    while "(" in l:
        l[l.index("(")] = "\("
    while ")" in l:
        l[l.index(")")] = "\)"
    return ''.join(l)

# start == 0 means find from head
def find_string(src, sub, start=0):
    if setting.use_ignorecase:
        src = src.lower()
        sub = sub.lower()
    return src.find(sub, start)

# start == 0 means rfind from tail
def rfind_string(src, sub, start=0):
    if start < 0: # start == -1 -> 0 -> len(src)
        start += 1
    if start == 0:
        start = len(src)
    if setting.use_ignorecase:
        src = src.lower()
        sub = sub.lower()
    return src.rfind(sub, 0, start)

def get_os_name():
    # this should be used only for debugging
    if setting.os_uname:
        return setting.os_uname
    # e.g. 'Linux'
    ret = platform.system()
    return ret if ret else UNKNOWN

def get_os_release():
    # e.g. '2.6.32-504.1.3.el6.x86_64'
    ret = platform.release()
    return ret if ret else UNKNOWN

def get_cpu_name():
    # e.g. 'x86_64'
    ret = platform.processor()
    return ret if ret else UNKNOWN

def raise_no_impl(s):
    raise NotImplementedError("No " + s)

KB = 10 ** 3
MB = 10 ** 6
GB = 10 ** 9
TB = 10 ** 12
PB = 10 ** 15
EB = 10 ** 18

KiB = 1 << 10
MiB = 1 << 20
GiB = 1 << 30
TiB = 1 << 40
PiB = 1 << 50
EiB = 1 << 60

_str_size_dict = {
    "KB" : KB,
    "MB" : MB,
    "GB" : GB,
    "TB" : TB,
    "PB" : PB,
    "EB" : EB,
    "KIB": KiB,
    "MIB": MiB,
    "GIB": GiB,
    "TIB": TiB,
    "PIB": PiB,
    "EIB": EiB, }

def parse_size_repr(s, sector_size=-1):
    if not s:
        return None
    if s.startswith("+"):
        s = s[1:]
        sign = 1
    elif s.startswith("-"):
        s = s[1:]
        sign = -1
    else:
        sign = 1
    for k, v in _str_size_dict.items():
        if s[-len(k):].upper() == k:
            n = v
            s = s[:-len(k)]
            break
    else:
        # no longer support "xxxB" for "xxx byte"
        # since this makes it unable to parse hexadcimal B as 11
        if s[-3:].upper() == "LBA":
            if sector_size == -1:
                return None
            n = sector_size
            s = s[:-3]
        else:
            n = 1
    base = 10
    if s == "0":
        s, base = "0", 10
    elif s.startswith("0b"):
        s, base = s[2:], 2
    elif s.startswith("0x"):
        s, base = s[2:], 16
    elif s.startswith("0"):
        s, base = s[1:], 8
    if not s:
        s = "1"
    try:
        ret = sign * n * int(s, base)
        if ret >= 0:
            return ret
        else:
            return 0
    except ValueError:
        return None

_si_str_dict = {
    1 : "B",
    KB: "KB",
    MB: "MB",
    GB: "GB",
    TB: "TB",
    PB: "PB",
    EB: "EB", }

_bi_str_dict = {
    1  : "B",
    KiB: "KiB",
    MiB: "MiB",
    GiB: "GiB",
    TiB: "TiB",
    PiB: "PiB",
    EiB: "EiB", }

def get_size_repr(arg):
    if arg < 0:
        return "{0}[B]".format(int(arg))
    if setting.use_siprefix:
        d = _si_str_dict
    else:
        d = _bi_str_dict
    for n in reversed(sorted(d.keys())):
        x = 1.0 * arg / n
        if x >= 1:
            s = "{0:f}".format(x)
            s = s.rstrip('0').rstrip('.')
            return "{0}[{1}]".format(s, d[n])
    return "0[B]"

def is_64bit_cpu():
    return _cpu_bits == 64

def is_32bit_cpu():
    return _cpu_bits == 32

def get_address_space():
    return 2 ** _cpu_bits # simply return 2 ^ size

def __get_cpu_bits():
    s = platform.architecture()[0]
    m = re.match(r"^(\d+)bit$", s)
    if m:
        return int(m.group(1))
    else:
        if MAX_INT > 2 ** 32:
            return 64
        else:
            return 32 # assume either 64 or 32
_cpu_bits = __get_cpu_bits()

def align_range(beg, end, align):
    beg = align_head(beg, align)
    end = align_tail(end, align)
    return beg, end

def align_head(addr, align):
    mask = ~(align - 1)
    return addr & mask

def align_tail(addr, align):
    mask = ~(align - 1)
    return (addr + align - 1) & mask

def is_le_cpu():
    return sys.byteorder == "little"

def is_be_cpu():
    return sys.byteorder == "big"

_struct_ufmts = {
    1: "B",
    2: "H",
    4: "I",
    8: "Q", }
U1F = _struct_ufmts.get(1)
U2F = _struct_ufmts.get(2)
U4F = _struct_ufmts.get(4)
U8F = _struct_ufmts.get(8)

_struct_sfmts = dict(
    [(k, v.lower()) for k, v in _struct_ufmts.items()])
S1F = _struct_sfmts.get(1)
S2F = _struct_sfmts.get(2)
S4F = _struct_sfmts.get(4)
S8F = _struct_sfmts.get(8)

_struct_sizes = tuple(sorted(_struct_ufmts.keys()))
_max_struct_size = _struct_sizes[-1]

def __get_endianness_prefix(s):
    if s == "little":
        return "<"
    elif s == "big":
        return ">"
    else:
        return ''

def __fail_unknown_byteorder():
    assert 0, "unknown byteorder: " + sys.byteorder

def byte_to_int(b, sign=False):
    if is_le_cpu():
        return __bin_to_int('', b[0:1], sign)
    elif is_be_cpu():
        return __bin_to_int('', b[-1:], sign)
    else:
        __fail_unknown_byteorder()

def bin_to_int(b, sign=False):
    """Result depends on setting.endianness"""
    prefix = __get_endianness_prefix(setting.endianness)
    return __bin_to_int(prefix, b, sign)

def le_to_int(b, sign=False):
    prefix = __get_endianness_prefix("little")
    return __bin_to_int(prefix, b, sign)

def be_to_int(b, sign=False):
    prefix = __get_endianness_prefix("big")
    return __bin_to_int(prefix, b, sign)

def host_to_int(b, sign=False):
    if is_le_cpu():
        return le_to_int(b, sign)
    elif is_be_cpu():
        return be_to_int(b, sign)
    else:
        __fail_unknown_byteorder()

def __bin_to_int(prefix, b, sign):
    assert len(b) <= _max_struct_size
    if len(b) not in _struct_sizes:
        b = __pad_bin(prefix, b, sign)
    s = prefix
    if sign:
        s += _struct_sfmts.get(len(b))
    else:
        s += _struct_ufmts.get(len(b))
    return struct.unpack(s, b)[0]

def __pad_bin(prefix, b, sign):
    for i in _struct_sizes:
        if i >= len(b):
            if prefix:
                if prefix == "<":
                    return b + __get_padding(i, b, len(b) - 1, sign)
                elif prefix == ">" or prefix == "!":
                    return __get_padding(i, b, 0, sign) + b
                else:
                    assert 0, "unknown prefix " + prefix
            else:
                if is_le_cpu():
                    return b + __get_padding(i, b, len(b) - 1, sign)
                elif is_be_cpu():
                    return __get_padding(i, b, 0, sign) + b
                else:
                    __fail_unknown_byteorder()
    return b

def __get_padding(size, b, high, sign):
    if sign and (ord(b[high : high + 1]) & 0x80):
        pad = _("\xFF")
    else:
        pad = _("\x00")
    return pad * (size - len(b))

def int_to_byte(x):
    return __int_to_bin('', x, 1)

def int_to_bin(x, size):
    """Result depends on setting.endianness"""
    prefix = __get_endianness_prefix(setting.endianness)
    return __int_to_bin(prefix, x, size)

def int_to_le(x, size):
    prefix = __get_endianness_prefix("little")
    return __int_to_bin(prefix, x, size)

def int_to_be(x, size):
    prefix = __get_endianness_prefix("big")
    return __int_to_bin(prefix, x, size)

def int_to_host(x, size):
    if is_le_cpu():
        return int_to_le(x, size)
    elif is_be_cpu():
        return int_to_be(x, size)
    else:
        __fail_unknown_byteorder()

def __int_to_bin(prefix, x, size):
    assert size <= _max_struct_size
    for i in _struct_sizes:
        if i >= size:
            packsize = i
            break
    b = __try_int_to_bin(prefix, x, packsize)
    if b is None:
        b = __try_int_to_bin(prefix, x, _max_struct_size)
        if b is None:
            return None
    return __strip_bin(prefix, b, size)

def __try_int_to_bin(prefix, x, size):
    s = prefix
    if x < 0:
        s += _struct_sfmts.get(size)
    else:
        s += _struct_ufmts.get(size)
    try:
        return struct.pack(s, x)
    except struct.error:
        return None

def __strip_bin(prefix, b, size):
    if prefix:
        if prefix == "<":
            return b[:size]
        elif prefix == ">" or prefix == "!":
            return b[len(b)-size:]
        else:
            assert 0, "unknown prefix " + prefix
    else:
        if is_le_cpu():
            return b[:size]
        elif is_be_cpu():
            return b[len(b)-size:]
        else:
            __fail_unknown_byteorder()

__mktmp = tempfile.NamedTemporaryFile # no delete= till Python 2.6
__mktmp_no_delete = tempfile.mkstemp

def open_temp_file(binary=True, delete=True):
    mode = 'w+b' if binary else 'w+'
    dir = setting.user_dir
    if not os.path.isdir(dir):
        dir = '.'
    if is_python_version_or_ht(2, 6):
        try:
            return __mktmp(mode=mode, delete=delete, dir=dir)
        except Exception:
            return __mktmp(mode=mode, delete=delete)
    elif delete:
        try:
            return __mktmp(mode=mode, dir=dir)
        except Exception:
            return __mktmp(mode=mode)
    else:
        try:
            l = __mktmp_no_delete(dir=dir)
        except Exception:
            l = __mktmp_no_delete()
        os.close(l[0])
        return open(l[1], mode)

@contextlib.contextmanager
def do_atomic_write(dst, binary=True, fsync=None, rename=None):
    try:
        src = ""
        with open_temp_file(binary, False) as tmp:
            src = tmp.name
            assert not os.path.islink(src)
            yield tmp
            if fsync:
                fsync(tmp)
        # see https://docs.python.org/2/library/os.html#os.rename
        if rename:
            rename(src, dst)
        else:
            os.rename(src, dst) # atomic
        assert os.path.isfile(dst)
    finally:
        if os.path.isfile(src):
            os.unlink(src) # exception before rename
        assert not os.path.exists(src)

def is_same_file(a, b):
    if os.path.exists(a) and os.path.exists(b):
        return os.path.samefile(a, b)
    else:
        return False

def is_readable(f):
    return os.access(f, os.R_OK)

def is_writable(f):
    return os.access(f, os.W_OK)

def parse_file_path(f):
    """Return tuple of path, offset, length"""
    if not setting.use_path_attr:
        return f, 0, 0
    if '@' in f:
        i = f.rindex('@')
        sep = os.path.sep
        if sep in f:
            if i > f.rindex(sep):
                s = f[i + 1:]
                f = f[:i]
                if '-' in s:
                    j = s.find('-')
                    a = s[:j]
                    b = s[j + 1:]
                    offset = __get_path_attribute(a)
                    endpos = __get_path_attribute(b)
                    if endpos > offset:
                        length = endpos - offset
                    else:
                        length = 0
                elif ':' in s:
                    j = s.find(':')
                    a = s[:j]
                    b = s[j + 1:]
                    offset = __get_path_attribute(a)
                    length = __get_path_attribute(b)
                else:
                    a = s
                    b = ''
                    offset = __get_path_attribute(a)
                    length = __get_path_attribute(b)
                return f, offset, length
    return f, 0, 0

def __get_path_attribute(s, default=0):
    if s:
        ret = parse_size_repr(s)
    else:
        ret = None
    if ret is None:
        return default
    else:
        return ret

def get_stamp(prefix=''):
    # e.g. profile.2014-07-03-00:24:32.python3.3.pid29097
    return "{0}.{1}.{2}.pid{3}".format(
        prefix,
        time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()),
        get_python_executable_string(),
        os.getpid())

def get_md5(b):
    if isinstance(b, str):
        b = _(b)
    if b:
        return hashlib.md5(b).hexdigest()

def execute(*l):
    """Return stdout string, stderr string, return code"""
    p = subprocess.Popen(l, stdout=subprocess.PIPE)
    out, err = p.communicate()
    if out is None:
        out = _('')
    if err is None:
        err = _('')
    return bytes_to_str(out), bytes_to_str(err), p.returncode

def __iter_next_2k(g):
    return g.next()
def __iter_next_3k(g):
    return next(g)

def __get_xrange_2k(*l):
    return xrange(*l)
def __get_xrange_3k(*l):
    return range(*l)

def __str_to_bytes_2k(s):
    return s
def __str_to_bytes_3k(s):
    return codecs.latin_1_encode(s)[0]

def __bytes_to_str_2k(b):
    return b
def __bytes_to_str_3k(b):
    return codecs.latin_1_decode(b)[0]

if is_python2():
    import __builtin__ as _builtin
    MAX_INT = sys.maxint
    iter_next = __iter_next_2k
    get_xrange = __get_xrange_2k
    str_to_bytes = __str_to_bytes_2k
    bytes_to_str = __bytes_to_str_2k
else:
    import builtins as _builtin
    import codecs
    MAX_INT = sys.maxsize
    iter_next = __iter_next_3k
    get_xrange = __get_xrange_3k
    str_to_bytes = __str_to_bytes_3k
    bytes_to_str = __bytes_to_str_3k

MIN_INT = -MAX_INT - 1
_ = str_to_bytes

def iter_site_module():
    for s in package.iter_module_name():
        o = import_module(s)
        if o:
            yield o

def iter_site_ext_module():
    pkg = package.get_prefix() + "ext."
    for s in package.iter_module_name():
        if s.startswith(pkg):
            o = import_module(s)
            if o:
                yield o

def iter_dir_items(obj):
    k = dir(obj)
    v = [getattr(obj, x) for x in k]
    for l in zip(k, v):
        yield l

def iter_dir_values(obj):
    for k, v in iter_dir_items(obj):
        yield v

def add_method(obj, fn, name=None):
    if not name:
        name = fn.__name__
    assert not name.startswith("__"), name
    prev = getattr(obj, name, None)
    setattr(obj, name, fn.__get__(obj, get_class(obj)))
    return prev

_modules = {}
_exceptions = {}
def import_module(s):
    if s in _modules:
        return _modules[s]
    try:
        ret = package.import_module(s)
        if ret:
            _modules[s] = ret
        return ret
    except Exception as e:
        _exceptions[s] = e_to_string(e)
        return None

def get_import_modules():
    return dict(_modules)

def get_import_exceptions():
    return dict(_exceptions)

def iter_traceback(tb=None):
    if tb:
        g = traceback.format_tb(tb)
    else:
        g = traceback.format_stack()
    for s in g:
        for x in s.split('\n'):
            if x:
                yield x.rstrip()

def get_traceback(tb=None):
    return tuple(iter_traceback(tb))

def __fprintf(o, error, verbose):
    if error:
        fd = sys.stderr
    else:
        fd = sys.stdout
    s = obj_to_string(o, verbose)
    print(s, file=fd)

def printf(o):
    __fprintf(o, False, True)

def printe(o):
    __fprintf(o, True, True)

def obj_to_string(o, verbose=True):
    if isinstance(o, Exception):
        return e_to_string(o, verbose)
    else:
        return str(o)

def e_to_string(e, verbose=True):
    # debug or verbose=True shows class name
    s = str(e)
    if isinstance(e, QuietError):
        return s
    if setting.use_debug or verbose:
        return "{0}: {1}".format(get_class_name(e), s)
    else:
        return s

def is_seq(o):
    return isinstance(o, (list, tuple))

def is_class(cls):
    return inspect.isclass(cls)

def is_subclass(cls, clsinfo, include_clsinfo=True):
    if not is_class(cls):
        return False
    ret = issubclass(cls, clsinfo)
    if include_clsinfo:
        return ret
    else:
        return ret and (cls is not clsinfo)

def get_class(o):
    assert not is_class(o), o
    return o.__class__

def get_class_name(o):
    if is_class(o):
        return o.__name__
    else:
        return get_class(o).__name__

def get_builtin(name):
    return getattr(_builtin, name, None)
