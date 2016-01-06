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
            a = os.path.join(d, s)
            b = os.path.join("./src", s)
            if os.path.isfile(a) and not os.path.isfile(b):
                l.append(a)
    if l:
        for f in l:
            sys.stderr.write("### %s has no such file %s\n" %
                (fileobj.version.get_version_string(), f))
        sys.stderr.write("### Prefer uninstalling older version if exists\n")
        sys.exit(1)
