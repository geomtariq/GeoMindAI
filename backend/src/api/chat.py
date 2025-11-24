from fastapi import APIRouter, HTTPException
from models.base import (
    DbConnectionRequest, ChatRequest, ChatResponse, ExecuteRequest,
    PreviewRequest, PreviewResponse, UndoRequest, RedoRequest, HistoryRequest
)
from services.ai_orchestrator import ai_orchestrator
from services.sql_validator import sql_validator
from services.oracle_gateway import oracle_gateway
from services.operation_history import operation_history
import logging
from datetime import datetime
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/connect")
async def connect_to_db(request: DbConnectionRequest):
    logger.info(f"Connection request for session: {request.session_id}")
    try:
        db_config = request.model_dump()
        oracle_gateway.create_pool_for_session(request.session_id, db_config)
        
        # Dynamic Schema Discovery
        try:
            logger.info(f"Discovering schema for session {request.session_id}...")
            metadata = oracle_gateway.get_schema_metadata()
            ai_orchestrator.update_schema_context(metadata)
            logger.info("Schema discovery completed and AI context updated.")
        except Exception as e:
            logger.error(f"Schema discovery failed: {e}")
            # Don't fail the connection if schema discovery fails, just log it
            
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

        # Comprehensive validation
        validation = sql_validator.validate_comprehensive(sql, intent)
        
        if not validation["is_valid"]:
            logger.warning(f"Invalid query: {validation['errors']}")
            return ChatResponse(
                response_type="error", 
                data={"message": f"Invalid query: {'; '.join(validation['errors'])}"}, 
                session_id=request.session_id
            )

        if intent == 'read':
            results = oracle_gateway.execute_query(request.session_id, sql)
            logger.info(f"Query executed successfully for session {request.session_id}")
            return ChatResponse(
                response_type="data", 
                data={
                    "results": results, 
                    "sql": sql,
                    "complexity": validation["metadata"].get("complexity", "LOW"),
                    "warnings": validation["warnings"]
                }, 
                session_id=request.session_id
            )
        
        elif intent == 'write':
            # Return for approval with warnings
            return ChatResponse(
                response_type="sql_approval", 
                data={
                    "sql": sql,
                    "warnings": validation["warnings"],
                    "requires_extra_confirmation": validation["metadata"].get("requires_extra_confirmation", False)
                }, 
                session_id=request.session_id
            )

        else:
            logger.warning(f"Unknown intent: {intent}")
            return ChatResponse(
                response_type="error", 
                data={"message": "Could not determine query intent."}, 
                session_id=request.session_id
            )

    except Exception as e:
        logger.error(f"Error processing chat request for session {request.session_id}: {e}", exc_info=True)
        return ChatResponse(
            response_type="error", 
            data={"message": str(e)}, 
            session_id=request.session_id
        )

@router.post("/preview", response_model=PreviewResponse)
async def preview_operation(request: PreviewRequest):
    """Preview a write operation without executing it."""
    logger.info(f"Preview request for session {request.session_id}: {request.sql}")
    try:
        # Capture before snapshot
        before_snapshot = operation_history.capture_snapshot(
            request.session_id, 
            request.sql, 
            oracle_gateway
        )
        
        # Simulate operation to get after state
        after_data = oracle_gateway.simulate_query(request.sql)
        
        # If simulation returned empty (write operation), get the modified data
        if not after_data:
            # For write operations, get the data that would be affected
            after_data = before_snapshot["affected_rows"]
        
        # Generate description
        description = operation_history.generate_description(
            request.sql, 
            before_snapshot, 
            {"affected_rows": after_data}
        )
        
        # Validate and get warnings
        validation = sql_validator.validate_comprehensive(request.sql, "write")
        
        return PreviewResponse(
            description=description,
            before_data=before_snapshot["affected_rows"],
            after_data=after_data,
            affected_rows=before_snapshot["row_count"],
            sql=request.sql,
            warnings=validation["warnings"]
        )
        
    except Exception as e:
        logger.error(f"Preview failed for session {request.session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

@router.post("/execute_approved")
async def execute_approved(request: ExecuteRequest):
    """Execute an approved write operation with history tracking."""
    logger.info(f"Execution request for session {request.session_id}: {request.sql}")
    try:
        # Validate again
        if not sql_validator.validate_write(request.sql):
            logger.warning(f"Invalid write query attempted in execution: {request.sql}")
            raise HTTPException(status_code=400, detail="Invalid write query.")

        # Capture before snapshot
        before_snapshot = operation_history.capture_snapshot(
            request.session_id, 
            request.sql, 
            oracle_gateway
        )
        
        # Execute
        oracle_gateway.execute_query(request.session_id, request.sql)
        
        # Capture after snapshot
        after_snapshot = operation_history.capture_snapshot(
            request.session_id, 
            request.sql, 
            oracle_gateway
        )
        
        # Determine operation type
        sql_upper = request.sql.upper()
        if "INSERT" in sql_upper:
            op_type = "INSERT"
        elif "UPDATE" in sql_upper:
            op_type = "UPDATE"
        elif "DELETE" in sql_upper:
            op_type = "DELETE"
        else:
            op_type = "OTHER"
        
        # Generate description
        description = operation_history.generate_description(
            request.sql, 
            before_snapshot, 
            after_snapshot
        )
        
        # Record operation
        operation = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "sql": request.sql,
            "operation_type": op_type,
            "description": description,
            "before_snapshot": before_snapshot,
            "after_snapshot": after_snapshot,
            "affected_rows": before_snapshot["row_count"],
            "can_undo": True
        }
        
        operation_history.record_operation(request.session_id, operation)
        
        logger.info(f"Write query executed successfully for session {request.session_id}")
        
        return {
            "status": "success", 
            "message": "Operation executed successfully.",
            "operation_id": operation["id"],
            "description": description,
            "before_data": before_snapshot["affected_rows"],
            "after_data": after_snapshot["affected_rows"]
        }

    except Exception as e:
        logger.error(f"Execution failed for session {request.session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@router.post("/undo")
async def undo_operation(request: UndoRequest):
    """Undo the last operation."""
    logger.info(f"Undo request for session {request.session_id}")
    try:
        result = operation_history.undo_last(request.session_id, oracle_gateway)
        
        if result:
            return {
                "status": "success",
                "message": f"Undone: {result['undone_operation']['description']}",
                "operation": result['undone_operation'],
                "undo_sql": result['undo_sql']
            }
        else:
            return {
                "status": "error",
                "message": "No operations to undo"
            }
    except Exception as e:
        logger.error(f"Undo failed for session {request.session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Undo failed: {str(e)}")

@router.post("/redo")
async def redo_operation(request: RedoRequest):
    """Redo the last undone operation."""
    logger.info(f"Redo request for session {request.session_id}")
    try:
        result = operation_history.redo_last(request.session_id, oracle_gateway)
        
        if result:
            return {
                "status": "success",
                "message": f"Redone: {result['redone_operation']['description']}",
                "operation": result['redone_operation'],
                "redo_sql": result['redo_sql']
            }
        else:
            return {
                "status": "error",
                "message": "No operations to redo"
            }
    except Exception as e:
        logger.error(f"Redo failed for session {request.session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Redo failed: {str(e)}")

@router.get("/history")
async def get_history(session_id: str, limit: int = 50):
    """Get operation history for a session."""
    logger.info(f"History request for session {session_id}")
    try:
        history = operation_history.get_history(session_id, limit)
        return {
            "status": "success",
            "operations": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"History retrieval failed for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")
