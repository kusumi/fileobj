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
#include <string.h>
#include "./_native.h"

#define PYERR_FORMAT(exception, ret)	\
	PyErr_Format(exception, "%s: %s", __func__, strerror(-ret))

static PyObject *__get_blkdev_info(PyObject *self, PyObject *args)
{
	const char *path;
	struct blkdev_info b;
	int ret;

	if (!PyArg_ParseTuple(args, "s", &path))
		return NULL;

	ret = get_blkdev_info(path, &b);
	if (ret) {
		PYERR_FORMAT(PyExc_IOError, ret);
		return NULL;
	}

	return Py_BuildValue("lis", b.size, b.sector_size, b.label);
}

static PyObject *__ptrace_cont(PyObject *self, PyObject *args)
{
	pid_t pid;
	int ret;

	if (!PyArg_ParseTuple(args, "i", &pid))
		return NULL;

	ret = ptrace_cont(pid);
	if (ret) {
		PYERR_FORMAT(PyExc_IOError, ret);
		return NULL;
	}

	return Py_BuildValue("i", ret);
}

static PyObject *__ptrace_kill(PyObject *self, PyObject *args)
{
	pid_t pid;
	int ret;

	if (!PyArg_ParseTuple(args, "i", &pid))
		return NULL;

	ret = ptrace_kill(pid);
	if (ret) {
		PYERR_FORMAT(PyExc_IOError, ret);
		return NULL;
	}

	return Py_BuildValue("i", ret);
}

static PyObject *__ptrace_attach(PyObject *self, PyObject *args)
{
	pid_t pid;
	int ret;

	if (!PyArg_ParseTuple(args, "i", &pid))
		return NULL;

	ret = ptrace_attach(pid);
	if (ret) {
		PYERR_FORMAT(PyExc_IOError, ret);
		return NULL;
	}

	return Py_BuildValue("i", ret);
}

static PyObject *__ptrace_detach(PyObject *self, PyObject *args)
{
	pid_t pid;
	int ret;

	if (!PyArg_ParseTuple(args, "i", &pid))
		return NULL;

	ret = ptrace_detach(pid);
	if (ret) {
		PYERR_FORMAT(PyExc_IOError, ret);
		return NULL;
	}

	return Py_BuildValue("i", ret);
}

static PyMethodDef __methods[] = {
	{"get_blkdev_info", (PyCFunction)__get_blkdev_info, METH_VARARGS, "",},
	{"ptrace_cont", (PyCFunction)__ptrace_cont, METH_VARARGS, "",},
	{"ptrace_kill", (PyCFunction)__ptrace_kill, METH_VARARGS, "",},
	{"ptrace_attach", (PyCFunction)__ptrace_attach, METH_VARARGS, "",},
	{"ptrace_detach", (PyCFunction)__ptrace_detach, METH_VARARGS, "",},
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
