from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from api.serializers import FavoriteItemsSerializer
from api.models import FavoriteItem, Product


class FavoritesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            items = request.user.favoriteItems.all()
            count = request.user.favoriteItems.count()

            return Response({
                'count': count,
                'items': FavoriteItemsSerializer(items, many=True, context={'request': request}).data
            })
        except:
            return Response({'error': 'Не удалось вернуть список товаров в избранном'}, status=400)

    def put(self, request):
        try:
            productId = request.data.get('productId')
            if not productId:
                return Response({'error': 'Укажите идентификатор товара, который хотите добавить'})
            product = Product.objects.filter(productId=productId).first()
            if not product:
                return Response({'error': 'Товар с данным идентификатором не найден'})
            alreadyInFav = FavoriteItem.objects.filter(
                product__productId=productId, user=request.user
            ).exists()

            if alreadyInFav:
                return Response({'error': 'Товар с данным идентификатором уже есть в избранном'})
            FavoriteItem.objects.create(product=product, user=request.user)

            return Response({
                'success': 'Вы добавили товар в избранное',
            })
        except:
            return Response({'error': 'Не удалось добавить товар в избранное'}, status=400)

    def delete(self, request):
        try:
            productId = request.data.get('productId')
            if not productId:
                return Response({'error': 'Укажите идентификатор товара, который хотите удалить'})
            FavoriteItem.objects.filter(
                product__productId=productId, user=request.user).delete()
            return Response({
                'success': 'Вы успешно удалили товар из избранных'
            })
        except:
            return Response({'error': 'Не удалось вернуть список товаров в избранном'}, status=400)
