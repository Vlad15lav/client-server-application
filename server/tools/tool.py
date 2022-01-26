# Find GCD
def find_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

# Fast Modular Exp
def fast_me(a: int, b: int, n: int) -> int:
    bin_b = list(bin(b).split('b')[-1])
    a_list = [a]
    for i in range(1, len(bin_b)):
        cur_a = a_list[i - 1]
        a_list.append((cur_a * cur_a * a) % n if int(bin_b[i]) \
                          else (cur_a * cur_a) % n)
    return a_list[-1]

# Euclidean Algorithm
def alg_euclid(A: int, B: int) -> [int, int]:
    # First four columns
    A_list, B_list, mod_list, div_list = [], [], [], []
    while A % B != 0:
        A_list.append(A)
        B_list.append(B)
        mod_list.append(A % B)
        div_list.append(A // B)

        A, B = B, mod_list[-1]
    A_list.append(A)
    B_list.append(B)
    mod_list.append(A % B)
    div_list.append(A // B)

    x, y = [0], [1]
    rows = len(div_list)
    for i in range(1, rows):
        x.append(y[i - 1])
        y.append(x[i - 1] - y[i - 1] * div_list[rows - i - 1])

    return B_list[-1], x[-1], y[-1]