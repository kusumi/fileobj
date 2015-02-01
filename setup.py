if __name__ == '__main__':
    import os
    import sys
    if not os.path.isfile("./setup.py") or \
        not os.path.isdir("./src"):
        # it'll fail anyway but just to make sure
        sys.stderr.write(
            "### Invalid current directory %s, cd %s and try again.\n" % (
            os.getcwd(),
            os.path.abspath(os.path.dirname(sys.argv[0]))))
        sys.exit(1)

    import src.nodep
    src.nodep.test()

    from distutils.core import setup
    from src.version import __version__

    setup(name      = "fileobj",
        version     = __version__,
        author      = "Tomohiro Kusumi",
        author_email= "`last_name_in_lower_case`@users.sourceforge.net",
        url         = "http://sourceforge.net/projects/fileobj",
        description = "Hex Editor for Linux/BSD",
        license     = "BSD License",
        scripts     = ["script/fileobj"],
        packages    = ["fileobj", "fileobj.ext"],
        package_dir = {"fileobj" : "src", "fileobj.ext" : "src/ext",})

    import fileobj.package
    import fileobj.version
    l = []
    for d in fileobj.package.get_paths():
        for x in fileobj.package.iter_module_name():
            s = x[len(fileobj.package.get_prefix()):]
            s = s.replace(".", "/") + ".py"
            a = os.path.join(d, s)
            b = os.path.join("./src", s)
            if os.path.isfile(a) and not os.path.isfile(b):
                l.append(a)
    if l:
        for f in l:
            sys.stderr.write("### %s has no such file %s\n" %
                (fileobj.version.get_version_string(), f))
        sys.stderr.write("### Prefer uninstalling older version if exists\n")
        sys.exit(2)
