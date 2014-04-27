fileobj (v0.7.1)
=======

## About

+ [http://sourceforge.net/projects/fileobj/](http://sourceforge.net/projects/fileobj/)

+ fileobj is a hex editor with vi like interface. This software is written in Python and works on Python 2.6 or above. It works on Linux, NetBSD, OpenBSD, FreeBSD and possibly other unix operating systems that support ncurses. This software provides basic vi commands for binary editing. Features include insert, replace, delete data in hexadecimal or ascii, cut and paste, undo and redo, visual select, saving buffers, multiple buffers support, multiple windows support, block device (raw disk) support, mapping binary data to C struct, etc.

## Prerequisites

+ Python 2.6 or above

+ Python 3 is supported since v0.7

+ Python 2.5 support is dropped in v0.7, use v0.6 for Python 2.5

+ Works on Linux and *BSD

## Install

+ Uninstall previous version if exists

+ Run *setup.py* using Python 2

        $ python --version
        Python 2.6.6
        $ sudo python ./setup.py install --force
        $ fileobj --version
        v0.7.1
        $ fileobj

+ or run *setup.py* using Python 3

        $ python3 --version
        Python 3.3.1
        $ sudo python3 ./setup.py install --force
        $ fileobj --version
        v0.7.1
        $ fileobj

## Uninstall

+ Remove *\`which fileobj\`* and site package directory of this package

+ Find site package directory using *--sitepkg* option

        $ fileobj --sitepkg
        /usr/local/lib/python3.3/site-packages/fileobj

## Help

+ Run the program with *--help* option

        $ fileobj --help
        Usage: fileobj [options] [path1 path2 ...]
        For more information, run the program and enter :help<ENTER>
        
        Options:
          --version          show program's version number and exit
          -h, --help         show this help message and exit
          -R                 Read only
          -o <num>           Open <num> windows
          -O                 Open each buffer in different window
          --width=<width>    Set window width [[0-9]+|max|min|auto]
          --fg=<color>       Set foreground color
                             [black|red|green|yellow|blue|magenta|cyan|white]
          --bg=<color>       Set background color
                             [black|red|green|yellow|blue|magenta|cyan|white]
          --command          Print command list
          --sitepkg          Print site package directory

## Note

+ New directory *~/.fileobj* will be made

+ Some keyboard keys may not work correctly on vt100 terminal
