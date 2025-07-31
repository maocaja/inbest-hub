from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
import asyncio
import json
import logging
from typing import Dict, Any, Optional

from services.document_processor import DocumentProcessor
from services.data_extractor import RealEstateDataExtractor
from services.data_validator import DataValidator
from models.schemas import (
    RealEstateProject,
    ExtractionRequest,
    ExtractionResponse,
    ValidationResult
)
from config import Config

load_dotenv()

# Configurar logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Real Estate Data Extractor Agent",
    description="Agente especializado en extraer información de proyectos inmobiliarios desde documentos PDF, DOCX y Excel",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_processor = DocumentProcessor()
data_extractor = RealEstateDataExtractor()
data_validator = DataValidator()

@app.get("/")
async def root():
    return {
        "message": "Real Estate Data Extractor Agent",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "real-estate-extractor"}

@app.post("/extract", response_model=ExtractionResponse)
async def extract_real_estate_data(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Extrae información de proyectos inmobiliarios desde documentos PDF, DOCX o Excel.
    """
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in Config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no soportado. Formatos permitidos: {', '.join(Config.ALLOWED_EXTENSIONS)}"
            )

        # Validate file size
        if file.size and file.size > Config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Archivo demasiado grande. Tamaño máximo: {Config.MAX_FILE_SIZE // (1024*1024)}MB"
            )

        logger.info(f"Procesando archivo: {file.filename} ({file.size} bytes)")

        # Process document
        content = await document_processor.process_document(file)
        
        # Extract real estate data
        extracted_data = await data_extractor.extract_project_data(content)
        
        # Validate extracted data
        validation_result = await data_validator.validate_project_data(extracted_data.dict())
        
        logger.info(f"Extracción completada para {file.filename}. Score: {validation_result.completeness_score}%")
        
        return ExtractionResponse(
            success=True,
            project_data=extracted_data,
            validation_result=validation_result,
            message="Datos extraídos exitosamente"
        )
        
    except Exception as e:
        logger.error(f"Error procesando {file.filename}: {str(e)}")
        return ExtractionResponse(
            success=False,
            project_data=None,
            validation_result=None,
            message=f"Error en la extracción: {str(e)}"
        )

@app.post("/validate")
async def validate_project_data(project_data: RealEstateProject):
    """
    Valida la información de un proyecto inmobiliario.
    """
    try:
        validation_result = await data_validator.validate_project_data(project_data.dict())
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/complete")
async def complete_project_data(project_data: RealEstateProject):
    """
    Completa información faltante en un proyecto inmobiliario usando IA.
    """
    try:
        completed_data = await data_extractor.complete_missing_data(project_data.dict())
        return completed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schema")
async def get_project_schema():
    """
    Retorna el esquema JSON del proyecto inmobiliario.
    """
    return RealEstateProject.schema()

if __name__ == "__main__":
    # Validar configuración
    config_errors = Config.validate_config()
    if config_errors:
        logger.error("Errores de configuración:")
        for error in config_errors:
            logger.error(f"  - {error}")
        exit(1)
    
    server_config = Config.get_server_config()
    logger.info(f"Iniciando servidor en {server_config['host']}:{server_config['port']}")
    
    uvicorn.run(
        "main:app",
        host=server_config['host'],
        port=server_config['port'],
        reload=server_config['reload']
    ) 