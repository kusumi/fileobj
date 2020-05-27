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

if __name__ == '__main__':
    import argparse
    import os
    import re
    import sys

    try:
        import fileobj.util as util
        import fileobj.version as version
    except ImportError as e:
        sys.stderr.write("{0}\n".format(e))
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", default=False)
    if util.is_python_version_or_ht(3, 7):
        parse_args = parser.parse_intermixed_args
    else:
        parse_args = parser.parse_args
    opts = parse_args()

    if opts.all:
        release_log = True
    else:
        release_log = False

    d = os.path.basename(os.getcwd())
    assert d.startswith("fileobj-devel"), os.getcwd()

    f = "./script/autogen.py"
    assert os.path.isfile(f), "No " + f
    assert os.path.samefile(sys.argv[0], f), "Not " + f

    try:
        util.execute("which", "fileobj")
        util.execute("which", "git")
    except Exception as e:
        sys.stderr.write("{0}\n".format(e))
        sys.exit(1)

    def write(f, s):
        assert os.path.isfile(f), "No " + f
        with open(f, "w") as fd:
            fd.write(s)
        assert os.path.isfile(f), "No " + f

    def writel(f, l):
        assert os.path.isfile(f), "No " + f
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

        o = util.execute_sh(cmd)
        assert o.retval == 0, (cmd, o.retval)
        s = o.stdout
        for x in s.split("\n")[:-1]:
            l.append("{0}{1}".format(I, x))
        f = "./doc/README.list_of_options.md"
        writel(f, l)
        print(f)
    except Exception as e:
        sys.stderr.write("{0}\n".format(e))
        sys.exit(1)

    try:
        cmd = "fileobj --env"
        l = ["## List of environment variables"]
        l.append("")
        l.append("{0}$ {1}".format(I, cmd))

        o = util.execute_sh(cmd)
        assert o.retval == 0, (cmd, o.retval)
        s = o.stdout
        for x in s.split("\n")[:-1]:
            l.append("{0}{1}".format(I, x))
        f = "./doc/README.list_of_environment_variables.md"
        writel(f, l)
        print(f)
    except Exception as e:
        sys.stderr.write("{0}\n".format(e))
        sys.exit(1)

    try:
        cmd = "fileobj --command"
        l = ["## List of commands"]
        l.append("")
        l.append("{0}$ {1}".format(I, cmd))

        o = util.execute_sh(cmd)
        assert o.retval == 0, (cmd, o.retval)
        s = o.stdout
        for x in s.split("\n")[:-1]:
            l.append("{0}{1}".format(I, x))
        f = "./doc/README.list_of_commands.md"
        writel(f, l)
        print(f)
    except Exception as e:
        sys.stderr.write("{0}\n".format(e))
        sys.exit(1)

    try:
        f = "./doc/fileobj.1.txt"
        cmd = "LESS= man ./doc/fileobj.1 | col -bx > {0}".format(f)
        o = util.execute_sh(cmd)
        assert o.retval == 0, (cmd, o.retval)
        print(f)
    except Exception as e:
        sys.stderr.write("{0}\n".format(e))
        sys.exit(1)

    try:
        cmd = "git log --pretty=\"%an\" | sort | uniq"
        o = util.execute_sh(cmd)
        assert o.retval == 0, (cmd, o.retval)
        s = o.stdout
        f = "./CONTRIBUTORS"
        write(f, s)
        print(f)
    except Exception as e:
        sys.stderr.write("{0}\n".format(e))
        sys.exit(1)

    # do this last
    try:
        cmd = "git status -s"
        o = util.execute_sh(cmd)
        assert o.retval == 0, (cmd, o.retval)
        s = o.stdout
        print("--")
        print(s)
    except Exception as e:
        sys.stderr.write("{0}\n".format(e))
        sys.exit(1)

    # done unless generating release log
    if not release_log:
        sys.exit(0)

    if os.system("git status | grep \"working directory clean\""):
        sys.stderr.write("Git repository must be clean\n")
        sys.exit(1)

    if not os.system("du -a | grep \"\.pyc\""):
        sys.stderr.write("Found invalid files\n")
        sys.exit(1)

    if not os.system("du -a | grep \"\.swp\""):
        sys.stderr.write("Found invalid files\n")
        sys.exit(1)

    try:
        def checkout(b):
            cmd = "git checkout {0}".format(b)
            if os.system(cmd):
                sys.exit(1)

        def wc():
            cmd = "find . -type f -not -path \"./.git/*\" | xargs wc -cl | tail -1"
            o = util.execute_sh(cmd)
            assert o.retval == 0, (cmd, o.retval)
            s = o.stdout.rstrip()
            if s.endswith(" total"):
                s = s[:-len(" total")]
            return s

        cmd = "git rev-parse --abbrev-ref HEAD"
        o = util.execute_sh(cmd)
        assert o.retval == 0, (cmd, o.retval)
        orig = o.stdout.rstrip()

        cmd = "git log --no-walk --tags --pretty=\"%d %ai\" --decorate=full"
        o = util.execute_sh(cmd)
        assert o.retval == 0, (cmd, o.retval)
        sl = o.stdout.split("\n")

        cmd = "git log -1 --pretty=\"%ai\""
        o = util.execute_sh(cmd)
        assert o.retval == 0, (cmd, o.retval)
        t = version.get_tag_string()
        sl.insert(0, " (refs/tags/{0}) {1}".format(t, o.stdout.rstrip()))

        regex = re.compile(r"^\s+\(.*refs/tags/(v\d\.\d\.\d+).*\)\s+(\d\d\d\d-\d\d-\d\d)\s")
        f = "./RELEASES"
        l = []
        for x in sl:
            m = regex.match(x)
            if m:
                tag, date = m.groups()
                if tag == version.get_tag_string():
                    checkout("HEAD")
                else:
                    checkout(tag)
                l.append("{0} {1} {2}".format(tag, date, wc()))
        checkout(orig)
        assert l, l
        writel(f, l)
    except Exception as e:
        sys.stderr.write("{0}\n".format(e))
        sys.exit(1)
