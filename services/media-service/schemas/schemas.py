from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class MediaFileBase(BaseModel):
    original_filename: str = Field(..., description="Nombre original del archivo")
    file_type: str = Field(..., description="Tipo de archivo (image, document, etc.)")
    mime_type: str = Field(..., description="Tipo MIME del archivo")
    file_size: int = Field(..., description="Tamaño del archivo en bytes")
    file_extension: str = Field(..., description="Extensión del archivo")
    
    # Metadatos opcionales
    width: Optional[int] = Field(None, description="Ancho de la imagen")
    height: Optional[int] = Field(None, description="Alto de la imagen")
    pages: Optional[int] = Field(None, description="Número de páginas del documento")
    duration: Optional[int] = Field(None, description="Duración del video en segundos")
    
    # Información de usuario/servicio
    uploaded_by: Optional[str] = Field(None, description="Usuario que subió el archivo")
    service_source: Optional[str] = Field(None, description="Servicio de origen")
    reference_id: Optional[str] = Field(None, description="ID de referencia")
    
    # Configuración de seguridad
    is_public: bool = Field(True, description="Si el archivo es público")
    access_token: Optional[str] = Field(None, description="Token de acceso")

class MediaFileCreate(MediaFileBase):
    pass

class MediaFileUpdate(BaseModel):
    is_public: Optional[bool] = None
    access_token: Optional[str] = None
    uploaded_by: Optional[str] = None
    service_source: Optional[str] = None
    reference_id: Optional[str] = None

class MediaFileResponse(MediaFileBase):
    id: int
    filename: str
    file_path: str
    is_processed: bool
    is_optimized: bool
    processing_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    file: Optional[MediaFileResponse] = None
    error: Optional[str] = None

class FileInfoResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    mime_type: str
    file_size: int
    file_extension: str
    width: Optional[int] = None
    height: Optional[int] = None
    pages: Optional[int] = None
    duration: Optional[int] = None
    is_processed: bool
    is_optimized: bool
    is_public: bool
    uploaded_by: Optional[str] = None
    service_source: Optional[str] = None
    reference_id: Optional[str] = None
    created_at: datetime
    download_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class FileProcessingLogResponse(BaseModel):
    id: int
    file_id: int
    operation: str
    status: str
    details: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class SupportedFormatsResponse(BaseModel):
    image_formats: list[str]
    document_formats: list[str]
    all_formats: list[str]
    max_file_size: int
    max_image_width: int
    max_image_height: int

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime
    database: str
    upload_directory: str 