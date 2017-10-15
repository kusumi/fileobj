/*
 * Copyright (c) 2010-2016, Tomohiro Kusumi
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
#include <sys/diskslice.h>
#include <sys/ptrace.h>

static int get_blkdev_info(const char *path, blkdev_info_t *b)
{
	int fd;
	struct partinfo pi;

	fd = open(path, O_RDONLY);
	if (fd == -1)
		return -errno;

	memset(b, 0, sizeof(*b));
	memset(&pi, 0, sizeof(pi));

	if (ioctl(fd, DIOCGPART, &pi) == -1) {
		close(fd);
		return -errno;
	}

	b->size = pi.media_size;
	b->sector_size = pi.media_blksize;

	close(fd);
	return 0;
}

static int ptrace_cont(pid_t pid)
{
	if (ptrace(PT_CONTINUE, pid, (caddr_t)1, 0) == -1)
		return -errno;

	return 0;
}

static int ptrace_kill(pid_t pid)
{
	if (ptrace(PT_KILL, pid, NULL, 0) == -1)
		return -errno;

	return 0;
}

static int ptrace_attach(pid_t pid)
{
	if (ptrace(PT_ATTACH, pid, NULL, 0) == -1)
		return -errno;

	return 0;
}

static int ptrace_detach(pid_t pid)
{
	if (ptrace(PT_DETACH, pid, NULL, 0) == -1)
		return -errno;

	return 0;
}
