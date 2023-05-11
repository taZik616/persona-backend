from api.utils import connectToPersonaDB


def getDescriptionForProductFields():
    """
    Usage:
    ```py
    description, podklad, country, sostav, manufacturer = getDescriptionForProductFields().values()
    ```
    """
    connection = connectToPersonaDB()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT Description FROM `mobper`.`Field` WHERE Field_Name = 'descr'")
        description = cursor.fetchone()[0]
        cursor.execute(
            "SELECT Description FROM `mobper`.`Field` WHERE Field_Name = 'podklad'")
        podklad = cursor.fetchone()[0]
        cursor.execute(
            "SELECT Description FROM `mobper`.`Field` WHERE Field_Name = 'country'")
        country = cursor.fetchone()[0]
        cursor.execute(
            "SELECT Description FROM `mobper`.`Field` WHERE Field_Name = 'sostav'")
        sostav = cursor.fetchone()[0]
        cursor.execute(
            "SELECT Description FROM `mobper`.`Field` WHERE Field_Name = 'manufacturer'")
        manufacturer = cursor.fetchone()[0]
        return {
            'description': description, 'podklad': podklad,
            'country': country, 'sostav': sostav,
            'manufacturer': manufacturer
        }
