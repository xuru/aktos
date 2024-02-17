"""
Encryption utility functions and classes
"""
import base64
import hashlib
from random import SystemRandom

from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import modes
from django.conf import settings

AES_BLOCK_SIZE = 16


def generate_random_key(size=32):
    """Generate random key using SystemRandom (same as urandom wrapper)"""
    return SystemRandom().randbytes(size)


class AESCipher:
    """
    AES Cipher class, used to encrypt and decrypt strings
    """

    def __init__(self, key=None):
        key = key if key is not None else settings.SECRET_KEY
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, ciphertext):
        """
        Encrypt a string, and return the b64 encrypted string
        Args:
            ciphertext: The text to be encrypted

        Returns:
              b64 encrypted string
        """
        ciphertext = self._pad(ciphertext)
        rand_iv = generate_random_key(AES_BLOCK_SIZE)
        encryptor = Cipher(algorithms.AES(self.key), modes.CBC(rand_iv)).encryptor()
        cipher_text = encryptor.update(ciphertext.encode()) + encryptor.finalize()
        return base64.b64encode(rand_iv + cipher_text).decode("utf-8")

    def decrypt(self, ciphertext):
        """
        Decrypt a b64 encrypted string, using the encrypt method of this class
        Args:
            ciphertext: b64 encrypted string

        Returns:
              The original string
        """
        ciphertext = base64.b64decode(ciphertext.encode("utf-8"))
        rand_iv = ciphertext[:AES_BLOCK_SIZE]
        ciphertext = bytes(ciphertext[AES_BLOCK_SIZE:])
        decryptor = Cipher(algorithms.AES(self.key), modes.CBC(rand_iv)).decryptor()
        return self._unpad(decryptor.update(ciphertext) + decryptor.finalize()).decode(
            "utf-8",
        )

    @staticmethod
    def _pad(text):
        return text + (AES_BLOCK_SIZE - len(text) % AES_BLOCK_SIZE) * chr(
            AES_BLOCK_SIZE - len(text) % AES_BLOCK_SIZE,
        )

    @staticmethod
    def _unpad(text):
        return text[: -ord(text[len(text) - 1 :])]
