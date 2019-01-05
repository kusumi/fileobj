# fileobj ([v0.7.83](https://github.com/kusumi/fileobj/releases/tag/v0.7.83))

## About

+ Ncurses based hex editor with vi interface.

+ Features include inserting and replacing data in hexadecimal or ascii, deleting data, cut and paste, undo and redo, visual select, multiple buffers and windows, partial file loading, raw disk/partition support, ptrace based userspace editing, data in C struct view, etc.

![fileobj-linux](https://a.fsdn.com/con/app/proj/fileobj/screenshots/fileobj-v0.7.82-linux.png/max/max/1)

![fileobj-windows](https://a.fsdn.com/con/app/proj/fileobj/screenshots/fileobj-v0.7.82-windows.png/max/max/1)

## Supported platforms

+ 1st tier - Linux

+ 2nd tier - \*BSD, Darwin, Solaris/illumos, Cygwin

+ 3rd tier - Other Unix-likes (untested)

+ experimental - Windows (feature limitations)

## Requirements

+ Python 2.7 or Python 3.2+

+ (Python 3.3+ for Windows)

+ ncurses (curses Python module)

## Install

+ Run *setup.py* as follows. Use *python3* for Python 3. On Windows, run without *sudo* with appropriate permission.

        $ sudo python ./setup.py clean --all
        $ sudo python ./setup.py install --force --record ./install.out

+ Run *./script/install_misc.sh* to install a manpage. The location defaults to /usr/local/share/man/man1, but can be specified by an argument. On Windows, see *[doc/fileobj.1.txt](doc/fileobj.1.txt)*.

        $ sudo bash ./script/install_misc.sh
        /usr/local/share/man/man1/fileobj.1.gz: gzip compressed data, from Unix, max compression

+ See *[Notes](doc/README.notes.md)* for compilation error due to a missing header file *Python.h*, and other platform specific information.

## Uninstall

+ Remove files listed in *install.out* from installation.

+ Remove the manpage if installed.

## Usage

+ *[paths]* are usually regular files or block devices. *[paths]* can be partially loaded via *offset* or *length* syntax. On Windows, run *fileobj.py* unless ".PY" is in *PATHEXT* environment variable.

        $ fileobj [options]... [paths]...
        $ fileobj [options]... [paths[@offset:length]]...
        $ fileobj [options]... [paths[@offset-(offset+length)]]...

+ Run with *--test_screen* to test appearance of ncurses.

        $ fileobj --test_screen

## Resource

+ Upstream [https://sourceforge.net/projects/fileobj/](https://sourceforge.net/projects/fileobj/)

+ Repository [https://github.com/kusumi/fileobj/](https://github.com/kusumi/fileobj/)

## [Notes](doc/README.notes.md)

## [Distributions](doc/README.distributions.md)

## [List of options](doc/README.list_of_options.md)

## [List of environment variables](doc/README.list_of_environment_variables.md)

## [List of commands](doc/README.list_of_commands.md)

## [Examples](doc/README.examples.md)
