import math
import random
 
# ---------------------------------------------------------------------------
# Primality testing (Miller-Rabin), with a wide trial-division pre-filter.
# For big random candidates, almost all composites get rejected by the cheap
# trial division below, so the expensive Miller-Rabin rounds only run on
# numbers that are already very likely prime. This lets us afford a large
# number of search attempts even for 1024/2048+ bit numbers.
# ---------------------------------------------------------------------------

def _sieve(limit):
    is_p = bytearray([1]) * (limit + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if is_p[i]:
            is_p[i * i::i] = bytearray(len(is_p[i * i::i]))
    return [i for i in range(2, limit + 1) if is_p[i]]
 
_SMALL_PRIMES = _sieve(3000)

def is_probable_prime(n, k=20):
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
    for _ in range(k):
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
# Tonelli-Shanks: sqrt(n) mod p, for prime p
# ---------------------------------------------------------------------------
 
def tonelli_shanks(n, p):
    if p == 2:
        return n % 2
    n %= p
    if n == 0:
        return 0
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    if s == 1:
        return pow(n, (p + 1) // 4, p)
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, temp = 0, t
        while temp != 1:
            temp = temp * temp % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r

# ---------------------------------------------------------------------------
# Cornacchia's algorithm: write prime p (p == 2 or p % 4 == 1) as s^2 + t^2
# ---------------------------------------------------------------------------
 
def cornacchia(p):
    if p == 2:
        return (1, 1)
    r1 = tonelli_shanks(p - 1, p)  # sqrt(-1) mod p, since -1 == p-1 (mod p)
    if (r1 * r1 + 1) % p != 0:
        r1 = p - r1
    r0 = p
    while r1 * r1 > p:
        r0, r1 = r1, r0 % r1
    s = r1
    t_sq = p - s * s
    t = math.isqrt(t_sq)
    return (s, t)
 

# ---------------------------------------------------------------------------
# Brute-force helpers, used only for small numbers where the parity/prime
# based construction has too few candidates to rely on statistically
# ---------------------------------------------------------------------------
 
SMALL_THRESHOLD = 10 ** 6  # tune as desired; brute force is instant below this

def brute_force_two_squares(p):
    a = math.isqrt(p)
    while a >= 0:
        rem = p - a * a
        b = math.isqrt(rem)
        if b * b == rem:
            return (a, b)
        a -= 1
    return None

def brute_force_three_squares(m):
    a = math.isqrt(m)
    for x1 in range(a, -1, -1):
        rem = m - x1 * x1
        r = brute_force_two_squares(rem)
        if r is not None:
            return (x1, r[0], r[1])
    return None

def brute_force_four_squares(n):
    a = math.isqrt(n)
    for x0 in range(a, -1, -1):
        r0 = n - x0 * x0
        b = math.isqrt(r0)
        for x1 in range(b, -1, -1):
            r1 = r0 - x1 * x1
            c = math.isqrt(r1)
            for x2 in range(c, -1, -1):
                r2 = r1 - x2 * x2
                x3 = math.isqrt(r2)
                if x3 * x3 == r2:
                    return (x0, x1, x2, x3)
    return None

# ---------------------------------------------------------------------------
# Three squares: reduce to "one prime p == 1 (mod 4), or p == 2" then
# Cornacchia. Key fix: p = m - x1^2 mod 4 is FORCED by x1's parity together
# with m's residue mod 4. If m == 3 (mod 4), p can only ever land on 2 or 3
# (mod 4) -- NEVER 1 -- so no amount of random search will ever find a
# usable prime. We therefore pick x1's parity deliberately so p == 1 (mod 4)
# is actually reachable, and we guarantee (in four_squares) that m is never
# == 3 (mod 4) in the first place.
# ---------------------------------------------------------------------------
 
def three_squares(m):
    if m == 0:
        return (0, 0, 0)

    k = 0
    mm = m
    while mm % 4 == 0:
        mm //= 4
        k += 1

    if mm <= SMALL_THRESHOLD:
        res = brute_force_three_squares(mm)
        if res is None:
            raise RuntimeError(f"no 3-square decomposition found for {mm}")
        return tuple(v << k for v in res)

    mm_mod4 = mm % 4
    if mm_mod4 == 3:
        # Should never happen: four_squares guarantees m != 3 (mod 4)
        # before calling us. If you call three_squares directly with such
        # an m, there may genuinely be no single-prime reduction available.
        raise RuntimeError(
            "three_squares invariant violated: m == 3 (mod 4) is not "
            "reducible via a single prime == 1 (mod 4)"
        )

    root = math.isqrt(mm)
    half = root // 2
    # Prime density near mm is ~ 1/ln(mm); scale attempts so the chance of
    # exhausting them without finding a usable prime is astronomically low
    # (roughly e^-40 per size class), even for numbers with thousands of bits.
    ln_mm = mm.bit_length() * 0.6931471805599453
    max_attempts = max(4000, int(40 * ln_mm))
    for _ in range(max_attempts):
        r = random.randint(0, half)
        x1 = 2 * r if mm_mod4 == 1 else 2 * r + 1
        if x1 > root:
            continue
        p = mm - x1 * x1
        if p <= 0:
            continue
        # by construction p % 4 == 1 always holds here; assert-style check:
        if p == 2 or (p % 4 == 1 and is_probable_prime(p)):
            a, b = cornacchia(p)
            return tuple(v << k for v in (x1, a, b))
    raise RuntimeError("three_squares: failed to find a prime candidate "
                        "(unexpected for large m)")


def is_3square_ok(m):
    """True iff m is expressible as a sum of 3 squares (Legendre)."""
    while m % 4 == 0:
        m //= 4
    return m % 8 != 7

# ---------------------------------------------------------------------------
# Four squares
# ---------------------------------------------------------------------------
 
def four_squares(n):
    if n == 0:
        return (0, 0, 0, 0)
    if n == 1:
        return (0, 0, 0, 1)
    if n <= SMALL_THRESHOLD:
        return brute_force_four_squares(n)

    k = 0
    while n % 4 == 0:
        n //= 4
        k += 1

    n_mod4 = n % 4
    # Choose x0's parity so that m = n - x0^2 is guaranteed to satisfy
    # m mod 4 in {1, 2} -- i.e. NEVER 3 (mod 4). This is what makes the
    # single-prime reduction in three_squares always solvable.
    #   n == 1 (mod 4): x0 even -> m == 1 (mod 4)            [good]
    #   n == 2 (mod 4): x0 even -> m == 2 (mod 4)            [good]
    #   n == 3 (mod 4): x0 odd  -> m == 2 (mod 4)            [good]
    x0 = 1 if n_mod4 == 3 else 0
    m = n - x0 * x0

    x1, a, b = three_squares(m)
    result = sorted([x0, x1, a, b])