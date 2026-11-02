import struct

MASK = 0xFFFFFFFF


def generate_sbox(key_words):
    tt = [
        0x726a8f3b, 0xe69a3b5c, 0xd3c71fe5, 0xab3c73d2,
        0x4d3a8eb3, 0x0396d6e8, 0x3d4c2f7a, 0x9ee27cf3
    ]

    sbox = [0] * 257

    sbox[0], sbox[1], sbox[2], sbox[3] = key_words

    for p in range(4, 256):
        x = (sbox[p - 4] + sbox[p - 1]) & MASK
        sbox[p] = ((x >> 3) ^ tt[x & 7]) & MASK

    for p in range(23):
        sbox[p] = (sbox[p] + sbox[p + 89]) & MASK

    x = sbox[33]
    z = (sbox[59] | 0x01000001) & 0xff7fffff
    for p in range(256):
        x = ((x & 0xff7fffff) + z) & MASK
        sbox[p] = ((sbox[p] & 0x00ffffff) ^ x) & MASK

    sbox[256] = sbox[0]
    y = x & 0xFF

    for p in range(256):
        y = (sbox[p ^ y] ^ y) & 0xFF
        sbox[p], sbox[y] = sbox[y], sbox[p + 1]

    return sbox


def _M(x, y, sbox):
    w = (x + y) & MASK
    return ((w >> 8) ^ sbox[w & 0xFF]) & MASK


class WAKE:
    def __init__(self, key: bytes):
        if len(key) != 16:
            raise ValueError("Ключ должен быть 16 байт (128 бит)")

        k0, k1, k2, k3 = struct.unpack(">4I", key)
        self.sbox = generate_sbox([k0, k1, k2, k3])
        self.r3 = k0
        self.r4 = k1
        self.r5 = k2
        self.r6 = k3

    def _keystream_word(self, feedback=0):
        keystream = self.r6

        self.r3 = _M(self.r3, self.r6, self.sbox)
        self.r4 = _M(self.r4, self.r3, self.sbox)
        self.r5 = _M(self.r5, self.r4, self.sbox)
        self.r6 = _M(self.r6, self.r5 ^ feedback, self.sbox)

        return keystream

    def encrypt(self, plaintext: bytes) -> bytes:
        pad_len = (4 - len(plaintext) % 4) % 4
        data = plaintext + b'\x00' * pad_len

        result = bytearray()
        feedback = 0

        for i in range(0, len(data), 4):
            p_word = struct.unpack(">I", data[i:i + 4])[0]
            k_word = self._keystream_word(feedback)
            c_word = p_word ^ k_word
            feedback = c_word
            result.extend(struct.pack(">I", c_word))

        return bytes(result)

    def decrypt(self, ciphertext: bytes) -> bytes:
        if len(ciphertext) % 4 != 0:
            raise ValueError("Длина шифртекста должна быть кратна 4 байтам")

        result = bytearray()
        feedback = 0

        for i in range(0, len(ciphertext), 4):
            c_word = struct.unpack(">I", ciphertext[i:i + 4])[0]
            k_word = self._keystream_word(feedback)
            p_word = c_word ^ k_word
            feedback = c_word
            result.extend(struct.pack(">I", p_word))

        return bytes(result)


if __name__ == "__main__":
    key = b"0123456789abcdef"
    plaintext = b"andryha polozhil prod"

    cipher = WAKE(key)
    encrypted = cipher.encrypt(plaintext)
    print(f"Исходный текст:   {plaintext}")
    print(f"Зашифрованный:    {encrypted.hex()}")

    cipher2 = WAKE(key)
    decrypted = cipher2.decrypt(encrypted)
    print(f"Расшифрованный:   {decrypted}")