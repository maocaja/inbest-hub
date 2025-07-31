from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime

class ProjectStatus(str, Enum):
    PREVENTA = "preventa"
    CONSTRUCCION = "construcción"
    ENTREGADO = "entregado"

class Currency(str, Enum):
    COP = "COP"
    USD = "USD"
    EUR = "EUR"

class UnitType(str, Enum):
    APARTAMENTO = "apartamento"
    CASA = "casa"
    DUPLEX = "duplex"
    PENTHOUSE = "penthouse"
    STUDIO = "studio"

class UsageType(str, Enum):
    VIVIENDA = "vivienda"
    INVERSION = "inversión"
    VACACIONAL = "vacacional"

class IncomeLevel(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"

class Location(BaseModel):
    country: Optional[str] = Field(None, description="País (ej. Colombia)")
    department: Optional[str] = Field(None, description="Departamento o estado")
    city: Optional[str] = Field(None, description="Ciudad o municipio")
    zone: Optional[str] = Field(None, description="Zona dentro de la ciudad")
    neighborhood: Optional[str] = Field(None, description="Barrio o sector")
    latitude: Optional[float] = Field(None, description="Latitud")
    longitude: Optional[float] = Field(None, description="Longitud")

class PriceInfo(BaseModel):
    currency: Optional[Currency] = Field(None, description="Moneda")
    price_min: Optional[float] = Field(None, description="Precio más bajo de unidad")
    price_max: Optional[float] = Field(None, description="Precio más alto")
    price_per_m2: Optional[float] = Field(None, description="Precio promedio por m²")
    maintenance_fee: Optional[float] = Field(None, description="Cuota de administración mensual")

class UnitInfo(BaseModel):
    unit_types: Optional[List[UnitType]] = Field(None, description="Tipos disponibles")
    area_m2_min: Optional[float] = Field(None, description="Área mínima en m²")
    area_m2_max: Optional[float] = Field(None, description="Área máxima en m²")
    bedrooms_min: Optional[int] = Field(None, description="Número mínimo de habitaciones")
    bedrooms_max: Optional[int] = Field(None, description="Número máximo de habitaciones")
    bathrooms_min: Optional[int] = Field(None, description="Número mínimo de baños")
    bathrooms_max: Optional[int] = Field(None, description="Número máximo de baños")
    parking_min: Optional[int] = Field(None, description="Número mínimo de parqueaderos")
    parking_max: Optional[int] = Field(None, description="Número máximo de parqueaderos")
    balcony: Optional[bool] = Field(None, description="¿Tiene balcón?")
    storage_room: Optional[bool] = Field(None, description="¿Tiene cuarto de almacenamiento?")

class Amenities(BaseModel):
    list: Optional[List[str]] = Field(None, description="Lista de amenidades")
    green_areas: Optional[bool] = Field(None, description="¿Tiene áreas verdes?")
    pet_friendly: Optional[bool] = Field(None, description="¿Permite mascotas?")
    security_features: Optional[List[str]] = Field(None, description="Características de seguridad")

class FinancialInfo(BaseModel):
    offers_financing: Optional[bool] = Field(None, description="¿El proyecto tiene financiación?")
    down_payment_percent: Optional[float] = Field(None, description="% cuota inicial")
    installment_months: Optional[int] = Field(None, description="Cuotas/plazo")
    expected_rent: Optional[float] = Field(None, description="Renta esperada mensual")
    appreciation_rate: Optional[float] = Field(None, description="% valorización anual esperada")
    investment_horizon_years: Optional[int] = Field(None, description="Horizonte de inversión en años")

class AudienceInfo(BaseModel):
    target_audience: Optional[List[str]] = Field(None, description="Audiencia objetivo")
    usage_type: Optional[UsageType] = Field(None, description="Tipo de uso")
    income_level: Optional[IncomeLevel] = Field(None, description="Nivel de ingresos")

class Media(BaseModel):
    images: Optional[List[str]] = Field(None, description="URLs de imágenes")
    videos: Optional[List[str]] = Field(None, description="URLs de videos")
    brochure_url: Optional[str] = Field(None, description="URL del brochure PDF")
    virtual_tour_url: Optional[str] = Field(None, description="URL del tour virtual")

class RealEstateProject(BaseModel):
    project_id: Optional[str] = Field(None, description="ID único del proyecto")
    name: Optional[str] = Field(None, description="Nombre del proyecto")
    description: Optional[str] = Field(None, description="Descripción breve del proyecto")
    builder: Optional[str] = Field(None, description="Constructora o desarrollador")
    status: Optional[ProjectStatus] = Field(None, description="Estado actual")
    delivery_date: Optional[str] = Field(None, description="Fecha estimada de entrega (YYYY-MM)")
    
    location: Optional[Location] = Field(None, description="Información de ubicación")
    price_info: Optional[PriceInfo] = Field(None, description="Información de precios")
    unit_info: Optional[UnitInfo] = Field(None, description="Información de unidades")
    amenities: Optional[Amenities] = Field(None, description="Amenidades")
    financial_info: Optional[FinancialInfo] = Field(None, description="Información financiera")
    audience_info: Optional[AudienceInfo] = Field(None, description="Información de audiencia")
    media: Optional[Media] = Field(None, description="Medios")

    @validator('delivery_date')
    def validate_delivery_date(cls, v):
        if v and len(v) != 7:  # YYYY-MM format
            raise ValueError('La fecha debe estar en formato YYYY-MM')
        return v

class ExtractionRequest(BaseModel):
    file_content: str
    file_type: str

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    completeness_score: float = 0.0
    suggestions: List[str] = []

class ExtractionResponse(BaseModel):
    success: bool
    project_data: Optional[RealEstateProject] = None
    validation_result: Optional[ValidationResult] = None
    message: str
    confidence_score: Optional[float] = None 