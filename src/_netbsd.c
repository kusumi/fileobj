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
#include <sys/dkio.h>
#include <sys/disklabel.h>
#include <sys/ptrace.h>

static int get_blkdev_info(const char *path, blkdev_info_t *b)
{
	int fd, i;
	struct disklabel dl;

	fd = open(path, O_RDONLY);
	if (fd == -1)
		return -errno;

	memset(b, 0, sizeof(*b));
	memset(&dl, 0, sizeof(dl));

	if (ioctl(fd, DIOCGDINFO, &dl) == -1) {
		close(fd);
		return -errno;
	}

	b->size = ((uint64_t)dl.d_secperunit) * dl.d_secsize;
	b->sector_size = dl.d_secsize;
	strlcpy(b->label, dl.d_typename, sizeof(dl.d_typename));

	i = strlen(b->label);
	while (i > 0) {
		i--;
		if (b->label[i] == ' ')
			b->label[i] = '\0';
		else
			break;
	}

	close(fd);
	return 0;
}

static int get_ptrace_word_size(void)
{
	return (int)sizeof(int);
}

static long ptrace_peektext(pid_t pid, long long addr)
{
	int ret;

	ret = ptrace(PT_READ_I, pid, (void*)addr, 0);
	if (ret == -1)
		return -errno;

	return ret;
}

static long ptrace_peekdata(pid_t pid, long long addr)
{
	int ret;

	ret = ptrace(PT_READ_D, pid, (void*)addr, 0);
	if (ret == -1)
		return -errno;

	return ret;
}

static int ptrace_poketext(pid_t pid, long long addr, long data)
{
	if (ptrace(PT_WRITE_I, pid, (void*)addr, (int)data) == -1)
		return -errno;

	return 0;
}

static int ptrace_pokedata(pid_t pid, long long addr, long data)
{
	if (ptrace(PT_WRITE_D, pid, (void*)addr, (int)data) == -1)
		return -errno;

	return 0;
}

static int ptrace_cont(pid_t pid)
{
	if (ptrace(PT_CONTINUE, pid, (void*)1, 0) == -1)
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
