from sqlalchemy import Column, String, DateTime, Integer, Text, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default="active")  # active, closed
    metadata_json = Column(JSON, default={})
    message_count = Column(Integer, default=0)
    
    # Relaciones
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    user = relationship("User", back_populates="conversations")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, default={})
    
    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    preferences = Column(JSON, default={})
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    conversations = relationship("Conversation", back_populates="user")

class ProjectInteraction(Base):
    __tablename__ = "project_interactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, nullable=False)
    interaction_type = Column(String, nullable=False)  # viewed, interested, contacted
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, default={})

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    status = Column(String, default="new")  # new, contacted, qualified, converted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project_interest = Column(JSON, default={})
    contact_info = Column(JSON, default={})
    
    # Relaciones
    user = relationship("User", backref="leads")
    conversation = relationship("Conversation", backref="leads") 