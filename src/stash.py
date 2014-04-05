# Copyright (c) 2010-2014, TOMOHIRO KUSUMI
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

import os
import shutil

from . import log
from . import path
from . import util

class TemporaryFile (object):
    def __init__(self, f, unlink=False):
        o = path.Path(f)
        self.__path = o.path
        self.__file = None
        if o.is_file:
            try:
                fd = util.open_temp_file()
                if self.__copy(self.__path, fd.name) != -1:
                    if unlink:
                        os.unlink(self.__path)
                    self.__file = fd
            except Exception as e:
                log.error(e)

    def __del__(self):
        self.cleanup()

    @property
    def name(self):
        if self.__file:
            return self.__file.name
        else:
            return ''

    def cleanup(self):
        if self.__file:
            self.__file = None
        else:
            return -1

    def restore(self):
        if self.__file:
            self.__copy(self.__file.name, self.__path)
            self.cleanup()
        else:
            return -1

    def __copy(self, src, dst):
        try:
            shutil.copyfile(src, dst)
            log.debug("Copy {0} -> {1}".format(src, dst))
            assert os.path.isfile(dst)
        except Exception as e:
            log.error(e)
            return -1
