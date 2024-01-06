# Copyright (c) 2016, Tomohiro Kusumi
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Don't replace "\n" with " ".
# usage.help needs exact format to be printed.
def _(s):
    assert r"\&" not in s, s
    assert r"\fB" not in s, s
    assert r"\fI" not in s, s
    assert r"\fP" not in s, s
    assert r"\fR" not in s, s
    assert r"\-" not in s, s
    assert r"\|" not in s, s

    s = s.replace("\n\n", "\n")
    if s.startswith("\n"):
        s = s[1:]
    if not s.endswith("\n"):
        s += "\n"
    return s

def _metavar(s):
    return "<{0}>".format(s)

help = _("""
\n
  fileobj [options]... [paths]...
  fileobj [options]... [paths[@offset:length]]...
  fileobj [options]... [paths[@offset-(offset+length)]]...
""")[:-1]

R = _("""
Use read-only mode.
""")

B = _("""
Use Python bytes based buffer for regular files.
This option is required to insert or delete bytes on some platforms.
""")

o = _("""
Initially assign buffers given by paths to horizontally splitted windows.
When <number_of_windows> is omitted, assign one window for each buffer.
""")
o_metavar = _metavar("number_of_windows")

O = _("""
Initially assign buffers given by paths to vertically splitted windows.
When <number_of_windows> is omitted, assign one window for each buffer.
""")
O_metavar = _metavar("number_of_windows")

bytes_per_line = _("""
Set number of bytes printed per line.
Each line prints <bytes_per_line> bytes.
Available formats for <bytes_per_line> are digit, "max", "min" and "auto".
"auto" sets the value to the maximum 2^N that fits in the terminal width.
"auto" is used by default.
""")
bytes_per_line_metavar = _metavar("bytes_per_line")

bytes_per_window = _("""
Set number of bytes printed per window.
Each window prints <bytes_per_window> bytes, using the current number of bytes per line.
Available formats for <bytes_per_window> are digit, "even" and "auto".
"even" sets all windows to have the same size.
"auto" is used by default.
""")
bytes_per_window_metavar = _metavar("bytes_per_window")

bytes_per_unit = _("""
Set number of bytes printed per unit.
Each unit prints <bytes_per_unit> bytes.
"1" is used by default.
""")
bytes_per_unit_metavar = _metavar("bytes_per_unit")

no_text = _("""
Disable text window.
""")

no_mouse = _("""
Disable mouse events.
""")

no_color = _("""
Disable color for buffer contents.
""")

force = _("""
Ignore warnings which can be ignored.
""")

verbose = _("""
Enable verbose mode.
""")

test_screen = _("""
Enter ncurses(3) screen test mode.
""")

test_mouse = _("""
Enter ncurses(3) mouse test mode.
""")

test_color = _("""
Enter ncurses(3) color test mode.
""")

list_color = _("""
Print list of available screen colors and exit.
"r:g:b" format is printed if a terminal supports it.
""")

env = _("""
Print list of environment variables and exit.
""")

command = _("""
Print list of editor commands and exit. Also see :help.
""")

sitepkg = _("""
Print python(1) site-package directory and exit.
""")

cmp = _("""
Compare contents of files and exit.
""")

md = _("""
Print message digest of files using <hash_algorithm> and exit.
Defaults to use SHA256.
""")
md_metavar = _metavar("hash_algorithm")

blkscan = _("""
Print file offsets of matched logical blocks and exit.
Defaults to use zero.
""")
blkscan_metavar = _metavar("scan_type")

lsblk = _("""
Print list of block devices and exit.
This prints character devices on some platforms.
""")

version = _("""
Show program's version number and exit.
""")

FILEOBJ_USE_READONLY = _("""
If defined, use read-only mode (equivalent to -R).
""")

FILEOBJ_USE_BYTES_BUFFER = _("""
If defined, use Python bytes based buffer for regular files (equivalent to -B).
""")

FILEOBJ_USE_ASCII_EDIT = _("""
If defined, use ASCII edit mode (equivalent to :set ascii).
Defaults to binary edit mode if undefined.
""")

FILEOBJ_USE_IGNORECASE = _("""
If defined, search operation is case-insensitive (equivalent to :set ic).
Defaults to case-sensitive if undefined.
""")

FILEOBJ_USE_SIPREFIX = _("""
If defined, use 10^3(K) for kilo (equivalent to :set si).
Defaults to 2^10(Ki) if undefined.
""")

FILEOBJ_USE_WRAPSCAN = _("""
If set to "false", search does not wrap around the end of the buffer (equivalent to :set nows).
Defaults to wrap around if undefined.
""")

FILEOBJ_USE_TEXT_WINDOW = _("""
If set to "false", do not use text window.
Defaults to use text window if undefined.
""")

FILEOBJ_USE_MOUSE_EVENTS = _("""
If set to "false", do not use mouse events.
Defaults to use mouse events if undefined.
""")

FILEOBJ_USE_COLOR = _("""
If set to "false", do not use color for buffer contents (equivalent to --no_color).
This set to "false" is equivalent to FILEOBJ_COLOR_ZERO, FILEOBJ_COLOR_FF, FILEOBJ_COLOR_PRINT, FILEOBJ_COLOR_DEFAULT, FILEOBJ_COLOR_OFFSET set to "none" or "white".
Defaults to use color if undefined.
""")

FILEOBJ_USE_UNIT_BASED = _("""
If defined, editor operations are on per unit basis where possible.
Defaults to on per byte basis.
""")

FILEOBJ_USE_BACKUP = _("""
If defined, create backup files under ~/.fileobj.
Backup files start with '.'.
Only applies to regular files.
""")

FILEOBJ_USE_TRUNCATE_SHRINK = _("""
If defined, allow :truncate to shrink truncate.
Defaults to disallow.
""")

FILEOBJ_USE_LINE_SCROLL = _("""
If set to "false", enable page scroll mode.
Defaults to line scroll mode.
""")

FILEOBJ_BUFFER_SIZE = _("""
Set custom buffer size if larger than 0.
Defaults to 0.
""")

FILEOBJ_LOGICAL_BLOCK_SIZE = _("""
Set custom logical block size if larger than 0.
Defaults to 0.
""")

FILEOBJ_ENDIANNESS = _("""
If set to "little" or "big", set endianness for multi-bytes data (equivalent to :set le and :set be).
Defaults to host endian if undefined.
""")

FILEOBJ_ADDRESS_RADIX = _("""
If set to "16", "10" or "8", show address in either hexadecimal, decimal or octal (equivalent to :set address).
Defaults to "16" if undefined.
""")

FILEOBJ_BYTES_PER_LINE = _("""
Set number of bytes printed per line (equivalent to --bytes_per_line and :set bytes_per_line).
""")

FILEOBJ_BYTES_PER_WINDOW = _("""
Set number of bytes printed per window (equivalent to --bytes_per_window and :set bytes_per_window).
""")

FILEOBJ_BYTES_PER_UNIT = _("""
Set number of bytes printed per unit (equivalent to --bytes_per_unit and :set bytes_per_unit).
""")

FILEOBJ_COLOR_CURRENT = _("""
Set current cursor and window color.
Defaults to "black,green" if undefined.
Set blank string to disable.
See --list_color for available colors.
""")

FILEOBJ_COLOR_ZERO = _("""
Set color for zero (0) bytes within buffer contents.
Defaults to "green" if undefined.
Set blank string to disable.
See --list_color for available colors.
""")

FILEOBJ_COLOR_FF = _("""
Set color for 0xff bytes within buffer contents.
Defaults to "magenta" if undefined.
Set blank string to disable.
See --list_color for available colors.
""")

FILEOBJ_COLOR_PRINT = _("""
Set color for printable bytes within buffer contents.
Defaults to "cyan" if undefined.
Set blank string to disable.
See --list_color for available colors.
""")

FILEOBJ_COLOR_DEFAULT = _("""
Set default color for buffer contents.
Defaults to "none" if undefined.
See --list_color for available colors.
""")

FILEOBJ_COLOR_VISUAL = _("""
Set color for visual region.
Defaults to "red,yellow" if undefined.
Set blank string to disable.
See --list_color for available colors.
""")

FILEOBJ_COLOR_OFFSET = _("""
Set color for offsets in editor windows.
Defaults to "none" if undefined.
See --list_color for available colors.
""")

FILEOBJ_DISAS_ARCH = _("""
Set architecture name to use for d command.
Defaults to "x86" if undefined, and currently only "x86" is supported.
""")

FILEOBJ_DISAS_PRIVATE = _("""
Set FILEOBJ_DISAS_ARCH specific data for d command.
Defaults to use 64 bit mode on x86 if undefined.
""")
