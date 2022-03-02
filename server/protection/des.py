import numpy as np
from bitarray import bitarray

# DES encrypt
class DES:
    def __init__(self, key: bytes):
        # const tables
        # IP table permutation
        self.IP = [58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4,
                  62, 54, 46, 38, 30, 22, 14, 6, 64, 56, 48, 40, 32, 24, 16, 8,
                  57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3,
                  61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7]
        # IP^-1 table permutation
        self.IP_inv = [40, 8, 48, 16, 56, 24, 64, 32, 39, 7, 47, 15, 55, 23, 63, 31,
                      38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21, 61, 29,
                      36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27,
                      34, 2, 42, 10, 50, 18, 58, 26, 33, 1, 41, 9, 49, 17, 57, 25]
        # E table expansion
        self.E = [32, 1, 2, 3, 4, 5,
                  4, 5, 6, 7, 8, 9,
                  8, 9, 10, 11, 12, 13,
                  12, 13, 14, 15, 16, 17,
                  16, 17, 18, 19, 20, 21,
                  20, 21, 22, 23, 24, 25,
                  24, 25, 26, 27, 28, 29,
                  28, 29, 30, 31, 32, 1]
        # S tables transformation
        self.S = [
            # S1
            [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
            [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
            [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
            [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
            ],
            # S2
            [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
            [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
            [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
            [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
            ],
            # S3
            [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
            [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
            [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
            [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
            ],
            # S4
            [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
            [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
            [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
            [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
            ],  
            # S5
            [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
            [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
            [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
            [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
            ], 
            # S6
            [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
            [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
            [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
            [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
            ], 
            # S7
            [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
            [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
            [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
            [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
            ],
            # S8         
            [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
            [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
            [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
            [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
            ]
        ]
        # P table permutation
        self.P = [16, 7, 20, 21, 29, 12, 28, 17,
                  1, 15, 23, 26, 5, 18, 31, 10,
                  2, 8, 24, 14, 32, 27, 3, 9,
                  19, 13, 30, 6, 22, 11, 4, 25]
        # tables for generation keys
        # CD permutation
        self.CD = [57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18,
                  10, 2, 59, 51, 43, 35, 27, 19, 11, 3, 60, 52, 44, 36,
                  63, 55, 47, 39, 31, 23, 15, 7, 62, 54, 46, 38, 30, 22,
                  14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 28, 20, 12, 4]
        # shift count for keys
        self.shift = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
        # CD compression
        self.CD_com = [14, 17, 11, 24, 1, 5, 3, 28, 15, 6, 21, 10, 23, 19, 12, 4,
                      26, 8, 16, 7, 27, 20, 13, 2, 41, 52, 31, 37, 47, 55, 30, 40,
                      51, 45, 33, 48, 44, 49, 39, 56, 34, 53, 46, 42, 50, 36, 29, 32]

        self.key = key
        self.round_keys = []
        self.n_byte = 8

        self.__init_table()
        self.__init_keys()
    
    # index processing for tables
    def __init_table(self):
        self.IP = (np.array(self.IP) - 1).tolist()
        self.IP_inv = (np.array(self.IP_inv) - 1).tolist()
        self.E = (np.array(self.E) - 1).tolist()
        self.P = (np.array(self.P) - 1).tolist()
        self.CD = (np.array(self.CD) - 1).tolist()
        self.CD_com = (np.array(self.CD_com) - 1).tolist()
    
    # calculate keys for 16 rounds
    def __init_keys(self):
        bits = bitarray()
        bits.frombytes(self.key)
        block = np.array(list(bits), dtype=bool)
        # CD permutation
        block = block[self.CD]
        # 16 rounds for keys
        for i in range(16):
            # left cyclic shift C and D
            block = np.concatenate((np.roll(block[:28], -self.shift[i]),
                                    np.roll(block[28:], -self.shift[i])))
            # compression to 48 bits and save round key
            self.round_keys.append(block[self.CD_com])

    # function feistal network
    def __feistel_func(self, block: np.array, key: np.array) -> np.array:
        # E expansion
        block = block[self.E]
        # XOR Key
        block = np.logical_xor(block, key)
        # S transfroms
        b_blocks = "".join(block.astype(int).astype(str).tolist())
        temp = ""
        for k, i in enumerate(range(0, 48, 6)):
            b = b_blocks[i:i + 6]
            row, col = int(b[0] + b[-1], 2), int(b[1:-1], 2)
            temp += bin(self.S[k][row][col])[2:].zfill(4)
        block = np.array(list(temp)).astype(int).astype(bool)
        # P permutation
        block = block[self.P]
        return block

    # one round feistal network
    def __feistel_net(self, L_block: np.array,
                            R_block: np.array,
                            key: np.array) -> tuple:

        return R_block.copy(), np.logical_xor(L_block,
                                              self.__feistel_func(R_block, key))

    # encode message
    def encode(self, message: bytes, forward=True) -> bytes:
        # add padding for bytes
        if forward:
            padding_length = self.n_byte - (len(message) % self.n_byte)
            message = message + padding_length * chr(padding_length).encode()

        result = b''
        for b in range(0, len(message), self.n_byte):
            # 8 byte block processing
            data = message[b:b + self.n_byte]
            bits = bitarray()
            bits.frombytes(data)
            data = np.array(list(bits), dtype=bool)
            # IP
            data = data[self.IP]
            # 16 rounds Feistel Network
            L_block, R_block = data[:32], data[32:]
            for i in range(16):
                if forward:
                    L_block, R_block = self.__feistel_net(L_block.copy(),
                                                          R_block.copy(),
                                                          self.round_keys[i])
                else:
                    R_block, L_block = self.__feistel_net(R_block.copy(),
                                                          L_block.copy(),
                                                          self.round_keys[15 - i])
            data = np.concatenate((L_block, R_block))
            # IP^-1
            data = data[self.IP_inv]
            # save block
            result += bytes(bitarray("".join(data.astype(int).astype(str).tolist())))
        
        # remove padding
        if not forward:
            result = result[:-result[-1]]
        return result