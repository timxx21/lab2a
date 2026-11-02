class RC4:
    def __init__(self, key: bytes):
        if not key:
            raise ValueError("Ключ не может быть пустым")
        if len(key) > 256:
            raise ValueError("Ключ должен быть не длиннее 256 байт")

        # KSA — инициализация S-блока
        self.S = list(range(256))
        j = 0
        key_len = len(key)

        for i in range(256):
            j = (j + self.S[i] + key[i % key_len]) & 0xFF
            self.S[i], self.S[j] = self.S[j], self.S[i]

        # Состояние генератора гаммы
        self.i = 0
        self.j = 0

    def _keystream_byte(self) -> int:
        self.i = (self.i + 1) & 0xFF
        self.j = (self.j + self.S[self.i]) & 0xFF
        self.S[self.i], self.S[self.j] = self.S[self.j], self.S[self.i]
        return self.S[(self.S[self.i] + self.S[self.j]) & 0xFF]

    def crypt(self, data: bytes) -> bytes:
        result = bytearray(len(data))
        for k in range(len(data)):
            result[k] = data[k] ^ self._keystream_byte()
        return bytes(result)

    def encrypt(self, plaintext: bytes) -> bytes:
        return self.crypt(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        return self.crypt(ciphertext)


if __name__ == "__main__":
    key = b"SecretKey"
    plaintext = b"aNdryha poLoZHil prod."

    cipher = RC4(key)
    encrypted = cipher.encrypt(plaintext)
    print(f"Исходный текст:   {plaintext}")
    print(f"Зашифрованный:    {encrypted.hex()}")

    cipher2 = RC4(key)
    decrypted = cipher2.decrypt(encrypted)
    print(f"Расшифрованный:   {decrypted}")
