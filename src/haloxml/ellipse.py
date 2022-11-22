"""
Scripts to generate a polygon from an ellipse
"""
import math


def ellipse2polygon(a: float, b: float, n: int = 65) -> list[(float, float)]:
    """
    Generate n points at equal angles along an ellipse with major axis a and minor axis b
    :param a:
    :param b:
    :param n:
    :return:
    """
    angles = [0]
    for i in range(n - 1):
        angles.append(angles[-1] + 2 * math.pi / n)
    x = [a * math.cos(t) for t in angles]
    y = [b * math.sin(t) for t in angles]
    return list(zip(x, y))


def ellipse2polygon_eqd(a: float, b: float, n: int) -> list[(float, float)]:
    """
    Generate n points at approxmately equal distance along an ellipse with major axis a and minor axis b
    :param a: major axis
    :param b: minor axis
    :param n: aproximate nr of points
    :return:
    """
    c = approx_circumference(a, b)
    d = c / n
    dt = 2 * math.pi / (n * 100)
    t = 0
    s = 0
    points = [(a * math.cos(t), b * math.sin(t))]
    loc = points[0]
    while t < (2 * math.pi):
        t += dt
        nloc = (a * math.cos(t), b * math.sin(t))
        s += math.sqrt((nloc[0] - loc[0]) ** 2 + (nloc[1] - loc[1]) ** 2)
        loc = nloc
        if s > d:
            s = 0
            points.append(loc)
    return points


def approx_circumference(a: float, b: float) -> float:
    """
    Approximation by Matt Parker
    :param a: long axis
    :param b: short axis
    :return:
    """
    if a < b:
        return approx_circumference(b, a)
    else:
        return math.pi * (6 * a / 5 + 3 * b / 4)
