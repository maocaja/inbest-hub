"""
Esquemas Pydantic para Projects Service
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum
from config import Config

class ProjectStatus(str, Enum):
    """Estados posibles de un proyecto"""
    INCOMPLETO = "incompleto"
    EN_PROCESO = "en_proceso"
    COMPLETO = "completo"
    INACTIVO = "inactivo"
    ARCHIVADO = "archivado"
    
    @classmethod
    def _missing_(cls, value):
        """Manejar valores en minúsculas"""
        for member in cls:
            if member.value == value:
                return member
        return None

class LocationSchema(BaseModel):
    """Esquema para información de ubicación"""
    address: Optional[str] = None
    city: Optional[str] = None
    department: Optional[str] = None
    country: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {lat, lng}

class PriceInfoSchema(BaseModel):
    """Esquema para información de precios"""
    currency: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_per_m2: Optional[float] = None
    
    @validator('min_price', 'max_price', 'price_per_m2')
    def validate_prices(cls, v):
        if v is not None and v < 0:
            raise ValueError('Los precios deben ser positivos')
        return v

class UnitInfoSchema(BaseModel):
    """Esquema para información de unidades"""
    total_units: Optional[int] = None
    available_units: Optional[int] = None
    unit_types: Optional[List[str]] = None
    areas: Optional[Dict[str, Dict[str, float]]] = None  # {unit_type: {min, max}}
    
    @validator('total_units', 'available_units')
    def validate_units(cls, v):
        if v is not None and v < 0:
            raise ValueError('El número de unidades debe ser positivo')
        return v

class FinancialInfoSchema(BaseModel):
    """Esquema para información financiera"""
    delivery_date: Optional[str] = None
    payment_plans: Optional[List[Dict[str, Any]]] = None
    financing_options: Optional[List[str]] = None

class AudienceInfoSchema(BaseModel):
    """Esquema para información de audiencia"""
    target_audience: Optional[List[str]] = None
    income_levels: Optional[List[str]] = None

class MediaSchema(BaseModel):
    """Esquema para medios y documentación"""
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    documents: Optional[List[str]] = None

class ProjectBase(BaseModel):
    """Esquema base para proyectos"""
    name: str = Field(..., min_length=Config.MIN_NAME_LENGTH, max_length=Config.MAX_NAME_LENGTH)
    description: Optional[str] = Field(None, min_length=Config.MIN_DESCRIPTION_LENGTH, max_length=Config.MAX_DESCRIPTION_LENGTH)
    project_owner_nit: str = Field(..., min_length=10, max_length=20)
    location: Optional[LocationSchema] = None
    price_info: Optional[PriceInfoSchema] = None
    unit_info: Optional[UnitInfoSchema] = None
    amenities: Optional[List[str]] = None
    financial_info: Optional[FinancialInfoSchema] = None
    audience_info: Optional[AudienceInfoSchema] = None
    media: Optional[MediaSchema] = None

class ProjectCreate(ProjectBase):
    """Esquema para crear un proyecto"""
    status: ProjectStatus = ProjectStatus.INCOMPLETO
    
    @validator('status', pre=True)
    def validate_status(cls, v):
        """Validar y convertir estado"""
        if isinstance(v, str):
            v = v.lower()
        return v
    
    @validator('project_owner_nit')
    def validate_nit(cls, v):
        """Validar formato de NIT"""
        if not v.replace('-', '').replace('.', '').isdigit():
            raise ValueError('NIT debe contener solo números, guiones y puntos')
        return v

class ProjectUpdate(BaseModel):
    """Esquema para actualizar un proyecto"""
    name: Optional[str] = Field(None, min_length=Config.MIN_NAME_LENGTH, max_length=Config.MAX_NAME_LENGTH)
    description: Optional[str] = Field(None, min_length=Config.MIN_DESCRIPTION_LENGTH, max_length=Config.MAX_DESCRIPTION_LENGTH)
    status: Optional[ProjectStatus] = None
    location: Optional[LocationSchema] = None
    price_info: Optional[PriceInfoSchema] = None
    unit_info: Optional[UnitInfoSchema] = None
    amenities: Optional[List[str]] = None
    financial_info: Optional[FinancialInfoSchema] = None
    audience_info: Optional[AudienceInfoSchema] = None
    media: Optional[MediaSchema] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

class ProjectResponse(ProjectBase):
    """Esquema de respuesta para proyectos"""
    id: int
    status: ProjectStatus
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProjectListResponse(BaseModel):
    """Esquema para lista de proyectos"""
    items: List[ProjectResponse]
    total: int
    page: int
    size: int
    
    class Config:
        from_attributes = True

class ProjectStateUpdate(BaseModel):
    """Esquema para actualizar estado de proyecto"""
    status: ProjectStatus
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ProjectStatus:
            raise ValueError(f'Estado debe ser uno de: {[s.value for s in ProjectStatus]}')
        return v 