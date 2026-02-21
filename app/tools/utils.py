import hashlib
import re


def hash_password(password: str) -> str:
    """Хэширует пароль с использованием алгоритма SHA-256.

    Преобразует строку пароля в байты с кодировкой UTF-8 и вычисляет
    хеш с помощью SHA-256. Результат возвращается в виде шестнадцатеричной строки.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def clean_text(text: str) -> str:
    """Очищает текст от markdown-разметки.

    Удаляет из строки все вхождения следующих символов разметки:
    жирный шрифт (**), курсив (*), заголовки (###, ##, #).
    """
    cleaned_text = re.sub(r"(\*\*|\*|###|##|#)", "", text)
    return cleaned_text
