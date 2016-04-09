# Copyright (c) 2010-2016, TOMOHIRO KUSUMI
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
        sys.stderr.write("### Invalid current directory %s\n" % os.getcwd())
        sys.stderr.write("### Change directory to %s and try again\n" %
            os.path.abspath(os.path.dirname(sys.argv[0])))
        sys.exit(1)

    import src.nodep
    src.nodep.test()

    from distutils.core import setup
    import src.version

    # Two warnings expected on sdist.
    # warning: sdist: missing meta-data: if 'author' supplied, 'author_email' must be supplied too
    # warning: sdist: standard file not found: should have one of README, README.txt

    setup(name      = "fileobj",
        version     = src.version.__version__,
        author      = "Tomohiro Kusumi",
        url         = "https://sourceforge.net/projects/fileobj/",
        description = "Hex Editor for Linux/BSD",
        license     = "BSD License (2-clause)",
        scripts     = ["script/fileobj"],
        packages    = ["fileobj", "fileobj.ext"],
        package_dir = {"fileobj" : "src", "fileobj.ext" : "src/ext",})
