import os
from typing import Optional

class Config:
    # Servidor
    PORT = int(os.getenv("PORT", 8006))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    
    # Base de datos
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat_api.db")
    
    # Servicios externos
    EMBEDDING_SERVICE_URL = os.getenv("EMBEDDING_SERVICE_URL", "http://localhost:8005")
    PROJECTS_SERVICE_URL = os.getenv("PROJECTS_SERVICE_URL", "http://localhost:8003")
    
    # Configuración del chat
    MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "10"))
    SEARCH_MAX_RESULTS = int(os.getenv("SEARCH_MAX_RESULTS", "10"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Timeouts
    REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30.0"))
    
    # Validaciones
    @classmethod
    def validate(cls):
        """Validar configuración requerida"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY es requerido")
        
        return True
