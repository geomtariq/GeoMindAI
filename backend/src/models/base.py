from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response_type: str
    data: dict
    session_id: str
