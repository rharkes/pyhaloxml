#include <Python.h>
#include <stdbool.h>

static PyObject* pointinpoly(PyObject* self, PyObject *args)
{
    PyObject* point;
    PyObject* polygon;
    PyArg_ParseTuple(args, "OO", &point, &polygon);
    PyList_Check(polygon);
    float pointx;
    float pointy;
    PyArg_ParseTuple(point, "ff", &pointx, &pointy);
    return Py_BuildValue("ff", pointx, pointy);

    // bool result = pointinpoly_c(point, polygon);
    // long output = result ? 1 : 0;

    // return PyBool_FromLong(output)
}

static PyMethodDef methods[] = {
    {"pointinpoly", (PyCFunction)pointinpoly, METH_VARARGS, "calculates if the point is in the polygon"},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "pointinpoly",
    NULL,
    -1,
    methods,
};

PyMODINIT_FUNC PyInit_pointinpoly(void)
{
    return PyModule_Create(&module);
}

bool pointinpoly_c(PyObject* point, PyObject* polygon) {
    PyObject* p1;  // polygon coordinate
    PyObject* p2;  // polygon coordinate
    int nvertices = PyList_Size(polygon);
    float xints = 0.0;
    bool inside = false;
    float p1x;
    float p1y;
    float p2x;
    float p2y;
    float pointx;
    float pointy;
    PyArg_ParseTuple(point, "ff", &pointx, &pointy);
    p1 = PyList_GetItem(polygon, 0);
    PyArg_ParseTuple(p1, "ff", &p1x, &p1y);
    for (int i = 1; i < nvertices; ++i){
        p2 = PyList_GetItem(polygon, i);
        PyArg_ParseTuple(p1, "ff", &p2x, &p2y);
        if (pointy > min(p1y, p2y)) {
            if (pointy <= max(p1y, p2y)) {
                if (pointx <= max(p1x,p2x)){
                    if (p1y != p2y){
                        xints = (pointy - p1y) * (p2x - p1x) / (p2y - p1y) + p1x;
                    }
                    if (p1x == p2x || pointx <= xints){
                        inside = !inside;
                    }
                }
            }
        }
        p1x = p2x;
        p1y = p2y;
    }
    return inside;
}
