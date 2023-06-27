GENDER_MUST_BE = 'Поле gender должно быть ≪men≫ или ≪women≫'
ONLY_ADMIN = 'Вы не администратор'
SEND_VERIFY_ERROR = "На этот номер не удалось отправить звонок с кодом"
SETTINGS_ERROR = 'На сервере возникла проблема с настройками'


def translateError(err: str):
    if err == 'Enter a valid email address.':
        return 'Email адрес не прошел проверку'
    elif err == 'Ensure this field has no more than 40 characters.':
        return 'Убедитесь, что это поле содержит не более 40 символов.'
    else:
        return err
