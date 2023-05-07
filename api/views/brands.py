from ..common_error_messages import GENDER_MUST_BE, ONLY_ADMIN
from ..serializers import BrandSerializer
from ..models import Brand

from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import permission_classes
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
                serialized_data = BrandSerializer(brand, many=False).data
                return Response(serialized_data)
            except Brand.DoesNotExist:
                return Response({'error': 'Бренд с данным идентификатором не найден'}, status=400)
            except:
                return Response({'error': 'Не удалось вернуть бренд'}, status=400)
        else:
            try:
                queryset = Brand.objects.all()
                if 'isTop' in request.data:
                    queryset = queryset.filter(isTop=request.data['isTop'])
                if 'gender' in request.data:
                    gender = request.data['gender']
                    if gender != 'men' and gender != 'women':
                        return Response({'error': GENDER_MUST_BE}, status=400)

                    queryset = queryset.filter(gender=gender)
                serialized_data = BrandSerializer(queryset, many=True).data
                return Response(serialized_data)
            except:
                return Response({'error': 'Не удалось вернуть список брендов'}, status=400)

    @permission_classes([IsAdminUser])
    def put(self, request):
        """
        Обновляем существующий или создаем новый бренд
        """
        if not request.user.is_superuser:
            return Response({'error': ONLY_ADMIN}, status=400)
        brandId = request.data.get('brandId')
        name = request.data.get('name', '')
        keywords = request.data.get('keywords')
        logoUrl = request.data.get('logoUrl', '')
        gender = request.data.get('gender', '')
        isTop = request.data.get('isTop')

        if not brandId:
            return Response({'error': 'Укажите brandId'})
        try:
            # Если объект не найден то нас выкинет в except блок
            brandObj = Brand.objects.get(brandId=brandId)

            brandObj.name = name or brandObj.name
            brandObj.keywords = keywords if keywords != None else brandObj.keywords
            brandObj.logoUrl = logoUrl or brandObj.logoUrl
            brandObj.gender = gender or brandObj.gender
            brandObj.isTop = isTop if isTop != None else brandObj.isTop

            if brandObj.gender != 'men' and brandObj.gender != 'women':
                return Response({'error': GENDER_MUST_BE}, status=400)

            brandObj.save()
            return Response({'success': 'Бренд успешно обновлен'})
        except Brand.DoesNotExist:
            if gender != 'men' and gender != 'women':
                return Response({'error': GENDER_MUST_BE}, status=400)
            Brand.objects.create(brandId=brandId,
                                 name=name, keywords=keywords, logoUrl=logoUrl, gender=gender, isTop=isTop)

            return Response({'success': "Новый бренд создан успешно"})

    @permission_classes([IsAdminUser])
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
