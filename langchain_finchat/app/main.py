import json
from fastapi import FastAPI, WebSocket
from service.fin_chat_service import process_finchat

app = FastAPI()

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
        await process_finchat(user_input, stock_name, stock_code, memory, websocket)

    except Exception as e:
        print(e)
        await websocket.send_text(json.dumps({"output": "종료"}))
        await websocket.send_text(json.dumps({"output":"다시 시도해주세요."}))
    finally:
        await websocket.close()