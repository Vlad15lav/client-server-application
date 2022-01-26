import random
from typing import Callable
from tools.tool import find_gcd

# Test Miller Rabin
def miller_rabin(n: int) -> bool:
    if n <= 1 or n == 4: return False
    if n <= 3: return True
    d = n - 1
    # find d: n - 1 = 2^t * d
    while not d % 2: d //= 2

    a = random.randint(2, n - 1)
    # first step
    x = pow(a, d, n)
    if x == 1 or x == n - 1: return True
    # second step
    while d != n - 1:
        x, d = pow(x, 2, n), d * 2
        if x == 1: return False
        if x == n - 1: return True
    return False