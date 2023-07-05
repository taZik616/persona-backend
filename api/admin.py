from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from api.models import (
    AnotherImage,
    BasketItem,
    Brand,
    Category,
    Collection,
    Color,
    DiscountCard,
    DiscountCardLevel,
    FastOrder,
    FavoriteItem,
    GiftCard,
    GiftCardType,
    HelpfulInfo,
    MainContent,
    MainSwiperImage,
    Order,
    OtherContent,
    Product,
    ProductImage,
    ProductVariant,
    Promocode,
    ServerSettings,
    User,
)

admin.site.register(User)
admin.site.register(Brand)
admin.site.register(AnotherImage)
admin.site.register(MainContent)
admin.site.register(ProductImage)
admin.site.register(FavoriteItem)
admin.site.register(BasketItem)
admin.site.register(Collection)
admin.site.register(DiscountCard)
admin.site.register(DiscountCardLevel)
admin.site.register(Promocode)
admin.site.register(ServerSettings)
admin.site.register(GiftCard)
admin.site.register(GiftCardType)
admin.site.register(HelpfulInfo)


@admin.register(OtherContent)
class OtherContentAdmin(admin.ModelAdmin):
    list_display = ['type', 'title']


@admin.register(MainSwiperImage)
class MainSwiperImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'imageUrl', 'productFilters']


@admin.register(FastOrder)
class FastOrderAdmin(admin.ModelAdmin):
    ordering = ('-orderId',)
    list_display = ['orderId', 'orderSberId',
                    'status', 'phoneNumber', 'address']
    search_fields = ('orderId', 'orderSberId', 'phoneNumber')
    list_per_page = 150


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = ('-orderId',)
    list_display = ['orderId', 'orderSberId', 'status', 'user', 'address']
    search_fields = ('orderId', 'orderSberId', 'user__phoneNumber')
    list_per_page = 150
    list_filter = ['status', 'user__phoneNumber']


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
    list_filter = ['gender', 'level']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['productName', 'price', 'lastUpdate', 'isNew', 'productId', 'brand',
                    'categoryId', 'subcategoryId', 'isAvailable', 'onlyOneVariant', 'checked']
    ordering = ('-lastUpdate', '-productName')
    search_fields = ('productId', 'productName',
                     'keywords', 'price', 'description')
    list_per_page = 250

    list_filter = ('brand__name', 'isNew', 'categoryId', 'subcategoryId', 'isAvailable', 'onlyOneVariant', 'checked')

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
    list_filter = ['product__productId']
