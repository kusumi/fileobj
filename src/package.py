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

import distutils.sysconfig
import os
import pkgutil
import sys

from . import setting

_major, _minor = sys.version_info[:2]

try:
    if _major == 2:
        import __init__ as pkg
    else:
        import fileobj as pkg
except ImportError:
    pkg = None
    if setting.use_debug:
        raise

def get_paths():
    return tuple(x for x in __get_paths() if
        os.path.isdir(x))

def __get_paths():
    if pkg is None:
        dir = distutils.sysconfig.get_python_lib()
        return [os.path.join(dir, get_name())]
    elif hasattr(pkg, "__path__"):
        return pkg.__path__
    elif get_sites:
        return get_sites()
    else:
        return [os.path.dirname(pkg.__file__)]

def get_name():
    if pkg is None:
        return "fileobj"
    else:
        return pkg.__name__.rstrip(".__init__")

def get_prefix():
    return get_name() + '.'

def iter_package_name():
    for s in _pkg_name:
        yield s

def iter_module_name():
    for s in _mod_name:
        yield s

if (_major == 2 and _minor >= 7) or \
    (_major == 3 and _minor >= 2):
    import site
    def get_sites():
        return [os.path.join(dir, get_name())
            for dir in site.getsitepackages()]
else:
    get_sites = None

if (_major == 2 and _minor >= 7) or \
    (_major == 3 and _minor >= 1):
    import importlib
    def import_module(s):
        return importlib.import_module(s)
else:
    def import_module(s):
        if s.startswith(get_prefix()):
            i = len(get_prefix())
        else:
            i = 0
        return __import__(s[i:], globals(), locals(), [''])

try:
    _pkg_name = []
    _mod_name = []
    for loader, name, ispkg in pkgutil.walk_packages(
        get_paths(), get_prefix()): # sorted
        if ispkg:
            _pkg_name.append(name)
        else:
            _mod_name.append(name)
except:
    if setting.use_debug:
        raise
