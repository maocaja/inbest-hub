import os
import logging
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

from config import Config
from database.database import get_db, create_tables
from models.models import MediaFile, FileProcessingLog
from schemas.schemas import (
    FileUploadResponse, FileInfoResponse, FileProcessingLogResponse,
    SupportedFormatsResponse, HealthCheckResponse
)
from services.file_service import FileService

# Configurar logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title=Config.APP_NAME,
    version=Config.APP_VERSION,
    description="Servicio de gestión de archivos multimedia para el backend inmobiliario"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas al iniciar
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info(f"{Config.APP_NAME} iniciado en puerto {Config.PORT}")

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz"""
    return {
        "service": Config.APP_NAME,
        "version": Config.APP_VERSION,
        "status": "running"
    }

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check del servicio"""
    return HealthCheckResponse(
        status="healthy",
        service=Config.APP_NAME,
        version=Config.APP_VERSION,
        timestamp=datetime.now(),
        database="SQLite",
        upload_directory=Config.UPLOAD_DIR
    )

@app.get("/supported-formats", response_model=SupportedFormatsResponse, tags=["Info"])
async def get_supported_formats():
    """Obtiene los formatos de archivo soportados"""
    return SupportedFormatsResponse(
        image_formats=Config.SUPPORTED_IMAGE_FORMATS,
        document_formats=Config.SUPPORTED_DOCUMENT_FORMATS,
        all_formats=Config.SUPPORTED_FORMATS,
        max_file_size=Config.MAX_FILE_SIZE,
        max_image_width=Config.MAX_IMAGE_WIDTH,
        max_image_height=Config.MAX_IMAGE_HEIGHT
    )

@app.post("/upload", response_model=FileUploadResponse, tags=["Files"])
async def upload_file(
    file: UploadFile = File(...),
    uploaded_by: Optional[str] = Form(None),
    service_source: Optional[str] = Form(None),
    reference_id: Optional[str] = Form(None),
    is_public: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Sube un archivo al servidor
    """
    try:
        file_service = FileService(db)
        media_file = await file_service.upload_file(
            file=file,
            uploaded_by=uploaded_by,
            service_source=service_source,
            reference_id=reference_id,
            is_public=is_public
        )
        
        return FileUploadResponse(
            success=True,
            message="Archivo subido exitosamente",
            file=media_file
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en upload: {str(e)}")
        return FileUploadResponse(
            success=False,
            message="Error subiendo archivo",
            error=str(e)
        )

@app.get("/files/{file_id}", response_model=FileInfoResponse, tags=["Files"])
async def get_file_info(file_id: int, db: Session = Depends(get_db)):
    """
    Obtiene información de un archivo
    """
    file_service = FileService(db)
    file_info = file_service.get_file_info(file_id)
    
    if not file_info:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileInfoResponse(**file_info)

@app.get("/files", tags=["Files"])
async def list_files(
    file_type: Optional[str] = Query(None, description="Tipo de archivo"),
    service_source: Optional[str] = Query(None, description="Servicio de origen"),
    reference_id: Optional[str] = Query(None, description="ID de referencia"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: Session = Depends(get_db)
):
    """
    Lista archivos con filtros opcionales
    """
    file_service = FileService(db)
    files = file_service.list_files(
        file_type=file_type,
        service_source=service_source,
        reference_id=reference_id,
        limit=limit,
        offset=offset
    )
    
    return {
        "files": [FileInfoResponse(**file_service.get_file_info(f.id)) for f in files],
        "total": len(files),
        "limit": limit,
        "offset": offset
    }

@app.get("/files/{file_id}/download", tags=["Files"])
async def download_file(file_id: int, db: Session = Depends(get_db)):
    """
    Descarga un archivo
    """
    file_service = FileService(db)
    media_file = file_service.get_file_by_id(file_id)
    
    if not media_file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    if not os.path.exists(media_file.file_path):
        raise HTTPException(status_code=404, detail="Archivo físico no encontrado")
    
    return FileResponse(
        path=media_file.file_path,
        filename=media_file.original_filename,
        media_type=media_file.mime_type
    )

@app.get("/files/{file_id}/thumbnail", tags=["Files"])
async def get_thumbnail(file_id: int, db: Session = Depends(get_db)):
    """
    Obtiene la miniatura de una imagen
    """
    file_service = FileService(db)
    media_file = file_service.get_file_by_id(file_id)
    
    if not media_file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    if media_file.file_type != "image":
        raise HTTPException(status_code=400, detail="Solo imágenes tienen miniaturas")
    
    # Buscar miniatura en metadatos
    thumbnail_path = None
    if media_file.processing_metadata and "thumbnail_path" in media_file.processing_metadata:
        thumbnail_path = media_file.processing_metadata["thumbnail_path"]
    
    if not thumbnail_path or not os.path.exists(thumbnail_path):
        raise HTTPException(status_code=404, detail="Miniatura no encontrada")
    
    return FileResponse(
        path=thumbnail_path,
        media_type="image/jpeg"
    )

@app.put("/files/{file_id}", tags=["Files"])
async def update_file(
    file_id: int,
    is_public: Optional[bool] = None,
    access_token: Optional[str] = None,
    uploaded_by: Optional[str] = None,
    service_source: Optional[str] = None,
    reference_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Actualiza información de un archivo
    """
    from schemas.schemas import MediaFileUpdate
    
    file_service = FileService(db)
    update_data = MediaFileUpdate(
        is_public=is_public,
        access_token=access_token,
        uploaded_by=uploaded_by,
        service_source=service_source,
        reference_id=reference_id
    )
    
    media_file = file_service.update_file(file_id, update_data)
    if not media_file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return {"message": "Archivo actualizado exitosamente", "file_id": file_id}

@app.delete("/files/{file_id}", tags=["Files"])
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    """
    Elimina un archivo
    """
    file_service = FileService(db)
    success = file_service.delete_file(file_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return {"message": "Archivo eliminado exitosamente", "file_id": file_id}

@app.get("/processing-logs", response_model=List[FileProcessingLogResponse], tags=["Logs"])
async def get_processing_logs(
    file_id: Optional[int] = Query(None, description="ID del archivo"),
    operation: Optional[str] = Query(None, description="Tipo de operación"),
    status: Optional[str] = Query(None, description="Estado de la operación"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Obtiene logs de procesamiento de archivos
    """
    query = db.query(FileProcessingLog)
    
    if file_id:
        query = query.filter(FileProcessingLog.file_id == file_id)
    
    if operation:
        query = query.filter(FileProcessingLog.operation == operation)
    
    if status:
        query = query.filter(FileProcessingLog.status == status)
    
    logs = query.offset(offset).limit(limit).all()
    
    return [FileProcessingLogResponse.from_orm(log) for log in logs]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    ) 