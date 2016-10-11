## Notes

+ A new directory *${HOME}/.fileobj* and some files under that directory are automatically created if they don't exist.

+ Some keyboard keys may not work correctly on vt100 terminal.

+ Set an environment variable *FILEOBJ_USE_TMUX_CAVEAT* (with a blank value as shown in below bash example) if using *--fg* and/or *--bg* options while in terminal multiplexer causes the cursor to disappear.

        $ export FILEOBJ_USE_TMUX_CAVEAT=

## Notes for PuTTY on Windows

+ Setting an environment variable *FILEOBJ_USE_PUTTY_CAVEAT* (with a blank value as shown in below bash example) is recommended.

        $ export FILEOBJ_USE_PUTTY_CAVEAT=

+ If the ncurses' line border characters are broken, change the settings of the section *"Window -> Appearance"* and/or *"Window -> Translation"*. Changing the character set from *"UTF-8"* (or whatever already there) to *"Use font encoding"* may fix the issue.

## Notes for BSDs

+ Entering block visual mode may require *CTRL-v CTRL-v* instead of *CTRL-v*.

+ NetBSD may require py-curses package other than the python package itself (seems no longer necessary in recent NetBSD versions).

        $ uname
        NetBSD
        $ sudo python ./setup.py install --force --record ./install.out
        No module named _curses
        $ cd /usr/pkgsrc/devel/py-curses
        $ sudo make install

## Notes for Darwin

+ Darwin support is experimental. Not all features are supported, but it at least runs.

## Notes for Cygwin

+ If Python binaries for both Windows and Cygwin are installed, the shebang line of the executable script (e.g. */usr/bin/fileobj*) may have Windows path which needs to be manually changed to Cygwin path.
