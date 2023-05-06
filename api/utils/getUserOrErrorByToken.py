import jwt
from jwt.exceptions import DecodeError, InvalidTokenError
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from ..models import User


class AuthenticationError(Exception):
    def __init__(self, message):
        super().__init__(message)


def getUserOrErrorByToken(token: str):
    """
    Функция внутри себя декодирует токен и возвращает объект модели `User`
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY)

        userData = User.objects.get(userId=decoded_token['userId'])
        return userData

    except jwt.exceptions.InvalidSignatureError:
        raise AuthenticationError(
            'Для данного токена не был найден соответствущий пользователь')
    except User.DoesNotExist:
        raise AuthenticationError('Ошибка декодирования токена')
    except ImproperlyConfigured:
        raise AuthenticationError(
            'Не определено значение SECRET_KEY в настройках Django')
    except DecodeError:
        raise AuthenticationError('Ошибка декодирования токена')
    except InvalidTokenError:
        raise AuthenticationError('Токен имеет недопустимый тип')
