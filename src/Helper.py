import hashlib
import random



class Helper():
    def __init__(self):
        pass

    
    def pixel_order(self, arr_len, password):
        seed = int.from_bytes(hashlib.sha256(password.encode("utf-8")).digest(), 'big')
        rng = random.Random(seed)
        indices = list(range(arr_len))
        rng.shuffle(indices)
        return indices


    def bytes_to_bits(self, data: bytes):
        return [int(b) for byte in data for b in f"{byte:08b}"]


    def bits_to_bytes(self, bits):
        return bytes(int("".join(str(b) for b in bits[i:i+8]), 2)
                    for i in range(0, len(bits), 8))



