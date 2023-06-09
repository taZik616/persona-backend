import random

def randomCardCode():
    code_length = random.randint(4, 10)  # Случайная длина кода от 4 до 10
    code = ''.join(str(random.randint(0, 9)) for _ in range(code_length))
    return f'MOB{code}'
