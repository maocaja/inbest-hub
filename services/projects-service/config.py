"""
Configuración centralizada para Projects Service
"""

import os
from typing import List

class Config:
    """
    Configuración centralizada para el servicio de proyectos
    """
    
    # Server Configuration
    PORT = int(os.getenv("PORT", 8003))
    HOST = os.getenv("HOST", "0.0.0.0")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    RELOAD = os.getenv("RELOAD", "True").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Database Configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./projects.db"
    )
    
    # Development Configuration
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Services URLs
    PROJECT_OWNERS_SERVICE_URL = os.getenv("PROJECT_OWNERS_SERVICE_URL", "http://localhost:8002")
    EMBEDDING_SERVICE_URL = os.getenv("EMBEDDING_SERVICE_URL", "http://localhost:8005")
    
    # Validation Rules
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    MIN_DESCRIPTION_LENGTH = 10
    MAX_DESCRIPTION_LENGTH = 2000
    
    # Project States
    PROJECT_STATES = [
        "incompleto",
        "en_proceso", 
        "completo",
        "inactivo",
        "archivado"
    ]
    
    # Validation Settings
    NAME_UNIQUE = True
    PROJECT_OWNER_REQUIRED = True
    
    @staticmethod
    def validate_config() -> List[str]:
        """
        Valida la configuración y retorna lista de errores
        """
        errors = []
        
        # Validar puerto
        if Config.PORT < 1 or Config.PORT > 65535:
            errors.append("PORT debe estar entre 1 y 65535")
        
        # Validar niveles de log
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if Config.LOG_LEVEL not in valid_log_levels:
            errors.append(f"LOG_LEVEL debe ser uno de: {valid_log_levels}")
        
        # Validar estados de proyecto
        if not all(state in Config.PROJECT_STATES for state in Config.PROJECT_STATES):
            errors.append("PROJECT_STATES debe contener estados válidos")
        
        return errors
    
    @staticmethod
    def get_server_config() -> dict:
        """
        Retorna configuración del servidor
        """
        return {
            "host": Config.HOST,
            "port": Config.PORT,
            "debug": Config.DEBUG,
            "reload": Config.RELOAD
        }
    
    @staticmethod
    def get_database_config() -> dict:
        """
        Retorna configuración de base de datos
        """
        return {
            "url": Config.DATABASE_URL,
            "environment": Config.ENVIRONMENT
        }
