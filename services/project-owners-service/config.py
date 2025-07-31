"""
Configuración del Project Owners Service
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración principal del servicio"""
    
    # Server Configuration
    PORT = int(os.getenv("PORT", 8002))
    HOST = os.getenv("HOST", "0.0.0.0")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    RELOAD = os.getenv("RELOAD", "True").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Database Configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./project_owners.db"
    )
    
    # Validation Configuration
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    MIN_NIT_LENGTH = 8
    MAX_NIT_LENGTH = 20
    
    # Business Rules
    NIT_UNIQUE = True
    EMAIL_UNIQUE = True
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """
        Valida la configuración y retorna errores si los hay
        """
        errors = []
        
        if cls.PORT < 1 or cls.PORT > 65535:
            errors.append("PORT debe estar entre 1 y 65535")
        
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL no está configurada")
        
        return errors
    
    @classmethod
    def get_server_config(cls) -> Dict[str, Any]:
        """
        Retorna la configuración del servidor
        """
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "debug": cls.DEBUG,
            "reload": cls.RELOAD
        }
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """
        Retorna la configuración de la base de datos
        """
        return {
            "url": cls.DATABASE_URL,
            "echo": cls.DEBUG
        } 