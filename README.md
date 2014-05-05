fileobj (v0.6.12)
=======

## About

+ [http://sourceforge.net/projects/fileobj/](http://sourceforge.net/projects/fileobj/)

+ fileobj is a hex editor with vi like interface. This software is written in Python and works on Python 2.5, 2.6 and 2.7. It works on Linux, NetBSD, OpenBSD, FreeBSD and possibly other unix operating systems that support ncurses. This software provides basic vi commands for binary editing. Features include insert, replace, delete data in hexadecimal or ascii, cut and paste, undo and redo, visual select, saving buffers, multiple buffers support, multiple windows support, block device (raw disk) support, mapping binary data to C struct, etc.

## Prerequisites

+ Python 2.5, 2.6 or 2.7

+ Python 3 is not supported in v0.6, use v0.7 for Python 3

+ Works on Linux and *BSD

## Install

+ Uninstall previous version if exists

+ Run *setup.py*

        $ sudo python ./setup.py install --force
        $ fileobj --version
        v0.6.12
        $ fileobj

## Uninstall

+ Remove *\`which fileobj\`* and site package directory of this package

+ Find site package directory using *--sitepkg* option

        $ fileobj --sitepkg
        /usr/local/lib/python2.7/site-packages/fileobj

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

+ Generates a new directory *~/.fileobj*

+ Some keyboard keys may not work correctly on vt100 terminal
