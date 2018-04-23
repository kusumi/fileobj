## FAQ

+ Can not install due to a missing header file *Python.h*. -> **Install *Python.h* via *python-devel* package for the Python version in use. The name may differ among platforms, however it's generally called *python-devel* or *python2-devel* or *python3-devel* or something along these lines. On Debian based Linux distributions, these are probably called *libpython-dev* or *libpython3-dev*.**

        Python.h: No such file or directory

+ Can not install the missing header file *Python.h*. -> **Run *setup.py* with *--no-native* option. This option provides the same functionality without using C extension. If an older version is installed without *--no-native* option, it should be uninstalled first.**

        $ sudo python ./setup.py clean --all
        $ sudo python ./setup.py install --force --record ./install.out --no-native

+ Installation warned below. -> **This can be ignored. GCC may complain this on some old Python versions.**

        warning: 'PyArg_ParseTuple' is an unrecognized format function type [-Wformat=]

+ Installation warned below. -> **This can be ignored. This seems to happen with Python 3.5 and certain versions of GCC.**

        In function '__get_ptrace_word_size':
        warning: will never be executed
        In function '__ptrace_detach':
        warning: will never be executed
        In function '__ptrace_attach':
        warning: will never be executed
        In function '__ptrace_pokedata':
        warning: will never be executed
        In function '__ptrace_poketext':
        warning: will never be executed

+ A directory *${HOME}/.fileobj* appeared after running *fileobj* for the first time. -> ***fileobj* automatically creates *${HOME}/.fileobj* and some files under the directory if they do not exist.**

+ Can not enter block visual mode via *CTRL-v*. -> **The terminal may require *CTRL-v CTRL-v* if *CTRL-v* does not work.**

## Terminal multiplexer

+ Window frames are corrupted with Python 3. -> **Try different *TERM* variable other than *"screen"*.**

+ Window frames disappear after once changing to a different terminal. -> **Refresh the entire screen with *CTRL-l*. This happens on some platforms.**

## PuTTY

+ Window frames are corrupted. -> **Modify the section *"Window -> Appearance"*. Modify the section *"Window -> Translation"* to use *"Use font encoding"*.**

## NetBSD

+ Can not install on NetBSD due to a missing module *_curses*. -> **NetBSD may require *py-curses* package. The binary package name would be for example *py27-curses* for Python 2.7.**

        $ uname
        NetBSD
        $ sudo python ./setup.py install --force --record ./install.out
        No module named _curses
        $ cd /usr/pkgsrc/devel/py-curses
        $ sudo make install

## Cygwin

+ Can not run *fileobj* after successful installation. -> **If Python is installed for both Windows and Cygwin, shebang line of *fileobj* (e.g. */usr/bin/fileobj*) may be Windows path instead of Cygwin path which then needs to be manually modified to Cygwin path (e.g. *#!/usr/bin/python*).**
