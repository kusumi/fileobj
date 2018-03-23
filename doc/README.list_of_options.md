## List of options

        $ fileobj --help
        Usage: fileobj [options]... [paths]...
        
        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -R                    Use read-only mode.
          -B                    Use malloc(3) based buffer for regular files. Regular
                                files internally use mmap(2) based buffer by default,
                                and relies on mremap(2) when resizing (i.e. insertion
                                or deletion) the buffer. This option is used when the
                                system does not support mremap(2), but need to resize
                                the buffer for regular files.
          -d                    Show the buffer offset from offset to offset+length
                                rather than from from 0 to length, when the buffer is
                                partially loaded. Using @offset:length or
                                @offset-(offset+length) syntax right after the path
                                without space (i.e. /path/to/file@offset:length or
                                /path/to/file@offset-(offset+length)) allows partial
                                buffer loading. See DOCUMENTATION for details of the
                                syntax.
          -x                    Show the buffer size and current position in
                                hexadecimal.
          -o                    Start the program with each buffer given by paths in
                                horizontally splitted windows, as long as the terminal
                                has enough size to accommodate windows.
          -O                    Start the program with each buffer given by paths in
                                vertically splitted windows, as long as the terminal
                                has enough size to accommodate windows.
          --bytes_per_line=<bytes_per_line>, --bpl=<bytes_per_line>
                                Set fixed number of bytes printed per line. The
                                program prints <bytes_per_line> bytes for each line as
                                long as the terminal has enough width to accommodate.
                                Available formats for <bytes_per_line> are digit,
                                "max", "min" and "auto". If this option is not
                                specified, the program assumes "auto" is specified.
                                Using "auto" sets the value to the maximum 2^N that
                                fits in the terminal width.
          --bytes_per_window=<bytes_per_window>, --bpw=<bytes_per_window>
                                Set fixed number of bytes printed per window. The
                                program prints <bytes_per_window> bytes for each
                                window as long as the terminal has enough size to
                                accommodate. This option technically sets number of
                                lines printed per window, based on the number of bytes
                                per line which can also manually be specified by
                                --bytes_per_line option. Available formats for
                                <bytes_per_window> are digit, "even" and "auto".
                                Specifying "even" does not set fixed number of bytes,
                                but makes all windows have the same size when a new
                                window is vertically added. If this option is not
                                specified, the program assumes "auto" is specified.
          --fg=<color>          Set foreground color of the terminal. Available colors
                                for <color> are "black", "blue", "cyan", "green",
                                "magenta", "red", "white" and "yellow". If neither
                                this option nor --bg option is specified, the program
                                assumes "black" is specified. This option is not
                                supported on VT1xx and VT2xx terminals.
          --bg=<color>          Set background color of the terminal. Available colors
                                for <color> are "black", "blue", "cyan", "green",
                                "magenta", "red", "white" and "yellow". If neither
                                this option nor --fg option is specified, the program
                                assumes "white" is specified. This option is not
                                supported on VT1xx and VT2xx terminals.
          --verbose_window      Use verbose status window format instead of the
                                default one.
          --backup              Create backup files for regular files. The program
                                keeps consistency of backing files if it terminates
                                normally, but this option guarantees safety by
                                creating a copy of regular files before loading them.
                                Backup files are created under ~/.fileobj by default,
                                and removed if the program terminates normally. Backup
                                files start with '.'.
          --force               Ignore warnings which can be ignored by specifying
                                this option and proceed.
          --test_screen         Enter ncurses(3) screen test mode.
          --command             Print the list of available editor commands and exit.
          --sitepkg             Print Python's site-package directory being used by
                                the program and exit.
