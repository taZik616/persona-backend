import hashlib


def specialEncodePassword(code: str):
    return hashlib.md5(bytes(code, encoding="utf-8")).hexdigest()
