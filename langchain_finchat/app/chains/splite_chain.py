from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
answer_system_prompt = """
    현재날짜:{formatted_time}
    분석할 기업:{stock_name}
    stock_code: 주식코드
    rcept_no: 보고서번호 (14자리 숫자지만, 문자열로 저장)
    bsns_year: 사업 연도 (정수형)
    reprt_code: 1분기보고서 : 11013 반기보고서 : 11012 3분기보고서 : 11014 사업보고서 : 11011
    account_nm: 계정명(예: 자본총계, 유형자산 등등)
    sj_nm : 재무상태표, 손익계산서, 현금흐름표
    thstrm_amount: 당기금액
    currency: 통화 단위
    fs-div: 개별/연결구분	OFS:재무제표, CFS:연결재무제표
    docs: {docs} -> 참고할 문서
    너는 해당 질문에 대해 주어진 정보를 요약해주는 AI이다. 
    주어진 문서에서 질문과 관련된 내용만 추려서 간결하고 명확하게 요약하라. 
    특히 숫자와 같은 중요한 데이터는 질문에 포함되는 관련된 내용만 최대한 간추려서 제공해라. 
    요약은 짧고 굵게 작성하되, 의미가 왜곡되지 않도록 주의해라. 보고서 번호도 꼭언급해라

"""

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

chat_prompt = ChatPromptTemplate.from_messages([
        ("system", answer_system_prompt),
        ("user", "{user_input}")
])
parser = StrOutputParser()

splite_chain = chat_prompt | llm | parser
