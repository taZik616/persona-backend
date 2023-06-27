from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.common_error_messages import GENDER_MUST_BE
from api.models import MainContent
from api.serializers import MainContentSerializer


@api_view(['GET'])
def MainContentView(request):
    try:
        gender = request.GET.get('gender')
        if not gender:
            return Response({"error": 'Укажите в запросе поле gender'}, status=400)
        if gender != 'men' and gender != 'women':
            return Response({'error': GENDER_MUST_BE}, status=400)
        content = MainContent.objects.get(gender=gender, isInactive=False)

        return Response(MainContentSerializer(content, context={'request': request}).data)
    except Exception as e:
        print(str(e))
        return Response({"error": 'Не удалось вернуть контент главной страницы'}, status=400)
