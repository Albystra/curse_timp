import hashlib
import os
from crypto import CryptoManager

class AuthManager:
    def __init__(self):
        self.crypto = CryptoManager()
        self.users_file = "data/users.json"
        self._ensure_data_dir()
        self._ensure_users_file()

    def _ensure_data_dir(self):
        # Создаём директорию, если её нет
        if not os.path.exists("data"):
            os.makedirs("data")

    def _ensure_users_file(self):
        # Создаём дефолт-файл, если его нет
        if not os.path.exists(self.users_file):
            initial_users = {
                "admin": {
                    "password": self._hash_password("admin"),
                    "role": "admin",
                    "first_name": "Admin",
                    "last_name": "User",
                    "father_name": "",
                    "group": "",
                    "subject": ""
                }
            }
            self.crypto.save_encrypted_file(self.users_file, initial_users)

    def _hash_password(self, password):
        # Хешируем пароль с SHA-256
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username, password):
        # Аутентификация
        users = self.crypto.load_encrypted_file(self.users_file)
        if not users or username not in users:
            return False, None
        
        if users[username]["password"] == self._hash_password(password):
            return True, users[username]["role"]
        return False, None

    def register_user(self, username, password, role):
        # Регистрация
        users = self.crypto.load_encrypted_file(self.users_file)
        if not users:
            users = {}
        
        if username in users:
            return False, "Такой логин уже существует."
        
        users[username] = {
            "password": self._hash_password(password),
            "role": role
        }
        
        self.crypto.save_encrypted_file(self.users_file, users)
        return True, "Пользователь успешно зарегистрирован."

    def change_password(self, username, old_password, new_password):
        # Смена пароля
        users = self.crypto.load_encrypted_file(self.users_file)
        if not users or username not in users:
            return False, "Не удалось найти пользователя."
        
        if users[username]["password"] != self._hash_password(old_password):
            return False, "Неверный старый пароль."
        
        users[username]["password"] = self._hash_password(new_password)
        self.crypto.save_encrypted_file(self.users_file, users)
        return True, "Пароль успешно изменён!"

    def get_all_users(self):
        # Список пользователей (админ)
        users = self.crypto.load_encrypted_file(self.users_file)
        if not users:
            return {}
        return {username: {"role": data["role"]} for username, data in users.items()}

    def delete_user(self, username):
        # Удаление пользователя (админ)
        users = self.crypto.load_encrypted_file(self.users_file)
        if not users or username not in users:
            return False, "Не удалось найти пользователя."
        
        del users[username]
        self.crypto.save_encrypted_file(self.users_file, users)
        return True, "Пользователь успешно удалён." 
