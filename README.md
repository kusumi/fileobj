fileobj ([v0.7.45](https://github.com/kusumi/fileobj/releases/tag/v0.7.45))
=======

## About

+ [https://sourceforge.net/projects/fileobj/](https://sourceforge.net/projects/fileobj/)

+ fileobj is a portable hex editor with vi like interface. This software is written in Python and runs on Python 2.6 or above. This software supports Linux, BSDs in general, and Cygwin. Other Unix-like operating systems with ncurses are experimentally supported. This software provides basic vi commands for binary editing. Features include inserting, replacing, deleting data in hexadecimal or ascii, cut and paste, undo and redo, visual select, partial buffer loading, support for multiple buffers and windows, block device editing, ptrace based userspace editing, mapping data to C style struct, etc.

+ Repository is available at [https://github.com/kusumi/fileobj/tree/v0.7/](https://github.com/kusumi/fileobj/tree/v0.7/).

## Supported Python versions

|<=2.5|2.6|2.7|3.0|3.1|3.2|3.3|3.4|3.5|3.6|
|:----|:--|:--|:--|:--|:--|:--|:--|:--|:--|
|NO   |YES|YES|YES|YES|YES|YES|YES|YES|YES|

## Supported operating systems

|Linux|NetBSD|OpenBSD|FreeBSD|DragonFlyBSD|Darwin |Windows|Cygwin|Others    |
|:----|:-----|:------|:------|:-----------|:------|:------|:-----|:---------|
|YES  |YES   |YES    |YES    |YES         |LIMITED|NO     |YES   |DON'T KNOW|

## Install

+ [Uninstall](#uninstall) older version(s) if possible.

+ For Python 2, run *[setup.py](https://docs.python.org/2/install/index.html)* as follows.

        $ sudo python ./setup.py clean --all
        $ sudo python ./setup.py install --force --record ./install.out

+ For Python 3, run *[setup.py](https://docs.python.org/3/installing/index.html)* as follows.

        $ sudo python3 ./setup.py clean --all
        $ sudo python3 ./setup.py install --force --record ./install.out

+ Run *./script/install.sh* to install fileobj(1) manpage under */usr/share/man/man1/*.

        $ sudo bash ./script/install.sh
        /usr/share/man/man1/fileobj.1.gz: gzip compressed data, from Unix, max compression

+ See [Notes](https://github.com/kusumi/fileobj/blob/v0.7/script/README.notes.md) specific to various supported operating systems.

## Uninstall

+ Remove files listed in *install.out*.

+ Remove */usr/share/man/man1/fileobj.1.gz* if fileobj(1) manpage is installed.

## [Reporting issues](https://github.com/kusumi/fileobj/issues)

## [Changes](https://github.com/kusumi/fileobj/blob/v0.7/script/README.changes.md)

## [Notes](https://github.com/kusumi/fileobj/blob/v0.7/script/README.notes.md)

## [Distributions](https://github.com/kusumi/fileobj/blob/v0.7/script/README.distributions.md)

## [List of options](https://github.com/kusumi/fileobj/blob/v0.7/script/README.list_of_options.md)

## [List of commands](https://github.com/kusumi/fileobj/blob/v0.7/script/README.list_of_commands.md)

## [Examples](https://github.com/kusumi/fileobj/blob/v0.7/script/README.examples.md)
