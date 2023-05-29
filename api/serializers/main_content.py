from rest_framework import serializers

from ..models import MainContent, MainSwiperImage, Brand, Product, ProductImage, Category
from . import CategorySerializer, BrandSerializer

class MainSwiperImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainSwiperImage
        fields = '__all__'


class MainContentSerializer(serializers.ModelSerializer):
    mainSwiperImages = MainSwiperImageSerializer(many=True)
    otherContent = serializers.SerializerMethodField()

    def get_otherContent(self, instance: MainContent):
        rawContent = instance.otherContent.all()
        request = self.context.get('request')
        content = []
        try:
            for contentPart in rawContent:
                preparedItems = []
                for index, item in enumerate(contentPart.items):
                    itemId = f"{instance.gender}-{index}"
                    match contentPart.type:
                        case 'CategoriesList':
                            category = Category.objects.filter(categoryId=item['subcategoryId']).first()
                            productsByCategory = Product.objects.filter(subcategoryId=item['subcategoryId']).order_by('?')
                            for product in productsByCategory:
                                prodImage = ProductImage.objects.filter(imageId=product.productId).first()
                                if prodImage:
                                    preparedItems.append({
                                        "id": itemId,
                                        "category": CategorySerializer(category, context={'request': request}).data,
                                        "imgUri": request.build_absolute_uri(prodImage.compressedImage.url),
                                        "queryFilters": {
                                            'subcategoryId': item['subcategoryId'],
                                            **item.get('queryFilters', {})
                                        }
                                    })
                                    break
                        case 'BrandsSwiper':
                            brand = Brand.objects.filter(brandId=item['brandId']).first()
                            preparedItems.append({
                                "id": itemId,
                                "brand": BrandSerializer(brand, context={'request': request}).data,
                                "imgUri": item['imgUri'],
                                "queryFilters": {
                                    'brand__brandId': item['brandId'],
                                    **item.get('queryFilters', {})
                                }
                            })
                        case 'BrandsList':
                            brand = Brand.objects.filter(brandId=item['brandId']).first()
                            productsByBrand = Product.objects.filter(brand=brand).order_by('?')
                            for product in productsByBrand:
                                prodImage = ProductImage.objects.filter(imageId=product.productId).first()
                                if prodImage:
                                    preparedItems.append({
                                        "id": itemId,
                                        "brand": BrandSerializer(brand, context={'request': request}).data,
                                        "imgUri": request.build_absolute_uri(prodImage.compressedImage.url),
                                        "queryFilters": {
                                            'brand__brandId': item['brandId'],
                                            **item.get('queryFilters', {})
                                        }
                                    })
                                    break

                        case 'FashionSwiper':
                            preparedItems.append({"id": itemId, **item})
                        case 'FashionList':
                            preparedItems.append({"id": itemId, **item})

                content.append({
                    "type": contentPart.type,
                    "title": contentPart.title,
                    "items": preparedItems
                })

            return content
        except Exception as e:
            print(str(e))
            return content

    class Meta:
        model = MainContent
        fields = ('mainSwiperImages', 'bannerCard', 'otherContent')
