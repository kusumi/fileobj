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

import fileobj.filebytes
import fileobj.path
import fileobj.setting
import fileobj.util

def I(x):
    return '    ' * x

class _node (object):
    def __init__(self, type):
        self.type = type
    def get_size(self):
        return 0
    def get_lines(self, buf, name, indent):
        return []

_toplevel_regex = \
    re.compile(r"\s*struct\s+(\S+)\s*{([\s\S]+?)}\s*;")
_struct_member_regex = \
    re.compile(r"^(\S+)\[([0-9]+)\]$")
_builtin_type_regex = \
    re.compile(r"^(u|s)(8|16|32|64)([a-z]*)$")

class _builtin (_node):
    def __init__(self):
        super(_builtin, self).__init__(fileobj.util.get_class_name(self))
        m = _builtin_type_regex.match(self.type)
        if not m:
            assert 0, "Invalid type %s" % self.type
        sign, size, byteorder = m.groups()
        self.__sign = sign == "s"
        if byteorder == "le":
            self.__to_int = fileobj.util.le_to_int
        elif byteorder == "be":
            self.__to_int = fileobj.util.be_to_int
        else:
            self.__to_int = fileobj.util.bin_to_int

    def get_lines(self, buf, name, indent):
        s = "%s%s %s;" % (I(indent), self.type, name)
        if len(buf) == self.get_size():
            n = self.__to_int(buf, self.__sign)
            a = ''.join(["\\x%02X" % x
                for x in fileobj.filebytes.ords(buf)])
            b = ''.join([fileobj.util.to_chr_repr(x) for x in buf])
            s += " %d %s [%s]" % (n, a, b)
        return [s]

class u8 (_builtin):
    def get_size(self):
        return 1
class u8le (u8):
    pass
class u8be (u8):
    pass

class s8 (_builtin):
    def get_size(self):
        return 1
class s8le (s8):
    pass
class s8be (s8):
    pass

class u16 (_builtin):
    def get_size(self):
        return 2
class u16le (u16):
    pass
class u16be (u16):
    pass

class s16 (_builtin):
    def get_size(self):
        return 2
class s16le (s16):
    pass
class s16be (s16):
    pass

class u32 (_builtin):
    def get_size(self):
        return 4
class u32le (u32):
    pass
class u32be (u32):
    pass

class s32 (_builtin):
    def get_size(self):
        return 4
class s32le (s32):
    pass
class s32be (s32):
    pass

class u64 (_builtin):
    def get_size(self):
        return 8
class u64le (u64):
    pass
class u64be (u64):
    pass

class s64 (_builtin):
    def get_size(self):
        return 8
class s64le (s64):
    pass
class s64be (s64):
    pass

class _struct (_node):
    def __init__(self, type, defs):
        super(_struct, self).__init__(type)
        self.__member = []
        for type, name in self.__iter_member(defs):
            o = get_node(type)
            assert o, "%s not defined yet" % type
            self.__member.append(fileobj.util.Namespace(node=o, name=name))

    def get_size(self):
        return sum(o.node.get_size() for o in self.__member)

    def get_lines(self, buf, name, indent):
        l = ["%sstruct %s {" % (I(indent), self.type)]
        for o in self.__member:
            n = o.node.get_size()
            l.extend(o.node.get_lines(buf[:n], o.name, indent+1))
            buf = buf[n:]
        x = " %s" % name
        l.append("%s}%s;" % (I(indent), x.rstrip()))
        return l

    def __iter_member(self, defs):
        for s in [x.strip() for x in defs.split(';')]:
            l = s.split()
            if l:
                if l[0] == "struct":
                    l = l[1:]
                assert len(l) == 2, "Invalid syntax: %s" % l
                type, name = l
                m = _struct_member_regex.match(name)
                if m:
                    n = int(m.group(2))
                    for i in range(n):
                        yield type, "%s[%d]" % (m.group(1), i)
                else:
                    yield type, name

_nodes = []
def init_node():
    global _nodes
    _nodes = [
        u8(), u8le(), u8be(),
        s8(), s8le(), s8be(),
        u16(), u16le(), u16be(),
        s16(), s16le(), s16be(),
        u32(), u32le(), u32be(),
        s32(), s32le(), s32be(),
        u64(), u64le(), u64be(),
        s64(), s64le(), s64be(),
    ]

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
        f = fileobj.setting.get_ext_cstruct_path()
        if fileobj.path.is_noent(f):
            return "Need %s with struct definition" % f
        if not os.path.isfile(f):
            return "Can not read %s" % f

    try:
        l = fileobj.util.open_text_file(f).readlines()
    except Exception, e:
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
            l.extend(o.get_lines(buf, '', 0))
        else:
            l.append("struct %s is not defined in %s" % (x, f))
        l.append('')
    return l
