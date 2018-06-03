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
\n
  \fBfileobj\fP [\fIoptions\fP]... [\fIpaths\fP]...
  \fBfileobj\fP [\fIoptions\fP]... [\fIpaths\fP[\fI@offset:length\fP]]...
  \fBfileobj\fP [\fIoptions\fP]... [\fIpaths\fP[\fI@offset\-(offset+length)\fP]]...
""")[:-1]

R = _("""
Use read\-only mode.
""")

B = _("""
Use \fBmalloc\fP\|(3) based buffer for regular files instead of the default \fBmmap\fP\|(2) based buffer.
This option is required to resize (i.e. insert or delete) regular files on platforms without \fBmremap\fP\|(2).
""")

d = _("""
Show the buffer offset from \fIoffset\fP to \fIoffset+length\fP rather than from \fI0\fP to \fIlength\fP, when the buffer is partially loaded.
""")

x = _("""
Show the buffer size and current position in hexadecimal.
""")

o = _("""
Initially assign buffers given by \fIpaths\fP to horizontally splitted windows, if the terminal has enough size.
When \fI<number_of_windows>\fP is omitted, assign one window for each buffer.
""")
o_metavar = _metavar("number_of_windows")

O = _("""
Initially assign buffers given by \fIpaths\fP to vertically splitted windows, if the terminal has enough size.
When \fI<number_of_windows>\fP is omitted, assign one window for each buffer.
""")
O_metavar = _metavar("number_of_windows")

bytes_per_line = _("""
Set fixed number of bytes printed per line.
Each line prints \fI<bytes_per_line>\fP bytes, if the terminal has enough width.
Available formats for \fI<bytes_per_line>\fP are digit, "max", "min" and "auto".
"auto" sets the value to the maximum 2^N that fits in the terminal width.
"auto" is used by default.
""")
bytes_per_line_metavar = _metavar("bytes_per_line")

bytes_per_window = _("""
Set fixed number of bytes printed per window.
Each window prints \fI<bytes_per_window>\fP bytes, if the terminal has enough size.
This option sets number of lines printed per window, based on the number of bytes printed per line.
Available formats for \fI<bytes_per_window>\fP are digit, "even" and "auto".
"even" does not set a fixed number of bytes printed per window, but makes all windows have the same size when a new window is vertically added.
"auto" is used by default.
""")
bytes_per_window_metavar = _metavar("bytes_per_window")

fg = _("""
Set foreground color of the terminal.
Available colors for \fI<color>\fP are "black", "blue", "cyan", "green", "magenta", "red", "white" and "yellow".
"black" is used by default.
This option is not supported on VTxxx terminal emulators.
""")
fg_metavar = _metavar("color")

bg = _("""
Set background color of the terminal.
Available colors for \fI<color>\fP are "black", "blue", "cyan", "green", "magenta", "red", "white" and "yellow".
"white" is used by default.
This option is not supported on VTxxx terminal emulators.
""")
bg_metavar = _metavar("color")

verbose_window = _("""
Use verbose status window instead of the default format.
""")

backup = _("""
Explicitly create backup files for regular files.
Backup files are created under \fI~/.fileobj\fP when \fBfileobj\fP starts, and removed when \fBfileobj\fP terminates.
Backup files start with '.'.
This option only applies to regular files.
""")

force = _("""
Ignore warnings which can be ignored by specifying this option.
""")

test_screen = _("""
Enter \fBncurses\fP\|(3) screen test mode.
""")

command = _("""
Print list of editor commands and exit.
""")

sitepkg = _("""
Print \fBpython\fP\|(1) site\-package directory and exit.
""")
