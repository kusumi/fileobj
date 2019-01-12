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

# this script must run on Python 2.4+

import os
import platform
import sys

support_if_argparse = True # unittest (false)

def is_windows():
    return platform.system() == "Windows"

def get_package_name():
    if is_windows():
        return "fileobj_" # avoid conflict with executable
    else:
        return "fileobj" # XXX integrate with above

def __test(version, name):
    version = tuple(version[:3])
    if name == "Windows":
        __test_windows(version, name)
    else:
        __test_xnix(version, name)
    import curses
    curses
    del curses

def __test_xnix(version, name):
    if name.startswith("CYGWIN") and sys.executable[0] in "ABCDEFG":
        raise Exception("Cygwin Python is required on Cygwin")
    __test_common(version, name)

def __test_windows(version, name):
    __test_common(version, name)

def __test_common(version, name):
    if not support_if_argparse:
        if version < (2, 7, 0) or ((3, 0, 0) <= version < (3, 2, 0)):
            raise Exception("Python 2.7 or Python 3.2+ is required")
    else:
        if version < (2, 6, 0):
            raise Exception("Python 2.7 or Python 3.2+ or Python 2.6 with "
                "backported argparse is required")
        if version < (2, 7, 0) or ((3, 0, 0) <= version < (3, 2, 0)):
            try:
                import argparse
                argparse
                del argparse
            except ImportError:
                raise Exception("Python 2.7 or Python 3.2+ is required")

def test():
    e = os.getenv("__FILEOBJ_USE_DEBUG")
    if e is None:
        debug = False
    else:
        debug = e.lower() != "false"
    try:
        name = platform.system()
        __test(sys.version_info, name)
    except Exception:
        e = sys.exc_info()[1]
        sys.stderr.write("%s\n" % e)
        if debug:
            return
        if name == "Windows" and os.getenv("PROMPT") is None:
            sys.stderr.write("Press Enter key to exit\n")
            sys.stdin.read(1)
        sys.exit(1)

if __name__ == '__main__':
    test()
