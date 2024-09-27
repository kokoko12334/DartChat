import pymysql
import os
from contextlib import contextmanager

HOST = os.getenv("HOST")
USER = os.getenv("USER")
PWD = os.getenv("PWD")
DB = os.getenv("DB")

@contextmanager
def get_db_connection():
    db = pymysql.connect(
        host=HOST,
        user=USER,
        passwd=PWD,
        database=DB
    )
    try:
        yield db
    finally:
        db.close()