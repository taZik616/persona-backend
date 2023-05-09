import hashlib


def specialEncodePassword(code: str):
    return hashlib.md5(code.encode('utf-8')).hexdigest()
