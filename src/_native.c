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
#include <Python.h>
#include <stdint.h>

typedef struct blkdev_info {
	uint64_t size;
	int sector_size;
	char label[64];
} *blkdev_info_t;

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
#else
static int __get_blkdev_info(const char *path, blkdev_info_t b)
{
	return -1;
}
#endif

static PyObject *get_blkdev_info(PyObject *self, PyObject *args)
{
	const char *path;
	struct blkdev_info b;
	int ret;

	if (!PyArg_ParseTuple(args, "s", &path))
		return NULL;

	ret = __get_blkdev_info(path, &b);
	if (ret) {
		PyErr_Format(PyExc_IOError, "Failed: %d", ret);
		return NULL;
	}

	return Py_BuildValue("lis", b.size, b.sector_size, b.label);
}

static PyMethodDef __methods[] = {
	{"get_blkdev_info", (PyCFunction)get_blkdev_info, METH_VARARGS, "",},
	{NULL, NULL, 0, NULL,},
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef __module = {
	PyModuleDef_HEAD_INIT,
	"_native",
	NULL,
	-1,
	__methods,
	NULL,
	NULL,
	NULL,
	NULL,
};

PyMODINIT_FUNC PyInit__native(void)
{
	PyObject *m = PyModule_Create(&__module);
	if (m == NULL)
		return NULL;
	return m;
}
#else
void init_native(void)
{
	Py_InitModule("_native", __methods);
}
#endif
