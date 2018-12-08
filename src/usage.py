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
    s = s.replace("\n\n", "\n")
    if s.startswith("\n"):
        s = s[1:]
    s = s.replace("\&", "")
    s = s.replace("\fB", "")
    s = s.replace("\fI", "")
    s = s.replace("\fP", "")
    s = s.replace("\fR", "")
    s = s.replace("\-", "-")
    s = s.replace("\|", "")
    if not s.endswith("\n"):
        s += "\n"
    return s

def _metavar(s):
    return "<{0}>".format(s)

help = _("""
\n
  \fBfileobj\fP [\fIoptions\fP]... [\fIpaths\fP]...
  \fBfileobj\fP [\fIoptions\fP]... [\fIpaths\fP[\fI@offset:length\fP]]...
  \fBfileobj\fP [\fIoptions\fP]... [\fIpaths\fP[\fI@offset\-(offset+length)\fP]]...
""")[:-1]

R = _("""
Use read\-only mode.
""")

B = _("""
Use Python bytes based buffer for regular files.
This option is required to insert or delete bytes on some platforms.
""")

o = _("""
Initially assign buffers given by \fIpaths\fP to horizontally splitted windows.
When \fI<number_of_windows>\fP is omitted, assign one window for each buffer.
""")
o_metavar = _metavar("number_of_windows")

O = _("""
Initially assign buffers given by \fIpaths\fP to vertically splitted windows.
When \fI<number_of_windows>\fP is omitted, assign one window for each buffer.
""")
O_metavar = _metavar("number_of_windows")

bytes_per_line = _("""
Set number of bytes printed per line.
Each line prints \fI<bytes_per_line>\fP bytes.
Available formats for \fI<bytes_per_line>\fP are digit, "max", "min" and "auto".
"auto" sets the value to the maximum 2^N that fits in the terminal width.
"auto" is used by default.
""")
bytes_per_line_metavar = _metavar("bytes_per_line")

bytes_per_window = _("""
Set number of bytes printed per window.
Each window prints \fI<bytes_per_window>\fP bytes, using the current number of bytes per line.
Available formats for \fI<bytes_per_window>\fP are digit, "even" and "auto".
"even" sets all windows to have the same size.
"auto" is used by default.
""")
bytes_per_window_metavar = _metavar("bytes_per_window")

bytes_per_unit = _("""
Set number of bytes printed per unit.
Each unit prints \fI<bytes_per_unit>\fP bytes.
"1" is used by default.
""")
bytes_per_unit_metavar = _metavar("bytes_per_unit")

no_text = _("""
Disable text window.
""")

no_color = _("""
Disable color for buffer contents.
""")

force = _("""
Ignore warnings which can be ignored.
""")

test_screen = _("""
Enter \fBncurses\fP\|(3) screen test mode.
""")

env = _("""
Print list of environment variables and exit.
""")

command = _("""
Print list of editor commands and exit. Also see \fB:help\fP.
""")

sitepkg = _("""
Print \fBpython\fP\|(1) site\-package directory and exit.
""")

FILEOBJ_USE_READONLY = _("""
If defined, use read\-only mode (equivalent to \fB\-R\fP).
""")

FILEOBJ_USE_BYTES_BUFFER = _("""
If defined, use Python bytes based buffer for regular files (equivalent to \fB\-B\fP).
""")

FILEOBJ_USE_ASCII_EDIT = _("""
If defined, use ASCII edit mode (equivalent to \fB:set ascii\fP).
Defaults to binary edit mode if undefined.
""")

FILEOBJ_USE_IGNORECASE = _("""
If defined, search operation is case-insensitive (equivalent to \fB:set ic\fP).
Defaults to case-sensitive if undefined.
""")

FILEOBJ_USE_SIPREFIX = _("""
If defined, use 10^3(K) for kilo (equivalent to \fB:set si\fP).
Defaults to 2^10(Ki) if undefined.
""")

FILEOBJ_USE_WRAPSCAN = _("""
If defined, search wraps around the end of the buffer (equivalent to \fB:set ws\fP).
Defaults to no wrap around if undefined.
""")

FILEOBJ_USE_TEXT_WINDOW = _("""
If set to "false", do not use text window.
Defaults to use text window if undefined.
""")

FILEOBJ_USE_BACKUP = _("""
If defined, create backup files under \fI~/.fileobj\fP.
Backup files start with '.'.
Only applies to regular files.
""")

FILEOBJ_ENDIANNESS = _("""
If set to "little" or "big", set endianness for multi-bytes data (equivalent to \fB:set le\fP and \fB:set be\fP).
Defaults to host endian if undefined.
""")

FILEOBJ_ADDRESS_RADIX = _("""
If set to "16", "10" or "8", show address in either hexadecimal, decimal or octal (equivalent to \fB:set address\fP).
Defaults to "16" if undefined.
""")

FILEOBJ_BYTES_PER_LINE = _("""
Set number of bytes printed per line (equivalent to \fB\-\-bytes_per_line\fP and \fB:set bytes_per_line\fP).
""")

FILEOBJ_BYTES_PER_WINDOW = _("""
Set number of bytes printed per window (equivalent to \fB\-\-bytes_per_window\fP and \fB:set bytes_per_window\fP).
""")

FILEOBJ_BYTES_PER_UNIT = _("""
Set number of bytes printed per unit (equivalent to \fB\-\-bytes_per_unit\fP and \fB:set bytes_per_unit\fP).
""")

FILEOBJ_COLOR_CURRENT = _("""
Set current cursor and window color.
Defaults to "black,green" if undefined.
Set blank string to disable.
Available colors are "black", "blue", "cyan", "green", "magenta", "red", "white", "yellow".
""")

FILEOBJ_COLOR_ZERO = _("""
Set color for zero (0) bytes within buffer contents.
Defaults to "green" if undefined.
Set blank string to disable.
Available colors are "black", "blue", "cyan", "green", "magenta", "red", "white", "yellow".
""")

FILEOBJ_COLOR_FF = _("""
Set color for 0xff bytes within buffer contents.
Defaults to "magenta" if undefined.
Set blank string to disable.
Available colors are "black", "blue", "cyan", "green", "magenta", "red", "white", "yellow".
""")

FILEOBJ_COLOR_PRINT = _("""
Set color for printable bytes within buffer contents.
Defaults to "cyan" if undefined.
Set blank string to disable.
Available colors are "black", "blue", "cyan", "green", "magenta", "red", "white", "yellow".
""")

FILEOBJ_COLOR_VISUAL = _("""
Set color for visual region.
Defaults to "red,yellow" if undefined.
Set blank string to disable.
Available colors are "black", "blue", "cyan", "green", "magenta", "red", "white", "yellow".
""")
