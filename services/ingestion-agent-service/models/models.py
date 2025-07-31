"""
Modelos SQLAlchemy para Ingestion Agent Service
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base
from config import Config
import enum

class IngestionStatus(enum.Enum):
    """Estados posibles de una ingestión"""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ConversationSession(Base):
    """
    Modelo para sesiones de conversación
    """
    __tablename__ = "conversation_sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    project_id = Column(Integer, nullable=True)  # ID del proyecto asociado
    project_owner_nit = Column(String(20), nullable=True)  # NIT de la constructora
    
    # Estado de la conversación
    status = Column(String(50), default="active", nullable=False)
    current_step = Column(String(100), nullable=True)
    
    # Información del usuario
    user_id = Column(String(100), nullable=True)
    user_name = Column(String(100), nullable=True)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relación con mensajes
    messages = relationship("ConversationMessage", back_populates="session")
    
    def __repr__(self):
        return f"<ConversationSession(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"

class ConversationMessage(Base):
    """
    Modelo para mensajes de conversación
    """
    __tablename__ = "conversation_messages"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("conversation_sessions.session_id"), nullable=False)
    
    # Contenido del mensaje
    role = Column(String(20), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    
    # Metadatos del mensaje
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    message_type = Column(String(50), default="text")  # "text", "file", "action"
    
    # Información adicional
    message_metadata = Column(JSON, nullable=True)  # Datos adicionales del mensaje
    
    # Relación con sesión
    session = relationship("ConversationSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ConversationMessage(id={self.id}, role='{self.role}', session_id='{self.session_id}')>"

class DocumentUpload(Base):
    """
    Modelo para documentos subidos
    """
    __tablename__ = "document_uploads"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("conversation_sessions.session_id"), nullable=False)
    
    # Información del archivo
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=False)
    
    # Estado del procesamiento
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    extracted_data = Column(JSON, nullable=True)  # Datos extraídos del documento
    
    # Metadatos
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relación con sesión
    session = relationship("ConversationSession")
    
    def __repr__(self):
        return f"<DocumentUpload(id={self.id}, filename='{self.filename}', status='{self.processing_status}')>"

class IngestionTask(Base):
    """
    Modelo para tareas de ingestión
    """
    __tablename__ = "ingestion_tasks"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("conversation_sessions.session_id"), nullable=False)
    
    # Información de la tarea
    task_type = Column(String(100), nullable=False)  # "document_processing", "data_extraction", "project_creation"
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed
    
    # Datos de la tarea
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relación con sesión
    session = relationship("ConversationSession")
    
    def __repr__(self):
        return f"<IngestionTask(id={self.id}, type='{self.task_type}', status='{self.status}')>"

class ProjectDraft(Base):
    """
    Modelo para borradores de proyectos
    """
    __tablename__ = "project_drafts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("conversation_sessions.session_id"), nullable=False)
    
    # Datos del proyecto
    project_data = Column(JSON, nullable=False)  # Datos completos del proyecto
    completion_percentage = Column(Integer, default=0)  # Porcentaje de completitud
    
    # Estado del borrador
    status = Column(String(50), default="draft")  # draft, ready, published
    validation_errors = Column(JSON, nullable=True)  # Errores de validación
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relación con sesión
    session = relationship("ConversationSession")
    
    def __repr__(self):
        return f"<ProjectDraft(id={self.id}, completion='{self.completion_percentage}%', status='{self.status}')>" 