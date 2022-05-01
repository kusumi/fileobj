## List of commands

        $ fileobj --command
        <CTRL>a                Add [count] to the number at cursor
        <CTRL>b                Scroll window [count] pages backward in the buffer
        <CTRL>u                Scroll window [count] half pages backward in the buffer
        <CTRL>f                Scroll window [count] pages forward in the buffer
        <CTRL>d                Scroll window [count] half pages forward in the buffer
        <CTRL>g                Print current size and position
        g<CTRL>g               Print current size and position in sector for block device
        <CTRL>l                Refresh screen
        <CTRL>w+               Increase current window height [count] lines
        <CTRL>w-               Decrease current window height [count] lines
        <CTRL>wW               Change to the prev window
        <CTRL>wb               Change to the bottom window
        <CTRL>w<CTRL>b         Change to the bottom window
        <CTRL>ws               Split current window
        <CTRL>w<CTRL>s         Split current window
        <CTRL>wt               Change to the top window
        <CTRL>w<CTRL>t         Change to the top window
        <CTRL>wv               Split current window vertically
        <CTRL>w<CTRL>v         Split current window vertically
        <CTRL>ww               Change to the next window
        <CTRL>w<CTRL>w         Change to the next window
        <CTRL>x                Subtract [count] from the number at cursor
        <ESCAPE>               Clear input or escape from current mode
        "[0-9a-zA-Z"]          Use register {0-9a-zA-Z"} for next delete, yank or put (use uppercase character to append with delete and yank)
        &[0-9a-fA-F]{2}        Replace [count] bytes with bitwise and-ed bytes
        ^[0-9a-fA-F]{2}        Replace [count] bytes with bitwise xor-ed bytes
        |[0-9a-fA-F]{2}        Replace [count] bytes with bitwise or-ed bytes
        )                      Go to the next zero (\x00)
        (                      Go to the previous zero (\x00)
        [                      Start reading buffered [count] value
        ]                      End reading buffered [count] value
        {                      Go to the previous non zero character
        }                      Go to the next non zero character
        *                      Go to the next occurrence of the character under the cursor
        #                      Go to the previous occurrence of the character under the cursor
        .                      Repeat last change
        /                      Search forward
        ?                      Search backward
        0                      Go to the first character of the line
        $                      Go to the end of the line. If a count is given go [count]-1 lines downward
        :args                  Print buffer list with the current buffer in brackets
        :argv                  Print arguments of this program
        :auto                  Optimize editor window size based on the current terminal size
        :bfirst                Go to the first buffer in buffer list
        :brewind               Go to the first buffer in buffer list
        :bind                  Run/bind given :command in argument, replayable with @:
        :blake2b               Print blake2b message digest of the current buffer
        :blake2s               Print blake2s message digest of the current buffer
        :blast                 Go to the last buffer in buffer list
        :bnext                 Change buffer to the next
        <TAB>                  Change buffer to the next
        :bprevious             Change buffer to the previous
        :bNext                 Change buffer to the previous
        :bufsiz                Print temporary buffer size
        :close                 Close current window
        <CTRL>wc               Close current window
        :cmp                   Compare two buffers and go to the first non matching byte
        :cmp!                  Compare two buffers and go to the first matching byte
        :cmpnext               Compare two buffers starting from the next byte and go to the first non matching byte
        :cmpnext!              Compare two buffers starting from the next byte and go to the first matching byte
        :cmpr                  Compare two buffers from the end and go to the first non matching byte
        :cmpr!                 Compare two buffers from the end and go to the first matching byte
        :cmprnext              Compare two buffers starting from the previous byte and go to the first non matching byte
        :cmprnext!             Compare two buffers starting from the previous byte and go to the first matching byte
        :date                  Print date
        :delmarks              Delete the specified marks
        :delmarks!             Delete all marks for the current buffer except for uppercase marks
        :e                     Open a buffer
        :bdelete               Close a buffer
        :extensions            Show list of extensions
        :fobj                  Print Python object name of the current buffer
        :help                  Show list of commands
        :hostname              Print hostname
        :kmod                  Print Python module name for the platform OS
        :lang                  Print locale type
        :md5                   Print md5 message digest of the current buffer
        :meminfo               Print free/total physical memory
        :only                  Make the current window the only one
        <CTRL>wo               Make the current window the only one
        <CTRL>w<CTRL>o         Make the current window the only one
        :open_base16_decode    Open base16 decoded buffer of the current buffer
        :open_base16_encode    Open base16 encoded buffer of the current buffer
        :open_base32_decode    Open base32 decoded buffer of the current buffer
        :open_base32_encode    Open base32 encoded buffer of the current buffer
        :open_base64_decode    Open base64 decoded buffer of the current buffer
        :open_base64_encode    Open base64 encoded buffer of the current buffer
        :open_base85_decode    Open base85 decoded buffer of the current buffer
        :open_base85_encode    Open base85 encoded buffer of the current buffer
        :open_blake2b          Open blake2b message digest of the current buffer
        :open_blake2s          Open blake2s message digest of the current buffer
        :open_md5              Open md5 message digest of the current buffer
        :open_sha1             Open sha1 message digest of the current buffer
        :open_sha224           Open sha224 message digest of the current buffer
        :open_sha256           Open sha256 message digest of the current buffer
        :open_sha384           Open sha384 message digest of the current buffer
        :open_sha3_224         Open sha3_224 message digest of the current buffer
        :open_sha3_256         Open sha3_256 message digest of the current buffer
        :open_sha3_384         Open sha3_384 message digest of the current buffer
        :open_sha3_512         Open sha3_512 message digest of the current buffer
        :open_sha512           Open sha512 message digest of the current buffer
        :osdep                 Print OS dependent information
        :platform              Print platform
        :pwd                   Print the current directory name
        :q                     Close current window if more than 1 windows exist else quit program
        <CTRL>wq               Close current window if more than 1 windows exist else quit program
        :q!                    Close current window if more than 1 windows exist else quit program without writing
        ZQ                     Close current window if more than 1 windows exist else quit program without writing
        :qa                    Close all windows and quit program
        :qa!                   Close all windows and quit program without writing
        :screen                Print screen information
        :sector                Print sector size for block device
        :self                  Print current console instance string
        :set                   Set option
            address            Set address radix to {16,10,8}
            status             Set buffer size and current position radix to {16,10,8}
            binary             Set binary edit mode (unset ascii edit mode)
            ascii              Set ascii edit mode (unset binary edit mode)
            bytes_per_line     Set bytes_per_line to {[0-9]+,"max","min","auto"}
            bpl                Set bytes_per_line to {[0-9]+,"max","min","auto"}
            bytes_per_unit     Set bytes_per_unit to {"1","2","4","8"}
            bpu                Set bytes_per_unit to {"1","2","4","8"}
            bytes_per_window   Set bytes_per_window to {[0-9]+,"even","auto"}
            bpw                Set bytes_per_window to {[0-9]+,"even","auto"}
            ic                 Set ic mode (ignore the case of alphabets on search)
            noic               Unset ic mode
            le                 Set endianness to little (unset big endian if set)
            be                 Set endianness to big (unset little endian if set)
            si                 Set SI prefix mode (kilo equals 10^3)
            nosi               Unset SI prefix mode (kilo equals 2^10)
            ws                 Set wrapscan mode (search wraps around the end of the buffer)
            nows               Unset wrapscan mode
        :sha1                  Print sha1 message digest of the current buffer
        :sha224                Print sha224 message digest of the current buffer
        :sha256                Print sha256 message digest of the current buffer
        :sha384                Print sha384 message digest of the current buffer
        :sha3_224              Print sha3_224 message digest of the current buffer
        :sha3_256              Print sha3_256 message digest of the current buffer
        :sha3_384              Print sha3_384 message digest of the current buffer
        :sha3_512              Print sha3_512 message digest of the current buffer
        :sha512                Print sha512 message digest of the current buffer
        :split                 Split current window
        :term                  Print terminal type
        :truncate              Truncate the current buffer to a specified length
        :version               Print version
        :vsplit                Split current window vertically
        :w                     Write the whole buffer to the file
        :w!                    Like :w, but overwrite an existing file
        :wq                    Write the current file and quit
        :x                     Like :wq, but write only when changes have been made
        ZZ                     Like :wq, but write only when changes have been made
        ;                      Repeat the latest character search
        ,                      Repeat the latest character search toward backward
        >>                     Rotate [count] bits to right
        <<                     Rotate [count] bits to left
        @:                     Execute the binded command
        @[0-9a-zA-Z]           Execute the contents of register [count] times
        @@                     Execute the previous @ command [count] times
        D                      Delete characters under the cursor until the end of buffer
        G                      Go to line [count] (default last line)
        gg                     Go to line [count] (default first line)
        H                      Go to line [count] from top of window
        L                      Go to line [count] from bottom of window
        M                      Go to the middle line of window
        N                      Repeat the latest search toward backward
        n                      Repeat the latest search
        O                      Replace the text befor the cursor [count] times
        o                      Replace the text after the cursor [count] times
        P                      Put the text before the cursor [count] times
        p                      Put the text after the cursor [count] times
        X                      Delete [count] characters before the cursor
        Y                      Yank characters under the cursor until the end of buffer
        y                      Yank [count] characters
        d                      Disassemble buffer at current position
        f?                     Search character forward
        F?                     Search character backward
        go                     Go to [count] byte in the buffer (default first byte)
        i                      Start insert edit mode
        A                      Start append edit mode at the end of buffer
        I                      Start insert edit mode at the first byte of buffer
        R                      Start replace edit mode
        a                      Start append edit mode
        cw                     Delete [count] characters under the cursor and start insert edit mode
        cW                     Delete [count] characters under the cursor and start insert edit mode
        r                      Replace [count] characters under the cursor
        m[0-9a-zA-Z]           Set mark at cursor position, uppercase marks are valid between buffers
        `[0-9a-zA-Z]           Go to marked position
        q[0-9a-zA-Z]           Record typed characters into register
        q                      Stop recording
        s$                     Go to the end of the sector. If a count is given go [count]-1 sectors downward
        s0                     Go to the first character of the sector
        sb                     Swap byte order of [count] characters
        sgo                    Go to [count] sector in the buffer (default first sector)
        sh                     Go [count] sectors to the left
        s<BACKSPACE2>          Go [count] sectors to the left
        s<BACKSPACE>           Go [count] sectors to the left
        sl                     Go [count] sectors to the right
        s<SPACE>               Go [count] sectors to the right
        t?                     Search character forward until before occurrence
        T?                     Search character backward until before occurrence
        u                      Undo changes
        <CTRL>r                Redo changes
        :redo_all              Redo all changes
        U                      Undo all changes
        v                      Start/End visual mode
        <CTRL>v                Start/End block visual mode
        V                      Start/End line visual mode
        w                      Go to the next printable character
        b                      Go to the previous printable character
        ~                      Switch case of the [count] characters under and after the cursor
        <DOWN>                 Go [count] lines downward
        <ENTER>                Go [count] lines downward
        j                      Go [count] lines downward
        <UP>                   Go [count] lines upward
        k                      Go [count] lines upward
        <LEFT>                 Go [count] characters to the left
        h                      Go [count] characters to the left
        <BACKSPACE2>           Go [count] characters to the left
        <BACKSPACE>            Go [count] characters to the left
        <RIGHT>                Go [count] characters to the right
        <SPACE>                Go [count] characters to the right
        l                      Go [count] characters to the right
        <DELETE>               Delete [count] characters under and after the cursor
        x                      Delete [count] characters under and after the cursor
        <MOUSE_CLICKED>        Move cursor to clicked position in the window
        <MOUSE_PRESSED>        Start visual mode or start visual scroll (if already in visual mode) followed by <MOUSE_RELEASED> event
        <MOUSE_RELEASED>       Set visual area in the window
        <MOUSE_DOUBLE_CLICKED> Start line visual mode or exit visual mode (if already in visual mode)
        <MOUSE_TRIPLE_CLICKED> Start block visual mode or exit visual mode (if already in visual mode)
