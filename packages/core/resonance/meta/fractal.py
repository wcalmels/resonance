"""Box-counting fractal dimension of a dependency graph adjacency matrix."""

from __future__ import annotations

import math


def fractal_dimension(matrix) -> float:
    """Estimate fractal dimension of the matrix support (occupied cells).

    Sparse isolated graphs → ~1.0. Dense integrated graphs → up to ~2.0.
    """
    n = matrix.shape[0] if hasattr(matrix, "shape") else 0
    if n < 2:
        return 1.0

    points = [
        (i, j)
        for i in range(n)
        for j in range(n)
        if float(matrix[i, j]) > 0
    ]
    if len(points) < 2:
        return 1.0

    xs, ys = zip(*points)
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    span = max(x_max - x_min + 1, y_max - y_min + 1, 1)

    log_inv_eps: list[float] = []
    log_counts: list[float] = []
    for div in (1, 2, 4, 8, 16):
        eps = max(span / div, 1.0)
        boxes: set[tuple[int, int]] = set()
        for x, y in points:
            boxes.add((int((x - x_min) / eps), int((y - y_min) / eps)))
        if not boxes:
            continue
        log_inv_eps.append(math.log(1.0 / eps))
        log_counts.append(math.log(len(boxes)))

    if len(log_inv_eps) < 2:
        return 1.0

    slope = _slope(log_inv_eps, log_counts)
    return round(max(1.0, min(2.0, slope)), 4)


def _slope(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    den = sum((x - x_mean) ** 2 for x in xs)
    if den == 0:
        return 1.0
    return num / den
