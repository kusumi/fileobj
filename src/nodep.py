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

import platform
import sys

def __test(version, name):
    if not version:
        version = sys.version_info
    version = tuple(version[:3])
    if not name:
        name = platform.system()

    s = "Using Python %s" % '.'.join([str(x) for x in version])
    if version < (2, 6, 0):
        raise Exception("%s\nPython 2.6 or above is required" % s)
    elif name == "Windows" and not is_cygwin(name):
        raise Exception("Windows is not supported")
    import curses
    del curses

def is_cygwin(name):
    if name.startswith("CYGWIN"):
        return True
    if not name.startswith("Windows"):
        return False
    try:
        import subprocess
        p = subprocess.Popen(["uname"], stdout=subprocess.PIPE)
        s = p.communicate()[0]
        return s.startswith("CYGWIN")
    except Exception:
        return False

def test():
    try:
        __test(None, None)
    except Exception:
        e = sys.exc_info()[1]
        for s in str(e).split("\n"):
            sys.stderr.write("### %s\n" % s)
        sys.exit(1)

if __name__ == '__main__':
    test()
