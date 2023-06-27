from .connect_to_persona_db import connectToPersonaDB

PRODUCT_ALL_FIELDS = [
    'Message_ID', 'User_ID', 'Subdivision_ID', 'Sub_Class_ID',
    'Priority', 'Keyword', 'ncTitle', 'ncKeywords', 'ncDescription',
    'ncSMO_Title', 'ncSMO_Description', 'ncSMO_Image', 'ncDemoContent',
    'Checked', 'IP', 'UserAgent', 'Parent_Message_ID', 'Created',
    'LastUpdated', 'LastUser_ID', 'LastIP', 'LastUserAgent',
    'caption', 'price', 'images', 'code', 'descr', 'ItemID',
    'item_type', 'size', 'color', 'stock', 'new', 'priceGroup',
    'brand', 'dop_images', 'manufacturer', 'country', 'podklad',
    'sostav', 'collection'
]


def selectAllFromProducts(filter='Subdivision_ID != 224'):
    connection = connectToPersonaDB()
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT {', '.join(PRODUCT_ALL_FIELDS)} FROM mobper.Message2001 WHERE {filter};"
        )
        products = cursor.fetchall()

        result = []
        for product in products:
            product_dict = dict(zip(PRODUCT_ALL_FIELDS, product))
            product_dict['LastUpdated'] = product_dict['LastUpdated'].strftime(
                '%Y-%m-%d %H:%M:%S')
            result.append(product_dict)
        return result
