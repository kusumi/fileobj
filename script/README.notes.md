## Notes

+ Creates a new directory *${HOME}/.fileobj* if it doesn't exist, and creates some files under the directory.

+ Some keyboard keys may not work correctly on vt100 terminal.

+ Set an environment variable *FILEOBJ_USE_TMUX_CAVEAT* (with a blank value as shown in below bash example) if using *--fg* and/or *--bg* options while in terminal multiplexer causes the cursor to disappear.

        $ export FILEOBJ_USE_TMUX_CAVEAT=

## Notes for PuTTY on Windows

+ Setting an environment variable *FILEOBJ_USE_PUTTY_CAVEAT* (with a blank value as shown in below bash example) is recommended.

        $ export FILEOBJ_USE_PUTTY_CAVEAT=

+ If the ncurses' line border characters are broken, change the settings of the section *"Window -> Appearance"* and/or *"Window -> Translation"*. Changing the character set from *"UTF-8"* (or whatever already there) to *"Use font encoding"* may fix the issue.

## Notes for BSDs

+ Binary package for older version is available on [FreeBSD](https://www.freebsd.org/cgi/ports.cgi?query=fileobj&stype=name).

        $ uname
        FreeBSD
        $ sudo pkg search fileobj
        fileobj-0.7.25                 Portable hex editor with vi like interface
        $ sudo pkg install fileobj

+ Binary package for older version is also available on DragonFlyBSD.

        $ uname
        DragonFly
        $ sudo pkg search fileobj
        fileobj-0.7.25                 Portable hex editor with vi like interface
        $ sudo pkg install fileobj

+ NetBSD requires py-curses package other than the python package itself.

        $ uname
        NetBSD
        $ sudo python ./setup.py install --force --record ./install.out
        No module named _curses
        $ cd /usr/pkgsrc/devel/py-curses
        $ sudo make install

+ Entering block visual mode may require *CTRL-v CTRL-v* instead of *CTRL-v*.

## Notes for Darwin

+ Darwin support is experimental. Not all features are supported, but it at least runs.

## Notes for Cygwin

+ Cygwin support is experimental. Not all features are supported, but it at least runs.

+ If Python binaries for both Windows and Cygwin are installed, the shebang line of the executable script (e.g. */usr/bin/fileobj*) may have Windows path which needs to be manually changed to Cygwin path.
