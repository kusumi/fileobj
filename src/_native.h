/*
 * Copyright (c) 2010-2017, Tomohiro Kusumi
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

#include <stdint.h>
#include <unistd.h>

typedef struct blkdev_info {
	uint64_t size;
	int sector_size;
	char label[64];
} blkdev_info_t;

#if defined __linux__
#include "./_linux.c"
#elif defined __NetBSD__
#include "./_netbsd.c"
#elif defined __OpenBSD__
#include "./_openbsd.c"
#elif defined __FreeBSD__
#include "./_freebsd.c"
#elif defined __DragonFly__
#include "./_dragonflybsd.c"
#elif defined __CYGWIN__
#include "./_cygwin.c"
#else
static int get_blkdev_info(const char *path, blkdev_info_t *b)
{
	return -1;
}
static int ptrace_cont(pid_t pid)
{
	return -1;
}
static int ptrace_kill(pid_t pid)
{
	return -1;
}
static int ptrace_attach(pid_t pid)
{
	return -1;
}
static int ptrace_detach(pid_t pid)
{
	return -1;
}
#endif
