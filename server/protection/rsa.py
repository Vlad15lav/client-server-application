from tools.gen import generate_prime, generate_number
from tools.tool import alg_euclid, find_gcd

class RSA:
    def __init__(self, bin_size: int=512):
        self.bin_size = bin_size
        self.__init_keys()

    def __init_keys(self):
        self.__p = generate_prime(self.bin_size)
        self.__q = generate_prime(self.bin_size)
        self.n = self.__p * self.__q

        self.__phi_n = (self.__p - 1) * (self.__q - 1)
        self.e = generate_number((len(bin(self.n)) - 2) // 3)
        while find_gcd(self.e, self.__phi_n) != 1: self.e += 1
        _, _, self.__d = alg_euclid(self.__phi_n, self.e)
        self.__d %= self.__phi_n

    def get_public(self) -> tuple:
        return self.e, self.n

    def encode(self, m: int) -> int:
        return pow(m, self.e, self.n)
    
    def decode(self, c: int) -> int:
        return pow(c, self.__d, self.n)