# fileobj ([v0.7.76](https://github.com/kusumi/fileobj/releases/tag/v0.7.76))

## About

+ Ncurses based hex editor with vi interface.

+ Features include inserting and replacing data in hexadecimal or ascii, deleting data, cut and paste, undo and redo, visual select, multiple buffers and windows, partial file loading, raw disk/partition support, ptrace based userspace editing, data in C struct view, etc.

![fileobj](https://a.fsdn.com/con/app/proj/fileobj/screenshots/fileobj-v0.7.76.png/max/max/1)

## Supported Python versions

|-2.6|2.7|3.0|3.1|3.2-3.7|
|:---|:--|:--|:--|-------|
|NO  |YES|NO |NO |YES    |

## Supported operating systems

|Linux|\*BSD|Darwin|Solaris/illumos|Cygwin|Other Unix-likes|Windows|
|:----|:----|:-----|:--------------|:-----|:---------------|:------|
|YES  |YES  |YES   |YES            |YES   |untested        |NO     |

## Install

+ Run *setup.py* as follows. Use *python3* for Python 3.

        $ sudo python ./setup.py clean --all
        $ sudo python ./setup.py install --force --record ./install.out

+ Run *./script/install.sh* to install a manpage. The location defaults to /usr/local/share/man/man1, but can be specified by an argument.

        $ sudo bash ./script/install.sh
        /usr/local/share/man/man1/fileobj.1.gz: gzip compressed data, from Unix, max compression

+ See *[Notes](doc/README.notes.md)* for compilation error due to a missing header file *Python.h*, and other platform specific information.

## Uninstall

+ Remove files listed in *install.out* from installation.

+ Remove the manpage if installed.

## Usage

+ *[paths]* are usually regular files or block devices. *[paths]* can be partially loaded via *offset* or *length* syntax.

        $ fileobj [options]... [paths]...
        $ fileobj [options]... [paths[@offset:length]]...
        $ fileobj [options]... [paths[@offset-(offset+length)]]...

## Resource

+ Upstream [https://sourceforge.net/projects/fileobj/](https://sourceforge.net/projects/fileobj/)

+ Repository [https://github.com/kusumi/fileobj/](https://github.com/kusumi/fileobj/)

## [Notes](doc/README.notes.md)

## [Distributions](doc/README.distributions.md)

## [List of options](doc/README.list_of_options.md)

## [List of commands](doc/README.list_of_commands.md)

## [Examples](doc/README.examples.md)
