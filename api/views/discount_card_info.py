from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from api.models import DiscountCard
from api.serializers import DiscountCardSerializer


class DiscountCardInfoView(RetrieveAPIView):
    queryset = DiscountCard.objects.all()
    serializer_class = DiscountCardSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.queryset.get(user=self.request.user)
