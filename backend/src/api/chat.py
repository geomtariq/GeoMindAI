from fastapi import APIRouter, HTTPException
from models.base import DbConnectionRequest, ChatRequest, ChatResponse
from services.ai_orchestrator import ai_orchestrator
from services.sql_validator import sql_validator
from services.oracle_gateway import oracle_gateway
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/connect")
async def connect_to_db(request: DbConnectionRequest):
    logger.info(f"Connection request for session: {request.session_id}")
    try:
        db_config = request.model_dump()
        oracle_gateway.create_pool_for_session(request.session_id, db_config)
        logger.info(f"Successfully connected session: {request.session_id}")
        return {"status": "success", "message": "Database connection successful."}
    except Exception as e:
        logger.error(f"Connection failed for session {request.session_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Database connection failed: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Chat request for session {request.session_id}: {request.message}")
    try:
        ai_response = ai_orchestrator.process_query(request.message)
        sql, intent = ai_response["sql"], ai_response["intent"]
        logger.info(f"AI Intent: {intent}, SQL: {sql}")

        if intent == 'read':
            if not sql_validator.validate_read_only(sql):
                logger.warning(f"Invalid read-only query attempted: {sql}")
                return ChatResponse(response_type="error", data={"message": "Invalid read-only query."}, session_id=request.session_id)
            
            results = oracle_gateway.execute_query(request.session_id, sql)
            logger.info(f"Query executed successfully for session {request.session_id}")
            return ChatResponse(response_type="data", data={"results": results, "sql": sql}, session_id=request.session_id)
        
        elif intent == 'write':
            if not sql_validator.validate_write(sql):
                logger.warning(f"Invalid write query attempted: {sql}")
                return ChatResponse(response_type="error", data={"message": "Invalid write query."}, session_id=request.session_id)
            return ChatResponse(response_type="sql_approval", data={"sql": sql}, session_id=request.session_id)

        else:
            logger.warning(f"Unknown intent: {intent}")
            return ChatResponse(response_type="error", data={"message": "Could not determine query intent."}, session_id=request.session_id)

    except Exception as e:
        logger.error(f"Error processing chat request for session {request.session_id}: {e}", exc_info=True)
        return ChatResponse(response_type="error", data={"message": str(e)}, session_id=request.session_id)
