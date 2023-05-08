import phonenumbers


def validateAndFormatPhoneNumber(phoneNumber: str):
    try:
        # Костыль для того чтобы номера по типу 89878686862 принимались.
        # Если будут проблемы то можно удалить эти 2 строчки
        if phoneNumber.startswith('8'):
            phoneNumber = '+7' + phoneNumber[:0] + phoneNumber[0+1:]

        parsedPhoneNumber = phonenumbers.parse(phoneNumber, None)

        if not phonenumbers.is_valid_number(parsedPhoneNumber):
            raise Exception('Invalid number')

        # Проверяем, что номер телефона принадлежит валидной коду страны
        region_code = phonenumbers.region_code_for_number(parsedPhoneNumber)
        if not phonenumbers.is_valid_number_for_region(parsedPhoneNumber, region_code):
            raise Exception('Invalid phone number region')

        formattedPhoneNumber = phonenumbers.format_number(
            parsedPhoneNumber, phonenumbers.PhoneNumberFormat.E164)

        return {
            "success": True,
            "formattedPhoneNumber": formattedPhoneNumber
        }
    except:
        return {
            "success": False,
            "error": "Номер не прошел проверку корректности"
        }
