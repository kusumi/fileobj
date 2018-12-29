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
import platform
import sys

support_if_argparse = True # unittest (false)

def __test(version, name):
    if not version:
        version = sys.version_info
    version = tuple(version[:3])
    if not name:
        name = platform.system()
    if name == "Windows":
        __test_windows(version)
    else:
        __test_xnix(version)
    import curses
    curses
    del curses

def __test_xnix(version):
    if version < (2, 6, 0): # this script must run on Python 2.5-
        raise Exception("Python 2.7 is required")
    if version < (2, 7, 0) or ((3, 0, 0) <= version < (3, 2, 0)):
        try:
            if support_if_argparse:
                import argparse # test if backported
                argparse
                del argparse
            else:
                raise ImportError("")
        except ImportError:
            if version[0] == 2:
                raise Exception("Python 2.7 is required")
            else:
                raise Exception("Python 3.2 or above is required")

def __test_windows(version):
    if sys.executable[0] not in "ABCDEFG": # test this first
        raise Exception("Cygwin Python binary is required on Cygwin")
    if version < (3, 3, 0):
        raise Exception("Python 3.3 or above is required")

def test():
    e = os.getenv("FILEOBJ_USE_DEBUG")
    if e is None:
        debug = False
    else:
        debug = e.lower() != "false"
    try:
        __test(None, None)
    except Exception:
        e = sys.exc_info()[1]
        sys.stderr.write("%s\n" % e)
        if not debug:
            sys.exit(1)

if __name__ == '__main__':
    test()
