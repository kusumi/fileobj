# Copyright (c) 2010-2016, Tomohiro Kusumi
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

from . import version

_ = version.get_version()

def get_project_url():
    return "https://sourceforge.net/projects/fileobj/"

def get_project_archive_url():
    return "https://downloads.sourceforge.net/project/fileobj/fileobj-{0}.{1}.{2}.tar.gz".format(*_)

def get_repository_url():
    return "https://github.com/kusumi/fileobj/"
    #return "https://github.com/kusumi/fileobj/tree/v{0}.{1}/".format(_[0], _[1])

def get_repository_archive_url():
    return "https://github.com/kusumi/fileobj/archive/v{0}.{1}.{2}.tar.gz".format(*_)

def get_readme_url():
    return "https://github.com/kusumi/fileobj/blob/v{0}.{1}/README.md".format(_[0], _[1])

def get_doc_url(s):
    return "https://github.com/kusumi/fileobj/blob/v{0}.{1}/doc/README.{2}.md".format(_[0], _[1], s)
