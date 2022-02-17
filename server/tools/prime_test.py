import math
import random
from typing import Callable
from tools.tool import find_gcd, legendre

# test Solovay Strassen
def solovay_strassen(n: int) -> bool:
    if n == 2: return True
    if n % 2 == 0: return False

    for _ in range(int(math.log2(n))):
        a = random.randint(2, n - 1)
        d = find_gcd(a, n)

        if d > 1: return False
        if pow(a, (n - 1) // 2, n) != legendre(a, n) % n:
            return False
    return True