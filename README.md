# fileobj ([v0.7.107](https://github.com/kusumi/fileobj/releases/tag/v0.7.107))

## About

+ Ncurses based hex editor with vi interface.

![fileobj-linux](https://raw.githubusercontent.com/kusumi/__misc/master/fileobj/v0.7.90/linux.png)

![fileobj-windows](https://raw.githubusercontent.com/kusumi/__misc/master/fileobj/v0.7.85/windows.png)

## Supported platforms

+ Linux and other Unix-likes

+ Windows (experimental, feature limitations)

## Requirements

+ Python 3.2+

+ ncurses (curses Python module)

+ C compiler (not required on Windows)

## Install

+ (Optionally define *__FILEOBJ_SETUP_USE_MAN* environment variable to make *setup.py* install *[fileobj(1)](doc/fileobj.1.txt)* man page. Unsupported on Windows.)

        $ export __FILEOBJ_SETUP_USE_MAN=

+ Run *setup.py* with following arguments.

        $ python ./setup.py clean --all
        $ python ./setup.py install --force --record ./install.out

## Uninstall

+ Remove files listed in *./install.out*.

## Usage

+ *[paths]* are usually regular files or block devices. *[paths]* can be partially loaded via *offset* and/or *length* specification. Run *fileobj.py* on Windows.

        $ fileobj [options]... [paths]...
        $ fileobj [options]... [paths[@offset:length]]...
        $ fileobj [options]... [paths[@offset-(offset+length)]]...

+ Run with below to test appearance of ncurses.

        $ fileobj --test_screen
        $ fileobj --test_color

+ Run with below to test mouse actions on ncurses.

        $ fileobj --test_mouse

## Resource

+ [https://sourceforge.net/projects/fileobj/](https://sourceforge.net/projects/fileobj/)

+ [https://github.com/kusumi/fileobj/](https://github.com/kusumi/fileobj/)

## [Notes](doc/README.notes.md)

## [Distributions](doc/README.distributions.md)

## [List of options](doc/README.list_of_options.md)

## [List of environment variables](doc/README.list_of_environment_variables.md)

## [List of commands](doc/README.list_of_commands.md)

## [Examples](doc/README.examples.md)
