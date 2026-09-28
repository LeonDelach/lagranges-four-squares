from typing import Tuple
import math


# def four_squares(n: int) -> Tuple[int, int, int, int]:

def isqrt(n):
    return int(math.isqrt(n))

def cornacchia(n):
    a = isqrt(n)
    if a * a == n:
        return a, 0
    b = a + 1
    while b * b <= n:
        a, b = b, int((n - a * a) ** 0.5)
        if a * a + b * b == n:
            return a, b
    return None

def sum_of_two_squares(n):
    if n == 0:
        return 0, 0
    if n % 4 == 3:
        return None
    while n % 2 == 0:
        n //= 2
    if n % 4 == 1:
        return cornacchia(n)
    for i in range(1, isqrt(n) + 1):
        if n % i == 0:
            j = n // i
            if i % 2 != j % 2:
                return cornacchia(n)
    return None

def sum_of_three_squares(n):
    if n == 0:
        return 0, 0, 0
    while n % 4 == 0:
        n //= 4
    if n % 8 == 7:
        return None
    for i in range(isqrt(n) + 1):
        result = sum_of_two_squares(n - i * i)
        if result:
            return i, result[0], result[1]
    return None

def four_squares(n):
    if n == 0:
        return 0, 0, 0, 0
    while n % 4 == 0:
        n //= 4
    if n % 8 == 7:
        s = isqrt(n // 8)
        return 1, 1, 1, 2 * s + 1
    result = sum_of_three_squares(n)
    if result:
        return result[0], result[1], result[2], 0
    s = isqrt(n)
    return sum_of_two_squares(n - s * s) + (s, 0)

    
    '''
    # If n is zero, return four zeros.
    if n == 0:
        return 0, 0, 0, 0
    
    if n == 1:
        return 1, 0, 0, 0

    limit = int(math.isqrt(n)) + 1 
    
    sum_squares = {}
    sum_set = set()
    
    sum_squares[0] = (0, 0)
    sum_set.add(0)
    
    sum_squares[1] = (0, 1)
    sum_set.add(1)
    
    i = 2
    while i < limit:
        s = i*i
        if n % s == 0:
            print("yes")
            recc = four_squares(n // s)
            return tuple([i*x for x in recc])
        else:
            sum_squares[s] = (0, i)
            sum_set.add(s)
            i = i + 1
    
    for i in range(limit-1):
        s_0 = i*i
        for j in range(i+1, limit):
            s_1 = j*j
            pair_sum = s_0 + s_1
            if pair_sum > n:
                break
            sum_squares[pair_sum] = (i, j)
            sum_set.add(pair_sum)
            remaining = n - pair_sum
            if remaining in sum_set:
                return i, j, sum_squares[remaining][0], sum_squares[remaining][1]

    print('error')
    return None
'''