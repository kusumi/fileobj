# Copyright (c) 2009, Tomohiro Kusumi
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
import re
import sys

import fileobj.env
import fileobj.extension
import fileobj.filebytes
import fileobj.kbd
import fileobj.kernel
import fileobj.libc
import fileobj.path
import fileobj.setting
import fileobj.util

def I(x):
    return ' ' * 4 * x

class _node (object):
    def __init__(self, type):
        self.type = type

    def get_size(self):
        return 0

    def get_repr(self, buf, name, indent):
        return []

class _builtin (_node):
    def __init__(self):
        super(_builtin, self).__init__(fileobj.util.get_class_name(self))

    def get_repr(self, buf, name, indent):
        s = "{0}{1} {2};".format(I(indent), self.type, name)
        if len(buf) == self.get_size():
            v = self.__get_value_expr(buf)
            a = ''.join(["\\x{0:02X}".format(x) for x in
                fileobj.filebytes.iter_ords(buf)])
            b = ''.join([fileobj.kbd.chr_repr[x] for x in
                fileobj.filebytes.iter_ords(buf)])
            s += " {0} {1} [{2}]".format(v, a, b)
        return [s]

    def __get_value_expr(self, buf):
        n = self.to_int(buf)
        m = _builtin_xtype_regex.match(self.type)
        if m:
            siz = builtin_int(m.group(1))
            siz //= 4 # string size in hex
            fmt = "0x{0:0" + str(siz) + "X}"
            return fmt.format(n)
        else:
            return str(n)

_toplevel_regex = re.compile(r"\s*struct\s+(\S+)\s*{([\s\S]+?)}\s*;")
_struct_member_regex = re.compile(r"^(\S+)\[([0-9]+)\]$")
_builtin_type_regex = re.compile(r"^(u|s|x)(8|16|32|64)(le|be)$")
_builtin_xtype_regex = re.compile(r"^x(8|16|32|64)") # only to detect x

# XXX
# This is necessary as this module uses int()
# while __create_builtin_class() overwrites int.
builtin_int = fileobj.util.get_builtin("int")

_classes = []
def __create_builtin_class(name, size):
    def get_size(self):
        return size
    sign = (name[0] == 's')
    m = _builtin_type_regex.match(name)
    if not m:
        def to_int(self, b):
            return fileobj.util.host_to_int(b, sign)
    elif m.group(3) == "le":
        def to_int(self, b):
            return fileobj.util.le_to_int(b, sign)
    elif m.group(3) == "be":
        def to_int(self, b):
            return fileobj.util.be_to_int(b, sign)
    else:
        assert False, m.group(0)
    cls = type(name, (_builtin,), dict(get_size=get_size, to_int=to_int,),)
    assert cls not in _classes
    _classes.append(cls)
    setattr(sys.modules[__name__], name, cls)

def __init_class():
    for x in fileobj.util.get_xrange(4):
        size = 2 ** x
        for sign in "usx":
            for suffix in ("", "le", "be"):
                name = "{0}{1}{2}".format(sign, size * 8, suffix)
                __create_builtin_class(name, size)
    for name, func_name, fn in fileobj.libc.iter_defined_type():
        __create_builtin_class(name, fn())

# A node for this class can't be added on import
class _string (_node):
    def __init__(self, size):
        self.__size = size
        super(_string, self).__init__(_string_type(self.__size))

    def get_size(self):
        return self.__size

    def get_repr(self, buf, name, indent):
        i = buf.find(fileobj.filebytes.ZERO)
        b = fileobj.filebytes.str(buf[:i])
        s = "{0}string {1}; \"{2}\"".format(I(indent), name, b)
        return [s]

def _string_type(n):
    return "string{0}".format(n)

class _struct (_node):
    def __init__(self, type, defs):
        super(_struct, self).__init__(type)
        self.__member = []
        for type, name in self.__iter_member(defs):
            o = get_node(type)
            if not o:
                fileobj.extension.fail(type + " not defined yet")
            self.__member.append((o, name))

    def get_size(self):
        return sum(_[0].get_size() for _ in self.__member)

    def get_repr(self, buf, name, indent):
        l = ["{0}struct {1} {{".format(I(indent), self.type)]
        for _ in self.__member:
            n = _[0].get_size()
            l.extend(_[0].get_repr(buf[:n], _[1], indent+1))
            buf = buf[n:]
        x = " " + name
        l.append("{0}}}{1};".format(I(indent), x.rstrip()))
        return l

    def __iter_member(self, defs):
        for s in [x.strip() for x in defs.split(';')]:
            l = s.split()
            if l:
                if l[0] == "struct":
                    l = l[1:]
                if len(l) != 2:
                    fileobj.extension.fail("Invalid syntax: {0}".format(l))
                type, name = l
                if type == "string":
                    yield self.__scan_string_type(type, name)
                else:
                    # anything but string, including struct
                    m = _struct_member_regex.match(name)
                    if m:
                        var = m.group(1)
                        num = builtin_int(m.group(2))
                        for i in fileobj.util.get_xrange(num):
                            yield type, "{0}[{1}]".format(var, i)
                    else:
                        yield type, name

    def __scan_string_type(self, type, name):
        m = _struct_member_regex.match(name)
        if m:
            var = m.group(1)
            num = builtin_int(m.group(2))
        else:
            var = name
            num = 1 # force "[1]"
        type = _string_type(num)
        if not get_node(type):
            add_node(_string(num))
        return type, "{0}[{1}]".format(var, num)

_nodes = []
def init_node():
    global _nodes
    _nodes = [cls() for cls in _classes]

def get_node(s):
    for o in _nodes:
        if o.type == s:
            return o

def add_node(o):
    while True:
        x = get_node(o.type)
        if x:
            del _nodes[_nodes.index(x)]
        else:
            _nodes.append(o)
            break

def get_text(co, fo, args):
    pos = args.pop()
    if not args:
        return "No struct name"

    f = fileobj.path.get_path(args[0])
    if os.path.exists(f):
        args = args[1:]
        if not args:
            return "No struct name"
    else:
        f = fileobj.setting.get_ext_path("cstruct")
        if fileobj.path.is_noent(f):
            return "Need {0} with struct definition".format(f)
        if not os.path.isfile(f):
            return "Can not read " + f

    try:
        l = fileobj.kernel.fopen_text(f).readlines()
    except Exception as e:
        return str(e)
    l = [x.strip() for x in l] # strip whitespaces and tabs first
    l = [x for x in l if not x.startswith('#')] # then ignore comments
    s = ''.join([x for x in l if x])
    s = re.sub(r"\s{1,}", ' ', s)

    init_node()
    while True:
        m = _toplevel_regex.match(s)
        if m:
            s = s[m.end():]
            add_node(_struct(*m.groups()))
        else:
            break

    l = []
    for x in args:
        o = get_node(x)
        if o:
            buf = fo.read(pos, o.get_size())
            l.extend(o.get_repr(buf, '', 0))
        else:
            l.append("struct {0} is not defined in {1}".format(x, f))
        l.append('')
    return l

def init():
    fileobj.setting.ext_add_name("path_cstruct", "cstruct")
    __init_class()
    # create an empty file
    f = fileobj.setting.get_ext_path("cstruct")
    if not os.path.exists(f):
        try:
            fileobj.kernel.fcreat_text(f)
        except Exception:
            pass

def cleanup():
    fileobj.setting.ext_delete("path_cstruct")

init()
