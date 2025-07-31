"""
Modelos SQLAlchemy para Projects Service
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base
from config import Config
import enum

class ProjectStatus(enum.Enum):
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

class Project(Base):
    """
    Modelo para proyectos inmobiliarios
    """
    __tablename__ = "projects"
    
    # Identificación básica
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(Config.MAX_NAME_LENGTH), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus, values_callable=lambda x: [e.value for e in x]), default=ProjectStatus.INCOMPLETO, nullable=False)
    
    # Relación con constructora
    project_owner_nit = Column(String(20), ForeignKey("project_owners.nit"), nullable=False)
    project_owner = relationship("ProjectOwner", back_populates="projects")
    
    # Información de ubicación
    location = Column(JSON, nullable=True)  # {address, city, department, country, coordinates}
    
    # Información de precios
    price_info = Column(JSON, nullable=True)  # {currency, min_price, max_price, price_per_m2}
    
    # Información de unidades
    unit_info = Column(JSON, nullable=True)  # {total_units, available_units, unit_types, areas}
    
    # Amenities y características
    amenities = Column(JSON, nullable=True)  # Lista de amenidades
    
    # Información financiera
    financial_info = Column(JSON, nullable=True)  # {delivery_date, payment_plans, etc}
    
    # Información de audiencia
    audience_info = Column(JSON, nullable=True)  # {target_audience, income_levels}
    
    # Medios y documentación
    media = Column(JSON, nullable=True)  # {images, videos, documents}
    
    # Metadatos
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status.value}')>"
    
    def to_dict(self):
        """
        Convierte el modelo a diccionario
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "project_owner_nit": self.project_owner_nit,
            "location": self.location,
            "price_info": self.price_info,
            "unit_info": self.unit_info,
            "amenities": self.amenities,
            "financial_info": self.financial_info,
            "audience_info": self.audience_info,
            "media": self.media,
            "is_active": self.is_active,
            "is_featured": self.is_featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# Importar el modelo ProjectOwner desde el otro servicio
# En un entorno real, esto se manejaría con migraciones o referencias externas
class ProjectOwner(Base):
    """
    Referencia al modelo ProjectOwner del project-owners-service
    """
    __tablename__ = "project_owners"
    
    nit = Column(String(20), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=False)
    department = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False, default="Colombia")
    website = Column(String(255), nullable=True)
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relación con proyectos
    projects = relationship("Project", back_populates="project_owner")
    
    def __repr__(self):
        return f"<ProjectOwner(nit='{self.nit}', name='{self.name}')>" 