from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.common_error_messages import SETTINGS_ERROR
from api.utils import getServerSettings


@api_view(['GET'])
def deliveryPrice(request):
    settings = getServerSettings()
    if not settings:
        return Response({'error': SETTINGS_ERROR}, status=400)
    return Response(settings['delivery_cost_in_rub'])
