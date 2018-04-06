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
\fBfileobj\fP [\fIoptions\fP]... [\fIpaths\fP]...
""")[:-1]

R = _("""
Use read\-only mode.
""")

B = _("""
Use \fBmalloc\fP\|(3) based buffer for regular files.
Regular files internally use \fBmmap\fP\|(2) based buffer by default, and relies on \fBmremap\fP\|(2) when resizing (i.e. insertion or deletion) the buffer.
This option is used when the system does not support \fBmremap\fP\|(2), but need to resize the buffer for regular files.
""")

d = _("""
Show the buffer offset from \fIoffset\fP to \fIoffset+length\fP rather than from from \fI0\fP to \fIlength\fP, when the buffer is partially loaded.
Using \fI@offset:length\fP or \fI@offset\-(offset+length)\fP syntax right after the path without space (i.e. /path/to/file\fI@offset:length\fP or /path/to/file\fI@offset\-(offset+length)\fP) allows partial buffer loading.
See \fBDOCUMENTATION\fP for details of the syntax.
""")

x = _("""
Show the buffer size and current position in hexadecimal.
""")

o = _("""
Start the program with each buffer given by \fIpaths\fP in horizontally splitted windows, as long as the terminal has enough size to accommodate windows.
""")

O = _("""
Start the program with each buffer given by \fIpaths\fP in vertically splitted windows, as long as the terminal has enough size to accommodate windows.
""")

bytes_per_line = _("""
Set fixed number of bytes printed per line.
The program prints \fI<bytes_per_line>\fP bytes for each line as long as the terminal has enough width to accommodate.
Available formats for \fI<bytes_per_line>\fP are digit, "max", "min" and "auto".
If this option is not specified, the program assumes "auto" is specified.
Using "auto" sets the value to the maximum 2^N that fits in the terminal width.
""")
bytes_per_line_metavar = _metavar("bytes_per_line")

bytes_per_window = _("""
Set fixed number of bytes printed per window.
The program prints \fI<bytes_per_window>\fP bytes for each window as long as the terminal has enough size to accommodate.
This option technically sets number of lines printed per window, based on the number of bytes per line which can also manually be specified by \fB\-\-bytes_per_line\fP option.
Available formats for \fI<bytes_per_window>\fP are digit, "even" and "auto".
Specifying "even" does not set fixed number of bytes, but makes all windows have the same size when a new window is vertically added.
If this option is not specified, the program assumes "auto" is specified.
""")
bytes_per_window_metavar = _metavar("bytes_per_window")

fg = _("""
Set foreground color of the terminal.
Available colors for \fI<color>\fP are "black", "blue", "cyan", "green", "magenta", "red", "white" and "yellow".
If neither this option nor \fB\-\-bg\fP option is specified, the program assumes "black" is specified.
This option is not supported on VT1xx and VT2xx terminals.
""")
fg_metavar = _metavar("color")

bg = _("""
Set background color of the terminal.
Available colors for \fI<color>\fP are "black", "blue", "cyan", "green", "magenta", "red", "white" and "yellow".
If neither this option nor \fB\-\-fg\fP option is specified, the program assumes "white" is specified.
This option is not supported on VT1xx and VT2xx terminals.
""")
bg_metavar = _metavar("color")

verbose_window = _("""
Use verbose status window format instead of the default one.
""")

backup = _("""
Create backup files for regular files. The program keeps consistency of backing files if it terminates normally, but this option guarantees safety by creating a copy of files. Backup files are created under \fI~/.fileobj\fP, and removed if the program terminates normally. Backup files start with '.'. This option only applies to regular files.
""")

force = _("""
Ignore warnings which can be ignored by specifying this option and proceed.
""")

test_screen = _("""
Enter \fBncurses\fP\|(3) screen test mode.
""")

command = _("""
Print the list of available editor commands and exit.
""")

sitepkg = _("""
Print \fBpython\fP\|(1) site\-package directory being used by the program and exit.
""")
