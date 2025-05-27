|platform|Q |A |
|:-------|:-|:-|
|-|Can not install due to missing *Python.h*.|Install *python3-devel*, *libpython3-dev*, etc via package manager.|
|-|A directory *${HOME}/.fileobj* is created.|Automatically created by *fileobj*.|
|-|Can not enter block visual mode via *CTRL-v*.|Some terminals require *CTRL-v CTRL-v*. Some terminals do not support it.|
|GNU Screen / tmux|Window frames are corrupted.|Try different *TERM* variable.|
|PuTTY|Window frames are corrupted.|Change *"Window -> Appearance"*.|
|PuTTY|Window frames are corrupted.|Change *"Window -> Translation"* to use *"Use font encoding"*.|
|PuTTY|Window frames are corrupted.|Try different *TERM* variable.|
|NetBSD|Can not install due to missing *_curses* module.|Install *py-curses*, etc via pkgsrc.|
|Windows 10|Can not install due to missing *_curses* module.|Install *windows-curses* via *pip install windows-curses*.|
|Windows 10|*CTRL-c* can not interrupt ongoing editor command.|Not supported.|
|WSL|Can not enter block visual mode via *CTRL-v*.|Not supported. See [https://github.com/microsoft/WSL/issues/2588](https://github.com/microsoft/WSL/issues/2588).|
|Windows Terminal|Can not enter block visual mode via *CTRL-v*.|Not supported.|
|Windows Terminal|Mouse events are ignored.|Not supported.|
