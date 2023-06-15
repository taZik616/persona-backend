from rest_framework.response import Response
from rest_framework.decorators import api_view

from api.utils import getServerSettings
from api.common_error_messages import SETTINGS_ERROR


@api_view(['GET'])
def deliveryPrice(request):
    settings = getServerSettings()
    if not settings:
        return Response({'error': SETTINGS_ERROR}, status=400)
    return Response({'success': settings['delivery_cost_in_rub']})
