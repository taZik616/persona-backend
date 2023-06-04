import hashlib


def specialEncodePassword(code: str):
    # Не знаю почему но может в 1 раз выбросить ошибку
    try:
        res = hashlib.md5(code.encode('utf-8')).hexdigest()
        return res
    except:
        return hashlib.md5(code.encode('utf-8')).hexdigest()
