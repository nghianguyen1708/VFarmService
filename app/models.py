from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

class ChatBox(Base):
    __tablename__ = 'chatboxes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    user = relationship("User", back_populates="chatboxes")

class ChatHistory(Base):
    __tablename__ = 'chathistory'
    id = Column(Integer, primary_key=True, index=True)
    chat_box_id = Column(Integer, ForeignKey('chatboxes.id'), nullable=False)
    message = Column(Text, nullable=False)
    sender = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    chat_box = relationship("ChatBox", back_populates="chathistory")

User.chatboxes = relationship("ChatBox", back_populates="user")
ChatBox.chathistory = relationship("ChatHistory", back_populates="chat_box")