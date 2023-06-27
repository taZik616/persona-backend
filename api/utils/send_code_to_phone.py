import requests
from rest_framework.response import Response

from api.common_error_messages import SEND_VERIFY_ERROR
from environment import SMS_RU_API_KEY


def sendCodeToPhone(phoneNumber):
    smsResponse = requests.post(
        f'https://sms.ru/code/call?phone={phoneNumber}&ip=-1&api_id={SMS_RU_API_KEY}'
    )

    if smsResponse.status_code != 200:
        return Response({"error": SEND_VERIFY_ERROR}, status=400)

    dataSmsRu = smsResponse.json()
    status = dataSmsRu.get('status')
    code = dataSmsRu.get('code')
    print(code)
    if status != 'OK' or not code:
        return Response({"error": SEND_VERIFY_ERROR}, status=400)
    return {'code': code}
