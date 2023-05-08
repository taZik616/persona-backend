import pymysql

from environment import PERSONA_DB_CONFIG


def connectToPersonaDB():
    return pymysql.connect(
        **PERSONA_DB_CONFIG
    )
