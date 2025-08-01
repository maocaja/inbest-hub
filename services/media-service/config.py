import os
from typing import List
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    # Configuración de la aplicación
    APP_NAME = "Media Service"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Configuración del servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8005))
    
    # Configuración de la base de datos
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./media_service.db")
    
    # Configuración de almacenamiento
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB por defecto
    
    # Formatos soportados
    SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
    SUPPORTED_DOCUMENT_FORMATS = [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt"]
    SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS + SUPPORTED_DOCUMENT_FORMATS
    
    # Configuración de procesamiento de imágenes
    MAX_IMAGE_WIDTH = int(os.getenv("MAX_IMAGE_WIDTH", 1920))
    MAX_IMAGE_HEIGHT = int(os.getenv("MAX_IMAGE_HEIGHT", 1080))
    IMAGE_QUALITY = int(os.getenv("IMAGE_QUALITY", 85))
    
    # Configuración de seguridad
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Configuración de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_upload_path(cls, file_type: str = "general") -> str:
        """Obtiene la ruta de almacenamiento para un tipo de archivo"""
        path = os.path.join(cls.UPLOAD_DIR, file_type)
        os.makedirs(path, exist_ok=True)
        return path 