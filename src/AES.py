from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from hashlib import pbkdf2_hmac


class AES():
    def __init__(self):
           pass

    def encrypt(self, payload: bytes, password: str):
            salt = get_random_bytes(16)
            key = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200000, dklen=32)

            cipher = AES.new(key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(payload)

            return salt, cipher.nonce, ciphertext, tag


    def decrypt(self, salt, nonce, ciphertext, tag, password):
        key = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200000, dklen=32)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)


