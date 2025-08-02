from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ProjectState(str, Enum):
    INCOMPLETE = "incomplete"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class ProjectStatus(str, Enum):
    INCOMPLETO = "incompleto"
    EN_PROCESO = "en_proceso"
    COMPLETO = "completo"
    INACTIVO = "inactivo"
    ARCHIVADO = "archivado"

class LocationSchema(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    department: Optional[str] = None
    country: Optional[str] = None

class PriceInfoSchema(BaseModel):
    currency: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_per_m2: Optional[float] = None

class UnitInfoSchema(BaseModel):
    total_units: Optional[int] = None
    available_units: Optional[int] = None
    unit_types: Optional[List[str]] = None
    areas: Optional[Dict[str, Dict[str, float]]] = None

class ProjectOwner(BaseModel):
    nit: str
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True

class RealEstateProject(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    
    # New schema fields
    project_owner_nit: Optional[str] = None
    location: Optional[LocationSchema] = None
    price_info: Optional[PriceInfoSchema] = None
    unit_info: Optional[UnitInfoSchema] = None
    amenities: Optional[List[str]] = None
    status: Optional[ProjectStatus] = None
    
    # Legacy schema fields (for backward compatibility)
    location_legacy: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    property_type: Optional[str] = None
    total_units: Optional[int] = None
    available_units: Optional[int] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    area_range_min: Optional[float] = None
    area_range_max: Optional[float] = None
    construction_company_nit: Optional[str] = None
    state_legacy: Optional[ProjectState] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class EmbeddingRequest(BaseModel):
    text: str = Field(..., description="Text to generate embedding for")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class EmbeddingResponse(BaseModel):
    embedding: List[float] = Field(..., description="Generated embedding vector")
    dimension: int = Field(..., description="Dimension of the embedding")
    model: str = Field(..., description="Model used for embedding")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    collection: str = Field(..., description="Collection to search in")
    max_results: Optional[int] = Field(10, description="Maximum number of results")
    similarity_threshold: Optional[float] = Field(0.7, description="Minimum similarity threshold")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")

class SearchResult(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any]
    document: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    query: str
    collection: str

class ProjectEmbedding(BaseModel):
    project_id: int
    project_data: RealEstateProject
    embedding: List[float]
    search_text: str = Field(..., description="Text used for search indexing")

class CollectionInfo(BaseModel):
    name: str
    count: int
    dimension: int
    model: str

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    services: Dict[str, str]

class SyncRequest(BaseModel):
    project_id: int
    action: str = Field(..., description="Action: create, update, delete")
    data: Optional[RealEstateProject] = None 