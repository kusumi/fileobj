# fileobj ([v0.7.95](https://github.com/kusumi/fileobj/releases/tag/v0.7.95))

## About

+ Ncurses based hex editor with vi interface.

![fileobj-linux](https://raw.githubusercontent.com/kusumi/__misc/master/fileobj/v0.7.90/linux.png)

![fileobj-windows](https://raw.githubusercontent.com/kusumi/__misc/master/fileobj/v0.7.85/windows.png)

## Supported platforms

+ 1st tier - Linux

+ 2nd tier - \*BSD, Darwin, Solaris/illumos, Cygwin

+ 3rd tier - Other Unix-likes (untested)

+ Experimental - Windows (feature limitations)

## Requirements

+ Python 3.2 or above

+ ncurses (curses Python module)

## Install

+ Run *setup.py* as follows. Use *python3* if the Python executable is *python3*. On Windows, run without *sudo* with appropriate permission.

        $ sudo python ./setup.py clean --all
        $ sudo python ./setup.py install --force --record ./install.out

+ Run *./script/install_misc.sh* to install a manpage. The location defaults to /usr/local/share/man/man1, but can be specified by an argument. On Windows, see *[doc/fileobj.1.txt](doc/fileobj.1.txt)*.

        $ sudo bash ./script/install_misc.sh
        /usr/local/share/man/man1/fileobj.1.gz: gzip compressed data, from Unix, max compression

+ See *[Notes](doc/README.notes.md)* for installation failure due to a missing header file *Python.h*.

## Uninstall

+ Remove files listed in *install.out* from installation.

+ Remove the manpage if installed.

## Usage

+ *[paths]* are usually regular files or block devices. *[paths]* can be partially loaded via *offset* and/or *length* syntax. On Windows, run *fileobj.py* unless ".PY" is in *PATHEXT* environment variable.

        $ fileobj [options]... [paths]...
        $ fileobj [options]... [paths[@offset:length]]...
        $ fileobj [options]... [paths[@offset-(offset+length)]]...

+ Run with *--test_screen* to test appearance of ncurses.

        $ fileobj --test_screen

## Resource

+ [https://sourceforge.net/projects/fileobj/](https://sourceforge.net/projects/fileobj/)

+ [https://github.com/kusumi/fileobj/](https://github.com/kusumi/fileobj/)

## [Notes](doc/README.notes.md)

## [Distributions](doc/README.distributions.md)

## [List of options](doc/README.list_of_options.md)

## [List of environment variables](doc/README.list_of_environment_variables.md)

## [List of commands](doc/README.list_of_commands.md)

## [Examples](doc/README.examples.md)
