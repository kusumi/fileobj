fileobj ([v0.7.27](https://github.com/kusumi/fileobj/releases/tag/v0.7.27))
=======

## About

+ [http://sourceforge.net/projects/fileobj/](http://sourceforge.net/projects/fileobj/)

+ fileobj is a portable hex editor with vi like interface. This software is written in Python and works on Python 2.6 or above. It works on Linux, NetBSD, OpenBSD, FreeBSD, DragonFlyBSD and possibly other unix operating systems that support ncurses. This software provides basic vi commands for binary editing. Features include insert, replace, delete data in hexadecimal or ascii, cut and paste, undo and redo, visual select, partial buffer loading, multiple buffers support, multiple windows support, block device (raw disk) support, mapping binary data to C struct, etc.

+ Repository is available at GitHub [https://github.com/kusumi/fileobj/tree/v0.7](https://github.com/kusumi/fileobj/tree/v0.7)

+ See CHANGES for changes

## Supported Python versions

|<=2.5|2.6|2.7|3.0|3.1|3.2|3.3|3.4|3.5|
|:----|:--|:--|:--|:--|:--|:--|:--|:--|
|-    |o  |o  |o  |o  |o  |o  |o  |o  |

## Supported OS

|Linux|NetBSD|OpenBSD|FreeBSD|DragonFlyBSD|Darwin          |Windows|Other Unix-like |
|:----|:-----|:------|:------|:-----------|:---------------|:------|:---------------|
|o    |o     |o      |o      |o           |o (experimental)|-      |? (experimental)|

## Install

+ Uninstall previous version if exists

+ Run *setup.py* using Python 2

        $ python --version
        Python 2.6.6
        $ sudo python ./setup.py install --force --record ./install.out
        $ sudo python ./script/check.py
        $ fileobj --version
        v0.7.27
        $ fileobj

    + See [Installing Python Modules](https://docs.python.org/2/install/index.html) for custom installation

+ or run *setup.py* using Python 3

        $ python3 --version
        Python 3.3.1
        $ sudo python3 ./setup.py install --force --record ./install.out
        $ sudo python3 ./script/check.py
        $ fileobj --version
        v0.7.27
        $ fileobj

    + See [Installing Python Modules](https://docs.python.org/3/installing/index.html) for custom installation

## Uninstall

+ Remove files listed in *install.out*

## Examples

+ Open a file *a.out*

        $ fileobj ./a.out

+ Open a file *a.out* in readonly mode

        $ fileobj ./a.out -R

+ Open a file *a.out* from offset 1234

        $ fileobj ./a.out@1234

+ Open a file *a.out* and read 1000 bytes from offset 1234

        $ fileobj ./a.out@1234:1000

+ Open a file *a.out* and read from offset 1234 to 2234 (equivalent to above)

        $ fileobj ./a.out@1234-2234

+ Open a file *a.out* and read the first 1000 bytes

        $ fileobj ./a.out@:1000
        $ fileobj ./a.out@-1000

+ Open files *a.out* and *aa.out*

        $ fileobj ./a.out ./aa.out

+ Open files *a.out* and *aa.out* with different offset/length for each

        $ fileobj ./a.out@1000:2000 ./aa.out@:10000

+ Open a loop device /dev/loop0

        $ sudo fileobj /dev/loop0

+ Open MBR of a block device /dev/sda

        $ sudo fileobj /dev/sda@:512

+ Open virtual address space of a user process (experimental and currently only for Linux)

        $ pgrep -l a.out
        10337 a.out
        $ objdump -s -j .rodata ./a.out
        
        ./a.out:     file format elf64-x86-64
        
        Contents of section .rodata:
         4005c8 01000200 00000000 00000000 00000000  ................
         4005d8 41424344 45464748 494a4b4c 4d4e4f50  ABCDEFGHIJKLMNOP
         4005e8 51525354 55565758 595a3031 32333435  QRSTUVWXYZ012345
         4005f8 36373839 00                          6789.           
        $ fileobj pid10337@0x4005c8:0x35

+ Map binary data (USB device descriptor of USB Root Hub on Linux) to C struct defined in *${HOME}/.fileobj/cstruct*

        $ cd /path/to/fileobj/source
        $ cp ./script/cstruct.usb ~/.fileobj/cstruct
        $ cd
        $ fileobj ./usb_device_descriptor.bin
          :cstruct usb_device_descriptor<ENTER>
          :wq ./usb_device_descriptor.out<ENTER>
        $ od -tx1 -Ax ./usb_device_descriptor.bin
        000000 12 01 00 03 09 00 03 09 6b 1d 03 00 06 02 03 02
        000010 01 01
        000012
        $ cat ./usb_device_descriptor.out
        struct usb_device_descriptor {
            struct usb_descriptor_header {
                u8 bLength; 18 \x12 [.]
                u8 bDescriptorType; 1 \x01 [.]
            } hdr;
            u16le bcdUSB; 768 \x00\x03 [..]
            u8 bDeviceClass; 9 \x09 [.]
            u8 bDeviceSubClass; 0 \x00 [.]
            u8 bDeviceProtocol; 3 \x03 [.]
            u8 bMaxPacketSize0; 9 \x09 [.]
            u16le idVendor; 7531 \x6B\x1D [k.]
            u16le idProduct; 3 \x03\x00 [..]
            u16le bcdDevice; 518 \x06\x02 [..]
            u8 iManufacturer; 3 \x03 [.]
            u8 iProduct; 2 \x02 [.]
            u8 iSerialNumber; 1 \x01 [.]
            u8 bNumConfigurations; 1 \x01 [.]
        };

## List of commands

+ Run the program with *--command* option

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
        &[0-9a-fA-F]{2}          Replace [count] bytes with logical and-ed bytes
        |[0-9a-fA-F]{2}          Replace [count] bytes with logical or-ed bytes
        ^[0-9a-fA-F]{2}          Replace [count] bytes with logical xor-ed bytes
        )                        Go to the next zero (\x00)
        (                        Go to the previous zero (\x00)
        }                        Go to the next non zero character
        {                        Go to the previous non zero character
        ]                        End reading [count]. e.g. '[-0x10KiB]l' '[-020KiB]l' '[-0b10000KiB]l' are all -16384l
        [                        Start reading [count]. e.g. '[0x10]x' '[020]x' '[0b10000]x' are all 16x
        +                        Go [count] lines downward, on the first character of the line
        -                        Go [count] lines upward, on the first character of the line
        .                        Repeat last change
        /                        Search forward. e.g. '/\x41\x42\x43', '/\X414243', '/ABC' all searches forward for "ABC"
        ?                        Search backward. e.g. '?\x41\x42\x43', '?\X414243', '?ABC' all searches backward for "ABC"
        0                        Go to the first character of the line
        $                        Go to the end of the line. If a count is given go [count]-1 lines downward
        :args                    Print buffer list with the current buffer in brackets
        :argv                    Print arguments of this application
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
        :q                       Close current window if >1 windows exist else quit program
        <CTRL>wq                 Close current window if >1 windows exist else quit program
        :q!                      Close current window if >1 windows exist else quit program without writing
        ZQ                       Close current window if >1 windows exist else quit program without writing
        :sector                  Print sector size for block device
        :self                    Print current console instance string
        :set                     Set option
                address          Set address radix to arg [16|10|8]
                status           Set buffer size and current position radix to arg [16|10|8]
                binary           Set binary edit mode (unset ascii edit mode)
                ascii            Set ascii edit mode (unset binary edit mode)
                bytes_per_line   Set bytes_per_line to arg [[0-9]+|max|min|auto]
                bytes_per_window Set bytes_per_window to arg [[0-9]+|auto]
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

## Help

+ Run the program with *--help* option

        $ fileobj --help
        Usage: fileobj [options] [file paths ...]
        For more information run fileobj and type :help<ENTER>
        
        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -R                    Read only mode
          -B                    Buffer allocation mode
          -d                    Show buffer address starting from @offset
          -x                    Show buffer size and current position in hexadecimal
          -o <num>              Open <num> windows
          -O                    Open each buffer in different window
          --bytes_per_line=<bytes_per_line>
                                Set bytes_per_line [[0-9]+|max|min|auto]
          --bytes_per_window=<bytes_per_window>
                                Set bytes_per_window [[0-9]+|even|auto]
          --terminal_height=<terminal_height>
                                Manually set terminal height [[0-9]+]
          --terminal_width=<terminal_width>
                                Manually set terminal width [[0-9]+]
          --fg=<color>          Set foreground color
                                [black|blue|cyan|green|magenta|red|white|yellow]
          --bg=<color>          Set background color
                                [black|blue|cyan|green|magenta|red|white|yellow]
          --simple              Use simplified status window
          --command             Print command list and exit
          --sitepkg             Print site package directory and exit

## Note

+ Generates a new directory *${HOME}/.fileobj*

+ Some keyboard keys may not work correctly on vt100 terminal

+ If the ncurses border lines are shown with messed up characters on Putty, try changing settings of the section *"Window -> Appearance"* and/or *"Window -> Translation"*. Changing the character set from *"UTF-8"* (or whatever the setting already there) to *"Use font encoding"* may work.

## Note for BSDs

+ NetBSD requires py-curses package other than the python package itself

        $ uname
        NetBSD
        $ sudo python ./setup.py install --force --record ./install.out
        No module named _curses
        $ cd /usr/pkgsrc/devel/py-curses
        $ sudo make install

+ Entering block visual mode may require *CTRL-v CTRL-v* instead of *CTRL-v*

## Note for Darwin

+ Darwin support is experimental, but consider trying notes for BSDs
