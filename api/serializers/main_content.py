from rest_framework import serializers

from ..models import MainContent, MainSwiperImage, OtherContent, Brand, Product, ProductImage, Category
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
                for item in contentPart.items:
                    match contentPart.type:
                        case 'CategoriesList':
                            category = Category.objects.filter(categoryId=item['categoryId']).first()
                            productsByCategory = Product.objects.filter(subcategoryId=item['categoryId']).order_by('?')
                            for product in productsByCategory:
                                prodImage = ProductImage.objects.filter(imageId=product.productId).first()
                                if prodImage:
                                    preparedItems.append({
                                        "category": CategorySerializer(category, context={'request': request}).data,
                                        "imgUri": request.build_absolute_uri(prodImage.compressedImage.url),
                                        "queryFilters": {
                                            'categoryId': item['categoryId'],
                                            **item.get('queryFilters', {})
                                        }
                                    })
                                    break
                        case 'BrandsSwiper':
                            brand = Brand.objects.filter(brandId=item['brandId']).first()
                            preparedItems.append({
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
                                        "brand": BrandSerializer(brand, context={'request': request}).data,
                                        "imgUri": request.build_absolute_uri(prodImage.compressedImage.url),
                                        "queryFilters": {
                                            'brand__brandId': item['brandId'],
                                            **item.get('queryFilters', {})
                                        }
                                    })
                                    break

                        case 'FashionSwiper':
                            preparedItems.append(item)
                        case 'FashionList':
                            preparedItems.append(item)

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
