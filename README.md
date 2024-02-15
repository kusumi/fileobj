# fileobj ([v0.8.4](https://github.com/kusumi/fileobj/releases/tag/v0.8.4))

## About

+ Ncurses based hex editor with vi interface.

![fileobj-linux](https://raw.githubusercontent.com/kusumi/__misc/master/fileobj/v0.8.0/linux.png)

![fileobj-windows](https://raw.githubusercontent.com/kusumi/__misc/master/fileobj/v0.8.0/windows.png)

## Supported platforms

+ Linux and other Unix-likes

+ Windows (experimental, feature limitations)

## Requirements

+ Python 3.2+

+ ncurses (curses Python module)

+ C compiler (not required on Windows)

## Install

+ Run the command below.

        $ sudo python3 -m pip install /path/to/repository

+ Or run the commands below (recent Python versions will warn as deprecated).

        $ cd /path/to/repository
        $ sudo python3 -m pip install setuptools
        $ sudo python3 ./setup.py install --force --record ./install.out

## Uninstall

+ Run the command below, or remove files listed in *install.out* from above.

        $ sudo python3 -m pip uninstall -y fileobj

## [Usage](doc/fileobj.1.txt)

+ *[paths]* are usually regular files or block devices. *[paths]* can be partially loaded via *offset* and/or *length* specification. Run *fileobj.py* on Windows.

        $ fileobj [options]... [paths]...
        $ fileobj [options]... [paths[@offset:length]]...
        $ fileobj [options]... [paths[@offset-(offset+length)]]...

+ Run with the following options to test appearance of ncurses.

        $ fileobj --test_screen
        $ fileobj --test_color

+ Run with the following option to test mouse actions on ncurses.

        $ fileobj --test_mouse

## [Notes](doc/README.notes.md)

## [Distributions](doc/README.distributions.md)

## [List of options](doc/README.list_of_options.md)

## [List of environment variables](doc/README.list_of_environment_variables.md)

## [List of commands](doc/README.list_of_commands.md)

## [Examples](doc/README.examples.md)
