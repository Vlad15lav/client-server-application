import struct

class RC4:
    def __init__(self, key: int, n: int = 8):
        self.key = list(map(int, list(str(key))))
        self.n = n

        self.N = 2 ** n
        self.L = len(self.key)

        self.S = [b for b in range(self.N)]
        self.i = 0
        self.j = 0

        self.init_s()

    def init_s(self):
        j = 0
        for i in range(self.N):
            j = (j + self.S[i] + self.key[i % self.L]) % self.N
            self.S[i], self.S[j] = self.S[j], self.S[i]

    def encode(self, message: bytes) -> bytes:
        result = b''
        for m in message:
            self.i = (self.i + 1) % self.N
            self.j = (self.j + self.S[self.i]) % self.N
            self.S[self.i], self.S[self.j] = self.S[self.j], self.S[self.i]
            t = (self.S[self.i] + self.S[self.j]) % self.N
            K = self.S[t]
            result += struct.pack("B", m ^ K)
        return result