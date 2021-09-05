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

# This script supports Python 2.4+ (need to show a proper error message).

if __name__ == '__main__':
    import atexit
    import gzip
    import os
    import shutil
    import sys
    from distutils.core import setup, Extension

    man_section = 1
    man_file = "./doc/fileobj.{0}".format(man_section)
    if not os.path.isfile("./setup.py") or \
        not os.path.isfile("./bin/fileobj") or \
        not os.path.isfile(man_file) or \
        not os.path.isfile("./README.md"):
        sys.stderr.write("Invalid current directory %s\n" % os.getcwd())
        sys.exit(1)

    import src.nodep
    import src.version
    src.nodep.test(installation=True)
    pkg = src.nodep.get_package_name()

    # Pretend "test" is supported.
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        sys.exit(0)

    # __FILEOBJ_SETUP_USE_NO_NATIVE: Ignore C extension.
    # __FILEOBJ_SETUP_USE_MAN: Install fileobj(1) man page.
    # __FILEOBJ_SETUP_USE_GZIP: Gzip fileobj(1) man page.
    def test_env(s):
        e = os.getenv("__FILEOBJ_%s" % s)
        if e is None:
            return False
        else:
            return e.lower() != "false"

    def create_gzip(src, dst):
        def cleanup(arg):
            if os.path.isfile(arg):
                os.unlink(arg)
        atexit.register(cleanup, dst)
        fd1 = open(src, "rb")
        fd2 = gzip.open(dst, "wb")
        shutil.copyfileobj(fd1, fd2)
        fd2.close()
        fd1.close()

    nonexistent_man_dir = []
    if src.nodep.is_windows():
        executable = "bin/fileobj.py"
        ext_modules = None
        data_files = None
    else:
        executable = "bin/fileobj"
        if test_env("SETUP_USE_NO_NATIVE"):
            ext_modules = None
        else:
            ext_modules = [Extension(pkg + "._native", ["src/_native.c"])]
        data_files = None
        if test_env("SETUP_USE_MAN"):
            man_dir_candidates = "man/man1", "share/man/man1"
            for man_dir in man_dir_candidates:
                d = os.path.join(sys.prefix, man_dir)
                if os.path.isdir(d):
                    if test_env("SETUP_USE_GZIP"):
                        try:
                            create_gzip(man_file, man_file + ".gz")
                        except Exception:
                            e = sys.exc_info()[1]
                            sys.stderr.write("%s\n" % e)
                            sys.exit(1)
                        f = man_file + ".gz"
                    else:
                        f = man_file
                    assert os.path.isfile(f), f
                    data_files = [(man_dir, [f])]
                    break
                else:
                    nonexistent_man_dir.append(d)
    assert os.path.isfile(executable), executable

    def get_data_files_path(data_files):
        d = os.path.join(sys.prefix, data_files[0][0])
        s = os.path.basename(data_files[0][1][0])
        f = os.path.join(d, s)
        return os.path.realpath(f)

    man_existed = False
    if data_files:
        f = get_data_files_path(data_files)
        if os.path.isfile(f):
            man_existed = True

    #long_description = open("./README.md").read()

    setup(name      = "fileobj",
        version     = src.version.__version__,
        author      = "Tomohiro Kusumi",
        url         = "https://sourceforge.net/projects/fileobj/",
        description = "Ncurses based hex editor with vi interface",
        #long_description = long_description,
        #long_description_content_type = "text/markdown",
        license     = "BSD License (2-clause)",
        scripts     = [executable],
        packages    = [pkg, pkg + ".ext"],
        package_dir = {pkg : "src", pkg + ".ext" : "src/ext",},
        ext_modules = ext_modules,
        data_files  = data_files,
        classifiers = [
            "Programming Language :: Python :: 3",
            "Programming Language :: C",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",],)
        #python_requires = ">=3.2",)

    man_installed = False
    if data_files:
        f = get_data_files_path(data_files)
        if os.path.isfile(f):
            if man_existed:
                sys.stdout.write("Overwrote %s\n" % f)
            else:
                sys.stdout.write("Installed %s\n" % f)
            man_installed = True # actually installed

    if nonexistent_man_dir and not man_installed:
        sys.stderr.write("No such directory %s to install %s\n" %
            (nonexistent_man_dir, os.path.basename(man_file)))
