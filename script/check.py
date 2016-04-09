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

# https://github.com/kusumi/fileobj/issues/2
# https://github.com/kusumi/fileobj/pull/3

if __name__ == '__main__':
    import os
    import sys

    import fileobj.nodep
    fileobj.nodep.test()

    import fileobj.package
    import fileobj.version

    l = []
    for d in fileobj.package.get_paths():
        for x in fileobj.package.iter_module_name():
            s = x[len(fileobj.package.get_prefix()):]
            s = s.replace(".", "/") + ".py"
            a = os.path.join(d, s) # installed
            b = os.path.join("./src", s) # local
            if os.path.isfile(a) and not os.path.isfile(b):
                l.append(a)
    if l:
        for f in l:
            sys.stderr.write("### %s has no such file %s\n" %
                (fileobj.version.get_version_string(), f))
        sys.stderr.write("### Uninstalling older version(s) "
            "first is recommended if exists\n")
        sys.exit(1)
