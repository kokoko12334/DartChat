from abc import ABC, abstractmethod
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from utils.aws_api import SSMService, AWSService
from chains.parser import IntentOutputParser
from chains.prompt import *

class BaseChain(ABC):
    def __init__(self):
        ssm: AWSService  = SSMService()
        self.api_key = ssm.get_parameter("OPENAIKEY")

    @abstractmethod
    def run(self, **kwargs) -> any:
        """
        체인 실행 메소드
        Args:
            model: gpt모델
            user_input (str): 사용자 질문
            stock_code (str): 주식코드
            stock_name (str): 주식이름
            memory (list): 이전 대화기록
            formaated_date (str): 현재 날짜
            docs (str): 답변 생성에 참고할 문서

        """
        pass

class AnalyzeIntentChain(BaseChain):
    def __init__(self):
        super().__init__()
        
    def run(self, model: str, user_input: str, stock_code: str, memory: list) -> IntentOutputParser:
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", intent_system_prompt),
            ("user", f"{user_input}, 분석할 주식코드:{stock_code}")
        ])
        llm = ChatOpenAI(model=model, api_key=self.api_key)
        parser = JsonOutputParser(pydantic_object=IntentOutputParser)

        chain = chat_prompt | llm | parser
        return chain.invoke(
            {
                "user_input": user_input, 
                "stock_code": stock_code, 
                "memory": memory, 
            }
        )

class SQLTransformerChain(BaseChain):
    def __init__(self):
        super().__init__()

    def run(self, model: str, user_input: str, stock_code: str, memory: list, now_date: str) -> IntentOutputParser:
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", sqlquery_system_prompt),
            ("user", f"{user_input}, 분석할 주식코드:{stock_code}")
        ])
        llm = ChatOpenAI(model=model, api_key=self.api_key, temperature=0.0)
        parser = JsonOutputParser(pydantic_object=IntentOutputParser)

        chain = chat_prompt | llm | parser
        return chain.invoke(
            {
                "user_input": user_input, 
                "stock_code": stock_code, 
                "memory": memory, 
                "now_date": now_date
            }
        )

class FinalAnswerChain(BaseChain):
    def __init__(self):
        super().__init__()

    def run(self, model: str, user_input: str, stock_name: str, memory: list, docs: str) -> str:
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", answer_system_prompt),
            ("user", user_input)
        ])
        llm = ChatOpenAI(model=model, api_key=self.api_key, temperature=0.0)
        parser = StrOutputParser()

        chain = chat_prompt | llm | parser
        return chain.invoke(
            { 
                "user_input":user_input,
                "stock_name": stock_name,
                "memory": memory,
                "docs": docs,
            }
        )

class ChainManager:
    def __init__(self):
        self.chains = {
            "analyze_question": AnalyzeIntentChain(),
            "sql_trans": SQLTransformerChain(),
            "final_answer": FinalAnswerChain(),
        }

    def run_chain(self, chain_type: str, **kwargs):
        chain: BaseChain = self.chains.get(chain_type)
        if chain:
            return chain.run(**kwargs)
        else:
            raise ValueError(f"Chain type '{chain_type}' not found.")

