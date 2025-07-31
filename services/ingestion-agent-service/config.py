"""
Configuración centralizada para Ingestion Agent Service
"""

import os
from typing import List
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    """
    Configuración centralizada para el servicio de agente de ingestión
    """
    
    # Server Configuration
    PORT = int(os.getenv("PORT", 8004))
    HOST = os.getenv("HOST", "0.0.0.0")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    RELOAD = os.getenv("RELOAD", "True").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Database Configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./ingestion_agent.db"
    )
    
    # Development Configuration
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Cambiado a modelo más económico
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", 4000))
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
    
    # Mock LLM Configuration
    USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "True").lower() == "true"  # Activar modo simulado por defecto
    MOCK_LLM_ENABLED = os.getenv("MOCK_LLM_ENABLED", "True").lower() == "true"
    
    # External Services
    PROJECT_OWNERS_SERVICE_URL = os.getenv("PROJECT_OWNERS_SERVICE_URL", "http://localhost:8002")
    PROJECTS_SERVICE_URL = os.getenv("PROJECTS_SERVICE_URL", "http://localhost:8003")
    
    # File Upload Configuration
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
    ALLOWED_FILE_TYPES = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "image/jpeg",
        "image/png"
    ]
    
    # Chat Configuration
    MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", 50))
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 3600))  # 1 hour
    
    # Validation Rules
    MIN_PROJECT_NAME_LENGTH = 2
    MAX_PROJECT_NAME_LENGTH = 100
    MIN_DESCRIPTION_LENGTH = 10
    MAX_DESCRIPTION_LENGTH = 2000
    
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
        
        # Validar OpenAI API Key
        if not Config.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY es requerida")
        
        # Validar URLs de servicios externos
        if not Config.PROJECT_OWNERS_SERVICE_URL:
            errors.append("PROJECT_OWNERS_SERVICE_URL es requerida")
        if not Config.PROJECTS_SERVICE_URL:
            errors.append("PROJECTS_SERVICE_URL es requerida")
        
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
    
    @staticmethod
    def get_openai_config() -> dict:
        """
        Retorna configuración de OpenAI
        """
        return {
            "api_key": Config.OPENAI_API_KEY,
            "model": Config.OPENAI_MODEL,
            "max_tokens": Config.OPENAI_MAX_TOKENS,
            "temperature": Config.OPENAI_TEMPERATURE
        }
