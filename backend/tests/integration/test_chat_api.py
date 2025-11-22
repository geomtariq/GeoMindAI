import pytest
from httpx import AsyncClient
from main import app
from unittest.mock import patch

@pytest.mark.asyncio
async def test_chat_read_intent():
    with patch('services.ai_orchestrator.ai_orchestrator.process_query') as mock_process_query, \
         patch('services.oracle_gateway.oracle_gateway.execute_query') as mock_execute_query:

        mock_process_query.return_value = {"intent": "read", "sql": "SELECT * FROM DUAL"}
        mock_execute_query.return_value = [{"DUMMY": "X"}]

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/chat", json={"message": "test", "session_id": "123"})

        assert response.status_code == 200
        data = response.json()
        assert data["response_type"] == "data"
        assert data["data"]["results"] == [{"DUMMY": "X"}]

@pytest.pytest.mark.asyncio
async def test_chat_write_intent():
    with patch('src.services.ai_orchestrator.ai_orchestrator.process_query') as mock_process_query:

        mock_process_query.return_value = {"intent": "write", "sql": "UPDATE DUAL SET DUMMY = 'Y'"}

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/chat", json={"message": "test", "session_id": "123"})

        assert response.status_code == 200
        data = response.json()
        assert data["response_type"] == "sql_approval"
        assert data["data"]["sql"] == "UPDATE DUAL SET DUMMY = 'Y'"
