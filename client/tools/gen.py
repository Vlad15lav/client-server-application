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