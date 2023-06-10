from ..common_error_messages import GENDER_MUST_BE, ONLY_ADMIN
from ..serializers import BrandSerializer
from ..models import Brand

from rest_framework.response import Response
from rest_framework.views import APIView


class BrandsView(APIView):
    def patch(self, request):
        """
        Запрос на получение списка брендов по параметрам `isTop` и `gender`
        Если искать по brandId, то вернется одиночный объект
        """
        if 'brandId' in request.data:
            try:
                brand = Brand.objects.get(brandId=request.data['brandId'])
                serialized_data = BrandSerializer(brand, many=False, context={'request': request}).data
                return Response(serialized_data)
            except Brand.DoesNotExist:
                return Response({'error': 'Бренд с данным идентификатором не найден'}, status=400)
            except:
                return Response({'error': 'Не удалось вернуть бренд'}, status=400)
        else:
            try:
                queryset = Brand.objects.all().filter(gender__isnull=False)
                if 'isTop' in request.data:
                    queryset = queryset.filter(isTop=request.data['isTop'])
                if 'gender' in request.data:
                    gender = request.data['gender']
                    if gender != 'men' and gender != 'women':
                        return Response({'error': GENDER_MUST_BE}, status=400)

                    queryset = queryset.filter(gender__in=[gender, 'both'])
                serialized_data = BrandSerializer(queryset, many=True, context={'request': request}).data
                return Response(serialized_data)
            except:
                return Response({'error': 'Не удалось вернуть список брендов'}, status=400)

    def delete(self, request):
        """
        Удаляем объект если он существует
        """
        if not request.user.is_superuser:
            return Response({'error': ONLY_ADMIN}, status=400)
        try:
            brandObj = Brand.objects.get(brandId=request.data['brandId'])
            brandObj.delete()
            return Response({'success': 'Бренд был успешно удален'})
        except Brand.DoesNotExist:
            return Response({'error': 'Не удалось найти бренд по указанному ID'}, status=400)
        except:
            return Response({'error': 'При удалении возникла ошибка'}, status=400)
