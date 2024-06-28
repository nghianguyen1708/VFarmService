from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class User(BaseModel):
    id: int
    username: str
    email: str  # New field
    full_name: Optional[str] = None  # New field
    created_at: datetime

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str
    email: str  # New field
    full_name: Optional[str] = None  # New field

class UserLogin(BaseModel):
    username: str
    password: str

class ChatBoxCreate(BaseModel):
    name: str

class ChatBox(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime

    class Config:
        orm_mode = True

class ChatMessageCreate(BaseModel):
    message: str
    sender: str

class ChatMessage(BaseModel):
    id: int
    chat_box_id: int
    message: str
    sender: str
    timestamp: datetime

    class Config:
        orm_mode = True

class ChatBoxDeleteResponse(BaseModel):
    result: bool