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

if __name__ == '__main__':
    import os
    import sys
    import fileobj.util

    # Don't run this in a production repository,
    # where a batch of commits are squashed into 1 for every release.
    d = os.path.basename(os.getcwd())
    assert d.startswith("fileobj-devel"), "Not in devel repository"

    f = "./script/autogen.py"
    d = os.path.dirname(f)
    assert os.path.isdir(d), "No " + d
    assert os.path.isfile(f), "No " + f
    assert os.path.samefile(sys.argv[0], f), "Not " + f

    try:
        fileobj.util.execute_sh("which fileobj")
        fileobj.util.execute_sh("which git")
    except Exception as e:
        print(e)
        sys.exit(1)

    def write(f, s):
        with open(f, "w") as fd:
            fd.write(s)
        assert os.path.isfile(f), "No " + f

    def writel(f, l):
        with open(f, "w") as fd:
            for x in l:
                fd.write("{0}\n".format(x))
        assert os.path.isfile(f), "No " + f

    I = " " * 8

    try:
        cmd = "fileobj --help"
        l = ["## List of options"]
        l.append("")
        l.append("{0}$ {1}".format(I, cmd))

        s = fileobj.util.execute_sh(cmd).stdout
        for x in s.split("\n")[:-1]:
            l.append("{0}{1}".format(I, x))
        f = os.path.join(d, "README.list_of_options.md")
        writel(f, l)
        print(f)
    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        cmd = "fileobj --command"
        l = ["## List of commands"]
        l.append("")
        l.append("{0}$ {1}".format(I, cmd))

        s = fileobj.util.execute_sh(cmd).stdout
        for x in s.split("\n")[:-1]:
            l.append("{0}{1}".format(I, x))
        f = os.path.join(d, "README.list_of_commands.md")
        writel(f, l)
        print(f)
    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        cmd = "git log --pretty=\"%an\" | sort | uniq"
        s = fileobj.util.execute_sh(cmd).stdout
        f = "./CONTRIBUTORS"
        write(f, s)
        print(f)
    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        cmd = "git status -s"
        s = fileobj.util.execute_sh(cmd).stdout
        print("--")
        print(s)
    except Exception as e:
        print(e)
        sys.exit(1)
