from pydantic import BaseModel

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
