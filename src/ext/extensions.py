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

from .. import extension
from .. import literal
from .. import util

def get_text(co, fo, args):
    try:
        extension.set_dryrun()
        l = [__test_module(co, fo, li) for li in literal.get_ext_literals()]
    except Exception:
        pass
    finally:
        extension.clear_dryrun()

    if not l:
        return "No extension"
    f = "{{0:{0}}} {{1:<{1}}} {{2:<{2}}} {{3}}".format(
        extension.get_index_width(l),
        max([len(x[0]) for x in l]),
        max([len(x[1]) for x in l]),)
    return [f.format(i + 1, x[0], x[1], x[2]) for i, x in enumerate(l)]

def __test_module(co, fo, li):
    x = [li.str, repr(li), '']
    if li.fn != get_text:
        try:
            li.fn(co, fo, [0])
        except extension.Error:
            pass
        except Exception as e:
            x[2] = util.e_to_string(e)
    return x

def get_description():
    return "Show list of extensions"
