from rest_framework import serializers

from ..models import MainContent, MainSwiperImage, OtherContent


class MainSwiperImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainSwiperImage
        fields = '__all__'


class OtherContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherContent
        fields = '__all__'


class MainContentSerializer(serializers.ModelSerializer):
    mainSwiperImages = MainSwiperImageSerializer(many=True)
    otherContent = OtherContentSerializer(many=True)

    class Meta:
        model = MainContent
        exclude = ['isInactive', 'gender', 'id']
