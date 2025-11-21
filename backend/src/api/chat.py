from fastapi import APIRouter
from src.models.base import ChatRequest, ChatResponse
from src.services.ai_orchestrator import ai_orchestrator
from src.services.sql_validator import sql_validator
from src.services.oracle_gateway import oracle_gateway

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Get SQL from AI Orchestrator
    sql = ai_orchestrator.process_query(request.message)

    # 2. Validate the SQL
    if not sql_validator.validate_read_only(sql):
        return ChatResponse(
            response_type="error",
            data={"message": "Only read-only queries are supported at this time."},
            session_id=request.session_id,
        )

    # 3. Execute the SQL
    try:
        results = oracle_gateway.execute_query(sql)
        return ChatResponse(
            response_type="data",
            data={"results": results, "sql": sql},
            session_id=request.session_id,
        )
    except Exception as e:
        return ChatResponse(
            response_type="error",
            data={"message": f"Error executing query: {e}"},
            session_id=request.session_id,
        )
