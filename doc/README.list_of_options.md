## List of options

        $ fileobj --help
        usage: 
          fileobj [options]... [paths]...
          fileobj [options]... [paths[@offset:length]]...
          fileobj [options]... [paths[@offset-(offset+length)]]...
        
        optional arguments:
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
                                the terminal width. "auto" is used by default.
          --bytes_per_window <bytes_per_window>, --bpw <bytes_per_window>
                                Set number of bytes printed per window. Each window
                                prints <bytes_per_window> bytes, using the current
                                number of bytes per line. Available formats for
                                <bytes_per_window> are digit, "even" and "auto".
                                "even" sets all windows to have the same size. "auto"
                                is used by default.
          --bytes_per_unit <bytes_per_unit>, --bpu <bytes_per_unit>
                                Set number of bytes printed per unit. Each unit prints
                                <bytes_per_unit> bytes. "1" is used by default.
          --no_text             Disable text window.
          --no_mouse            Disable mouse events.
          --no_color            Disable color for buffer contents.
          --force               Ignore warnings which can be ignored.
          --test_screen         Enter ncurses(3) screen test mode.
          --list_color          Print list of available screen colors and exit.
          --env                 Print list of environment variables and exit.
          --command             Print list of editor commands and exit. Also see
                                :help.
          --sitepkg             Print python(1) site-package directory and exit.
          --version             show program's version number and exit
