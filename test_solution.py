"""
test_solution.py
=================

Test suite for four_squares(), adapted from this kata's own CodeWars
test file so it can run standalone (`python3 test_solution.py`) or be
picked up by pytest (`pytest test_solution.py`).

STATIC_CASES and the validation logic below (type checks + sum check)
are taken directly from the kata's test file:

    from solution import four_squares

    @test.describe("Static tests")
    def static_tests():
        for i in [0, 1, 17, 33, 215, 333, 2**12-3, 1234567890,
                  106369249365575352836589875696130383747]:
            a, b, c, d = four_squares(i)
            ...
            if s != i: error_msg = ...
            if error_msg is not None: test.fail(error_msg)
            else: test.pass_()

Only the `test` object is different: CodeWars injects its own
`test.describe` / `test.it` / `test.pass_` / `test.fail` helpers, which
we stand in for locally with `_MockTest` so the exact same test logic
runs anywhere.
"""

import sys
import time

from main import four_squares

# Same values as the kata's own static test.
STATIC_CASES = [
    0, 1, 17, 33, 215, 333, 2 ** 12 - 3, 1234567890,
    106369249365575352836589875696130383747,
]


class _MockTest:
    """Minimal stand-in for the `test` object CodeWars injects."""

    def __init__(self):
        self.passes = 0
        self.failures = 0

    def describe(self, name):
        def decorator(fn):
            print(f"\n=== {name} ===")
            fn()
            return fn
        return decorator

    def it(self, name):
        def decorator(fn):
            print(f"-- {name}")
            fn()
            return fn
        return decorator

    def pass_(self):
        self.passes += 1
        print("   [PASS]")

    def fail(self, message):
        self.failures += 1
        print(f"   [FAIL] {message}")


def run_static_tests(func=four_squares, verbose: bool = True) -> bool:
    """Runs the kata's static test cases against `func`.

    Returns True if every case passed, False otherwise.
    """
    test = _MockTest()

    @test.describe("Static tests")
    def static_tests():
        for i in STATIC_CASES:
            t0 = time.perf_counter()
            a, b, c, d = func(i)
            elapsed_ms = (time.perf_counter() - t0) * 1000

            error_msg = None
            if type(a) is not int:
                error_msg = "1st square is not of type int"
            if type(b) is not int:
                error_msg = "2nd square is not of type int"
            if type(c) is not int:
                error_msg = "3rd square is not of type int"
            if type(d) is not int:
                error_msg = "4th square is not of type int"

            s = a * a + b * b + c * c + d * d
            if s != i:
                error_msg = (
                    f"Incorrect sum.\nSquares: [{a}, {b}, {c}, {d}]\n"
                    f"Actual: {s}\nExpected: {i}"
                )

            if verbose:
                print(f"n={i}  ->  ({a}, {b}, {c}, {d})  [{elapsed_ms:.2f} ms]")

            if error_msg is not None:
                test.fail(error_msg)
            else:
                test.pass_()

    print(f"\n{test.passes} passed, {test.failures} failed")
    return test.failures == 0


def test_four_squares_static():
    """pytest entry point: `pytest test_solution.py`."""
    assert run_static_tests(verbose=False)


if __name__ == "__main__":
    ok = run_static_tests()
    sys.exit(0 if ok else 1)