from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class IntentType(str, Enum):
    SEARCH_PROJECTS = "search_projects"
    GET_PROJECT_DETAILS = "get_project_details"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    HELP = "help"
    UNKNOWN = "unknown"

class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensaje del usuario")
    conversation_id: Optional[str] = Field(None, description="ID de conversación existente")
    user_id: Optional[str] = Field(None, description="ID del usuario")

class ChatResponse(BaseModel):
    conversation_id: str
    response: str = Field(..., description="Respuesta natural generada por LLM")
    projects: Optional[List[Dict[str, Any]]] = Field(None, description="Proyectos encontrados")
    suggestions: Optional[List[str]] = Field(None, description="Sugerencias para el usuario")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")

class ConversationInfo(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message: str
    status: str = "active"

class MessageInfo(BaseModel):
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class IntentAnalysis(BaseModel):
    type: IntentType
    confidence: float
    entities: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None

class ProjectInfo(BaseModel):
    id: int
    name: str
    location: str
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    amenities: Optional[List[str]] = None
    available_units: Optional[int] = None
    score: Optional[float] = None

class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    max_results: int = 10

class SearchResponse(BaseModel):
    results: List[ProjectInfo]
    total_results: int
    query: str
    filters_applied: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    services: Dict[str, str] 