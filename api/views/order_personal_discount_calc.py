from api.views.check_promocode import checkPromocode

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import ProductSerializer, ProductVariantSerializer
from api.utils import splitString, getWomenAndMenCats
from api.models import ProductVariant, DiscountCard, Promocode, User, Product


def orderPersonalDiscountCalc(productVariantIds: str, user: User, promocode: str):
    try:
        if not productVariantIds:
            return {'error': 'Укажите товары для того чтобы узнать сколько составит цена со скидкой'}

        productVariantIds = splitString(productVariantIds)

        variants = ProductVariant.objects.filter(uniqueId__in=productVariantIds)
        productIdsForVariants = [productId for productId in variants.values_list('product', flat=True)]
        products = Product.objects.filter(productId__in=productIdsForVariants)

        if promocode:
            promoCheckRes = checkPromocode(promocode, user)
            if promoCheckRes.get('error'):
                return promoCheckRes
        promocode = Promocode.objects.filter(code=promocode).first()

        preparedProductsData = []
        priceWithoutPersonalDiscount = 0
        priceWithPersonalDiscount = 0

        if promocode: # Промокод найден и действителен
            productFilters = promocode.productFilters or {}
            subcategoryIds = productFilters.get('subcategoryIds')
            categoryId = productFilters.get('categoryId')
            productIds = productFilters.get('productIds')
            brandIds = productFilters.get('brandIds')
            gender = productFilters.get('gender')
            priceGroup = productFilters.get('priceGroup')

            promoProducts = products
            if productIds:
                promoProducts = promoProducts.filter(productId__in=productIds)
            else:
                if subcategoryIds:
                    promoProducts = promoProducts.filter(subcategoryId__in=subcategoryIds)
                if categoryId:
                    promoProducts = promoProducts.filter(categoryId=categoryId)
                if brandIds:
                    promoProducts = promoProducts.filter(brand__brandId__in=brandIds)
                if priceGroup:
                    promoProducts = promoProducts.filter(priceGroup=priceGroup)
                if gender:
                    [menCats, womenCats] = getWomenAndMenCats()
                    if gender == 'men':
                        promoProducts = promoProducts.filter(categoryId__in=menCats)
                    elif gender == 'women':
                        promoProducts = promoProducts.filter(categoryId__in=womenCats)
            if promoProducts.count() <= 0:
                return {'error': 'Ни к одному товару нельзя применить промокод промо-кода'}
            for variant in variants:
                parentId = variant.product.productId
                participatesInPromo = promoProducts.filter(productId=parentId).exists()
                if participatesInPromo:
                    price = variant.price - variant.price / 100 * variant.discountPercent

                    discountPercent = promocode.benefit.get('discountPercent', 0)
                    discountSum = promocode.benefit.get('discountSum', 0)
                    startSumForDiscountSum = promocode.benefit.get('startSumForDiscountSum', 0)
                    personalDiscountInRub = 0
                    if discountPercent:
                        if not discountSum:
                            personalDiscountInRub = price / 100 * discountPercent
                        else:
                            if price >= discountSum:
                                personalDiscountInRub = min(price / 100 * discountPercent, discountSum)
                    elif discountSum and price >= startSumForDiscountSum:
                        personalDiscountInRub = price / 100 * discountPercent
                    elif discountSum:
                        return {'error': f'Для активации кода сумма заказа должна составлять {startSumForDiscountSum} ₽'}

                    priceWithoutPersonalDiscount += price
                    priceWithPersonalDiscount += price - personalDiscountInRub
                    preparedProductsData.append({
                        'product': ProductSerializer(variant.product).data,
                        'variant': ProductVariantSerializer(variant).data,
                        'personalDiscountInRub': personalDiscountInRub
                    })
                    
                else:
                    preparedProductsData.append({
                        'product': ProductSerializer(variant.product).data,
                        'variant': ProductVariantSerializer(variant).data
                    })
        else:
            discountCard = DiscountCard.objects.filter(user=user).first()
            if discountCard and discountCard.cardLevel:
                discountPercent = discountCard.cardLevel.discountPercent

                # Применяем скидку на каждый вариант товара
                for variant in variants:
                    price = variant.price - variant.price / 100 * variant.discountPercent
                    personalDiscountInRub = price / 100 * discountPercent

                    priceWithoutPersonalDiscount += price
                    priceWithPersonalDiscount += price - personalDiscountInRub

                    preparedProductsData.append({
                        'product': ProductSerializer(variant.product).data,
                        'variant': ProductVariantSerializer(variant).data,
                        'personalDiscountInRub': personalDiscountInRub
                    })

        return {
            'priceWithoutPersonalDiscount': priceWithoutPersonalDiscount,
            'priceWithPersonalDiscount': priceWithPersonalDiscount,
            'products':preparedProductsData
        }
    except Exception as e:
        print(e)
        return {'error': 'При расчете персональной скидки возникла ошибка'}




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orderPersonalDiscountCalcView(request):
    productVariantIds = request.GET.get('productVariantIds', '')
    promocode = request.GET.get('promocode', '')
    data = orderPersonalDiscountCalc(productVariantIds, request.user, promocode)

    if isinstance(data, dict) and data.get('error'):
        return Response(data, status=400)
    else:
        return Response(data)


    