"""
Modelos SQLAlchemy para Project Owners Service
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from database.database import Base
from config import Config

class ProjectOwner(Base):
    """
    Modelo para constructoras/propietarios de proyectos
    """
    __tablename__ = "project_owners"
    
    nit = Column(String(Config.MAX_NIT_LENGTH), primary_key=True, index=True)
    name = Column(String(Config.MAX_NAME_LENGTH), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=False)
    department = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False, default="Colombia")
    
    # Información adicional
    website = Column(String(255), nullable=True)
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)
    
    # Estados
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ProjectOwner(nit='{self.nit}', name='{self.name}')>"
    
    def to_dict(self):
        """
        Convierte el modelo a diccionario
        """
        return {
            "nit": self.nit,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "department": self.department,
            "country": self.country,
            "website": self.website,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 