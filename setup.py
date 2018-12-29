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

if __name__ == '__main__':
    import os
    import sys

    if not os.path.isfile("./setup.py") or not os.path.isdir("./src"):
        sys.stderr.write("Invalid current directory %s\n" % os.getcwd())
        sys.exit(1)

    import src.nodep
    src.nodep.test()

    from distutils.core import setup, Extension
    import src.version

    # The C extension is enabled by default.
    ext_modules = [Extension("fileobj._native", ["src/_native.c"])]

    # Ignore C extension if --no-native is specified.
    s = "--no-native"
    if s in sys.argv:
        ext_modules = None
        while s in sys.argv:
            sys.argv.remove(s)

    # Force Windows specific behavior.
    s = "--windows"
    if s in sys.argv:
        ext_modules = None
        while s in sys.argv:
            sys.argv.remove(s)

    # Two warnings expected on sdist.
    # warning: sdist: missing meta-data: if 'author' supplied, 'author_email' must be supplied too
    # warning: sdist: standard file not found: should have one of README, README.txt

    setup(name      = "fileobj",
        version     = src.version.__version__,
        author      = "Tomohiro Kusumi",
        url         = "https://sourceforge.net/projects/fileobj/",
        description = "Ncurses based hex editor with vi interface",
        license     = "BSD License (2-clause)",
        scripts     = ["script/fileobj"],
        packages    = ["fileobj", "fileobj.ext"],
        package_dir = {"fileobj" : "src", "fileobj.ext" : "src/ext",},
        ext_modules = ext_modules,)
