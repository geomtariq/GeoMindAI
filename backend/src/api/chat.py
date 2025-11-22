from fastapi import APIRouter
from src.models.base import ChatRequest, ChatResponse
from src.services.ai_orchestrator import ai_orchestrator
from src.services.sql_validator import sql_validator
from src.services.oracle_gateway import oracle_gateway

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Get SQL and intent from AI Orchestrator
    ai_response = ai_orchestrator.process_query(request.message)
    sql = ai_response["sql"]
    intent = ai_response["intent"]

    # 2. Handle different intents
    if intent == 'read':
        if not sql_validator.validate_read_only(sql):
            return ChatResponse(
                response_type="error",
                data={"message": "The generated query is not a valid read-only query."},
                session_id=request.session_id,
            )
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
    elif intent == 'write':
        if not sql_validator.validate_write(sql):
            return ChatResponse(
                response_type="error",
                data={"message": "The generated query is not a valid write query."},
                session_id=request.session_id,
            )
        # For write queries, return the SQL for approval
        return ChatResponse(
            response_type="sql_approval",
            data={"sql": sql},
            session_id=request.session_id,
        )
    else:
        return ChatResponse(
            response_type="error",
            data={"message": "Could not determine the intent of the query."},
            session_id=request.session_id,
        )

# TODO: Create a new endpoint to handle the approved SQL, e.g., /execute_write
