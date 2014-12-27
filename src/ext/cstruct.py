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
    def get_expr(self, buf, name, indent):
        return []

class _builtin (_node):
    def __init__(self):
        super(_builtin, self).__init__(
            fileobj.util.get_class_name(self))

    def get_expr(self, buf, name, indent):
        s = "{0}{1} {2};".format(I(indent), self.type, name)
        if len(buf) == self.get_size():
            n = self.to_int(buf)
            a = ''.join(["\\x{0:02X}".format(x)
                for x in fileobj.filebytes.ords(buf)])
            b = ''.join([fileobj.kbd.to_chr_repr(x) for x in buf])
            s += " {0} {1} [{2}]".format(n, a, b)
        return [s]

_toplevel_regex = re.compile(
    r"\s*struct\s+(\S+)\s*{([\s\S]+?)}\s*;")
_struct_member_regex = re.compile(
    r"^(\S+)\[([0-9]+)\]$")
_builtin_type_regex = re.compile(
    r"^(u|s)(8|16|32|64)(le|be)$")

_classes = []
def __create_builtin_class(name, size):
    def get_size(self):
        return size
    sign = name[0] != 'u'
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
        assert 0, m.group(0)
    cls = type(name, (_builtin,),
        dict(get_size=get_size, to_int=to_int,),)
    assert cls not in _classes
    _classes.append(cls)
    setattr(sys.modules[__name__], name, cls)

def __init_class():
    for x in range(4):
        size = 2 ** x
        for sign in "us":
            for suffix in ("", "le", "be"):
                name = "{0}{1}{2}".format(sign, size * 8, suffix)
                __create_builtin_class(name, size)

    if fileobj.setting.use_ext_cstruct_libc:
        for name, func_name, fn in fileobj.libc.iter_defined_type():
            __create_builtin_class(name, fn())

class _struct (_node):
    def __init__(self, type, defs):
        super(_struct, self).__init__(type)
        self.__member = []
        for type, name in self.__iter_member(defs):
            o = get_node(type)
            if not o:
                fileobj.extension.fail(type + " not defined yet")
            self.__member.append(fileobj.util.Namespace(node=o, name=name))

    def get_size(self):
        return sum(o.node.get_size() for o in self.__member)

    def get_expr(self, buf, name, indent):
        l = ["{0}struct {1} {{".format(I(indent), self.type)]
        for o in self.__member:
            n = o.node.get_size()
            l.extend(o.node.get_expr(buf[:n], o.name, indent+1))
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
                m = _struct_member_regex.match(name)
                if m:
                    n = int(m.group(2))
                    for i in range(n):
                        yield type, "{0}[{1}]".format(m.group(1), i)
                else:
                    yield type, name

_nodes = []
def init_node():
    global _nodes
    _nodes = [cls() for cls in _classes]

def get_node(s):
    for o in _nodes:
        if o.type == s:
            return o
    l = [o for o in _nodes if s and o.type.startswith(s)]
    if len(l) == 1:
        return l[0]

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
        f = fileobj.setting.get_path("ext_cstruct")
        if fileobj.path.is_noent(f):
            return "Need " + f + " with struct definition"
        if not os.path.isfile(f):
            return "Can not read " + f

    try:
        l = fileobj.kernel.fopen_text(f).readlines()
    except Exception as e:
        return str(e)
    l = [x.strip() for x in l if not x.startswith('#')]
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
            l.extend(o.get_expr(buf, '', 0))
        else:
            l.append("struct {0} is not defined in {1}".format(x, f))
        l.append('')
    return l

def init():
    fileobj.setting.add("ext_cstruct_path",
        os.getenv("FILEOBJ_EXT_CSTRUCT_PATH"))
    fileobj.setting.add("ext_cstruct_base",
        fileobj.env.test_name("FILEOBJ_EXT_CSTRUCT_BASE", "cstruct"))
    fileobj.setting.add("ext_cstruct_dir",
        os.getenv("FILEOBJ_EXT_CSTRUCT_DIR"))
    fileobj.setting.add("use_ext_cstruct_libc",
        fileobj.env.test_bool("FILEOBJ_USE_EXT_CSTRUCT_LIBC", True))
    __init_class()

def cleanup():
    fileobj.setting.delete("ext_cstruct_path")
    fileobj.setting.delete("ext_cstruct_base")
    fileobj.setting.delete("ext_cstruct_dir")
    fileobj.setting.delete("use_ext_cstruct_libc")

init()
