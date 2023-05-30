import re
from pytz import utc
from api.models import Brand, Category
from api.utils import connectToPersonaDB


def getBrandByName(name):
    brand = None
    try:
        brand = Brand.objects.filter(name__icontains=name).first()
    except:
        brand = None
    return brand


PRODUCT_FIELDS = 'caption, price, Subdivision_ID, Message_ID, brand, size, color, \
    stock, new, ncKeywords, priceGroup, manufacturer, country, podklad, sostav, collection, LastUpdated'


def prepareFields(row: tuple, isSingle: bool = False, podklads: dict = {}, sostavs: dict = {}):
    productName, price, subcategoryId, uniqueId, \
        brandName, size, color, stockCount, isNew, \
        keywords, priceGroup, manufacturer, country, \
        podklad, sostav, collection, lastUpdate = row
    podklad = podklads.get(podklad or '', '')
    sostav = sostavs.get(sostav or '', '')
    discount = re.search(r"\d+%", priceGroup)
    if discount:
        discount = int(discount.strip("%"))
    else: 
        discount =  0

    categoryId = Category.objects.get(categoryId=subcategoryId).parentId
    brand = getBrandByName(brandName)

    return {
        'uniqueId': uniqueId,
        'product': {
            'onlyOneVariant': isSingle,
            'brand': brand,
            'productName': productName if not isSingle else re.sub(r'\s*\([^)]*\)$', '', str(productName)),
            'price': price,
            'subcategoryId': subcategoryId,
            'categoryId': categoryId,
            'isAvailable': bool(stockCount),
            'isNew': bool(isNew),
            'keywords': keywords or '',
            'priceGroup': priceGroup or '' or '',
            'lastUpdate': utc.localize(lastUpdate),
            'collection': collection or '',
            'manufacturer': manufacturer or '',
            'country': country or '',
            'podklad': podklad,
            'sostav': sostav,
            'discountPercent': discount
        },
        'variantForSingleProduct': {
            'size': size,
            'color': color,
        }
    }


PRODUCT_VARIANT_FIELDS = 'price, Message_ID, Parent_Message_ID, size, color, stock, priceGroup'


def prepareVariantFields(row: tuple):
    price, uniqueId, parentId, size, color, stockCount, priceGroup = row
    discount = re.search(r"\d+%", priceGroup)
    if discount:
        discount = int(discount.strip("%"))
    else: 
        discount =  0
    return {
        'uniqueId': uniqueId,
        'price': price,
        'priceGroup': priceGroup or '' or '',
        'size': size,
        'color': color,
        'isAvailable': bool(stockCount),
        'discountPercent': discount
    }


def getPodklads():
    connection = connectToPersonaDB()
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT podklad_ID, podklad_Name FROM mobper.Classificator_podklad;"
        )
        podklads = cursor.fetchall()
        return {t[0]: t[1] for t in podklads}


def getSostavs():
    connection = connectToPersonaDB()
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT sostav_ID, sostav_Name FROM mobper.Classificator_sostav;"
        )
        sostavs = cursor.fetchall()
        return {t[0]: t[1] for t in sostavs}


firstSyncShouldBeHard = 'Перед использованием этой синхронизации нужно хотя бы раз сделать полную синхронизацию'
