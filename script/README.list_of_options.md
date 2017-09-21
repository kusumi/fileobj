## List of options

        $ fileobj --help
        Usage: fileobj [options]... [paths]...
        
        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -R                    Use read-only mode.
          -B                    Use malloc\|(3) based buffer for regular files, which
                                may put pressure on the system depending on the file
                                size. Regular files use mmap\|(2) based buffer by
                                default, and relies on mremap\|(2) when resizing (i.e.
                                insert or delete bytes) the buffer. This option is
                                used when the system doesn't support mremap\|(2), but
                                need to resize the buffer for regular files. Linux
                                kernel has mremap\|(2), but many of the *BSD do not.
          -d                    Enable a window to show the buffer offset from offset
                                to offset+length rather than from from 0 to length,
                                when the buffer is partially loaded. Using
                                @offset:length or @offset-(offset+length) syntax right
                                after the path allows partial buffer loading. See
                                DOCUMENTATION for details of the syntax.
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
                                neither this option nor --bg option is specified, the
                                program assumes "black" is specified.
          --bg=<color>          Specify background color of the terminal. Available
                                colors for <color> are "black", "blue", "cyan",
                                "green", "magenta", "red", "white" and "yellow". If
                                neither this option nor --fg option is specified, the
                                program assumes "white" is specified.
          --simple              Use simplified status window format.
          --command             Print the list of available editor commands and exit.
          --sitepkg             Print Python's site-package directory being used by
                                the program and exit.
