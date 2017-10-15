## General

+ Installation failed due to a missing Python header file. -> **Install *python-devel* package for the Python version in use. The name may differ among platforms, however it's generally called *python-devel* or *python2-devel* or *python3-devel* or something along these lines.**

        Python.h: No such file or directory

+ Installation warned below warning. -> **This can be ignored. GCC may complain this on some old Python versions.**

        warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]

+ An unknown directory appeared under *${HOME}* after running the program. -> **A directory *${HOME}/.fileobj* and some files used by the program are automatically created unless already exist.**

+ Using *--fg* or *--bg* options while running in a terminal multiplexer may cause the cursor to disappear. -> **Defining an environment variable *FILEOBJ_USE_TMUX_CAVEAT* (with any value) may help. See below bash example.**

        $ export FILEOBJ_USE_TMUX_CAVEAT=

## PuTTY on Windows

+ Bold characters are not in bold while running in PuTTY. -> **Defining an environment variable *FILEOBJ_USE_PUTTY_CAVEAT* (with any value) may help. See below bash example.**

        $ export FILEOBJ_USE_PUTTY_CAVEAT=

+ Window frame characters are broken. -> **Modify the section *"Window -> Appearance"*. Modify the section *"Window -> Translation"* to use *"Use font encoding"*.**

## *BSD

+ Can't install on NetBSD due to a missing module *_curses*. -> **NetBSD may require *py-curses* package. See below pkgsrc example.**

        $ uname
        NetBSD
        $ sudo python ./setup.py install --force --record ./install.out
        No module named _curses
        $ cd /usr/pkgsrc/devel/py-curses
        $ sudo make install

+ Can't enter block visual mode via *CTRL-v*. -> **The terminal may require *CTRL-v CTRL-v* instead of *CTRL-v*.**

## Cygwin

+ Can't execute the program after installation. -> **If Python is installed for both Windows and Cygwin, the shebang line of the program (e.g. */usr/bin/fileobj*) may have Windows path which then needs to be manually modified to Cygwin path.**
