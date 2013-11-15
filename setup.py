if __name__ == '__main__':
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
