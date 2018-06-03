## List of options

        $ fileobj --help
        usage: 
          fileobj [options]... [paths]...
          fileobj [options]... [paths[@offset:length]]...
          fileobj [options]... [paths[@offset-(offset+length)]]...
        
        optional arguments:
          -h, --help            show this help message and exit
          -R                    Use read-only mode.
          -B                    Use malloc(3) based buffer for regular files instead
                                of the default mmap(2) based buffer. This option is
                                required to resize (i.e. insert or delete) regular
                                files on platforms without mremap(2).
          -d                    Show the buffer offset from offset to offset+length
                                rather than from 0 to length, when the buffer is
                                partially loaded.
          -x                    Show the buffer size and current position in
                                hexadecimal.
          -o [<number_of_windows>]
                                Initially assign buffers given by paths to
                                horizontally splitted windows, if the terminal has
                                enough size. When <number_of_windows> is omitted,
                                assign one window for each buffer.
          -O [<number_of_windows>]
                                Initially assign buffers given by paths to vertically
                                splitted windows, if the terminal has enough size.
                                When <number_of_windows> is omitted, assign one window
                                for each buffer.
          --bytes_per_line <bytes_per_line>, --bpl <bytes_per_line>
                                Set fixed number of bytes printed per line. Each line
                                prints <bytes_per_line> bytes, if the terminal has
                                enough width. Available formats for <bytes_per_line>
                                are digit, "max", "min" and "auto". "auto" sets the
                                value to the maximum 2^N that fits in the terminal
                                width. "auto" is used by default.
          --bytes_per_window <bytes_per_window>, --bpw <bytes_per_window>
                                Set fixed number of bytes printed per window. Each
                                window prints <bytes_per_window> bytes, if the
                                terminal has enough size. This option sets number of
                                lines printed per window, based on the number of bytes
                                printed per line. Available formats for
                                <bytes_per_window> are digit, "even" and "auto".
                                "even" does not set a fixed number of bytes printed
                                per window, but makes all windows have the same size
                                when a new window is vertically added. "auto" is used
                                by default.
          --fg <color>          Set foreground color of the terminal. Available colors
                                for <color> are "black", "blue", "cyan", "green",
                                "magenta", "red", "white" and "yellow". "black" is
                                used by default. This option is not supported on VTxxx
                                terminal emulators.
          --bg <color>          Set background color of the terminal. Available colors
                                for <color> are "black", "blue", "cyan", "green",
                                "magenta", "red", "white" and "yellow". "white" is
                                used by default. This option is not supported on VTxxx
                                terminal emulators.
          --verbose_window      Use verbose status window instead of the default
                                format.
          --backup              Explicitly create backup files for regular files.
                                Backup files are created under ~/.fileobj when fileobj
                                starts, and removed when fileobj terminates. Backup
                                files start with '.'. This option only applies to
                                regular files.
          --force               Ignore warnings which can be ignored by specifying
                                this option.
          --test_screen         Enter ncurses(3) screen test mode.
          --command             Print list of editor commands and exit.
          --sitepkg             Print python(1) site-package directory and exit.
          --version             show program's version number and exit
