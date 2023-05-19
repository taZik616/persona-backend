from django.contrib import admin

from api.models import Brand, MainContent, AnotherImage, User, \
    Category, ProductVariant, Product, ProductImage, \
    FavoriteItem, BasketItem, OtherContent, MainSwiperImage, Color

admin.site.register(User)
admin.site.register(Brand)
admin.site.register(AnotherImage)
admin.site.register(MainContent)
admin.site.register(MainSwiperImage)
admin.site.register(OtherContent)
admin.site.register(ProductImage)
admin.site.register(FavoriteItem)
admin.site.register(BasketItem)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    ordering = ('name',)
    search_fields = ('name', 'hex')
    list_per_page = 150


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'level', 'categoryId']
    ordering = ('level', 'gender')
    search_fields = ('name', 'categoryId', 'keywords', 'description')
    list_per_page = 150


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['productName', 'price', 'lastUpdate', 'isNew', 'productId', 'brand',
                    'categoryId', 'subcategoryId', 'isAvailable', 'onlyOneVariant']
    ordering = ('-lastUpdate', '-productName')
    search_fields = ('productId', 'productName',
                     'keywords', 'price', 'description')
    list_per_page = 250


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    def product_name(self, obj):
        return obj.product.productName or ''

    def product_id(self, obj):
        return obj.product.productId

    list_display = ['product_name', 'price', 'isAvailable', 'color', 'size',
                    'uniqueId']
    ordering = ('product_id', '-size', 'isAvailable')
    search_fields = ('uniqueId', 'product__productName',
                     'price', 'color', 'size')
    list_per_page = 250
