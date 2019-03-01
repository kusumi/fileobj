## List of environment variables

        $ fileobj --env
        FILEOBJ_ADDRESS_RADIX    If set to "16", "10" or "8", show address in either hexadecimal, decimal or octal (equivalent to :set address). Defaults to "16" if undefined.
        FILEOBJ_BYTES_PER_LINE   Set number of bytes printed per line (equivalent to --bytes_per_line and :set bytes_per_line).
        FILEOBJ_BYTES_PER_UNIT   Set number of bytes printed per unit (equivalent to --bytes_per_unit and :set bytes_per_unit).
        FILEOBJ_BYTES_PER_WINDOW Set number of bytes printed per window (equivalent to --bytes_per_window and :set bytes_per_window).
        FILEOBJ_COLOR_CURRENT    Set current cursor and window color. Defaults to "black,green" if undefined. Set blank string to disable. Available colors are "black", "blue", "cyan", "green", "magenta", "red", "white", "yellow".
        FILEOBJ_COLOR_DEFAULT    Set default color for buffer contents. Defaults to "white" if undefined. Available colors are "black", "blue", "cyan", "green", "magenta", "red", "white", "yellow".
        FILEOBJ_COLOR_FF         Set color for 0xff bytes within buffer contents. Defaults to "magenta" if undefined. Set blank string to disable. Available colors are "black", "blue", "cyan", "green", "magenta", "red", "white", "yellow".
        FILEOBJ_COLOR_PRINT      Set color for printable bytes within buffer contents. Defaults to "cyan" if undefined. Set blank string to disable. Available colors are "black", "blue", "cyan", "green", "magenta", "red", "white", "yellow".
        FILEOBJ_COLOR_VISUAL     Set color for visual region. Defaults to "red,yellow" if undefined. Set blank string to disable. Available colors are "black", "blue", "cyan", "green", "magenta", "red", "white", "yellow".
        FILEOBJ_COLOR_ZERO       Set color for zero (0) bytes within buffer contents. Defaults to "green" if undefined. Set blank string to disable. Available colors are "black", "blue", "cyan", "green", "magenta", "red", "white", "yellow".
        FILEOBJ_ENDIANNESS       If set to "little" or "big", set endianness for multi-bytes data (equivalent to :set le and :set be). Defaults to host endian if undefined.
        FILEOBJ_USE_ASCII_EDIT   If defined, use ASCII edit mode (equivalent to :set ascii). Defaults to binary edit mode if undefined.
        FILEOBJ_USE_BACKUP       If defined, create backup files under ~/.fileobj. Backup files start with '.'. Only applies to regular files.
        FILEOBJ_USE_BYTES_BUFFER If defined, use Python bytes based buffer for regular files (equivalent to -B).
        FILEOBJ_USE_IGNORECASE   If defined, search operation is case-insensitive (equivalent to :set ic). Defaults to case-sensitive if undefined.
        FILEOBJ_USE_MOUSE_EVENTS If set to "false", do not use mouse events. Defaults to use mouse events if undefined.
        FILEOBJ_USE_READONLY     If defined, use read-only mode (equivalent to -R).
        FILEOBJ_USE_SIPREFIX     If defined, use 10^3(K) for kilo (equivalent to :set si). Defaults to 2^10(Ki) if undefined.
        FILEOBJ_USE_TEXT_WINDOW  If set to "false", do not use text window. Defaults to use text window if undefined.
        FILEOBJ_USE_UNIT_BASED   If defined, editor operations are on per unit basis where possible. Defaults to on per byte basis.
        FILEOBJ_USE_WRAPSCAN     If defined, search wraps around the end of the buffer (equivalent to :set ws). Defaults to no wrap around if undefined.
