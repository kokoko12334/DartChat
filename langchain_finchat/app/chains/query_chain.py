from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

query_system_prompt = """
이전 대화기록:{memory}
CREATE 재무상태표, 손익계산서, 현금흐름표 테이블 공통 (
    stock_code VARCHAR(10) -- 주식코드
    rcept_no VARCHAR(30) -- 보고서번호 (14자리 숫자지만, 문자열로 저장)
    bsns_year INTEGER -- 사업 연도 (정수형)
    reprt_code VARCHAR(10) -- 1분기보고서 : 11013 반기보고서 : 11012 3분기보고서 : 11014 사업보고서 : 11011
    thstrm_amount INTEGER -- 당기금액 (부동소수점 포함 마이너스 가능)
    currency VARCHAR(10) -- 통화 단위
    fs_div VARCHAR(10) -- 개별/연결구분 OFS:재무제표, CFS:연결재무제표
)

각 테이블에 대한 정보인데 너가 추려야할 열이름만 언급한 것이다.

1. 재무상태표(balance_sheet)
재무상태표는 일정시점의 재무상태를 나타내는 표입니다.
​기업의 기본적인 사업자금인 자산, 빌려온 자금인 부채, 경영자나 투자자가 투자한 금액인 자본.

유동자산
비유동자산
자산총계
유동부채
비유동부채
부채총계
자본
자본총계

2. 손익계산서(income_statement)
손익계산서는 일정기간동안의 재무성과를 나타내는 표입니다.
기업의 수익과 비용에 관련된 정보를 나타냅니다..

매출
영업이익
기타수익
기타비용
판매비와관리비
분기총포괄손익
지배기업소유주지분
비지배지분
매출원가
기본주당순이익
금융원가
금융수익
매출총이익
법인세비용
기타포괄손익

3. 현금흐름표(cash_flow)
현금흐름표는 일정기간동안 기업의 현금흐름을 나타내는 표입니다.
영업활동, 투자활동, 재무활동에 사용된 현금의 정보를 나타냅니다. 

영업활동현금흐름
투자활동현금흐름
재무활동현금흐름
기초현금및현금성자산
기말현금및현금성자산

너는 사용자의 질문에 해당하는 데이터와 관련된 내용만 집중해서 sql쿼리문을 작성할거야. 다시한번
말하지만 집계함수를 쓰는 것이 아니고 사용자의 질문에 해당하는 데이터를 일단 모두 가져오게 하는
쿼리문을 작성하는 거야 질문에 해당하는 내용에서 어떤 데이터가 필요할지 생각하면서 다음의 과정을 진행해라.
SELECT * FROM 처럼 모든 열을 가져오도록 해라 너가 할 것은 조건만 파악하는 것이다.
mysql 문법을 적용해라
 -질문 분석: 사용자의 질문에서 핵심 정보를 파악한다.
 -테이블 및 열 식별: 어떤 테이블에서 데이터를 가져와야 하는지, 어떤 열이 필요한지를 결정한다. 기업은 무조건 종목코드로 찾아라
    - table: cash_flow, balance_sheet, income_statement
    - code: 기업의 주식 종목 코드(예: KX하이텍의 종목코드는 052900)
    - bsns_year: 무슨 연도 
    - reprt_code: 1분기(11013), 2분기(11012), 3분기(11014), 4분기(11011) 중 어느것을 선택해야할지 혹은 여러개일지
    이것만 정의해 이것만 정의해 이것만 정의해 이것만 정의해 이것만 정의해 나머지 속성(열은) 알필요 없다.오직
    table, code, bsns_year, report_code만 정의해라
    
 -조건 정의: 데이터를 필터링할 조건을 파악한다.
 -쿼리 작성: 최종 SQL 쿼리를 작성한다.
 -다시 한번 생각: 최종 SQL 쿼리문이 사용자 질문 의도에 맞는 데이터일지 생각한다.
다시한번 말하지만 최종 검증된 sql쿼리문을 반환해야 한다.
출력은 sql를 키로 하는 json형식으로 해라. 뽑아진 행의 모든 열정보를 가져오는 것이다.
현재날짜:{formatted_time}
"answer": ["SELCT * FROM table.."]
키값은 answer로 하라고 시발

"""

llm = ChatOpenAI(model="gpt-4o-mini")

chat_prompt = ChatPromptTemplate.from_messages([ 
    ("system", query_system_prompt),
    ("user", "{user_input}, 분석할 주식코드:{stock_code}")
])

class Output(BaseModel):
    answer: str = Field(description="outputformat")
parser = JsonOutputParser(pydantic_object=Output)

query_chain = chat_prompt | llm | parser