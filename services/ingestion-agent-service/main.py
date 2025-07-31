"""
Aplicación principal de FastAPI para Ingestion Agent Service
"""

import logging
import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from database.database import get_db, engine
from models.models import Base
from schemas.schemas import (
    IngestionStartRequest, IngestionStartResponse,
    ChatMessageRequest, ChatMessageResponse,
    IngestionStatusResponse, FileUploadResponse
)
from services.ingestion_service import IngestionService
from config import Config

# Configurar logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Ingestion Agent Service",
    description="Servicio de agente conversacional para ingestión de proyectos inmobiliarios",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciar servicios
ingestion_service = IngestionService()

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("Ingestion Agent Service starting up...")
    
    # Validar configuración
    config_errors = Config.validate_config()
    if config_errors:
        logger.error(f"Configuration errors: {config_errors}")
        raise ValueError(f"Configuration errors: {config_errors}")
    
    logger.info("Configuration validated successfully")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Ingestion Agent Service API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ingestion-agent-service",
        "version": "1.0.0"
    }

@app.post("/ingest/start", response_model=IngestionStartResponse)
async def start_ingestion(
    request: IngestionStartRequest,
    db: Session = Depends(get_db)
):
    """
    Iniciar una nueva sesión de ingestión
    """
    try:
        result = ingestion_service.create_session(db, request)
        
        if result["success"]:
            logger.info(f"Nueva sesión de ingestión iniciada: {result['session_id']}")
            return IngestionStartResponse(
                session_id=result["session_id"],
                status="started",
                message=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error iniciando ingestión: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@app.post("/ingest/message", response_model=ChatMessageResponse)
async def process_chat_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Procesar mensaje de chat del usuario
    """
    try:
        result = ingestion_service.process_message(
            db, 
            request.session_id, 
            request.message, 
            request.metadata
        )
        
        if result["success"]:
            logger.info(f"Mensaje procesado para sesión: {request.session_id}")
            return ChatMessageResponse(
                session_id=result["session_id"],
                assistant_message=result["assistant_message"],
                project_updates=result.get("project_updates"),
                missing_fields=result.get("missing_fields"),
                status=result.get("status", "active"),
                actions=result.get("actions")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando mensaje: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@app.get("/ingest/status/{session_id}", response_model=IngestionStatusResponse)
async def get_ingestion_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtener estado de una sesión de ingestión
    """
    try:
        result = ingestion_service.get_session_status(db, session_id)
        
        if result["success"]:
            return IngestionStatusResponse(
                session_id=result["session_id"],
                status=result["status"],
                completion_percentage=result["completion_percentage"],
                current_step=result["current_step"],
                project_data=result["project_data"],
                missing_fields=result["missing_fields"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@app.post("/ingest/upload", response_model=FileUploadResponse)
async def upload_document(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Subir y procesar documento
    """
    try:
        # Validar archivo
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo no válido"
            )
        
        # Crear directorio temporal si no existe
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Guardar archivo temporalmente
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Procesar documento
            result = ingestion_service.upload_document(
                db, 
                session_id, 
                file_path, 
                file.filename
            )
            
            if result["success"]:
                logger.info(f"Documento procesado: {file.filename} para sesión: {session_id}")
                return FileUploadResponse(
                    upload_id=result["upload_id"],
                    processing_status=result["processing_status"],
                    extracted_data=result.get("extracted_data"),
                    message=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"]
                )
                
        finally:
            # Limpiar archivo temporal
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo documento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@app.post("/ingest/generate-description")
async def generate_project_description(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Generar descripción del proyecto
    """
    try:
        result = ingestion_service._generate_description(db, session_id)
        
        if result["success"]:
            logger.info(f"Descripción generada para sesión: {session_id}")
            return {
                "success": True,
                "description": result["description"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando descripción: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@app.get("/ingest/supported-formats")
async def get_supported_formats():
    """
    Obtener formatos de archivo soportados
    """
    try:
        formats = ingestion_service.document_processor.get_supported_formats()
        return {
            "supported_formats": formats,
            "max_file_size": Config.MAX_FILE_SIZE,
            "allowed_file_types": Config.ALLOWED_FILE_TYPES
        }
    except Exception as e:
        logger.error(f"Error obteniendo formatos soportados: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@app.get("/ingest/sessions/{session_id}/history")
async def get_conversation_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Obtener historial de conversación
    """
    try:
        from models.models import ConversationMessage
        
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        ).order_by(ConversationMessage.timestamp.desc()).limit(limit).all()
        
        history = []
        for message in reversed(messages):  # Ordenar cronológicamente
            history.append({
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "message_type": message.message_type,
                "metadata": message.message_metadata
            })
        
        return {
            "session_id": session_id,
            "messages": history,
            "total_messages": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@app.get("/ingest/sessions/{session_id}/documents")
async def get_session_documents(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtener documentos de una sesión
    """
    try:
        from models.models import DocumentUpload
        
        documents = db.query(DocumentUpload).filter(
            DocumentUpload.session_id == session_id
        ).order_by(DocumentUpload.uploaded_at.desc()).all()
        
        docs = []
        for doc in documents:
            docs.append({
                "id": doc.id,
                "filename": doc.filename,
                "file_size": doc.file_size,
                "file_type": doc.file_type,
                "processing_status": doc.processing_status,
                "uploaded_at": doc.uploaded_at.isoformat(),
                "processed_at": doc.processed_at.isoformat() if doc.processed_at else None
            })
        
        return {
            "session_id": session_id,
            "documents": docs,
            "total_documents": len(docs)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo documentos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

if __name__ == "__main__":
    import uvicorn
    
    # Crear tablas en la base de datos
    Base.metadata.create_all(bind=engine)
    
    # Configuración del servidor
    server_config = Config.get_server_config()
    
    # Ejecutar servidor
    uvicorn.run(
        "main:app",
        host=server_config["host"],
        port=server_config["port"],
        reload=server_config["reload"],
        log_level=Config.LOG_LEVEL.lower()
    )
