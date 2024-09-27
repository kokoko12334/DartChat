from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
question_system_prompt = """
이전 대화기록:{memory}

대화의 흐름과 사용자의 질문을 보고 매출,실적발표,부채,사업성 등 재무관련 sql에 대한 질문인지 아닌지 판단해라. 
관련 SQL로 확일 할수 있는것은 손익계산서, 재무상태표, 현금흐름표이다.
실적발표는 재무상태표니까 sql 질의문을 해야하는 게 맞는거야
json으로 키값은 sql, answer로 반환해라

1.sql 질의문을 해야할 경우의 예시
    "sql": 1, 
    "answer": ""(그냥 빈칸으로)
2. 이전의 대화 기록을 보고 sql질의문 없시 질문에 대답할 수 있는 경우 메모리(이전대화기록)에 풍분히 데이터가 있으면 sql쿼리를 작성하지 않거나 재무제표와 관련된 내용이 아닌 경우.
    "sql": 0, 
    "answer": "너의 답변내용"
"""

llm = ChatOpenAI(model="gpt-4o-mini")

chat_prompt = ChatPromptTemplate.from_messages([ 
    ("system", question_system_prompt),
    ("user", "{user_input}, 분석할 주식코드:{stock_code}")
])

class Output(BaseModel):
    answer: str = Field(description="outputformat")
    sql: str = Field(description="outputformat")
parser = JsonOutputParser(pydantic_object=Output)

question_chain = chat_prompt | llm | parser