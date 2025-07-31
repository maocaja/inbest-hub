"""
Esquemas Pydantic para Project Owners Service
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from config import Config

class ProjectOwnerBase(BaseModel):
    """Esquema base para project owners"""
    name: str = Field(..., min_length=Config.MIN_NAME_LENGTH, max_length=Config.MAX_NAME_LENGTH)
    nit: str = Field(..., min_length=Config.MIN_NIT_LENGTH, max_length=Config.MAX_NIT_LENGTH)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: str = Field(..., max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    country: str = Field(default="Colombia", max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[EmailStr] = None

class ProjectOwnerCreate(ProjectOwnerBase):
    """Esquema para crear un project owner"""
    
    @validator('nit')
    def validate_nit(cls, v):
        """Validar formato de NIT"""
        if not v.replace('-', '').replace('.', '').isdigit():
            raise ValueError('NIT debe contener solo números, guiones y puntos')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validar formato de teléfono"""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Teléfono debe contener solo números, espacios, guiones y +')
        return v

class ProjectOwnerUpdate(BaseModel):
    """Esquema para actualizar un project owner"""
    name: Optional[str] = Field(None, min_length=Config.MIN_NAME_LENGTH, max_length=Config.MAX_NAME_LENGTH)
    nit: Optional[str] = Field(None, min_length=Config.MIN_NIT_LENGTH, max_length=Config.MAX_NIT_LENGTH)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    
    @validator('nit')
    def validate_nit(cls, v):
        """Validar formato de NIT"""
        if v and not v.replace('-', '').replace('.', '').isdigit():
            raise ValueError('NIT debe contener solo números, guiones y puntos')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validar formato de teléfono"""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Teléfono debe contener solo números, espacios, guiones y +')
        return v

class ProjectOwnerResponse(ProjectOwnerBase):
    """Esquema de respuesta para project owners"""
    nit: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProjectOwnerListResponse(BaseModel):
    """Esquema para lista de project owners"""
    items: list[ProjectOwnerResponse]
    total: int
    page: int
    size: int
    
    class Config:
        from_attributes = True 