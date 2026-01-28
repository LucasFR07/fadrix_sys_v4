import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AESTools:
    
    KEY_ALGORITHM = "AES"
    BLOCK_LENGTH = 128
    DEFAULT_CIPHER_ALGORITHM = "AES/CBC/PKCS5Padding"
    DEFAULT_IV_SEED = "space-station-de"
    IV_LENGTH = 16

    @staticmethod
    def encrypt(content, key, iv_seed=DEFAULT_IV_SEED):
        if not content or not key or not iv_seed:
            raise ValueError("text and key cannot be empty")

        try:
            content_bytes = content.encode("utf-8")
            iv_seed_bytes = iv_seed.encode("utf-8")
            if len(iv_seed_bytes) < AESTools.IV_LENGTH:
                raise ValueError("iv cannot be shorter than 16 bytes")
            iv_bytes = iv_seed_bytes[:AESTools.IV_LENGTH]

            cipher = AES.new(key.encode("utf-8")[:AESTools.IV_LENGTH], AES.MODE_CBC, iv_bytes)
            encrypted_bytes = cipher.encrypt(pad(content_bytes, AES.block_size))
            return base64.b64encode(encrypted_bytes).decode("utf-8")
        except Exception:
            return None

    @staticmethod
    def decrypt(content, key, iv_seed=DEFAULT_IV_SEED):
        if not content or not key:
            raise ValueError("Encrypted text and key cannot be empty")

        try:
            iv_seed_bytes = iv_seed.encode("utf-8")
            if len(iv_seed_bytes) < AESTools.IV_LENGTH:
                raise ValueError("iv cannot be shorter than 16 bytes")
            iv_bytes = iv_seed_bytes[:AESTools.IV_LENGTH]

            cipher = AES.new(key.encode("utf-8")[:AESTools.IV_LENGTH], AES.MODE_CBC, iv_bytes)
            decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(content)), AES.block_size)
            return decrypted_bytes.decode("ascii")
        except Exception:
            return None
