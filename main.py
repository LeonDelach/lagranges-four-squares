"""
main.py
=======
 
Efficient solution to the "Sum of Four Squares" kata.
 
Given any non-negative integer n, four_squares(n) returns integers
(a, b, c, d) such that a^2 + b^2 + c^2 + d^2 == n. Lagrange's four-square
theorem guarantees such a decomposition always exists; the algorithm
below constructs one directly, without brute-force search, so it stays
fast even for numbers with thousands of bits.
 
See README.md for a full explanation of the theory behind each step.
 
High-level pipeline
--------------------
1. Strip factors of 4 from n (scale the answer back up at the very end).
2. Handle Legendre's three-square exception (n == 7 mod 8) by peeling
   off one square.
3. Search for x such that k = n - x^2 reduces, after removing at most
   one factor of 2, to 1 or to a prime p == 1 (mod 4).
4. Build the two-square decomposition of k: get the prime's two-square
   decomposition via Cornacchia's algorithm, then combine it with the
   trivial decomposition of the cofactor (1 or 2) using the
   Brahmagupta-Fibonacci identity.
5. Undo the scaling from step 1.
"""
 
from typing import Tuple
from math import isqrt
 
# ---------------------------------------------------------------------------
# Primality testing
# ---------------------------------------------------------------------------
# We use gmpy2's `is_prime` when it's available: it's a compiled,
# highly optimized primality test that makes the whole algorithm
# noticeably faster on very large inputs. If gmpy2 isn't installed
# (e.g. plain CPython, or most CodeWars environments), we fall back to
# a pure-Python Miller-Rabin test with a small-prime trial-division
# pre-filter, which is plenty fast for this purpose.
 
try:
    from gmpy2 import is_prime as _gmpy_is_prime
 
    def is_probable_prime(n: int) -> bool:
        return bool(_gmpy_is_prime(n))
 
except ImportError:
    import random
 
    def _sieve(limit: int):
        is_p = bytearray([1]) * (limit + 1)
        is_p[0] = is_p[1] = 0
        for i in range(2, isqrt(limit) + 1):
            if is_p[i]:
                is_p[i * i::i] = bytearray(len(is_p[i * i::i]))
        return [i for i in range(2, limit + 1) if is_p[i]]
 
    _SMALL_PRIMES = _sieve(3000)
 
    def is_probable_prime(n: int, rounds: int = 25) -> bool:
        """Miller-Rabin primality test (probabilistic).
 
        With `rounds` random witnesses, the probability of misclassifying
        a composite number as prime is at most 4**-rounds (about 1e-15
        for the default of 25 rounds) -- safe for any practical purpose.
        """
        if n < 2:
            return False
        for p in _SMALL_PRIMES:
            if n == p:
                return True
            if n % p == 0:
                return False
        d, r = n - 1, 0
        while d % 2 == 0:
            d //= 2
            r += 1
        for _ in range(rounds):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n)
            if x in (1, n - 1):
                continue
            for _ in range(r - 1):
                x = x * x % n
                if x == n - 1:
                    break
            else:
                return False
        return True
 
 
# ---------------------------------------------------------------------------
# Sum of two squares, for a prime p == 1 (mod 4), or p == 2
# ---------------------------------------------------------------------------
 
def _sqrt_minus_one_mod(p: int) -> int:
    """Return x such that x^2 == -1 (mod p), for a prime p == 1 (mod 4).
 
    By Euler's criterion, a quadratic non-residue q satisfies
    q^((p-1)/2) == -1 (mod p). Since p == 1 (mod 4), (p-1)/4 is an
    integer, so x = q^((p-1)/4) satisfies x^2 == q^((p-1)/2) == -1.
    """
    for q in range(2, p):
        if pow(q, (p - 1) // 2, p) == p - 1:
            return pow(q, (p - 1) // 4, p)
    raise ValueError(f"no quadratic non-residue found for p={p} (is it prime?)")
 
 
def prime_to_two_squares(p: int) -> Tuple[int, int]:
    """Write p as s^2 + t^2, where p == 1, p == 2, or p is prime == 1 (mod 4).
 
    Uses Cornacchia's algorithm: run the Euclidean algorithm on
    (p, sqrt(-1) mod p) and take the first two remainders that drop to
    or below sqrt(p) -- those are s and t.
    """
    if p == 1:
        return (1, 0)
    if p == 2:
        return (1, 1)
 
    x = _sqrt_minus_one_mod(p)
    a, b = p, x
    sqrt_p = isqrt(p)
    remainders = []
    while len(remainders) < 2:
        if b <= sqrt_p:
            remainders.append(b)
        a, b = b, a % b
    return remainders[0], remainders[1]
 
 
def compose_two_squares(pair1: Tuple[int, int], pair2: Tuple[int, int]) -> Tuple[int, int]:
    """Brahmagupta-Fibonacci identity:
 
        (a^2 + b^2)(c^2 + d^2) = (ac + bd)^2 + (ad - bc)^2
 
    Combines two sum-of-two-squares decompositions into a decomposition
    of their product.
    """
    a, b = pair1
    c, d = pair2
    return a * c + b * d, abs(a * d - b * c)
 
 
# ---------------------------------------------------------------------------
# Sum of four squares
# ---------------------------------------------------------------------------
 
def four_squares(n: int) -> Tuple[int, int, int, int]:
    """Decompose n as a sum of four integer squares (Lagrange's theorem).
 
    Returns (a, b, c, d) with a^2 + b^2 + c^2 + d^2 == n.
    """
    if n == 0:
        return 0, 0, 0, 0
 
    # Step 1: strip factors of 4 (n = 4^k * n'); scale the answer back
    # up by 2^k at the end, since (2w)^2+(2x)^2+(2y)^2+(2z)^2 = 4*(w^2+..).
    scale = 1
    while n % 4 == 0:
        n //= 4
        scale *= 2
 
    result = []
 
    # Step 2: Legendre's three-square theorem excludes m == 4^a*(8b+7).
    # We've already removed every factor of 4, so a == 0 here -- the
    # only bad residue left to avoid is n == 7 (mod 8). Peel off one
    # square to escape it.
    if n % 8 == 7:
        x = isqrt(n)
        while (n - x * x) % 8 in (0, 4, 7):
            x -= 1
        result.append(x)
        n -= x * x
    else:
        result.append(0)
 
    # Step 3: search for x such that k = n - x^2 reduces (after removing
    # at most one factor of 2) to 1 or to a prime == 1 (mod 4).
    x = isqrt(n)
    while True:
        k = n - x * x
        k_odd_part = k // 2 if k % 2 == 0 else k
        if k_odd_part == 1 or (k_odd_part % 4 == 1 and is_probable_prime(k_odd_part)):
            break
        x -= 1
    result.append(x)
 
    # Step 4: build the two-square decomposition of k from the prime's
    # decomposition, combined with the trivial decomposition of the
    # cofactor (1 = 1^2+0^2, or 2 = 1^2+1^2) via Brahmagupta-Fibonacci.
    k = n - x * x
    k_odd_part = k // 2 if k % 2 == 0 else k
    cofactor = (1, 1) if k % 2 == 0 else (1, 0)
    two_squares = compose_two_squares(prime_to_two_squares(k_odd_part), cofactor)
    result.extend(two_squares)
 
    # Step 5: undo the scaling from step 1.
    a, b, c, d = (v * scale for v in result)
    return a, b, c, d