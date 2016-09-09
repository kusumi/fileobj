fileobj ([v0.7.35](https://github.com/kusumi/fileobj/releases/tag/v0.7.35))
=======

## About

+ [https://sourceforge.net/projects/fileobj/](https://sourceforge.net/projects/fileobj/)

+ fileobj is a portable hex editor with vi like interface. This software is written in Python and runs on Python 2.6 or above. This software supports Linux distributions and BSDs in general. Other Unix-like operating systems with ncurses are experimentally supported. This software provides basic vi commands for binary editing. Features include inserting, replacing, deleting data in hexadecimal or ascii, cut and paste, undo and redo, visual select, partial buffer loading, support for multiple buffers and windows, block device editing, ptrace based userspace editing, mapping data to C style struct, etc.

+ Repository is available at [https://github.com/kusumi/fileobj/tree/v0.7/](https://github.com/kusumi/fileobj/tree/v0.7/).

+ See [CHANGES](https://github.com/kusumi/fileobj/blob/v0.7/CHANGES) for changes.

## Supported Python versions

|<=2.5|2.6|2.7|3.0|3.1|3.2|3.3|3.4|3.5|
|:----|:--|:--|:--|:--|:--|:--|:--|:--|
|NO   |YES|YES|YES|YES|YES|YES|YES|YES|

## Supported OS

|Linux|NetBSD|OpenBSD|FreeBSD|DragonFlyBSD|Darwin      |Windows|Cygwin      |Other Unix-like |
|:----|:-----|:------|:------|:-----------|:-----------|:------|:-----------|:---------------|
|YES  |YES   |YES    |YES    |YES         |EXPERIMENTAL|NO     |EXPERIMENTAL|DON'T KNOW      |

## Prerequisites

+ ncurses

## Install

+ Uninstalling older version(s) first is recommended if exists.

+ Run *setup.py* using Python 2.

        $ python --version
        Python 2.6.6
        $ sudo python ./setup.py install --force --record ./install.out
        $ fileobj --version
        v0.7.35

    + See [Installing Python Modules](https://docs.python.org/2/install/index.html) for custom installation.

+ or run *setup.py* using Python 3.

        $ python3 --version
        Python 3.3.1
        $ sudo python3 ./setup.py install --force --record ./install.out
        $ fileobj --version
        v0.7.35

    + See [Installing Python Modules](https://docs.python.org/3/installing/index.html) for custom installation.

+ See *Note for BSDs* for binary packages available on FreeBSD and DragonFlyBSD.

+ See *Note for Cygwin* if Python binaries for both Windows and Cygwin are installed.

+ Run *./script/install.sh* to install fileobj(1) manpage under */usr/share/man/man1/*.

        $ sudo bash ./script/install.sh
        /usr/share/man/man1/fileobj.1.gz: gzip compressed data, from Unix, max compression
        $ man 1 fileobj

## Uninstall

+ Remove files listed in *install.out*.

+ Remove */usr/share/man/man1/fileobj.1.gz* if fileobj(1) manpage is installed.

## List of options

        $ fileobj --help
        Usage: fileobj [options]... [paths]...
        
        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -R                    Use read-only mode.
          -B                    Use malloc(3) based buffer for regular files, which
                                may put pressure on the system depending on the file
                                size. Regular files use mmap(2) based buffer by
                                default, and relies on mremap(2) when resizing (i.e.
                                insert or delete bytes) the buffer. This option is
                                used when the system doesn't support mremap(2), but
                                need to resize the buffer for regular files. Linux
                                kernel has mremap(2), but many of the BSDs do not.
          -d                    Enable a window to show the buffer offset from offset
                                to offset+length rather than from from 0 to length,
                                when the buffer is partially loaded. Using
                                @offset:length or @offset-(offset+length) syntax right
                                after the path allows partial buffer loading. See
                                DOCUMENTATION section of fileobj(1) for details of the
                                syntax.
          -x                    Enable a window to show the buffer size and current
                                position in hexadecimal.
          -o <num>              Start the program with each buffer given by paths
                                loaded in <num> windows, as long as the terminal has
                                enough size to store the number of windows specified.
          -O                    Start the program with each buffer given by paths
                                loaded in different windows, as long as the terminal
                                has enough size to store the number of windows
                                specified.
          --bytes_per_line=<bytes_per_line>
                                Specify number of bytes printed per line. The program
                                prints <bytes_per_line> bytes for each line as long as
                                the terminal has enough width to store bytes.
                                Available formats for <bytes_per_line> are digits,
                                "max", "min" and "auto". If this option isn't
                                specified, the program assumes "auto" is specified.
                                Using "auto" sets the value to the maximum 2^N that
                                fits in the terminal width.
          --bytes_per_window=<bytes_per_window>
                                Specify number of bytes printed per window, based on
                                the current number of bytes per line. The program
                                prints <bytes_per_window> bytes for each window as
                                long as the terminal has enough size to store bytes.
                                Available formats for <bytes_per_window> are digits,
                                "even" and "auto". Specifying "even" doesn't specify
                                the size of window, but makes all windows have the
                                same size. If this option isn't specified, the program
                                assumes "auto" is specified. Using "auto" sets the
                                value to the maximum available that fits in the
                                terminal size, based on the current number of bytes
                                per line.
          --terminal_height=<terminal_height>
                                Specify the terminal height. The program uses
                                <terminal_height> lines as long as the terminal has
                                enough height to store lines. This option is usually
                                unnecessary as the program is able to retrieve the
                                terminal height by default.
          --terminal_width=<terminal_width>
                                Specify the terminal width. The program uses
                                <terminal_width> bytes for each line as long as the
                                terminal has enough width to store the bytes. This
                                option is usually unnecessary as the program is able
                                to retrieve the terminal width by default.
          --fg=<color>          Specify foreground color of the terminal. Available
                                colors for <color> are "black", "blue", "cyan",
                                "green", "magenta", "red", "white" and "yellow". If
                                neither this option nor --bg option are specified, the
                                program assumes "black" is specified.
          --bg=<color>          Specify background color of the terminal. Available
                                colors for <color> are "black", "blue", "cyan",
                                "green", "magenta", "red", "white" and "yellow". If
                                neither this option nor --fg option are specified, the
                                program assumes "white" is specified.
          --simple              Use simplified status window format.
          --command             Print the list of available editor commands and exit.
          --sitepkg             Print Python's site-package directory being used by
                                the program and exit.

## List of commands

        $ fileobj --command
        <CTRL>a                  Add [count] to the number at cursor
        <CTRL>b                  Scroll window [count] pages backward in the buffer
        <CTRL>u                  Scroll window [count] half pages backward in the buffer
        <CTRL>f                  Scroll window [count] pages forward in the buffer
        <CTRL>d                  Scroll window [count] half pages forward in the buffer
        <CTRL>g                  Print current size and position
        g<CTRL>g                 Print current size and position in sector for block device
        <CTRL>l                  Refresh screen
        <CTRL>r                  Redo changes
        <CTRL>w+                 Increase current window height [count] lines
        <CTRL>w-                 Decrease current window height [count] lines
        <CTRL>wW                 Change to the prev window
        <CTRL>wb                 Change to the bottom window
        <CTRL>w<CTRL>b           Change to the bottom window
        <CTRL>ws                 Split current window
        <CTRL>w<CTRL>s           Split current window
        <CTRL>wv                 Split current window
        <CTRL>w<CTRL>v           Split current window
        <CTRL>wt                 Change to the top window
        <CTRL>w<CTRL>t           Change to the top window
        <CTRL>ww                 Change to the next window
        <CTRL>w<CTRL>w           Change to the next window
        <CTRL>x                  Subtract [count] from the number at cursor
        <ESCAPE>                 Clear input or escape from current mode
        "[0-9a-zA-Z"]            Use register {0-9a-zA-Z"} for next delete, yank or put (use uppercase character to append with delete and yank)
        &[0-9a-fA-F]{2}          Replace [count] bytes with bitwise and-ed bytes
        |[0-9a-fA-F]{2}          Replace [count] bytes with bitwise or-ed bytes
        ^[0-9a-fA-F]{2}          Replace [count] bytes with bitwise xor-ed bytes
        )                        Go to the next zero (\x00)
        (                        Go to the previous zero (\x00)
        }                        Go to the next non zero character
        {                        Go to the previous non zero character
        ]                        End reading buffered [count] value
        [                        Start reading buffered [count] value
        +                        Go [count] lines downward, on the first character of the line
        -                        Go [count] lines upward, on the first character of the line
        .                        Repeat last change
        /                        Search forward
        ?                        Search backward
        0                        Go to the first character of the line
        $                        Go to the end of the line. If a count is given go [count]-1 lines downward
        :args                    Print buffer list with the current buffer in brackets
        :argv                    Print arguments of this program
        :bfirst                  Go to the first buffer in buffer list
        :brewind                 Go to the first buffer in buffer list
        :blast                   Go to the last buffer in buffer list
        :bnext                   Change buffer to the next
        <TAB>                    Change buffer to the next
        :bprevious               Change buffer to the previous
        :bNext                   Change buffer to the previous
        :bufsiz                  Print temporary buffer size
        :close                   Close current window
        <CTRL>wc                 Close current window
        :cmp                     Compare two buffers and go to the first non matching byte
        :cmp!                    Compare two buffers and go to the first matching byte
        :cmpnext                 Compare two buffers starting from the next byte and go to the first non matching byte
        :cmpnext!                Compare two buffers starting from the next byte and go to the first matching byte
        :date                    Print date
        :delmarks                Delete the specified marks
        :delmarks!               Delete all marks for the current buffer except for uppercase marks
        :e                       Open a buffer
        :bdelete                 Close a buffer
        :extensions              Show list of extensions
        :fcls                    Print Python class name of the current buffer
        :help                    Show list of commands
        :hostname                Print hostname
        :kmod                    Print Python module name for the platform OS
        :lang                    Print locale type
        :md5                     Print md5 message digest of the current buffer
        :only                    Make the current window the only one
        <CTRL>wo                 Make the current window the only one
        <CTRL>w<CTRL>o           Make the current window the only one
        :platform                Print platform
        :pwd                     Print the current directory name
        :q                       Close current window if more than 1 windows exist else quit program
        <CTRL>wq                 Close current window if more than 1 windows exist else quit program
        :q!                      Close current window if more than 1 windows exist else quit program without writing
        ZQ                       Close current window if more than 1 windows exist else quit program without writing
        :sector                  Print sector size for block device
        :self                    Print current console instance string
        :set                     Set option
                address          Set address radix to {16,10,8}
                status           Set buffer size and current position radix to {16,10,8}
                binary           Set binary edit mode (unset ascii edit mode)
                ascii            Set ascii edit mode (unset binary edit mode)
                bytes_per_line   Set bytes_per_line to {[0-9]+,"max","min","auto"}
                bytes_per_window Set bytes_per_window to {[0-9]+,"even","auto"}
                ic               Set ic mode (ignore the case of alphabets on search)
                noic             Unset ic mode
                le               Set endianness to little (unset big endian if set)
                be               Set endianness to big (unset little endian if set)
                si               Set SI prefix mode (kilo equals 10^3)
                nosi             Unset SI prefix mode (kilo equals 2^10)
                ws               Set wrapscan mode (search wrap around the end of the buffer)
                nows             Unset wrapscan mode
        :split                   Split current window
        :term                    Print terminal type
        :version                 Print version
        :w                       Write the whole buffer to the file
        :w!                      Like :w, but overwrite an existing file
        :wq                      Write the current file and quit
        :x                       Like :wq, but write only when changes have been made
        ZZ                       Like :wq, but write only when changes have been made
        >>                       Rotate [count] bits to right
        <<                       Rotate [count] bits to left
        @[0-9a-zA-Z]             Execute the contents of register [count] times
        @@                       Execute the previous @ command [count] times
        D                        Delete characters under the cursor until the end of buffer
        G                        Go to line [count] where default is last
        gg                       Go to line [count] where default is first
        H                        Go to line [count] from top of window
        M                        Go to the middle line of window
        L                        Go to line [count] from bottom of window
        N                        Repeat the latest search toward backward
        n                        Repeat the latest search
        O                        Replace the text befor the cursor [count] times
        o                        Replace the text after the cursor [count] times
        P                        Put the text before the cursor [count] times
        p                        Put the text after the cursor [count] times
        U                        Undo all changes
        X                        Delete [count] characters before the cursor
        Y                        Yank characters under the cursor until the end of buffer
        y                        Yank [count] characters
        go                       Go to [count] byte in the buffer where default is start of the buffer
        i                        Start insert edit mode
        I                        Start insert edit mode at the first byte of buffer
        a                        Start append edit mode
        A                        Start append edit mode at the end of buffer
        R                        Start replace edit mode
        r                        Replace [count] characters under the cursor
        m[0-9a-zA-Z]             Set mark at cursor position, uppercase marks are valid between buffers
        `[0-9a-zA-Z]             Go to marked position
        q[0-9a-zA-Z]             Record typed characters into register
        q                        Stop recording
        sb                       Swap byte order of [count] characters
        u                        Undo changes
        v                        Start/End visual mode
        V                        Start/End line visual mode
        <CTRL>v                  Start/End block visual mode
        w                        Go to the next printable character
        b                        Go to the previous printable character
        ~                        Switch case of the [count] characters under and after the cursor
        <DOWN>                   Go [count] lines downward
        j                        Go [count] lines downward
        <ENTER>                  Go [count] lines downward
        <UP>                     Go [count] lines upward
        k                        Go [count] lines upward
        <LEFT>                   Go [count] characters to the left
        h                        Go [count] characters to the left
        <BACKSPACE>              Go [count] characters to the left
        <RIGHT>                  Go [count] characters to the right
        l                        Go [count] characters to the right
        <SPACE>                  Go [count] characters to the right
        <DELETE>                 Delete [count] characters under and after the cursor
        x                        Delete [count] characters under and after the cursor
        d                        Delete [count] characters under and after the cursor

## Examples

+ Note that some commands can take *[count]* prefix, see *List of commands* section for details.

+ Note that *offset 0* means the first byte of the buffer (*offset 1* is the second byte).

+ Print the help message and exit.

        $ fileobj -h

+ Print the list of commands and exit.

        $ fileobj --command

+ Run the program with an empty buffer.

        $ fileobj

+ Run the program and then quit.

        $ fileobj
          (command):q<ENTER>

+ Run the program and discard input that has been typed after the previous command.

        $ fileobj
          (command)ttttttttt<ESC>
          (command):elhwefsdhnkfjsd<ESC>
          (command)[123456789<ESC>

+ Open a file *./a.out*.

        $ fileobj ./a.out

+ Open a file *./a.out* and quit the program.

        $ fileobj ./a.out
          (command):q<ENTER>

+ Open a file *./a.out* and quit the program without saving.

        $ fileobj ./a.out
          (command):q!<ENTER>

+ Open a file *./a.out* and save the buffer.

        $ fileobj ./a.out
          (command):w<ENTER>

+ Open a file *./a.out* and quit the program after saving the buffer.

        $ fileobj ./a.out
          (command):wq<ENTER>

+ Open an empty buffer and save it as *./a.out*.

        $ fileobj
          (command):w ./a.out<ENTER>

+ Open a file *./a.out* and move the cursor.

        $ fileobj ./a.out
          (command)j
          or
          (command)k
          or
          (command)h
          or
          (command)l
          or
          (command)<DOWN>
          or
          (command)<UP>
          or
          (command)<LEFT>
          or
          (command)<RIGHT>

+ Open a file *./a.out* and move the cursor to offset 0 of the buffer.

        $ fileobj ./a.out
          (command)(move the cursor)
          (command)gg

+ Open a file *./a.out* and move the cursor to the last byte of the buffer.

        $ fileobj ./a.out
          (command)G

+ Open a file *./a.out* and move the cursor to offset 1024.

        $ fileobj ./a.out
          (command)1024go

+ Open a file *./a.out* and move the cursor to the next printable character.

        $ fileobj ./a.out
          (command)w

+ Open a file *./a.out* and move the cursor to the previous printable character.

        $ fileobj ./a.out
          (command)b

+ Open a file *./a.out* and move the cursor to the next zero (\x00).

        $ fileobj ./a.out
          (command))

+ Open a file *./a.out* and move the cursor to the previous zero (\x00).

        $ fileobj ./a.out
          (command)(

+ Open a file *./a.out* and move the cursor to the next non-zero (not \x00).

        $ fileobj ./a.out
          (command)}

+ Open a file *./a.out* and move the cursor to the previous non-zero (not \x00).

        $ fileobj ./a.out
          (command){

+ Open a file *./a.out* and move the cursor to the first byte of the current line.

        $ fileobj ./a.out
          (command)(move the cursor)
          (command)0

+ Open a file *./a.out* and move the cursor to the last byte of the current line.

        $ fileobj ./a.out
          (command)$

+ Open a file *./a.out* and move the cursor forward to the next page.

        $ fileobj ./a.out
          (command)CTRL-f

+ Open a file *./a.out* and move the cursor forward for 1/2 page.

        $ fileobj ./a.out
          (command)CTRL-d

+ Open a file *./a.out* and move the cursor backward to the previous page.

        $ fileobj ./a.out
          (command)CTRL-b

+ Open a file *./a.out* and move the cursor backward for 1/2 page.

        $ fileobj ./a.out
          (command)CTRL-u

+ Open a file *./a.out* and move the cursor to offset 0x10000.

        $ fileobj ./a.out
          (command)[0x10000]go
          or
          (command)[64KiB]go
          or
          (command)65536go

+ Open a file *./a.out* and print the current buffer size and position.

        $ fileobj ./a.out
          (command)(move the cursor)
          (command)CTRL-g

+ Open a file *./a.out* and delete a character.

        $ fileobj ./a.out
          (command)x

+ Open a file *./a.out* and delete 256 bytes.

        $ fileobj ./a.out
          (command)256x
          or
          (command)x
          (command)256.

+ Open a file *./a.out* and delete 256 bytes at offset 1024.

        $ fileobj ./a.out
          (command)1024go
          or
          (command)1024l
          then
          (command)256x

+ Open a file *./a.out* and delete 256 bytes before offset 1024.

        $ fileobj ./a.out
          (command)1024go
          or
          (command)1024l
          then
          (command)256X

+ Open a file *./a.out*, delete 256 bytes, and insert it 4 times at offset 1024 (before delete).

        $ fileobj ./a.out
          (command)256x
          (command)768go
          (command)4P

+ Open a file *./a.out*, delete 256 bytes, and replace with it 4 times at offset 1024 (before delete).

        $ fileobj ./a.out
          (command)256x
          (command)768go
          (command)4O

+ Open a file *./a.out* and yank a character.

        $ fileobj ./a.out
          (command)y

+ Open a file *./a.out* and yank 256 bytes.

        $ fileobj ./a.out
          (command)256y

+ Open a file *./a.out* and yank 256 bytes at offset 1024.

        $ fileobj ./a.out
          (command)1024go
          or
          (command)1024l
          then
          (command)256y

+ Open a file *./a.out*, yank 256 bytes, and insert it 4 times at offset 1024.

        $ fileobj ./a.out
          (command)256y
          (command)1024go
          (command)4P

+ Open a file *./a.out*, yank 256 bytes, and replace with it 4 times at offset 1024.

        $ fileobj ./a.out
          (command)256y
          (command)1024go
          (command)4O

+ Open a file *./a.out* and toggle 256 bytes (switch upper <-> lower case for alphabets).

        $ fileobj ./a.out
          (command)256~

+ Open a file *./a.out* and apply &0xAA (bitwise and 0xAA) for 256 bytes.

        $ fileobj ./a.out
          (command)256&aa

+ Open a file *./a.out* and apply |0xAA (bitwise or 0xAA) for 256 bytes.

        $ fileobj ./a.out
          (command)256|aa

+ Open a file *./a.out* and apply ^0xAA (bitwise xor 0xAA) for 256 bytes.

        $ fileobj ./a.out
          (command)256^aa

+ Open a file *./a.out* and swap byte order of 4 bytes from the current cursor.

        $ fileobj ./a.out
          (command)4sb

+ Open a file *./a.out* and enter insert edit mode to insert "\x41\x42\x43".

        $ fileobj ./a.out
          (command)i414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)iABC<ESC>

+ Open a file *./a.out* and enter insert edit mode to insert "\x41\x42\x43" for 4 times.

        $ fileobj ./a.out
          (command)4i414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)4iABC<ESC>

+ Open a file *./a.out* and enter append edit mode to insert "\x41\x42\x43".

        $ fileobj ./a.out
          (command)a414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)aABC<ESC>

+ Open a file *./a.out* and enter append edit mode to insert "\x41\x42\x43" for 4 times.

        $ fileobj ./a.out
          (command)4a414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)4aABC<ESC>

+ Open a file *./a.out* and enter replace edit mode to replace with "\x41\x42\x43".

        $ fileobj ./a.out
          (command)R414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)RABC<ESC>

+ Open a file *./a.out* and enter replace edit mode to replace with "\x41\x42\x43" for 4 times.

        $ fileobj ./a.out
          (command)4R414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)4RABC<ESC>

+ Open a file *./a.out* and undo.

        $ fileobj ./a.out
          (command)(do some edit)
          (command)u

+ Open a file *./a.out* and undo all.

        $ fileobj ./a.out
          (command)(do some edit)
          (command)U

+ Open a file *./a.out* and redo.

        $ fileobj ./a.out
          (command)(do some edit)
          (command)(do undo)
          (command)CTRL-r

+ Open a file *./a.out* and search forward for "GNU".

        $ fileobj ./a.out
          (command)/GNU<ENTER>

+ Open a file *./a.out* and search forward (backward if the previous search was backward) for the next.

        $ fileobj ./a.out
          (command)n

+ Open a file *./a.out* and search backward for "GNU".

        $ fileobj ./a.out
          (command)?GNU<ENTER>

+ Open a file *./a.out* and search backward (forward if the previous search was backward) for the next.

        $ fileobj ./a.out
          (command)N

+ Open a file *./a.out* and search for "\x7fELF" (can't search for ascii string in "\x??\x??.." or "\X??.." format).

        $ fileobj ./a.out
          (command)/\x7fELF<ENTER>
          or
          (command)/\x7f\x45\x4c\x46<ENTER>
          or
          (command)/\X7f454c46<ENTER>

+ Open a file *./a.out* and search for "\x41\x42\x43" (can't search for ascii string in "\x??\x??.." or "\X??.." format).

        $ fileobj ./a.out
          (command)/\x41\x42\x43<ENTER>
          or
          (command)/\X414243<ENTER>
          or
          (command)/ABC<ENTER>

+ Open a file *./a.out* from offset 1024.

        $ fileobj ./a.out@1024
        or
        $ fileobj ./a.out@0x400
        or
        $ fileobj ./a.out@02000

+ Open a file *./a.out* and read 512 bytes from offset 1024.

        $ fileobj ./a.out@1024:512
        or
        $ fileobj ./a.out@0x400:512
        or
        $ fileobj ./a.out@0x400-0x600

+ Open a file *./a.out* and read the first 1024 bytes.

        $ fileobj ./a.out@0:1024
        or
        $ fileobj ./a.out@0-1024
        or
        $ fileobj ./a.out@:1024
        or
        $ fileobj ./a.out@-1024
        or
        $ fileobj ./a.out@:0x400
        or
        $ fileobj ./a.out@-0x400

+ Open a file *./a.out* and close the buffer.

        $ fileobj ./a.out
          (command):bdelete<ENTER>

+ Open an empty buffer and then open *./a.out*.

        $ fileobj
          (command):e ./a.out<ENTER>

+ Open a file *./a.out* and then open a file */path/to/b.out*.

        $ fileobj ./a.out
          (command):e /path/to/b.out<ENTER>

+ Open files *./a.out* and *./b.out*.

        $ fileobj ./a.out ./b.out

+ Open files *./a.out* and *./b.out*, and switch the buffer to *./b.out*.

        $ fileobj ./a.out ./b.out
          (command)<TAB>
          or
          (command):bnext<ENTER>

+ Open files *./a.out* and *./b.out* with different offset/length for each.

        $ fileobj ./a.out@0x400:0x200 ./b.out@:4096

+ Open files *./a.out* and *./b.out*, and start with a window for each.

        $ fileobj ./a.out ./b.out -O

+ Open files *./a.out*, *./b.out*, *./c.out* with 3 windows, and move to the next window.

        $ fileobj ./a.out ./b.out -O
          (command)CTRL-W w

+ Open files *./a.out*, *./b.out*, *./c.out* with 3 windows, and close all windows except for the current window.

        $ fileobj ./a.out ./b.out ./c.out -O
          (command)CTRL-W o
          or
          (command):only<ENTER>

+ Open files *./a.out*, *./b.out*, *./c.out* and print the list of buffers.

        $ fileobj ./a.out ./b.out ./c.out
          (command):args<ENTER>
          or
          (command):ls<ENTER>

+ Open a file *./a.out* and open (split) another window.

        $ fileobj ./a.out
          (command)CTRL-W s
          or
          (command):split<ENTER>

+ Open a file *./a.out* and open (split) another window and then close it.

        $ fileobj ./a.out
          (command)(split window)
          then
          (command)CTRL-W c
          or
          (command):close<ENTER>

+ Open a file *./a.out* and enter visual mode.

        $ fileobj ./a.out
          (command)v
          and press escape or CTRL-c or v to exit
          (command)<ESC>

+ Open a file *./a.out* and enter line visual mode.

        $ fileobj ./a.out
          (command)V
          and press escape or CTRL-c or V to exit
          (command)<ESC>

+ Open a file *./a.out* and enter block visual mode (see *Note for BSDs* section for BSDs).

        $ fileobj ./a.out
          (command)CTRL-v
          and press escape or CTRL-c or CTRL-v to exit
          (command)<ESC>

+ Open a file *./a.out* and delete visually selected region.

        $ fileobj ./a.out
          (command)v
          or
          (command)V
          or
          (command)CTRL-v
          then
          (command)(move the cursor)
          then
          (command)x

+ Open a file *./a.out* and yank visually selected region.

        $ fileobj ./a.out
          (command)v
          or
          (command)V
          or
          (command)CTRL-v
          then
          (command)(move the cursor)
          then
          (command)y

+ Open a file *./a.out* and replace visually selected region with \xff.

        $ fileobj ./a.out
          (command)v
          or
          (command)V
          or
          (command)CTRL-v
          then
          (command)(move the cursor)
          then
          (command)rff

+ Open a file *./a.out* in readonly mode.

        $ fileobj ./a.out -R

+ Open a file *./a.out* in simple window mode.

        $ fileobj ./a.out --simple

+ Open a file *./a.out* with green foreground and black background color.

        $ fileobj ./a.out --fg=green --bg=black

+ Open a file *./a.out* with 8 bytes per line (whereas default is maximum 2^x that fits in the terminal).

        $ fileobj ./a.out --bytes_per_line=8

+ Open a file *./a.out* with 512 bytes per window (whereas default is maximum bytes that fits in the terminal using the current bytes per line value).

        $ fileobj ./a.out --bytes_per_window=512

+ Open a file *./a.out* and always keep the same window size after split.

        $ fileobj ./a.out --bytes_per_window=even
          (command)CTRL-W s
          (command)CTRL-W s
          (command)CTRL-W s
          ...
          (command)CTRL-W c
          (command)CTRL-W c
          (command)CTRL-W c

+ Open an empty buffer and fill in the first 512 bytes with a pattern of "\x55\xaa" and save it as *./a.img*.

        $ fileobj
          (command)256i55aa<ESC>
          (command):wq ./a.img<ENTER>

+ Open above *./a.img* and overwrite the first 4 bytes with "\x7fELF".

        $ fileobj ./a.img
          (command)R7f454c46<ESC>
          or
          (command)R7f<ESC>
          (command):set ascii<ENTER>
          (command)l
          (command)RELF<ESC>

+ Open above *./a.img* and rotate the whole buffer 1 bit to right and then restore.

        $ fileobj ./a.img
          (command)>>
          (command)G
          (command)<<

+ Open above *./a.img* and rotate the whole buffer 8 bits (1 byte) to right.

        $ fileobj ./a.img
          (command)8>>

+ Open above *./a.img* and rotate the whole buffer 8 bits (1 byte) to left.

        $ fileobj ./a.img
          (command)G
          (command)8<<

+ Open a loop device */dev/loop0* on Linux.

        $ sudo fileobj /dev/loop0

+ Open the first 512 bytes of a block device */dev/sdb* on Linux.

        $ sudo fileobj /dev/sdb@:512
          or
        $ sudo fileobj /dev/sdb@:0x200

+ Open the first 512 bytes of a block device */dev/sdb* and zero clear that.

        $ sudo fileobj /dev/sdb@:512
          (command)v
          (command)G
          (command)r00

+ Open a block device */dev/sdb* and move the cursor to offset 320 MiB.

        $ sudo fileobj /dev/sdb
          (command)335544320go
          or
          (command)[320MiB]go
          or
          (command)[327680KiB]go

+ Open a block device */dev/sdb*, move the cursor to offset 320 MiB, and mark that offset to 'a'.

        $ sudo fileobj /dev/sdb
          (command)[320MiB]go
          (command)ma

+ Open a block device */dev/sdb* and jump to the mark 'a'.

        $ sudo fileobj /dev/sdb
          (command)`a

+ Open a block device */dev/sdb* and print the sector size recognized by the userspace program.

        $ sudo fileobj /dev/sdb
          (command):sector<ENTER>

+ Open a block device */dev/sdb* and print the current buffer size and position in sector.

        $ sudo fileobj /dev/sdb
          (command)(move the cursor)
          (command)gCTRL-g

+ Open a file *./a.out* and then open a help page.

        $ fileobj ./a.out
          (command):help<ENTER>

+ Open a file *./a.out* and then open a list of extensions.

        $ fileobj ./a.out
          (command):extensions<ENTER>

+ Open and modify userspace of a process *(experimental feature currently available only on Linux)*.

        # uname
        Linux
        # cat > ./test1.c << EOF
        > #include <stdio.h>
        > #include <unistd.h>
        > const char *p = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        > int main(void) {
        > while (1) {
        > printf("%s\n", p);
        > sleep(10);
        > }
        > return 0;
        > }
        > EOF
        # gcc -Wall -g ./test1.c -o test1
        # ./test1
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        abcdefghijklmnopqrstuvwxyz <- .rodata overwritten with lower case (see below)
        abcdefghijklmnopqrstuvwxyz
        abcdefghijklmnopqrstuvwxyz
        abcdefghijklmnopqrstuvwxyz
        abcdefghijklmnopqrstuvwxyz
        abcdefghijklmnopqrstuvwxyz
        ^C

+ Modify .rodata while running test1.

        # objdump -s -j .rodata ./test1
        
        ./test1:     file format elf64-x86-64
        
        Contents of section .rodata:
         400618 01000200 00000000 00000000 00000000  ................
         400628 41424344 45464748 494a4b4c 4d4e4f50  ABCDEFGHIJKLMNOP
         400638 51525354 55565758 595a00             QRSTUVWXYZ.
        # pgrep -l test1
        8549 test1
        # fileobj pid8549@0x400628:26
          (command)26~
          (command):wq

+ Map binary data to C struct defined in *${HOME}/.fileobj/cstruct*.

        $ cat > ~/.fileobj/cstruct << EOF
        > struct test1 {
        > char s[4];
        > u16 a;
        > s16 b;
        > u32 c;
        > s64 d;
        > string s[32];
        > };
        > EOF
        $ fileobj /path/to/data
          (command):cstruct test1<ENTER>
          (command):wq ./test1.out<ENTER>
        $ cat ./test1.out
        struct test1 {
            char s[0]; 127 \x7F [.]
            char s[1]; 69 \x45 [E]
            char s[2]; 76 \x4C [L]
            char s[3]; 70 \x46 [F]
            u16 a; 258 \x02\x01 [..]
            s16 b; 1 \x01\x00 [..]
            u32 c; 0 \x00\x00\x00\x00 [....]
            s64 d; 17451457145995264 \x00\x00\x00\x00\x02\x00\x3E\x00 [......>.]
            string s[32]; "\x01"
        };

+ Map binary data to C struct using a predefined example in *fileobj/script/cstruct.usb*.

        $ cd /path/to/fileobj/source
        $ cp ./script/cstruct.usb ~/.fileobj/cstruct
        $ cd /path/to/somewhere
        $ od -tx1 -Ax ./usb_device_descriptor.bin
        000000 12 01 00 03 09 00 03 09 6b 1d 03 00 06 02 03 02
        000010 01 01
        000012
        $ fileobj ./usb_device_descriptor.bin
          (command):cstruct usb_device_descriptor<ENTER>
          (command):wq ./usb_device_descriptor.out<ENTER>
        $ cat ./usb_device_descriptor.out
        struct usb_device_descriptor {
            struct usb_descriptor_header {
                u8 bLength; 18 \x12 [.]
                u8 bDescriptorType; 1 \x01 [.]
            } hdr;
            x16le bcdUSB; 0x0300 \x00\x03 [..]
            u8 bDeviceClass; 9 \x09 [.]
            u8 bDeviceSubClass; 0 \x00 [.]
            u8 bDeviceProtocol; 3 \x03 [.]
            u8 bMaxPacketSize0; 9 \x09 [.]
            x16le idVendor; 0x1D6B \x6B\x1D [k.]
            x16le idProduct; 0x0003 \x03\x00 [..]
            x16le bcdDevice; 0x0206 \x06\x02 [..]
            u8 iManufacturer; 3 \x03 [.]
            u8 iProduct; 2 \x02 [.]
            u8 iSerialNumber; 1 \x01 [.]
            u8 bNumConfigurations; 1 \x01 [.]
        };

## Note

+ Creates a new directory *${HOME}/.fileobj* if it doesn't exist, and creates some files under the directory.

+ Some keyboard keys may not work correctly on vt100 terminal.

+ Set an environment variable *FILEOBJ_USE_TMUX_CAVEAT* (with a blank value as shown in below bash example) if using *--fg* and/or *--bg* options while in terminal multiplexer causes the cursor to disappear.

        $ export FILEOBJ_USE_TMUX_CAVEAT=

## Note for PuTTY on Windows

+ Setting an environment variable *FILEOBJ_USE_PUTTY_CAVEAT* (with a blank value as shown in below bash example) is recommended.

        $ export FILEOBJ_USE_PUTTY_CAVEAT=

+ If the ncurses' line border characters are broken, change the settings of the section *"Window -> Appearance"* and/or *"Window -> Translation"*. Changing the character set from *"UTF-8"* (or whatever already there) to *"Use font encoding"* may fix the issue.

## Note for BSDs

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

## Note for Darwin

+ Darwin support is experimental, but consider trying notes for BSDs.

## Note for Cygwin

+ If Python binaries for both Windows and Cygwin are installed, the shebang line of the executable script (e.g. */usr/bin/fileobj*) may have Windows path which needs to be manually changed to Cygwin path.
