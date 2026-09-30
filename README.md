# Lagranges Sum of Four Squares
https://www.codewars.com/kata/63022799acfb8d00285b4ea0

An efficient, constructive solution to the CodeWars kata "Sum of Four
Squares": given any non-negative integer `n`, find integers `a, b, c, d`
such that `a² + b² + c² + d² = n`. Guaranteed to exist by **Lagrange's
four-square theorem**, and the code here finds one directly — no
brute-force search — so it comfortably handles numbers with thousands
of bits (the kata tests up to `2^1024`).

## Files

| File | Contents |
|---|---|
| `main.py` | The efficient `four_squares(n)` and all of its helper functions. |
| `brute_force.py` | A simple, obviously-correct exhaustive-search `four_squares(n)`, for small `n` only — used as a sanity check, not as the real solution. |
| `test_solution.py` | Test suite, adapted from the kata's own CodeWars test file. Runs standalone or under `pytest`. |
| `notebook.ipynb` | Interactive playground: run the tests, call either solution on your own input, and time them. |

## Running things

```bash
# Run the test suite directly
python3 test_solution.py

# ...or with pytest
pytest test_solution.py -v
```

```python
# Use it directly
from main import four_squares
four_squares(106369249365575352836589875696130383747)
```

**Optional speed-up:** if [`gmpy2`](https://gmpy2.readthedocs.io/) is
installed, `main.py` automatically uses its compiled primality test
instead of the pure-Python fallback, which is noticeably faster for
very large inputs. Nothing else changes — it's a drop-in optimization,
not a requirement. Install it with `pip install gmpy2` if you want it;
the code works fine without it (CodeWars itself typically won't have
it available).

## Submitting to CodeWars

CodeWars expects the solution in a file conventionally imported as
`solution` (`from solution import four_squares`). Just paste the
contents of `main.py` into the CodeWars solution editor — the function
signature and behavior are exactly what the kata expects. The
`test_solution.py` here uses `from main import four_squares` purely
for local/offline testing.

---

## The approach, step by step

The naive approach — try every `a`, then every `b`, then every `c`,
hoping the remainder is a perfect square — is a brute-force search
whose cost grows with `n` itself. That's fine for small numbers (see
`brute_force.py`), but hopeless once `n` has hundreds or thousands of
digits.

The efficient approach instead **reduces** the problem through a chain
of classical number-theory results, each shrinking it further, until
we reach a sub-problem that has a fast, direct construction:

```
4 squares  →  3 squares  →  2 squares  →  DONE
   (n)          (m)          (p, prime)
```

### 1. Strip factors of 4

If `n = 4·m`, then a decomposition `m = w²+x²+y²+z²` immediately gives
one for `n`: `(2w)² + (2x)² + (2y)² + (2z)² = 4·(w²+x²+y²+z²) = n`. So we
divide out every factor of 4 up front, solve the smaller problem, and
multiply the answer back by the appropriate power of 2 at the end. This
is a free simplification — it doesn't just make the numbers smaller, it
also simplifies the residue-class bookkeeping in the next steps.

### 2. Legendre's three-square theorem

**Legendre's theorem**: an integer `m` is a sum of *three* squares
unless `m = 4^a·(8b+7)`. Since we've already stripped out every factor
of 4, the only case left to worry about is the simple one: `m ≡ 7
(mod 8)`. When that happens, we peel off one square (`x0²`, for a
carefully chosen `x0`) so the remainder escapes that bad residue class,
then only need to solve the *three*-square problem for what's left.

📖 [Wikipedia — Legendre's three-square theorem](https://en.wikipedia.org/wiki/Legendre%27s_three-square_theorem)

### 3. Why primes matter: Fermat's two-square theorem

**Fermat's theorem on sums of two squares**: an odd prime `p` can be
written as `p = s² + t²` if and only if `p ≡ 1 (mod 4)`. This is a
clean, constructive fact for *primes* specifically — general composite
numbers have no simple direct formula (it depends on their full prime
factorization). So the strategy for the three-square step is: don't
try to write the remaining number directly as two squares — instead
search for a way to peel off one more square so that what's left is
*(a small cofactor) × (a prime ≡ 1 mod 4)*, which we know how to handle.

📖 [Wikipedia — Fermat's theorem on sums of two squares](https://en.wikipedia.org/wiki/Fermat%27s_theorem_on_sums_of_two_squares)

### 4. Finding that prime: Miller–Rabin

We search over candidate values `x` for `k = m - x²`, checking whether
`k` (or `k/2`, if `k` is even) is `1` or a prime `≡ 1 (mod 4)`. Since
about one in every `ln(k)` numbers near `k` is prime, this search
succeeds quickly — but we need a *fast* primality test to make trying
many candidates cheap, especially for huge `k`.

**Miller–Rabin** is a probabilistic primality test based on Fermat's
little theorem: it picks random "witnesses" and checks an algebraic
property that composite numbers are very unlikely to satisfy. It runs
in `O(log³ k)`-ish time — fast even for 1000+ digit numbers — and with
enough rounds, the chance of a wrong answer is astronomically small
(about `4^-rounds`).

📖 [Wikipedia — Miller–Rabin primality test](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test)
📖 [Brilliant.org's more visual walkthrough](https://brilliant.org/wiki/miller-rabin-primality-test/)

### 5. Actually building the two squares: √(−1) and Cornacchia's algorithm

Knowing `p = s²+t²` *exists* isn't the same as knowing `s` and `t`. The
construction:

1. Find `x` with `x² ≡ -1 (mod p)`. This is possible precisely because
   `p ≡ 1 (mod 4)` — that residue condition is *why* it matters. We use
   Euler's criterion: pick any quadratic non-residue `q` mod `p` (found
   by trial), and `x = q^((p-1)/4) mod p` works directly.
2. Run the ordinary **Euclidean algorithm** on `(p, x)`, and simply
   stop early: the moment two consecutive remainders both drop to or
   below `√p`, those two remainders are `s` and `t`. This is
   **Cornacchia's algorithm** — the same GCD machinery from school,
   just halted at the right moment.

📖 [Wikipedia — Cornacchia's algorithm](https://en.wikipedia.org/wiki/Cornacchia%27s_algorithm) (has a worked example)

### 6. Combining pieces: the Brahmagupta–Fibonacci identity

The search in step 4 doesn't require `k` itself to be a prime ≡ 1 mod
4 — it's enough for `k` to be *twice* such a prime, or the prime
itself, or just `1`. To go from the prime's two-square decomposition to
`k`'s, we use:

```
(a² + b²)(c² + d²) = (ac + bd)² + (ad − bc)²
```

This identity says: if two numbers are each sums of two squares, so is
their product — with an explicit formula for the result. Since
`1 = 1²+0²` and `2 = 1²+1²` are trivially sums of two squares, this
lets us combine the prime's decomposition with the trivial cofactor
directly, without needing `k` itself to satisfy any residue condition.
(This sidesteps a fiddly bit of parity bookkeeping that earlier, more
manual versions of this algorithm needed.)

📖 [Wikipedia — Brahmagupta–Fibonacci identity](https://en.wikipedia.org/wiki/Brahmagupta%E2%80%93Fibonacci_identity)

### 7. Lagrange's four-square theorem

Finally, this is what guarantees the whole approach can't fail:
**Lagrange's four-square theorem** states that *every* non-negative
integer is a sum of four squares, no exceptions. Steps 1–6 are simply a
constructive proof of this fact, turned into an algorithm.

📖 [Wikipedia — Lagrange's four-square theorem](https://en.wikipedia.org/wiki/Lagrange%27s_four-square_theorem)

### Further reading

This overall technique (search for a prime via random/sequential
sampling + Miller–Rabin, then build up via Cornacchia and the
two-squares identity) is sometimes called the **Rabin–Shallit
algorithm**. Searching for that name will turn up lecture notes and
slides that present the full pipeline end to end, if you want a single
narrative tying every piece above together.
