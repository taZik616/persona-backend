from api.models.server_settings import ServerSettings

def getServerSettings():
    '''
    `sber_api_login`, `sber_api_password`, `sber_api_url`, `sms_ru_api_key`, `delivery_cost_in_rub`, `sber_api_payment_time_limit`
    '''
    settings = ServerSettings.objects.filter(isActive=True).first()
    if settings:
        return {
            'sber_api_login': settings.sber_api_login,
            'sber_api_password': settings.sber_api_password,
            'sber_api_url': settings.sber_api_url,
            'sms_ru_api_key': settings.sms_ru_api_key,
            'delivery_cost_in_rub': settings.delivery_cost_in_rub,
            'sber_api_payment_time_limit': settings.sber_api_payment_time_limit_sec,
        }
    else:
        return None