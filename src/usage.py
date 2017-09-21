# Copyright (c) 2010-2016, Tomohiro Kusumi
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
Use \fBmalloc\fP\|(3) based buffer for regular files, which may put pressure on the system depending on the file size.
Regular files use \fBmmap\fP\|(2) based buffer by default, and relies on \fBmremap\fP\|(2) when resizing (i.e. insert or delete bytes) the buffer.
This option is used when the system doesn't support \fBmremap\fP\|(2), but need to resize the buffer for regular files.
Linux kernel has \fBmremap\fP\|(2), but many of the *BSD do not.
""")

d = _("""
Enable a window to show the buffer offset from \fIoffset\fP to \fIoffset+length\fP rather than from from \fI0\fP to \fIlength\fP, when the buffer is partially loaded.
Using \fI@offset:length\fP or \fI@offset\-(offset+length)\fP syntax right after the path allows partial buffer loading.
See \fBDOCUMENTATION\fP for details of the syntax.
""")

x = _("""
Enable a window to show the buffer size and current position in hexadecimal.
""")

o = _("""
Start the program with each buffer given by paths loaded in \fI<num>\fP windows, as long as the terminal has enough size to store the number of windows specified.
""")
o_metavar = _metavar("num")

O = _("""
Start the program with each buffer given by paths loaded in different windows, as long as the terminal has enough size to store the number of windows specified.
""")

bytes_per_line = _("""
Specify number of bytes printed per line.
The program prints \fI<bytes_per_line>\fP bytes for each line as long as the terminal has enough width to store bytes.
Available formats for \fI<bytes_per_line>\fP are digits, "max", "min" and "auto".
If this option isn't specified, the program assumes "auto" is specified.
Using "auto" sets the value to the maximum 2^N that fits in the terminal width.
""")
bytes_per_line_metavar = _metavar("bytes_per_line")

bytes_per_window = _("""
Specify number of bytes printed per window, based on the current number of bytes per line.
The program prints \fI<bytes_per_window>\fP bytes for each window as long as the terminal has enough size to store bytes.
Available formats for \fI<bytes_per_window>\fP are digits, "even" and "auto".
Specifying "even" doesn't specify the size of window, but makes all windows have the same size.
If this option isn't specified, the program assumes "auto" is specified.
Using "auto" sets the value to the maximum available that fits in the terminal size, based on the current number of bytes per line.
""")
bytes_per_window_metavar = _metavar("bytes_per_window")

terminal_height = _("""
Specify the terminal height.
The program uses \fI<terminal_height>\fP lines as long as the terminal has enough height to store lines.
This option is usually unnecessary as the program is able to retrieve the terminal height by default.
""")
terminal_height_metavar = _metavar("terminal_height")

terminal_width = _("""
Specify the terminal width.
The program uses \fI<terminal_width>\fP bytes for each line as long as the terminal has enough width to store the bytes.
This option is usually unnecessary as the program is able to retrieve the terminal width by default.
""")
terminal_width_metavar = _metavar("terminal_width")

fg = _("""
Specify foreground color of the terminal.
Available colors for \fI<color>\fP are "black", "blue", "cyan", "green", "magenta", "red", "white" and "yellow".
If neither this option nor \fB\-\-bg\fP option is specified, the program assumes "black" is specified.
""")
fg_metavar = _metavar("color")

bg = _("""
Specify background color of the terminal.
Available colors for \fI<color>\fP are "black", "blue", "cyan", "green", "magenta", "red", "white" and "yellow".
If neither this option nor \fB\-\-fg\fP option is specified, the program assumes "white" is specified.
""")
bg_metavar = _metavar("color")

simple = _("""
Use simplified status window format.
""")

command = _("""
Print the list of available editor commands and exit.
""")

sitepkg = _("""
Print Python's site\-package directory being used by the program and exit.
""")
