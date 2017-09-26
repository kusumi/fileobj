## Notes

+ A new directory *${HOME}/.fileobj* and some files under that directory are automatically created by the program if they don't exist.

+ Some keyboard keys may not work correctly on vt100 terminal.

+ Using *--fg* and/or *--bg* options while running in a terminal multiplexer may cause the cursor to disappear. => Define an environment variable *FILEOBJ_USE_TMUX_CAVEAT* (with any value as shown in below bash example).

        $ export FILEOBJ_USE_TMUX_CAVEAT=

## Notes for PuTTY on Windows

+ Defining an environment variable *FILEOBJ_USE_PUTTY_CAVEAT* (with any value as shown in below bash example) is recommended.

        $ export FILEOBJ_USE_PUTTY_CAVEAT=

+ The window border lines may be shown broken. => Change the section *"Window -> Appearance"* and/or *"Window -> Translation"* to use *"Use font encoding"*.

## Notes for *BSD

+ Entering block visual mode may require *CTRL-v CTRL-v* instead of *CTRL-v*.

+ NetBSD may require py-curses package other than the python package itself (seems no longer necessary in recent NetBSD versions).

        $ uname
        NetBSD
        $ sudo python ./setup.py install --force --record ./install.out
        No module named _curses
        $ cd /usr/pkgsrc/devel/py-curses
        $ sudo make install

## Notes for Darwin

+ Darwin support is experimental and untested. Not all features are supported.

## Notes for Cygwin

+ If Python binaries for both Windows and Cygwin are installed, the shebang line of the executable script (e.g. */usr/bin/fileobj*) may have Windows path which needs to be manually changed to Cygwin path.
