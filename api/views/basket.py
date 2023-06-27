from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import BasketItem, Product, ProductVariant
from api.serializers import BasketItemsSerializer


class BasketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            items = request.user.basketItems.all()
            count = request.user.basketItems.count()

            return Response({
                'count': count,
                'items': BasketItemsSerializer(items, many=True, context={'request': request}).data
            })
        except:
            return Response({'error': 'Не удалось вернуть список товаров в избранном'}, status=400)

    def put(self, request):
        try:
            productId = request.data.get('productId')
            variantId = request.data.get('variantId')
            if not productId:
                return Response({'error': 'Укажите идентификатор товара, который хотите добавить'})
            if not variantId:
                return Response({'error': 'Укажите идентификатор конфигурации товара'})
            alreadyInBasket = BasketItem.objects.filter(
                product__productId=productId, variant__uniqueId=variantId,
                user=request.user
            ).exists()
            if alreadyInBasket:
                return Response({'error': 'Товар с данным идентификатором уже есть в корзине'})

            product = Product.objects.filter(productId=productId).first()
            variant = ProductVariant.objects.filter(uniqueId=variantId).first()
            if not product or not variant:
                return Response({'error': 'Товар или его вариация с данным идентификатором не найден'})
            if variant.product.productId != productId:
                return Response({'error': 'Вариация товара не совпадает с самим товаром'})
            BasketItem.objects.create(
                product=product, variant=variant,
                user=request.user
            )

            return Response({'success': 'Вы добавили товар в корзину'})
        except:
            return Response({'error': 'Не удалось добавить товар в избранное'}, status=400)

    def delete(self, request):
        try:
            productId = request.data.get('productId')
            variantId = request.data.get('variantId')
            if not productId:
                return Response({'error': 'Укажите идентификатор товара, который хотите удалить'})
            if not variantId:
                return Response({'error': 'Укажите идентификатор конфигурации товара'})
            BasketItem.objects.filter(
                product__productId=productId, variant__uniqueId=variantId,
                user=request.user
            ).delete()
            return Response({
                'success': 'Вы успешно удалили товар из корзины'
            })
        except:
            return Response({'error': 'Не удалось вернуть список товаров в избранном'}, status=400)
