"""
brute_force.py
===============
 
A straightforward, unoptimized decomposition of n into four squares by
exhaustive search over decreasing candidate values. It is correct for
any non-negative integer, but its running time grows quickly with n, so
it is only practical for small-to-medium n (roughly up to 10**7 -- see
README.md for guidance).
 
Useful mainly as a simple, obviously-correct reference to sanity-check
the efficient algorithm in main.py.
"""
 
from typing import Tuple
from math import isqrt
 
 
def four_squares(n: int) -> Tuple[int, int, int, int]:
    """Decompose n as a sum of four integer squares, by exhaustive search.
 
    Returns (a, b, c, d) with a^2 + b^2 + c^2 + d^2 == n and a >= b >= c >= d.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
 
    a_max = isqrt(n)
    for x0 in range(a_max, -1, -1):
        r0 = n - x0 * x0
        b_max = isqrt(r0)
        for x1 in range(b_max, -1, -1):
            r1 = r0 - x1 * x1
            c_max = isqrt(r1)
            for x2 in range(c_max, -1, -1):
                r2 = r1 - x2 * x2
                x3 = isqrt(r2)
                if x3 * x3 == r2:
                    return x0, x1, x2, x3
 
    # Lagrange's theorem guarantees this is unreachable.
    raise ValueError(f"no decomposition found for n={n} (should not happen)")