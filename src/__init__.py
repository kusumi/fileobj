import os
import sys

if sys.argv and (os.path.basename(sys.argv[0])
    not in ("fileobj", "profile")):
    # is running outbox
    def alloc(f, name=''):
        from . import fileops
        return fileops.alloc(f, name)
