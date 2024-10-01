import pymysql
from contextlib import contextmanager
from utils.aws_api import AWSService, SSMService

ssm: AWSService = SSMService()
HOST = ssm.get_parameter("HOST")
USER = ssm.get_parameter("USER")
PWD = ssm.get_parameter("PWD")
DB = ssm.get_parameter("DB")

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

def fetch_data(queries):
    with get_db_connection() as db:
        cursor = db.cursor()
        results = []
        cols = ('stock_code', 'rcept_no','bsns_year', 'reprt_code','account_nm','sj_nm','thstrm_amount','currency',"fs_div")
        arr = [str(cols)]
        for query in queries:
            results = cursor.execute(query)
            results = cursor.fetchall()
            for row in results[::-1]:
                arr.append(str(row))
        docs = "\n".join(arr)
    
        return docs