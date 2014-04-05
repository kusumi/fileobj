fileobj
=======

## About

+ [http://sourceforge.net/projects/fileobj/](http://sourceforge.net/projects/fileobj/)

+ fileobj is a hex editor with vi like interface. This software is written in Python and works on Python 2.5, 2.6 and 2.7. It works on Linux, NetBSD, OpenBSD, FreeBSD and possibly other unix operating systems that support ncurses. This software provides basic vi commands for binary editing. Features include insert, replace, delete data in hexadecimal or ascii, cut and paste, undo and redo, visual select, saving buffers, multiple buffers support, multiple windows support, block device (raw disk) support, mapping binary data to C struct, etc.

## Prerequisites

+ Python 2.5, 2.6 or 2.7

+ Python 3.x is not supported

+ Works on Linux and *BSD

## Install

+ Uninstall previous version if exists

+ Run *setup.py*

        $ sudo python ./setup.py install --force
        $ fileobj --version
        v0.6.10
        $ fileobj

## Uninstall

+ Remove *\`which fileobj\`* and site package directory of this package

+ Find site package directory using *--sitepkg* option

        $ fileobj --sitepkg
        /usr/local/lib/python2.7/site-packages/fileobj

## Help

+ Execute *:help* command

+ or run the program using *--help* option

        $ fileobj --help

## Note

+ New directory *~/.fileobj* will be made

+ Some keyboard keys may not work correctly on vt100 terminal
