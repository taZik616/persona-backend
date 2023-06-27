from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Order
from api.serializers import OrderSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOwnOrders(request):
    try:
        orders = Order.objects.filter(user=request.user)
        return Response(OrderSerializer(orders, many=True).data)
    except:
        return Response({'error': 'Не удалось вернуть список ваших заказов'}, status=400)
