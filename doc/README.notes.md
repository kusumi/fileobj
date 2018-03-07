## FAQ

+ Installation failed due to a missing Python header file. -> **Install *Python.h* via *python-devel* package for the Python version in use. The name may differ among platforms, however it's generally called *python-devel* or *python2-devel* or *python3-devel* or something along these lines. On Debian based Linux distributions, these packages are probably called *libpython-dev* or *libpython3-dev*.**

        Python.h: No such file or directory

+ Unable to install a missing header file *Python.h*. -> **Run *setup.py* with *--no-native* option. This option mostly provides the same functionality without using C extension. Note that if an older version is installed without *--no-native* option, it should be manually uninstalled first.**

        $ sudo python ./setup.py clean --all
        $ sudo python ./setup.py install --force --record ./install.out --no-native

+ Installation warned below warning. -> **This can be ignored. GCC may complain this on some old Python versions.**

        warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]

+ An unknown directory appeared under *${HOME}* after running the program. -> **A directory *${HOME}/.fileobj* and some files used by the program are automatically created unless already exist.**


## Running in a terminal multiplexer

+ The editor cursor disappears when using *--fg* or *--bg*. -> **Defining an environment variable *FILEOBJ_USE_TMUX_CAVEAT* (with any value) may help. See below bash example.**

        $ export FILEOBJ_USE_TMUX_CAVEAT=

+ Window frames disappear after once changing to a different terminal. -> **Refresh the entire screen with *CTRL-l*. This happens on some platforms.**

## Running in PuTTY on Windows

+ Bold characters are not in bold. -> **Defining an environment variable *FILEOBJ_USE_PUTTY_CAVEAT* (with any value) may help. See below bash example.**

        $ export FILEOBJ_USE_PUTTY_CAVEAT=

+ Window frame characters are broken. -> **Modify the section *"Window -> Appearance"*. Modify the section *"Window -> Translation"* to use *"Use font encoding"*.**

## *BSD

+ Can not install on NetBSD due to a missing module *_curses*. -> **NetBSD may require *py-curses* package. See below pkgsrc example. The binary package name would be for example *py27-curses* for Python 2.7.**

        $ uname
        NetBSD
        $ sudo python ./setup.py install --force --record ./install.out
        No module named _curses
        $ cd /usr/pkgsrc/devel/py-curses
        $ sudo make install

+ Can not enter block visual mode via *CTRL-v*. -> **The terminal may require *CTRL-v CTRL-v* instead of *CTRL-v*.**

## Solaris/illumos

+ Can not enter block visual mode via *CTRL-v*. -> **The terminal may require *CTRL-v CTRL-v* instead of *CTRL-v*.**

## Cygwin

+ Can not execute the program after installation. -> **If Python is installed for both Windows and Cygwin, the shebang line of the program (e.g. *#!/usr/bin/fileobj*) may have Windows path which then needs to be manually modified to Cygwin path.**