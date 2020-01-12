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

# This script must run on Python 2.4 or above.
# Although Python 2 is unsupported, it needs to exit with an error message.

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

def __test(version, name, permissive):
    version = tuple(version[:3])
    if name == "Windows":
        __test_windows(version, name, permissive)
    else:
        __test_xnix(version, name, permissive)
    import curses
    curses
    del curses

def __test_xnix(version, name, permissive):
    if name.startswith("CYGWIN") and sys.executable[0] in "ABCDEFG":
        raise Exception("Cygwin Python is required on Cygwin")
    __test_common(version, name, permissive)

def __test_windows(version, name, permissive):
    __test_common(version, name, permissive)

def __test_common(version, name, permissive):
    if permissive:
        __test_permissive_install(version, name)
    else:
        __test_strict_install(version, name)

# https://www.python.org/doc/sunset-python-2/
# Given EOL of Python 2.7, fileobj no longer officially supports Python 2,
# but the code still runs on Python 2.7 as of January 2020.

def __test_strict_install(version, name):
    if version[0] <= 2 or ((3, 0, 0) <= version < (3, 2, 0)):
        raise Exception("Python 3.2 or above is required")

def __test_permissive_install(version, name):
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

def test(installation=False):
    e = os.getenv("__FILEOBJ_USE_DEBUG")
    if e is None:
        debug = False
    else:
        debug = e.lower() != "false"

    e = os.getenv("__FILEOBJ_USE_PERMISSIVE_INSTALL")
    if e is None:
        permissive = False
    else:
        permissive = e.lower() != "false"
    if not installation:
        permissive = True # allow Python 2.7 unless installation

    try:
        name = platform.system()
        __test(sys.version_info, name, permissive)
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
