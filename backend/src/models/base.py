from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DbConnectionRequest(BaseModel):
    host: str
    port: int
    service_name: str
    user: str
    password: str
    session_id: str

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response_type: str
    data: dict
    session_id: str

class ExecuteRequest(BaseModel):
    session_id: str
    sql: str

class PreviewRequest(BaseModel):
    session_id: str
    sql: str

class PreviewResponse(BaseModel):
    description: str
    before_data: List[Dict[str, Any]]
    after_data: List[Dict[str, Any]]
    affected_rows: int
    sql: str
    warnings: List[str]

class UndoRequest(BaseModel):
    session_id: str

class RedoRequest(BaseModel):
    session_id: str

class HistoryRequest(BaseModel):
    session_id: str
    limit: Optional[int] = 50
