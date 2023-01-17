# distutils: language=c++
from libcpp cimport bool

def pointinpoly(float[:] point, float[:] polygon):
    """
    Determines if a point is inside a polgyon
    :param point: float array of x,y
    :param polygon: float array of vertices x1,y1,x2,y2 etc.
    :return:
    """
    if point.shape[0] != 2:
        raise Exception("Point should have length 2")
    cdef int nvertex = polygon.shape[0]//2
    cdef float p1x,p2x,p1y,p2y
    cdef bool inside = False
    cdef int idx = 0
    p1x = polygon[0]
    p1y = polygon[1]
    for i in range(nvertex + 1):
        idx = (i % nvertex)*2
        p2x = polygon[idx]
        p2y = polygon[1+idx]
        if point[1] > min(p1y, p2y):
            if point[1] <= max(p1y, p2y):
                if point[0] <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (point[1] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or point[0] <= xints:
                        inside = not inside
        p1x = p2x
        p1y = p2y
    return inside
