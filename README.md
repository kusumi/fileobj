fileobj ([v0.7.56](https://github.com/kusumi/fileobj/releases/tag/v0.7.56))
=======

## About

+ fileobj is a portable console hex editor with vi interface. Requires Python 2.6 or above, and runs on Unix-like operating systems with ncurses.

+ Provides basic vi commands for binary editing. Features include inserting and replacing data in hexadecimal or ascii, deleting data, cut and paste, undo and redo, visual select, multiple buffers and windows, partial file loading, raw disk/partition support, ptrace based userspace editing, data in C struct view, etc.

## Supported Python versions

|-2.5|2.6|2.7|3.0-3.6|
|:---|:--|:--|:------|
|NO  |YES|YES|YES    |

## Supported operating systems

|Linux|\*BSD|Solaris/illumos|Cygwin|Other Unix-likes|Windows|
|:----|:----|:--------------|:-----|:---------------|:------|
|YES  |YES  |YES            |YES   |untested        |NO     |

## Install

+ Run *setup.py* as follows. Use *python3* for Python 3.

        $ sudo python ./setup.py clean --all
        $ sudo python ./setup.py install --force --record ./install.out

+ Run *./script/install.sh* to install a manpage. The location defaults to /usr/share/man/man1, but can be specified by an argument.

        $ sudo bash ./script/install.sh
        /usr/share/man/man1/fileobj.1.gz: gzip compressed data, max compression, from Unix

+ See *[Notes](https://github.com/kusumi/fileobj/blob/v0.7/doc/README.notes.md)* specific to various supported operating systems.

## Uninstall

+ Remove files listed in *install.out* which was generated on installation.

+ Remove the manpage if installed.

## Resource

+ Upstream [https://sourceforge.net/projects/fileobj/](https://sourceforge.net/projects/fileobj/)

+ Repository [https://github.com/kusumi/fileobj/](https://github.com/kusumi/fileobj/)

## [Reporting issues](https://github.com/kusumi/fileobj/issues)

## [Changes](doc/README.changes.md)

## [Notes](doc/README.notes.md)

## [Distributions](doc/README.distributions.md)

## [List of options](doc/README.list_of_options.md)

## [List of commands](doc/README.list_of_commands.md)

## [Examples](doc/README.examples.md)
