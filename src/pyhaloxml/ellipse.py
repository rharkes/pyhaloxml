"""
Scripts to generate a polygon from an ellipse
"""

import math


def ellipse2polygon(a: float, b: float, n: int = 65) -> list[tuple[float, float]]:
    """
    Generate n points at equal angles along an ellipse with major axis a and minor axis b
    :param a:
    :param b:
    :param n:
    :return:
    """
    angles = [0.0]
    for i in range(n - 1):
        angles.append(angles[-1] + 2 * math.pi / n)
    x = [a * math.cos(t) for t in angles]
    y = [b * math.sin(t) for t in angles]
    return list(zip(x, y))
