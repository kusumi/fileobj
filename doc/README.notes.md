## General

+ Can not install due to a missing header file *Python.h*. -> **Install *Python.h* via *python-devel* package. The name may differ among platforms, but it's generally called *python-devel* or *python2-devel* or *python3-devel* or something along these lines. On Debian based Linux distributions, these are probably called *libpython-dev* or *libpython3-dev*.**

        Python.h: No such file or directory

+ A directory *${HOME}/.fileobj* appeared after running *fileobj* for the first time. -> ***fileobj* automatically creates *${HOME}/.fileobj* and some files under the directory if they do not exist.**

+ Can not enter block visual mode via *CTRL-v*. -> **Some terminals require *CTRL-v CTRL-v* if *CTRL-v* does not work, but some terminals do not support *CTRL-V*.**

## Terminal multiplexer

+ Window frames are corrupted with Python 3. -> **Try different *TERM* variable other than *"screen"*.**

+ Window frames disappear after once changing to a different terminal. -> **Refresh the entire screen with *CTRL-l*. This happens on some platforms.**

## PuTTY

+ Window frames are corrupted. ->

    + **Modify the section *"Window -> Appearance"*.**

    + **Modify the section *"Window -> Translation"* to use *"Use font encoding"*.**

    + **Try different *TERM* variable.**

## NetBSD

+ Can not install due to a missing module *_curses*. -> **NetBSD may require *py-curses* package. The binary package name would be for example *py37-curses* for Python 3.7.**

        $ cd /usr/pkgsrc/devel/py-curses
        $ make install

## Windows 10

+ Can not install due to a missing module *_curses*. -> **Install *windows-curses*.**

        > pip install windows-curses

+ *CTRL-c* can not interrupt ongoing editor command. -> ***windows-curses* module can not handle Unix signals, whereas regular Python applications on Windows can handle some Unix signals.**

+ There is no *fileobj* package in site-packages directory. -> **On Windows, *fileobj* package is installed as *fileobj_*.**

## Windows Subsystem for Linux

+ Can not enter block visual mode via *CTRL-v*. -> **WSL does not seem to support *CTRL-V*. See [https://github.com/microsoft/WSL/issues/2588](https://github.com/microsoft/WSL/issues/2588) for details.**

## Windows Terminal

+ Can not enter block visual mode via *CTRL-v*. -> **Windows Terminal does not seem to support *CTRL-V*.**

+ Mouse events are ignored. -> **Windows Terminal does not seem to support mouse events.**
