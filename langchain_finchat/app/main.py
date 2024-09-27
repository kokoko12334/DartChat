import json
import pytz
from fastapi import FastAPI, WebSocket
from datetime import datetime
from services.functions import * 

app = FastAPI()
kst = pytz.timezone('Asia/Seoul')
current_time_kst = datetime.now(kst)
now_time = current_time_kst.strftime('%Y-%m-%d-%H-%M-%S')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()
    try:
        data = await websocket.receive_text()
        json_data = json.loads(data)

        user_input = json_data.get("user_input")
        stock_name = json_data.get("stock_name")
        stock_code = json_data.get("stock_code")
        memory = json_data.get("memory")
        # 최근 2개의 문답 내용만 포함
        memory_arr = [] 
        if memory:
            for i in range(min(2, len(memory)-1),-1,-1):
                memory_arr.append(f"question: {memory[i]['question']} => answer: {memory[i]['answer']}")
        memory = "\n".join(memory_arr)

        # Step 1: 질문 의도 분석
        msg = {"output": "1.질문의도 분석중..."}
        await websocket.send_text(json.dumps(msg))
        result = analyze_question(user_input, stock_code, memory)
        print(result)
        if not result['sql']:
            await websocket.send_text(json.dumps({"output": "종료"}))
            await websocket.send_text(json.dumps({"output": result["answer"]}))
            return

        # Step 2: sql쿼리문 변환
        msg = {"output": "2.데이터 쿼리 변환중..."}
        await websocket.send_text(json.dumps(msg))
        result = trans_query(user_input, stock_code, memory, now_time)
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
        final_answer = generate_final_answer(user_input, docs, stock_name, now_time)
        print(final_answer)

        # Step 5: 최종 결과 전송
        result = {"output": final_answer}
        await websocket.send_text(json.dumps({"output": "종료"}))
        await websocket.send_text(json.dumps(result))

    except Exception as e:
        print(e)
        await websocket.send_text(json.dumps({"output": "종료"}))
        await websocket.send_text(json.dumps({"output":"다시 시도해주세요."}))
    finally:
        await websocket.close()