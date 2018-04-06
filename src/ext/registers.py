# Copyright (c) 2016, Tomohiro Kusumi
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

import string

import fileobj.filebytes
import fileobj.kbd
import fileobj.setting

def get_text(co, fo, args):
    sl = []
    d = co.get_registers()
    for k in sorted(d.keys()):
        b = d[k]
        assert isinstance(b, fileobj.filebytes.TYPE)
        if b:
            s = fileobj.filebytes.str(b)
            if len(s) > fileobj.setting.ext_registers_max_string:
                s = s[:fileobj.setting.ext_registers_max_string] + "..."
        elif k == '"' or (k in string.digits): # always show " and 0-9
            s = "(not used)"
        else:
            s = ""
        if s:
            sl.append("\"{0} {1}".format(k, s))
    if sl:
        return sl
    else:
        return "No register" # should never come here

def init():
    fileobj.setting.ext_add_gt_zero("registers_max_string", 1024)

def cleanup():
    fileobj.setting.ext_delete("registers_max_string")

init()
