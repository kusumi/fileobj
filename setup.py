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
    import src.version

    setup(name      = "fileobj",
        version     = src.version.__version__,
        author      = "Tomohiro Kusumi",
        url         = "http://sourceforge.net/projects/fileobj",
        description = "Hex Editor for Linux/BSD",
        license     = "BSD License",
        scripts     = ["script/fileobj"],
        packages    = ["fileobj", "fileobj.ext"],
        package_dir = {"fileobj" : "src", "fileobj.ext" : "src/ext",})

    if sys.argv[1] == "install":
        print(">>> Complete")
        print(">>> README is available at " + src.version.get_readme_url())
