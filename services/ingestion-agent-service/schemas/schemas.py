"""
Esquemas Pydantic para Ingestion Agent Service
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    """Roles de mensaje en la conversación"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageType(str, Enum):
    """Tipos de mensaje"""
    TEXT = "text"
    FILE = "file"
    ACTION = "action"

class SessionStatus(str, Enum):
    """Estados de sesión"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskStatus(str, Enum):
    """Estados de tarea"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentProcessingStatus(str, Enum):
    """Estados de procesamiento de documentos"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Schemas para mensajes
class MessageBase(BaseModel):
    """Esquema base para mensajes"""
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    metadata: Optional[Dict[str, Any]] = None

class MessageCreate(MessageBase):
    """Esquema para crear mensaje"""
    session_id: str

class MessageResponse(MessageBase):
    """Esquema de respuesta para mensajes"""
    id: int
    session_id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Schemas para sesiones
class SessionBase(BaseModel):
    """Esquema base para sesiones"""
    project_owner_nit: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None

class SessionCreate(SessionBase):
    """Esquema para crear sesión"""
    pass

class SessionResponse(SessionBase):
    """Esquema de respuesta para sesiones"""
    id: int
    session_id: str
    project_id: Optional[int] = None
    status: SessionStatus
    current_step: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_activity: datetime
    
    class Config:
        from_attributes = True

# Schemas para documentos
class DocumentUploadBase(BaseModel):
    """Esquema base para documentos"""
    filename: str
    file_size: int
    file_type: str

class DocumentUploadCreate(DocumentUploadBase):
    """Esquema para crear documento"""
    session_id: str
    file_path: str

class DocumentUploadResponse(DocumentUploadBase):
    """Esquema de respuesta para documentos"""
    id: int
    session_id: str
    file_path: str
    processing_status: DocumentProcessingStatus
    extracted_data: Optional[Dict[str, Any]] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para tareas
class TaskBase(BaseModel):
    """Esquema base para tareas"""
    task_type: str
    input_data: Optional[Dict[str, Any]] = None

class TaskCreate(TaskBase):
    """Esquema para crear tarea"""
    session_id: str

class TaskResponse(TaskBase):
    """Esquema de respuesta para tareas"""
    id: int
    session_id: str
    status: TaskStatus
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para borradores de proyectos
class ProjectDraftBase(BaseModel):
    """Esquema base para borradores"""
    project_data: Dict[str, Any]
    completion_percentage: int = Field(ge=0, le=100)

class ProjectDraftCreate(ProjectDraftBase):
    """Esquema para crear borrador"""
    session_id: str

class ProjectDraftResponse(ProjectDraftBase):
    """Esquema de respuesta para borradores"""
    id: int
    session_id: str
    status: str
    validation_errors: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schemas para ingestión
class IngestionStartRequest(BaseModel):
    """Esquema para iniciar ingestión"""
    project_owner_nit: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None

class IngestionStartResponse(BaseModel):
    """Esquema de respuesta para inicio de ingestión"""
    session_id: str
    status: str
    message: str

class ChatMessageRequest(BaseModel):
    """Esquema para mensaje de chat"""
    session_id: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    """Esquema de respuesta para mensaje de chat"""
    session_id: str
    assistant_message: str
    project_updates: Optional[Dict[str, Any]] = None
    missing_fields: Optional[List[str]] = None
    status: str
    actions: Optional[List[str]] = None

class IngestionStatusResponse(BaseModel):
    """Esquema de respuesta para estado de ingestión"""
    session_id: str
    status: str
    completion_percentage: int
    current_step: Optional[str] = None
    project_data: Optional[Dict[str, Any]] = None
    missing_fields: Optional[List[str]] = None

class FileUploadRequest(BaseModel):
    """Esquema para subida de archivo"""
    session_id: str
    filename: str
    file_size: int
    file_type: str

class FileUploadResponse(BaseModel):
    """Esquema de respuesta para subida de archivo"""
    upload_id: int
    processing_status: str
    extracted_data: Optional[Dict[str, Any]] = None
    message: str

# Schemas para tool calling
class ToolCallRequest(BaseModel):
    """Esquema para llamada de herramienta"""
    tool_name: str
    parameters: Dict[str, Any]

class ToolCallResponse(BaseModel):
    """Esquema de respuesta para llamada de herramienta"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None

# Schemas para validación
class ValidationError(BaseModel):
    """Esquema para errores de validación"""
    field: str
    message: str
    value: Optional[Any] = None

class ProjectValidationResponse(BaseModel):
    """Esquema de respuesta para validación de proyecto"""
    is_valid: bool
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    completion_percentage: int 