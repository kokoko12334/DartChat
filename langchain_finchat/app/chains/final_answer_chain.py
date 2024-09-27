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
    너는 재무 분석가이다. 전문가스러운 분석을 수행해라.

    데이터베이스의 결과인 docs를 확인하여 사용자의 질문에 대답해라.
    이때 출력하는 거는 Markdown으로하고 만약에 표를 출력할 필요가 있다면 이쁘게 표로 정리해서
    사용자가 보기 편하게 이쁘게 양식으로 정리해라
    또한 참고 데이터의 신뢰를 위해 보고서 번호도 마지막에 정리해라.이때 보고서 참고문서를 언급할때는 참고한 보고서들을 맨 마지막에만 적고
    'https://dart.fss.or.kr/dsaf001/main.do?rcpNo=보고서번호'로 링크를 만들어서 해라 링크이름은 bsns_year reprt_code를 결합해서
    예를 들면 bsns_year=2024, reprt_code=11013이면 2024년-1분기보고서 이런식으로 링크이름으로 정하고 위에서 언급한 url로 링크를 만들어라.
    OFS:재무제표, CFS:연결재무제표 를 보고 연결재무제표인지 아닌지도 언급해라 반드시 언급해야 한다. 출처를 밝히는 것이 매우매우중요하다.
    docs: {docs} -> 참고할 문서

"""

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

chat_prompt = ChatPromptTemplate.from_messages([
        ("system", answer_system_prompt),
        ("user", "{user_input}")
])
parser = StrOutputParser()

final_answer_chain = chat_prompt | llm | parser
