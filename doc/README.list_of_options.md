## List of options

        $ fileobj --help
        usage: 
          fileobj [options]... [paths]...
          fileobj [options]... [paths[@offset:length]]...
          fileobj [options]... [paths[@offset-(offset+length)]]...
        
        options:
          -h, --help            show this help message and exit
          -R                    Use read-only mode.
          -B                    Use Python bytes based buffer for regular files. This
                                option is required to insert or delete bytes on some
                                platforms.
          -o [<number_of_windows>]
                                Initially assign buffers given by paths to
                                horizontally splitted windows. When
                                <number_of_windows> is omitted, assign one window for
                                each buffer.
          -O [<number_of_windows>]
                                Initially assign buffers given by paths to vertically
                                splitted windows. When <number_of_windows> is omitted,
                                assign one window for each buffer.
          --bytes_per_line <bytes_per_line>, --bpl <bytes_per_line>
                                Set number of bytes printed per line. Each line prints
                                <bytes_per_line> bytes. Available formats for
                                <bytes_per_line> are digit, "max", "min" and "auto".
                                "auto" sets the value to the maximum 2^N that fits in
                                the terminal width. Defaults to "auto".
          --bytes_per_window <bytes_per_window>, --bpw <bytes_per_window>
                                Set number of bytes printed per window. Each window
                                prints <bytes_per_window> bytes, using the current
                                number of bytes per line. Available formats for
                                <bytes_per_window> are digit, "even" and "auto".
                                "even" sets all windows to have the same size.
                                Defaults to "auto".
          --bytes_per_unit <bytes_per_unit>, --bpu <bytes_per_unit>
                                Set number of bytes printed per unit. Each unit prints
                                <bytes_per_unit> bytes. Defaults to "1".
          --no_text             Disable text window.
          --no_mouse            Disable mouse events.
          --no_color            Disable color for buffer contents.
          --force               Ignore warnings which can be ignored.
          --verbose             Enable verbose mode.
          --test_screen         Enter ncurses(3) screen test mode.
          --test_mouse          Enter ncurses(3) mouse test mode.
          --test_color          Enter ncurses(3) color test mode.
          --list_color          Print list of available screen colors and exit.
                                "r:g:b" format is printed if a terminal supports it.
          --env                 Print list of environment variables and exit.
          --command             Print list of editor commands and exit. Also see
                                :help.
          --sitepkg             Print python(1) site-package directory and exit.
          --md [<hash_algorithm>]
                                Print message digest of files using <hash_algorithm>
                                and exit. Defaults to "sha256".
          --blkcmp              Compare contents of files and exit.
          --blkdump [<dump_type>]
                                Print contents of files to stdout and exit. Available
                                options are "text" and "raw". Defaults to "text". If
                                multiple files are specified, this command assumes a
                                single concatenated file. To handle them separately,
                                append "x" to option string (e.g. "textx").
          --blkscan [<scan_type>]
                                Print file offsets of matched logical blocks and exit.
                                Available options are "zero", "nonzero", "ff",
                                "nonff", "<hash_algorithm>:<value>" and
                                "<hash_algorithm>". Defaults to "zero". If multiple
                                files are specified, this command assumes a single
                                concatenated file. To handle them separately, append
                                "x" to option string (e.g. "zerox").
          --lsblk               Print list of block devices and exit. This prints
                                character devices on some platforms.
          --version             show program's version number and exit
