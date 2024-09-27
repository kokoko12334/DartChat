from chains.question_chain import question_chain
from chains.query_chain import query_chain
from chains.splite_chain import splite_chain
from chains.final_answer_chain import final_answer_chain
from db.connection import get_db_connection
from typing import List

# 질문의도를 분석하는 함수
def analyze_question(user_input:str, stock_code:str, memory:List[dict]):
    result = question_chain.invoke(
        {
            "user_input": user_input, 
            "stock_code": stock_code, 
            "memory": memory, 
        }
    )
    return result

# SQL쿼리 변환 함수
def trans_query(user_input:str, stock_code:str, memory:List[dict], now_time:str):
    result = query_chain.invoke(
        {
            "user_input": user_input, 
            "stock_code": stock_code, 
            "memory": memory, 
            "formatted_time":now_time
        }
    )
    return result

# SQL쿼리를 실행하는 함수
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

# 질문 쪼개기
def split_and_respond(user_input:str, docs:str, stock_name:str, now_time):
    result = splite_chain.invoke(
        {"docs": docs, 
         "user_input":user_input, 
         "stock_name": stock_name, 
         "formatted_time":now_time
         }
    )
    
    return result


# 최종 답변을 생성하는 함수
def generate_final_answer(user_input:str, docs:str, stock_name:str, now_time):
    result = final_answer_chain.invoke(
        {"docs": docs, 
         "user_input":user_input, 
         "stock_name": stock_name, 
         "formatted_time":now_time
         }
    )
    
    return result
