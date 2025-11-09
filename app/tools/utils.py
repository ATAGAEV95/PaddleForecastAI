import hashlib
import re


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def clean_text(text):
    """Очищает текст от markdown-стилей: **, *, ###, ##, #."""
    cleaned_text = re.sub(r"(\*\*|\*|###|##|#)", "", text)
    return cleaned_text
