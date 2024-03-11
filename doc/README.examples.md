## Examples

### Note

+ There are many options not mentioned in here, see *[List of options](README.list_of_options.md)* for details.

+ There are many environment variables not mentioned in here, see *[List of environment variables](README.list_of_environment_variables.md)* for details.

+ There are many commands not mentioned in here, see *[List of commands](README.list_of_commands.md)* for details.

+ Some commands can take *[count]* prefix, see *[List of commands](README.list_of_commands.md)* for details.

+ *offset 0* means first byte of a buffer.

+ *sector 0* means first sector of a buffer.

+ Sector based commands assume 512 bytes sector if a buffer is not of block device.

### Command line options

+ Print help message and exit.

        $ fileobj -h

+ Print list of available editor commands and exit.

        $ fileobj --command

+ Use read-only mode.

        $ fileobj -R

+ Use fixed *bytes per line* within an editor window.

        $ fileobj --bytes_per_line=8

+ Use fixed *bytes per window* within an editor window.

        $ fileobj --bytes_per_window=512

+ Keep *bytes per window* the same for all editor windows.

        $ fileobj --bytes_per_window=even

### Basic commands

+ Run the program with an empty buffer.

        $ fileobj

+ Quit the program.

        $ fileobj
          (command):q<ENTER>

+ Discard incomplete commands via *ESC* key.

        $ fileobj
          (command)ttttttttt<ESC>
          (command):elhwefsdhnkfjsd<ESC>
          (command)[123456789<ESC>

### Open file

+ Open a file *./a.out*.

        $ fileobj ./a.out

+ Open a file *./a.out* and quit.

        $ fileobj ./a.out
          (command):q<ENTER>

+ Open a file *./a.out* and quit without saving.

        $ fileobj ./a.out
          (command):q!<ENTER>

+ Open a file *./a.out* and save the buffer.

        $ fileobj ./a.out
          (command):w<ENTER>

+ Open a file *./a.out* and quit after saving the buffer.

        $ fileobj ./a.out
          (command):wq<ENTER>

+ Open an empty buffer and save as *./a.out*.

        $ fileobj
          (command):w ./a.out<ENTER>

### Move cursor

+ Open a file *./a.out* and move a cursor.

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

+ Open a file *./a.out* and go to offset 0.

        $ fileobj ./a.out
          (command)(move a cursor)
          (command)gg

+ Open a file *./a.out* and go to the last byte.

        $ fileobj ./a.out
          (command)G

+ Open a file *./a.out* and go to offset 1024.

        $ fileobj ./a.out
          (command)1024go

+ Open a file *./a.out* and go to the next printable character.

        $ fileobj ./a.out
          (command)w

+ Open a file *./a.out* and go to the previous printable character.

        $ fileobj ./a.out
          (command)b

+ Open a file *./a.out* and go to the next zero (\x00).

        $ fileobj ./a.out
          (command))

+ Open a file *./a.out* and go to the previous zero (\x00).

        $ fileobj ./a.out
          (command)(

+ Open a file *./a.out* and go to the next non-zero (not \x00).

        $ fileobj ./a.out
          (command)}

+ Open a file *./a.out* and go to the previous non-zero (not \x00).

        $ fileobj ./a.out
          (command){

+ Open a file *./a.out* and go to the first byte of the current line.

        $ fileobj ./a.out
          (command)(move a cursor)
          (command)0

+ Open a file *./a.out* and go to the last byte of the current line.

        $ fileobj ./a.out
          (command)$

+ Open a file *./a.out* and move forward to the next page.

        $ fileobj ./a.out
          (command)CTRL-f

+ Open a file *./a.out* and move forward for 1/2 page.

        $ fileobj ./a.out
          (command)CTRL-d

+ Open a file *./a.out* and move backward to the previous page.

        $ fileobj ./a.out
          (command)CTRL-b

+ Open a file *./a.out* and move backward for 1/2 page.

        $ fileobj ./a.out
          (command)CTRL-u

+ Open a file *./a.out* and go to offset 0x10000. *[...]* syntax is evaluated by Python's *eval()* function. Python3 requires *0o* prefix for an octal value.

        $ fileobj ./a.out
          (command)[0x10000]go
          or
          (command)[64KiB]go
          or
          (command)65536go

+ Open a file *./a.out* and show the current buffer size and position.

        $ fileobj ./a.out
          (command)(move a cursor)
          (command)CTRL-g

### Edit buffer

+ Open a file *./a.out* and delete 1 byte.

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

+ Open a file *./a.out*, delete (implicitly yank) 256 bytes, and insert 4 times at offset 1024.

        $ fileobj ./a.out
          (command)256x
          (command)1024go
          (command)4P

+ Open a file *./a.out*, delete (implicitly yank) 256 bytes, and replace 4 times at offset 1024.

        $ fileobj ./a.out
          (command)256x
          (command)1024go
          (command)4O

+ Open a file *./a.out* and yank 1 byte.

        $ fileobj ./a.out
          (command)y

+ Open a file *./a.out* and yank 256 bytes.

        $ fileobj ./a.out
          (command)256y

+ Open a file *./a.out* and toggle (switch upper <-> lower case for alphabets) 256 bytes.

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

+ Open a file *./a.out* and swap byte order of the next 4 bytes.

        $ fileobj ./a.out
          (command)4sb

+ Open a file *./a.out*, enter insert edit mode to insert "\x41\x42\x43", and then exit.

        $ fileobj ./a.out
          (command)i414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)iABC<ESC>

+ Open a file *./a.out*, enter insert edit mode to insert "\x41\x42\x43" for 4 times, and then exit.

        $ fileobj ./a.out
          (command)4i414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)4iABC<ESC>

+ Open a file *./a.out*, enter append edit mode to insert "\x41\x42\x43", and then exit.

        $ fileobj ./a.out
          (command)a414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)aABC<ESC>

+ Open a file *./a.out*, enter append edit mode to insert "\x41\x42\x43" for 4 times, and then exit.

        $ fileobj ./a.out
          (command)4a414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)4aABC<ESC>

+ Open a file *./a.out*, enter replace edit mode to replace with "\x41\x42\x43", and then exit.

        $ fileobj ./a.out
          (command)R414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)RABC<ESC>

+ Open a file *./a.out*, enter replace edit mode to replace with "\x41\x42\x43" for 4 times, and then exit.

        $ fileobj ./a.out
          (command)4R414243<ESC>
          or
          (command):set ascii<ENTER>
          (command)4RABC<ESC>

### Rotate buffer contents

+ Open an empty buffer, insert 512 bytes with "\x55\xaa", and save it as *./a.img*.

        $ fileobj
          (command)256i55aa<ESC>
          (command):wq ./a.img<ENTER>

+ Open a file *./a.img* and overwrite the first 4 bytes with "\x7fELF".

        $ fileobj ./a.img
          (command)R7f454c46<ESC>
          or
          (command)R7f<ESC>
          (command):set ascii<ENTER>
          (command)l
          (command)RELF<ESC>

+ Open a file *./a.img*, rotate the entire buffer 1 bit to right, and then 1 bit to left.

        $ fileobj ./a.img
          (command)>>
          (command)G
          (command)<<

+ Open a file *./a.img*, rotate the entire buffer 8 bits (1 byte) to right, and then 8 bits (1 byte) to left.

        $ fileobj ./a.img
          (command)8>>
          (command)G
          (command)8<<

### Undo buffer changes

+ Open a file *./a.out* and undo changes.

        $ fileobj ./a.out
          (command)(do some edit)
          (command)u

+ Open a file *./a.out* and undo all changes.

        $ fileobj ./a.out
          (command)(do some edit)
          (command)U

+ Open a file *./a.out* and redo the undo'ed changes.

        $ fileobj ./a.out
          (command)(do some edit)
          (command)(do undo)
          (command)CTRL-r

### Search buffer contents

+ Open a file *./a.out* and search forward for "GNU".

        $ fileobj ./a.out
          (command)/GNU<ENTER>

+ Open a file *./a.out* and search (forward or backward depending on previous direction) for the next.

        $ fileobj ./a.out
          (command)n

+ Open a file *./a.out* and search backward for "GNU".

        $ fileobj ./a.out
          (command)?GNU<ENTER>

+ Open a file *./a.out* and search (backward or forward depending on previous direction) for the next.

        $ fileobj ./a.out
          (command)N

+ Open a file *./a.out* and search for "\x7fELF" (limitation: can not search for ASCII string "\x??\x??.." or "\X??..").

        $ fileobj ./a.out
          (command)/\x7fELF<ENTER>
          or
          (command)/\x7f\x45\x4c\x46<ENTER>
          or
          (command)/\X7f454c46<ENTER>

+ Open a file *./a.out* and search for "\x41\x42\x43" (limitation: can not search for ASCII string "\x??\x??.." or "\X??..").

        $ fileobj ./a.out
          (command)/\x41\x42\x43<ENTER>
          or
          (command)/\X414243<ENTER>
          or
          (command)/ABC<ENTER>

### Set mark

+ Open a file *./a.out*, go to offset 1024, and mark the current position as 'a'.

        $ fileobj ./a.out
          (command)1024go
          (command)ma

+ Open a file *./a.out* and go to mark 'a' position.

        $ fileobj ./a.out
          (command)`a

### Partial open

+ Open a file *./a.out* from offset 1024.

        $ fileobj ./a.out@1024
        or
        $ fileobj ./a.out@0x400
        or
        $ fileobj ./a.out@02000

+ Open a file *./a.out* from offset 1024 for 512 bytes.

        $ fileobj ./a.out@1024:512
        or
        $ fileobj ./a.out@0x400:512
        or
        $ fileobj ./a.out@0x400-0x600

+ Open a file *./a.out* for first 1024 bytes.

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

### Multiple files

+ Open a file *./a.out* and then close.

        $ fileobj ./a.out
          (command):bdelete<ENTER>

+ Open a file *./a.out* via command.

        $ fileobj
          (command):e ./a.out<ENTER>

+ Open a file *./a.out* and open another file */path/to/b.out* via command.

        $ fileobj ./a.out
          (command):e /path/to/b.out<ENTER>

+ Open two files *./a.out* and *./b.out* via command line arguments.

        $ fileobj ./a.out ./b.out

+ After opening files, switch current buffer from one file to another.

        $ fileobj ./a.out ./b.out
          (command)<TAB>
          or
          (command):bnext<ENTER>

### Multiple windows

+ Open two files *./a.out* and *./b.out* with horizontally splitted windows for each file respectively.

        $ fileobj ./a.out ./b.out -o

+ Open two files *./a.out* and *./b.out* with vertically splitted windows for each file respectively.

        $ fileobj ./a.out ./b.out -O

+ After opening files with multiple windows, change focus to the next window.

        $ fileobj ./a.out ./b.out ./c.out -o
          (command)CTRL-W w

+ After opening files with multiple windows, close all windows except for the current one.

        $ fileobj ./a.out ./b.out ./c.out -o
          (command)CTRL-W o
          or
          (command):only<ENTER>

+ Open (split) another window, and then close.

        $ fileobj
          (command)CTRL-W s
          or
          (command):split<ENTER>
          then
          (command)CTRL-W c
          or
          (command):close<ENTER>

### Visual mode

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

+ Open a file *./a.out* and enter block visual mode (also see *[Notes](README.notes.md)*).

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
          (command)(move a cursor)
          (command)x

+ Open a file *./a.out* and yank visually selected region.

        $ fileobj ./a.out
          (command)v
          or
          (command)V
          or
          (command)CTRL-v
          then
          (command)(move a cursor)
          (command)y

+ Open a file *./a.out* and replace visually selected region with \xff.

        $ fileobj ./a.out
          (command)v
          or
          (command)V
          or
          (command)CTRL-v
          then
          (command)(move a cursor)
          (command)rff

+ Open a file *./a.out* and right rotate visually selected region.

        $ fileobj ./a.out
          (command)v
          or
          (command)V
          or
          (command)CTRL-v
          then
          (command)(move a cursor)
          (command)>>

### Set editor options

+ Set binary edit mode (unset ascii edit mode, default).

        $ fileobj ./a.out
          (command):set binary<ENTER>

+ Set ascii edit mode (unset binary edit mode).

        $ fileobj ./a.out
          (command):set ascii<ENTER>

+ Set *bytes per line* to a specified number, "max", "min" or "auto".

        $ fileobj ./a.out
          (command):set bytes_per_line 8<ENTER>
          or
          (command):set bpl 8<ENTER>

+ Set *bytes per window* to a specified number, "even" or "auto".

        $ fileobj ./a.out
          (command):set bytes_per_window 512<ENTER>
          or
          (command):set bpw 512<ENTER>

+ Enable case sensitive search (no ignore case, default).

        $ fileobj ./a.out
          (command):set noic<ENTER>

+ Enable case insensitive search (ignore case).

        $ fileobj ./a.out
          (command):set ic<ENTER>

+ Search wrap around the end of the buffer (default).

        $ fileobj ./a.out
          (command):set ws<ENTER>

+ Search to not wrap around the end of the buffer.

        $ fileobj ./a.out
          (command):set nows<ENTER>

### Block device

+ Open a block device */dev/sdb* on Linux.

        $ sudo fileobj /dev/sdb

+ Open a block device */dev/sdb* for first 512 bytes and zero clear that region.

        $ sudo fileobj /dev/sdb@:512
          (command)v
          (command)G
          (command)r00

+ Open a block device */dev/sdb* and go to offset 320 MiB.

        $ sudo fileobj /dev/sdb
          (command)335544320go
          or
          (command)[320MiB]go
          or
          (command)[327680KiB]go

+ Open a block device */dev/sdb* and show sector size.

        $ sudo fileobj /dev/sdb
          (command):sector<ENTER>

+ Open a block device */dev/sdb* and show the current buffer size and cursor position in sector.

        $ sudo fileobj /dev/sdb
          (command)(move a cursor)
          (command)g CTRL-g

+ Open a block device */dev/sdb* and go to first byte of the previous sector. This is sector based version of `h`.

        $ sudo fileobj /dev/sdb
          (command)sh

+ Open a block device */dev/sdb* and go to first byte of the next sector. This is sector based version of `l`.

        $ sudo fileobj /dev/sdb
          (command)sl

+ Open a block device */dev/sdb* and go to sector 128. This is sector based version of `go`.

        $ sudo fileobj /dev/sdb
          (command)128sgo

+ Open a block device */dev/sdb* and go to first byte of the current sector. This is sector based version of `0`.

        $ sudo fileobj /dev/sdb
          (command)s0

+ Open a block device */dev/sdb* and go to last byte of the current sector. This is sector based version of `$`.

        $ sudo fileobj /dev/sdb
          (command)s$

### Binary edit user space memory (experimental and platform specific feature)

+ Prepare a test program *test1* which continues to print "ABCDEFGHIJKLMNOPQRSTUVWXYZ".

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
        ...

+ Modify .rodata section of a running *test1* process. *pid\<PID\>* syntax indicates to open process address space provided *\<PID\>* exists.

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
          (command):wq<ENTER>

+ A running *test1* process starts to print "abcdefghijklmnopqrstuvwxyz".

        ...
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        abcdefghijklmnopqrstuvwxyz <- .rodata section overwritten in lower case
        abcdefghijklmnopqrstuvwxyz
        abcdefghijklmnopqrstuvwxyz
        abcdefghijklmnopqrstuvwxyz
        abcdefghijklmnopqrstuvwxyz
        abcdefghijklmnopqrstuvwxyz
        ^C

+ If *test1* was executed via absolute path (i.e. */path/to/test1*), *@objdump[section]* syntax can be used to open the entire .rodata section.

        # fileobj pid8549@objdump.rodata
          (command)/A<ENTER>
          (command)26~
          (command):wq<ENTER>

### Extensions

+ Extensions open a new buffer in text only representation.

#### :extensions extension

+ Open a list of extensions buffer.

        $ fileobj
          (command):extensions<ENTER>

#### :help extension

+ Open a usage buffer.

        $ fileobj
          (command):help<ENTER>

#### :ls extension

+ Open a list of buffers buffer.

        $ fileobj ./a.out ./b.out ./c.out
          (command):args<ENTER>
          or
          (command):ls<ENTER>

#### :disas_x86 extension

+ Disassemble the current buffer assuming x86 instructions, and open a x86 assembly buffer.

        $ fileobj ./a.out
          (command):disas_x86<ENTER>

+ Disassemble the current buffer starting from offset 1024, and open a x86 assembly buffer.

        $ fileobj ./a.out
          (command)1024go
          (command):disas_x86<ENTER>

+ Disassemble a visually selected region of the current buffer, and open a x86 assembly buffer.

        $ fileobj ./a.out
          (command)v
          or
          (command)V
          or
          (command)CTRL-v
          then
          (command)(move a cursor)
          (command):disas_x86<ENTER>

+ Disassemble a single x86 instruction at the current position.

        $ fileobj ./a.out
          (command)(move a cursor)
          (command)d

#### :cstruct extension

+ Define a C struct *test1* in *${HOME}/.fileobj/cstruct*.

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

+ Open a file */path/to/data* which contains data in interest.

        $ fileobj /path/to/data

+ Open a *:cstruct* buffer with *test1* argument. The *test1* source starts from the current position, which is 0 in this case.

        $ fileobj /path/to/data
          (command):cstruct test1<ENTER>

+ C structs can be defined in external files.

        $ fileobj /path/to/data
          (command):cstruct /path/to/struct/defines test1<ENTER>

+ Save the *:cstruct* buffer as *./test1.out*.

        ...
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

### Misc command line options

+ *--lsblk* option lists block devices.

        # fileobj --lsblk
           name      size         sector_size size            sector_size label error
         1 /dev/dm-0 0x2fffc00000 0x200       191.996094[GiB] 512[B]      -     -
         2 /dev/dm-1 0x100000000  0x200       4[GiB]          512[B]      -     -
         3 /dev/sda  0x500000000  0x200       20[GiB]         512[B]      -     -
         4 /dev/sda1 0x4ff600000  0x200       19.990234[GiB]  512[B]      -     -
         5 /dev/sda9 0x800000     0x200       8[MiB]          512[B]      -     -
         6 /dev/sdb  0x3200000000 0x200       200[GiB]        512[B]      -     -
         7 /dev/sdb1 0x100000000  0x200       4[GiB]          512[B]      -     -
         8 /dev/sdb2 0x30fff00000 0x200       195.999023[GiB] 512[B]      -     -
         9 /dev/sr0  -            -           -               -           -     [Errno 123] No medium found: '/dev/sr0'

+ *--md* option prints message digest of files using a specified hash algorithm (defaults to "sha256"). A block size defaults to 64KiB, and is tunable via *FILEOBJ_LOGICAL_BLOCK_SIZE* environment variable.

        $ fileobj ./a.out ./b.out ./c.out --md=sha256 --verbose
        blake2b blake2s md4 md5 md5-sha1 ripemd160 sha1 sha224 [sha256] sha384 sha3_224 sha3_256 sha3_384 sha3_512 sha512 sha512_224 sha512_256 shake_128 shake_256 sm3 whirlpool
        55350da17b75659b2a9b5aaa500f68051c2c1d75b783e50241b75d40fe8ecd07  /path/to/a.out
        2bb675364295d86027ba1c366dd1f3c3eed73da74283c028d884538edf11a58f  /path/to/b.out
        ef4130886a206f5c86093e74b4afa2b18e206d72c9c72897be3d4f8a8ab5dc2f  /path/to/c.out

        $ fileobj ./a.out@1024:0x10000 ./b.out ./c.out@0x1000-0x2000 --md=md5 --verbose
        blake2b blake2s md4 [md5] md5-sha1 ripemd160 sha1 sha224 sha256 sha384 sha3_224 sha3_256 sha3_384 sha3_512 sha512 sha512_224 sha512_256 shake_128 shake_256 sm3 whirlpool
        64376d47e18eb5d130b1b9c27abd0a02  /path/to/a.out
        62c81971892dcb0ca2c0d58b4811b6bf  /path/to/b.out
        d3c205dbb1777dc60486ccfedc93cbe6  /path/to/c.out

+ *--blkcmp* option compares contents of specified files. A block size defaults to 64KiB, and is tunable via *FILEOBJ_LOGICAL_BLOCK_SIZE* environment variable.

        $ fileobj ./a.out ./b.out ./c.out --blkcmp
        #0 0.0% 0x000000 -> 0 0x000000 (141, 21, 174) 1 65533/65536 100.0%
        #1 13.3% 0x010000 -> 0 0x010000 (215, 158, 230) 1 65535/65536 100.0%
        #2 26.5% 0x020000 -> 0 0x020000 (243, (98, 'b'), 214) 1 65535/65536 100.0%
        #3 39.8% 0x030000 -> 0 0x030000 (207, (97, 'a'), 189) 1 65535/65536 100.0%
        #4 53.1% 0x040000 -> 0 0x040000 (171, 217, 192) 1 65535/65536 100.0%
        #5 66.4% 0x050000 -> 0 0x050000 (159, 217, 230) 1 65533/65536 100.0%
        #6 79.6% 0x060000 -> 0 0x060000 (0, 218, (85, 'U')) 1 65535/65536 100.0%
        #7 92.9% 0x070000 -> 0 0x070000 (128, 200, 240) 0 35048/35048 100.0%
        scanned 8 blocks

        $ fileobj ./img1 ./img2@1024:0x40000 --blkcmp | head -10
        #0 0.0% 0x0000000000|[0x0000000400|0x0000000000] -> 0 0x0000000000|[0x0000000400|0x0000000000] (0, 175) 63107 382/65536 0.6%
        #1 0.0% 0x0000010000|[0x0000010400|0x0000010000] -> 0 0x0000010000|[0x0000010400|0x0000010000] (248, 0) 65516 20/65536 0.0%
        #2 0.0% 0x0000020000|[0x0000020400|0x0000020000] -> 64512 0x000002fc00|[0x0000030000|0x000002fc00] (0, 255) 64512 52/65536 0.1%
        #3 0.0% 0x0000030000|[0x0000030400|0x0000030000] -> 0 0x0000030000|[0x0000030400|0x0000030000] (255, 0) 31694 6206/65536 9.5%
        #4 0.0% 0x0000040000|[0x0000040400|0x0000040000] -> 0 0x0000040000|[0x0000040400|0x0000040000] (3, None) 0 65536/65536 100.0%
        #5 0.0% 0x0000050000|[0x0000050400|0x0000050000] -> 0 0x0000050000|[0x0000050400|0x0000050000] (0, None) 0 65536/65536 100.0%
        #6 0.0% 0x0000060000|[0x0000060400|0x0000060000] -> 0 0x0000060000|[0x0000060400|0x0000060000] ((35, '#'), None) 0 65536/65536 100.0%
        #7 0.0% 0x0000070000|[0x0000070400|0x0000070000] -> 0 0x0000070000|[0x0000070400|0x0000070000] ((35, '#'), None) 0 65536/65536 100.0%
        #8 0.0% 0x0000080000|[0x0000080400|0x0000080000] -> 0 0x0000080000|[0x0000080400|0x0000080000] ((35, '#'), None) 0 65536/65536 100.0%
        #9 0.1% 0x0000090000|[0x0000090400|0x0000090000] -> 0 0x0000090000|[0x0000090400|0x0000090000] ((35, '#'), None) 0 65536/65536 100.0%

+ *--blkscan* option prints file offsets of matched logical blocks using a specified method (defaults to "zero"). A block size defaults to 64KiB, and is tunable via *FILEOBJ_LOGICAL_BLOCK_SIZE* environment variable.

        $ fileobj ./img1@0x10000 --blkscan=nonzero | head -10
        0x0000010000|0x0000000000
        0x0000030000|0x0000020000
        0x0000040000|0x0000030000
        0x0000050000|0x0000040000
        0x0000060000|0x0000050000
        0x0000070000|0x0000060000
        0x0000080000|0x0000070000
        0x0000090000|0x0000080000
        0x00000a0000|0x0000090000
        0x00000b0000|0x00000a0000

        $ fileobj ./img1 --blkscan=sha256 | head -10
        0x0000000000 287929a3d00bf80e7c773dec7f1384be23d3d905ac49b3d9b33c1e511c0339a9
        0x0000010000 66438ce150257546926c2f7c5f06959e2e7737413f66b965fd138a37e6850f57
        0x0000020000 de2f256064a0af797747c2b97505dc0b9f3df0de4f489eac731c23ae9ca9cc31
        0x0000030000 f306d0ad1a78f73a28e16dba189cae0674433ad8ee5e5a95da77a808fe5c4350
        0x0000040000 0f0ae1b7fb36c0da65ba00f28222556c6e7f01eb5589ac9346a28809b5495342
        0x0000050000 54f2b5c6491d4d527d79359bbcaf62df7cbaff8ef77e3abc7ca8863fd14d9d24
        0x0000060000 cbc3bd03ac237aa649fc713320e77a5ded7c58eec224d93e5a96d3c57ed401eb
        0x0000070000 19874dc886d589feb8ed01b0ff4bec35c4e5406436ed588de932e609e74bfad8
        0x0000080000 8e8b8d118df5c5cf4d3cb85b7c1e6910d0632d9b4f1d628fd08683758706980d
        0x0000090000 0144d2e852b5c927b17430de2e213c6b4aa2c110403c7c5ab532db09121c5281

+ *--blkdump* option prints contents of files using a specified method (defaults to "text"). A block size defaults to 64KiB, and is tunable via *FILEOBJ_LOGICAL_BLOCK_SIZE* environment variable. The second example concatenates first 512 bytes of two files into a new file *./out.bin*.

        $ FILEOBJ_BYTES_PER_LINE=16 fileobj --blkdump= ./img | head -10
        0x0000000000| 06 E6 09 BB A2 17 79 2C FD 0D 9C 5E C7 89 49 91 ......y,...^..I.
        0x0000000010| 41 84 46 33 39 62 5E 44 EA B3 0D CA F9 88 73 5E A.F39b^D......s^
        0x0000000020| 63 1B 77 29 3A 7C A8 32 DC AD 8E 22 6E 9D 0C D7 c.w):|.2..."n...
        0x0000000030| 09 A7 2D F7 EC 71 B4 19 DF E2 8B 70 3C 5C B9 B9 ..-..q.....p<\..
        0x0000000040| B9 2C 53 A7 A5 96 92 36 C5 5B CF 6B 38 2E C3 32 .,S....6.[.k8..2
        0x0000000050| 2F 26 AA 4C 54 28 35 A2 5F C5 34 B2 46 B1 D4 0E /&.LT(5._.4.F...
        0x0000000060| 7A F8 91 3D B8 FF F4 9A 29 63 B0 83 5A 84 E2 64 z..=....)c..Z..d
        0x0000000070| 4A BB 79 A8 DC 89 73 2B A3 EC 9B 83 E1 D4 F2 25 J.y...s+.......%
        0x0000000080| 4E 62 F1 E9 5B E1 EB 7A 20 3E 51 3F 1B 21 78 37 Nb..[..z >Q?.!x7
        0x0000000090| 47 E6 D1 26 CA F8 9E F2 ED 53 55 7D ED 05 F2 90 G..&.....SU}....

        $ fileobj --blkdump=raw ./img1@0:512 ./img2@0:512 > ./out.bin
        $ file ./out.bin
        ./out.bin: data
        $ wc -c ./out.bin
        1024 ./out.bin
