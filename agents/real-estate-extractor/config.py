"""
Configuración del Real Estate Data Extractor Agent
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración principal del agente"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4"
    OPENAI_TEMPERATURE = 0.1
    OPENAI_MAX_TOKENS = 4000
    
    # Server Configuration
    PORT = int(os.getenv("PORT", 8012))
    HOST = os.getenv("HOST", "0.0.0.0")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    RELOAD = os.getenv("RELOAD", "True").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # File Processing Configuration
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.xlsx', '.xls']
    
    # Validation Configuration
    REQUIRED_FIELDS = [
        "name", "builder", "status"
    ]
    
    IMPORTANT_FIELDS = [
        "location.city", "location.neighborhood",
        "price_info.price_min", "price_info.currency",
        "unit_info.area_m2_min", "unit_info.unit_types"
    ]
    
    # Real Estate Keywords for extraction
    REAL_ESTATE_KEYWORDS = [
        # Tipos de propiedades
        "apartamento", "casa", "duplex", "penthouse", "studio", "loft",
        "residencial", "conjunto", "edificio", "torre", "bloque",
        
        # Estados del proyecto
        "preventa", "construcción", "entregado", "nuevo", "usado",
        "en desarrollo", "en obra", "listo para entrega",
        
        # Información de precios
        "precio", "valor", "costo", "m2", "metros cuadrados",
        "millones", "pesos", "dólares", "euros",
        
        # Características de unidades
        "habitaciones", "baños", "parqueadero", "balcón", "terraza",
        "área", "superficie", "dimensiones",
        
        # Amenidades
        "amenidades", "piscina", "gimnasio", "zona BBQ", "parque",
        "juegos infantiles", "coworking", "sala comunal",
        
        # Financiación
        "financiación", "crédito", "cuota inicial", "cuotas",
        "hipoteca", "leasing", "leasing habitacional",
        
        # Ubicación
        "ubicación", "zona", "barrio", "ciudad", "municipio",
        "departamento", "estado", "país", "dirección",
        
        # Constructora
        "constructora", "desarrollador", "inmobiliaria", "promotora",
        "empresa constructora", "desarrollador inmobiliario",
        
        # Fechas
        "entrega", "fecha de entrega", "tiempo de entrega",
        "inicio de obra", "finalización", "completado"
    ]
    
    # Validation rules
    VALIDATION_RULES = {
        "delivery_date": "YYYY-MM format",
        "price_info.price_min": "positive number",
        "price_info.price_max": "positive number",
        "unit_info.area_m2_min": "positive number",
        "unit_info.area_m2_max": "positive number",
        "location.latitude": "between -90 and 90",
        "location.longitude": "between -180 and 180"
    }
    
    # Currency options
    CURRENCIES = ["COP", "USD", "EUR", "MXN", "ARS", "BRL", "CLP", "PEN"]
    
    # Project status options
    PROJECT_STATUSES = ["preventa", "construcción", "entregado"]
    
    # Unit types
    UNIT_TYPES = ["apartamento", "casa", "duplex", "penthouse", "studio"]
    
    # Usage types
    USAGE_TYPES = ["vivienda", "inversión", "vacacional"]
    
    # Income levels
    INCOME_LEVELS = ["bajo", "medio", "alto"]
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """
        Valida la configuración y retorna errores si los hay
        """
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY no está configurada")
        
        if cls.PORT < 1 or cls.PORT > 65535:
            errors.append("PORT debe estar entre 1 y 65535")
        
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
    def get_openai_config(cls) -> Dict[str, Any]:
        """
        Retorna la configuración de OpenAI
        """
        return {
            "api_key": cls.OPENAI_API_KEY,
            "model": cls.OPENAI_MODEL,
            "temperature": cls.OPENAI_TEMPERATURE,
            "max_tokens": cls.OPENAI_MAX_TOKENS
        } 