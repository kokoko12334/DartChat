import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.mark.asyncio
async def test_websocket_process_order():

    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        
        message_data = {
            "user_input": "삼성전자 2024년 매출액",
            "stock_name": "삼성전자",
            "stock_code": "005930",
            "memory": []
        }
        websocket.send_json(message_data)

        expected_messages = [
            "1.질문의도 분석중...",
            "2.데이터 쿼리 변환중...",
            "3.데이터 가져오는 중...",
            "4.데이터 정리 중...",
            "종료"
        ]
        
        for expected_output in expected_messages:
            response = websocket.receive_json()
            assert response["output"] == expected_output, f"Expected {expected_output}, but got {response['output']}"