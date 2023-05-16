from rest_framework import serializers

from api.models import Category, CategoryLevel, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, category):
        # Ваша логика для получения URL изображения
        request = self.context.get('request')
        try:
            if category.level == CategoryLevel.CATEGORY:
                img = category.categoryPreviewImage
                return request.build_absolute_uri(img.url) if img else None
            else:
                if not category.subcategoryPreviewProduct:
                    return None

                productId = category.subcategoryPreviewProduct.productId
                img = ProductImage.objects.filter(
                    imageId=productId
                ).order_by('priority').first().compressedImage

                return request.build_absolute_uri(img.url) if img else None
        except:
            return None

    class Meta:
        model = Category
        fields = (
            'categoryId', 'name', 'gender', 'parentId', 'image'
        )
