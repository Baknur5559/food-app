from passlib.context import CryptContext

# Настройка библиотеки для хеширования паролей (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли введенный пароль с хешем в БД"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Превращает пароль '123456' в кашу вроде '$2b$12$EixZa...'"""
    return pwd_context.hash(password)