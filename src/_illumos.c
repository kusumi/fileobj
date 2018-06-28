/*
 * Copyright (c) 2017, Tomohiro Kusumi
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <sys/dkio.h>

static int get_blkdev_info(const char *path, blkdev_info_t *b)
{
	int fd;
	struct dk_minfo dm;

	errno = 0;
	fd = open(path, O_RDONLY);
	if (fd == -1)
		return -errno;

	memset(b, 0, sizeof(*b));

	if (ioctl(fd, DKIOCGMEDIAINFO, &dm) == -1) {
		close(fd);
		return -errno;
	}

	b->size = ((uint64_t)dm.dki_capacity) * dm.dki_lbsize;
	b->sector_size = dm.dki_lbsize;

	close(fd);
	return 0;
}

/*
 * The ptrace() function is available only with the 32-bit version of
 * libc(3LIB). It is not available with the 64-bit version of this library.
 */
static long ptrace_peektext(pid_t pid, long long addr)
{
	return -EOPNOTSUPP;
}

static long ptrace_peekdata(pid_t pid, long long addr)
{
	return -EOPNOTSUPP;
}

static int ptrace_poketext(pid_t pid, long long addr, long data)
{
	return -EOPNOTSUPP;
}

static int ptrace_pokedata(pid_t pid, long long addr, long data)
{
	return -EOPNOTSUPP;
}

static int ptrace_attach(pid_t pid)
{
	return -EOPNOTSUPP;
}

static int ptrace_detach(pid_t pid)
{
	return -EOPNOTSUPP;
}

static int get_ptrace_word_size(void)
{
	return -1;
}
