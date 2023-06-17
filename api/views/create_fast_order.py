import re
import requests
from api.common_error_messages import SETTINGS_ERROR

from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.utils import selectAllFromProducts, getServerSettings, validateAndFormatPhoneNumber
from api.models import ProductVariant, FastOrder
from api.views.check_order_status import checkOrderStatusAndUpdateStateTask
from api.serializers import ProductSerializer, ProductVariantSerializer

@api_view(['POST'])
def createFastOrder(request):
    productVariantId = request.data.get('productVariantId')
    address = request.data.get('address')
    phoneNumber = request.data.get('phoneNumber')
    name = request.data.get('name')

    if not address:
        return Response({'error': 'Укажите адрес на который нужно отправить заказ'}, status=400)
    if not productVariantId:
        return Response({'error': 'Укажите товар который хотите разместить в заказе'}, status=400)
    if not phoneNumber:
        return Response({'error': 'Укажите номер телефона для того, чтобы менеджеры имели возможность связаться с вами'}, status=400)
    if not name:
        return Response({'error': 'Укажите ваше имя и(или) фамилию'}, status=400)

    variant = ProductVariant.objects.filter(uniqueId=productVariantId).first()
    if not variant:
        return Response({'error': 'Товар с данным идентификатором не найден'}, status=400)

    res = validateAndFormatPhoneNumber(phoneNumber)
    if not res['success']:
        return Response({"error": res.get('error')}, status=400)
    formattedPhoneNumber = res.get('formattedPhoneNumber')

    orderPrice = (variant.price - variant.price / 100 * variant.discountPercent) * 100

    createdOrder: FastOrder
    try:
        productData = selectAllFromProducts(f'Message_ID = {productVariantId}')

        settings = getServerSettings()
        if not settings:
            return Response({'error': SETTINGS_ERROR}, status=400)
        
        createdOrder = FastOrder.objects.create(
            productInfo={
                'product': ProductSerializer(variant.product, context={'request': request}).data,
                'variant': ProductVariantSerializer(variant).data
            },
            productLegacyInfo=productData[0],
            phoneNumber=formattedPhoneNumber,
            name=name,
            status='NotPaid',
            address=address
        )

        deliveryCost = settings["delivery_cost_in_rub"]
        if deliveryCost:
            orderPrice += deliveryCost * 100

        params = {
            'userName': settings["sber_api_login"],
            'password': settings["sber_api_password"],
            'currency': 643,
            'orderNumber': createdOrder.orderId,
            'description': f'Оплата заказа "{createdOrder.orderId}" в магазине Персона. Артикул товара: {variant.uniqueId}'[:512],
            'amount': int(orderPrice),
            'returnUrl': 'personashop://success-fast-payment',
            'failUrl': 'personashop://fast-order-pay-failed'
        }

        registerUrl = f'{settings["sber_api_url"]}/register.do'
        data = requests.get(registerUrl, params=params, verify=False).json()
        if data.get('orderId'):
            createdOrder.orderSberId = data['orderId']
            createdOrder.save()
            checkOrderStatusAndUpdateStateTask.apply_async(
                (data['orderId'], True),
                countdown=settings["sber_api_payment_time_limit"]
            )
        return Response({
            **data,
            'orderIdInBackend': createdOrder.orderId
        })
    except Exception as e:
        print(str(e))
        if createdOrder:
            createdOrder.delete()
        return Response({'error': 'При создании заказа возникла ошибка'}, status=400)
