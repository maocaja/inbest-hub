from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from database.database import Base

class MediaFile(Base):
    __tablename__ = "media_files"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # image, document, etc.
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_extension = Column(String(20), nullable=False)
    
    # Metadatos del archivo
    width = Column(Integer, nullable=True)  # Para imágenes
    height = Column(Integer, nullable=True)  # Para imágenes
    pages = Column(Integer, nullable=True)  # Para documentos
    duration = Column(Integer, nullable=True)  # Para videos
    
    # Información de procesamiento
    is_processed = Column(Boolean, default=False)
    is_optimized = Column(Boolean, default=False)
    processing_metadata = Column(JSON, nullable=True)
    
    # Información de seguridad
    is_public = Column(Boolean, default=True)
    access_token = Column(String(255), nullable=True)
    
    # Información de usuario/servicio
    uploaded_by = Column(String(100), nullable=True)
    service_source = Column(String(100), nullable=True)  # ingestion-agent, projects, etc.
    reference_id = Column(String(100), nullable=True)  # ID del proyecto, constructora, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<MediaFile(id={self.id}, filename='{self.filename}', type='{self.file_type}')>"

class FileProcessingLog(Base):
    __tablename__ = "file_processing_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, nullable=False)
    operation = Column(String(100), nullable=False)  # upload, optimize, resize, etc.
    status = Column(String(50), nullable=False)  # success, failed, processing
    details = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<FileProcessingLog(id={self.id}, file_id={self.file_id}, operation='{self.operation}')>" 