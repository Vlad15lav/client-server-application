import random
from tools.tool import find_gcd
from tools.prime_test import solovay_strassen

# generate number where length is binary
def generate_number(length: int) -> int:
    return random.randint(pow(2, length - 1), pow(2, length) - 1)

# generate prime number
def generate_prime(length: int) -> int:
    n = generate_number(length)
    if n == 2: return n
    n += n % 2 == 0 # to odd

    while not solovay_strassen(n): n += 2
    return n

# generate public key
def generate_public(length: int, euler: int) -> int:
    e = generate_number(length)
    while find_gcd(e, euler) != 1: e += 1
    return e

# generate primitive root modulo p
def generate_primitive(length_g: int, length_p: int, count_div: int=4) -> tuple:
    fact = [2]
    p = 2
    for _ in range(count_div - 1):
        p_i = generate_prime(length_p // (count_div - 1))
        fact.append(p_i)
        p *= p_i
    
    while not solovay_strassen(p + 1):
        p //= fact[-1]
        fact[-1] = generate_prime(length_p // (count_div - 1))
        p *= fact[-1]
    p = p + 1
    size = len(fact)

    phi = p - 1
    g = generate_number(length_g)
    for res in range(g, p + 1):
        flag = True
        i = 0
        while i < size and flag:
            flag &= pow(res, phi // fact[i], p) != 1
            i += 1
        if flag: return res, p
    return -1, -1