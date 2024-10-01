import json
import pytz
import tiktoken
from chains.rag_chain import ChainManager
from fastapi import WebSocket
from datetime import datetime
from db.connection import fetch_data

kst = pytz.timezone('Asia/Seoul')
current_time_kst = datetime.now(kst)
now_date = current_time_kst.strftime('%Y-%m-%d-%H-%M-%S')

async def process_finchat(user_input: str, stock_name: str, stock_code: str, memory: list, websocket: WebSocket):
    chain_manager = ChainManager()

    # Step 1: 질문 의도 분석
    msg = {"output": "1.질문의도 분석중..."}
    await websocket.send_text(json.dumps(msg))

    result = chain_manager.run_chain(
        chain_type="analyze_question",
        model="gpt-4o-mini",
        user_input=user_input,
        stock_code=stock_code,
        memory=memory,
    )
    print(result)
    if not result['sql']:
        await websocket.send_text(json.dumps({"output": "종료"}))
        await websocket.send_text(json.dumps({"output": result["answer"]}))
        return

    # Step 2: sql쿼리문 변환
    msg = {"output": "2.데이터 가져오기 준비중..."}
    await websocket.send_text(json.dumps(msg))

    result = chain_manager.run_chain(
        chain_type="sql_trans",
        model="gpt-4o-mini",
        user_input=user_input,
        stock_code=stock_code,
        memory=memory,
        now_date=now_date,
    )
    print(result)

    # Step 3: DB조회
    msg = {"output": "3.데이터 가져오는 중..."}
    await websocket.send_text(json.dumps(msg))

    queries = result['answer']
    docs = fetch_data(queries)
    print(docs)

    # Step 4: 결과를 바탕으로 답변 생성
    msg = {"output": "4.데이터 정리 중..."}
    await websocket.send_text(json.dumps(msg))

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(docs)
    print(len(tokens))
    if len(tokens) <= 15000:
        final_answer = chain_manager.run_chain(
            chain_type="final_answer",
            model="gpt-3.5-turbo-0125",
            user_input=user_input, 
            stock_name=stock_name, 
            memory=memory, 
            docs=docs,
        )
    else:
        final_answer = chain_manager.run_chain(
            chain_type="final_answer",
            model="gpt-4o-mini",
            user_input=user_input, 
            stock_name=stock_name, 
            memory=memory, 
            docs=docs,
        )
    print(final_answer)

    # Step 5: 최종 결과 전송
    result = {"output": final_answer}
    await websocket.send_text(json.dumps({"output": "종료"}))
    await websocket.send_text(json.dumps(result))
    return