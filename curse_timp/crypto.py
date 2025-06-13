from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import json
import os

class CryptoManager:
    def __init__(self):
        self.key_path = "data/keys"
        self._ensure_keys_exist()

    def _ensure_keys_exist(self):
        # Чек - RSA ключи существуют, если нет, то создаём новые
        if not os.path.exists(self.key_path):
            os.makedirs(self.key_path)
        
        if not os.path.exists(os.path.join(self.key_path, "private.pem")):
            key = RSA.generate(2048)
            with open(os.path.join(self.key_path, "private.pem"), "wb") as f:
                f.write(key.export_key())
            with open(os.path.join(self.key_path, "public.pem"), "wb") as f:
                f.write(key.publickey().export_key())

    def _get_keys(self):
        # Достаём RSA из файла
        with open(os.path.join(self.key_path, "private.pem"), "rb") as f:
            private_key = RSA.import_key(f.read())
        with open(os.path.join(self.key_path, "public.pem"), "rb") as f:
            public_key = RSA.import_key(f.read())
        return private_key, public_key

    def encrypt_data(self, data):
        # Энкрипт RSA + AES
        # Конвертируем в json
        json_data = json.dumps(data)
        data_bytes = json_data.encode()

        # Создаём рандомный AES ключ
        aes_key = get_random_bytes(32)  # 256 bits
        iv = get_random_bytes(16)  # Initialization vector

        # Энкрипт AES
        cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
        encrypted_data = cipher_aes.encrypt(pad(data_bytes, AES.block_size))

        # Энкрипт ключа AES с RSA
        _, public_key = self._get_keys()
        cipher_rsa = PKCS1_OAEP.new(public_key)
        encrypted_key = cipher_rsa.encrypt(aes_key)

        # Собираем всё в один энкрипт
        encrypted_package = {
            'encrypted_key': encrypted_key.hex(),
            'iv': iv.hex(),
            'encrypted_data': encrypted_data.hex()
        }

        return encrypted_package

    def decrypt_data(self, encrypted_package):
        # Дескрипт RSA + AES
        # Конвертируем в байты
        encrypted_key = bytes.fromhex(encrypted_package['encrypted_key'])
        iv = bytes.fromhex(encrypted_package['iv'])
        encrypted_data = bytes.fromhex(encrypted_package['encrypted_data'])

        # Дескрипт ключа AES с RSA
        private_key, _ = self._get_keys()
        cipher_rsa = PKCS1_OAEP.new(private_key)
        aes_key = cipher_rsa.decrypt(encrypted_key)

        # Дескрипт AES
        cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher_aes.decrypt(encrypted_data), AES.block_size)

        # Конвертируем обратно в Python
        return json.loads(decrypted_data.decode())

    def save_encrypted_file(self, filename, data):
        # Сохраняем в файл
        try:
            # Создаём директорию, если её нет
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Энкрипт
            encrypted_package = self.encrypt_data(data)
            
            # Сохраняем в файл
            with open(filename, "w") as f:
                json.dump(encrypted_package, f)
        except Exception as e:
            print(f"Error saving file {filename}: {str(e)}")
            raise

    def load_encrypted_file(self, filename):
        # Загрузка-дескрипт из файла
        try:
            if not os.path.exists(filename):
                return None
            
            with open(filename, "r") as f:
                content = f.read()
                if not content.strip():  # Проверяем, пустой ли файл
                    return None
                encrypted_package = json.loads(content)
            
            return self.decrypt_data(encrypted_package)
        except Exception as e:
            print(f"Error loading file {filename}: {str(e)}")
            return None 