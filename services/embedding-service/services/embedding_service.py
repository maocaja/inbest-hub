import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any, Optional
import httpx
from loguru import logger
import json

from config import Config
from schemas.schemas import RealEstateProject, ProjectOwner, SearchRequest, SearchResponse, SearchResult

class EmbeddingService:
    def __init__(self):
        self.config = Config()
        self._initialize_embedding_model()
        self._initialize_vector_db()
        
    def _initialize_embedding_model(self):
        """Initialize the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.config.EMBEDDING_MODEL}")
            self.model = SentenceTransformer(self.config.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def _initialize_vector_db(self):
        """Initialize ChromaDB client"""
        try:
            logger.info("Initializing ChromaDB client")
            self.client = chromadb.PersistentClient(
                path=self.config.CHROMA_PERSIST_DIRECTORY,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info("ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text"""
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def get_or_create_collection(self, collection_name: str):
        """Get existing collection or create new one"""
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "model": self.config.EMBEDDING_MODEL,
                    "dimension": self.config.EMBEDDING_DIMENSION
                }
            )
            return collection
        except Exception as e:
            logger.error(f"Error getting/creating collection {collection_name}: {e}")
            raise
    
    def create_project_search_text(self, project: RealEstateProject, owner: Optional[ProjectOwner] = None) -> str:
        """Create searchable text from project data"""
        text_parts = [
            project.name,
            project.description or "",
        ]
        
        # Add location information
        if hasattr(project, 'location') and project.location:
            if hasattr(project.location, 'address'):
                text_parts.append(project.location.address or "")
            if hasattr(project.location, 'city'):
                text_parts.append(project.location.city or "")
            if hasattr(project.location, 'department'):
                text_parts.append(project.location.department or "")
        else:
            # Fallback for old schema
            text_parts.extend([
                getattr(project, 'location', ''),
                getattr(project, 'city', ''),
                getattr(project, 'state', ''),
            ])
        
        # Add property type (from unit_info or fallback)
        if hasattr(project, 'unit_info') and project.unit_info and project.unit_info.unit_types:
            text_parts.extend(project.unit_info.unit_types)
        else:
            text_parts.append(getattr(project, 'property_type', ''))
        
        # Add owner information
        if owner:
            text_parts.extend([owner.name, owner.email])
        
        # Add amenities if available
        if project.amenities:
            text_parts.extend(project.amenities)
        
        # Add price information
        if hasattr(project, 'price_info') and project.price_info:
            if project.price_info.min_price and project.price_info.max_price:
                text_parts.append(f"precio {project.price_info.min_price} a {project.price_info.max_price}")
        else:
            # Fallback for old schema
            if hasattr(project, 'price_range_min') and hasattr(project, 'price_range_max'):
                if project.price_range_min and project.price_range_max:
                    text_parts.append(f"precio {project.price_range_min} a {project.price_range_max}")
        
        # Add area information
        if hasattr(project, 'unit_info') and project.unit_info and project.unit_info.areas:
            for unit_type, area_info in project.unit_info.areas.items():
                if 'min' in area_info and 'max' in area_info:
                    text_parts.append(f"area {unit_type} {area_info['min']} a {area_info['max']}")
        else:
            # Fallback for old schema
            if hasattr(project, 'area_range_min') and hasattr(project, 'area_range_max'):
                if project.area_range_min and project.area_range_max:
                    text_parts.append(f"area {project.area_range_min} a {project.area_range_max}")
        
        # Add units information
        if hasattr(project, 'unit_info') and project.unit_info and project.unit_info.total_units:
            text_parts.append(f"unidades {project.unit_info.total_units}")
        else:
            # Fallback for old schema
            if hasattr(project, 'total_units') and project.total_units:
                text_parts.append(f"unidades {project.total_units}")
        
        return " ".join(filter(None, text_parts)).lower()
    
    async def index_project(self, project: RealEstateProject) -> bool:
        """Index a project in the vector database"""
        try:
            # Get project owner information
            owner = await self._get_project_owner(project.construction_company_nit)
            
            # Create searchable text
            search_text = self.create_project_search_text(project, owner)
            
            # Generate embedding
            embedding = self.generate_embedding(search_text)
            
            # Get or create collection
            collection = self.get_or_create_collection(self.config.PROJECTS_COLLECTION)
            
            # Prepare metadata - ensure no None values
            project_id = getattr(project, 'id', None)
            if project_id is None:
                logger.error(f"Project ID is None for project: {project.name}")
                return False
                
            metadata = {
                "project_id": int(project_id),
                "name": str(project.name or ""),
                "owner_name": str(owner.name if owner else ""),
                "amenities": json.dumps(project.amenities) if project.amenities else "[]",
                "search_text": str(search_text)
            }
            
            # Add location information
            if hasattr(project, 'location') and project.location:
                metadata.update({
                    "location": str(project.location.address or ""),
                    "city": str(project.location.city or ""),
                    "department": str(project.location.department or ""),
                })
            else:
                # Fallback for old schema
                metadata.update({
                    "location": str(getattr(project, 'location', '') or ""),
                    "city": str(getattr(project, 'city', '') or ""),
                    "property_type": str(getattr(project, 'property_type', '') or ""),
                })
            
            # Add status/state
            if hasattr(project, 'status'):
                metadata["state"] = str(project.status.value if hasattr(project.status, 'value') else project.status)
            else:
                metadata["state"] = str(getattr(project, 'state', '') or "")
            
            # Add owner NIT
            if hasattr(project, 'project_owner_nit'):
                metadata["construction_company_nit"] = str(project.project_owner_nit or "")
            else:
                metadata["construction_company_nit"] = str(getattr(project, 'construction_company_nit', '') or "")
            
            # Add price information
            if hasattr(project, 'price_info') and project.price_info:
                metadata.update({
                    "price_min": float(project.price_info.min_price or 0),
                    "price_max": float(project.price_info.max_price or 0),
                })
            else:
                # Fallback for old schema
                metadata.update({
                    "price_min": float(getattr(project, 'price_range_min', 0) or 0),
                    "price_max": float(getattr(project, 'price_range_max', 0) or 0),
                })
            
            # Add area information
            if hasattr(project, 'unit_info') and project.unit_info and project.unit_info.areas:
                area_min = min([float(area.get('min', 0)) for area in project.unit_info.areas.values()]) if project.unit_info.areas else 0.0
                area_max = max([float(area.get('max', 0)) for area in project.unit_info.areas.values()]) if project.unit_info.areas else 0.0
                metadata.update({
                    "area_min": area_min,
                    "area_max": area_max,
                })
            else:
                # Fallback for old schema
                metadata.update({
                    "area_min": float(getattr(project, 'area_range_min', 0) or 0),
                    "area_max": float(getattr(project, 'area_range_max', 0) or 0),
                })
            
            # Add units information
            if hasattr(project, 'unit_info') and project.unit_info:
                metadata.update({
                    "total_units": int(project.unit_info.total_units or 0),
                    "available_units": int(project.unit_info.available_units or 0),
                })
            else:
                # Fallback for old schema
                metadata.update({
                    "total_units": int(getattr(project, 'total_units', 0) or 0),
                    "available_units": int(getattr(project, 'available_units', 0) or 0),
                })
            
            # Filter out None values from metadata
            filtered_metadata = {k: v for k, v in metadata.items() if v is not None}
            
            # Debug: print metadata to see what's causing the issue
            logger.info(f"Metadata for project {project.id}: {filtered_metadata}")
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[search_text],
                metadatas=[filtered_metadata],
                ids=[f"project_{project.id}"]
            )
            
            logger.info(f"Project {project.id} indexed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing project {project.id}: {e}")
            return False
    
    async def search_projects(self, request: SearchRequest) -> SearchResponse:
        """Search projects using vector similarity"""
        try:
            collection = self.get_or_create_collection(request.collection)
            
            # Generate query embedding
            query_embedding = self.generate_embedding(request.query)
            
            # Search in collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=request.max_results,
                where=request.filters
            )
            
            # Process results
            search_results = []
            for i in range(len(results['ids'][0])):
                result = SearchResult(
                    id=results['ids'][0][i],
                    score=results['distances'][0][i],
                    metadata=results['metadatas'][0][i],
                    document=results['documents'][0][i] if results['documents'] else None
                )
                search_results.append(result)
            
            # Filter by similarity threshold
            filtered_results = [
                result for result in search_results 
                if result.score >= request.similarity_threshold
            ]
            
            return SearchResponse(
                results=filtered_results,
                total_results=len(filtered_results),
                query=request.query,
                collection=request.collection
            )
            
        except Exception as e:
            logger.error(f"Error searching projects: {e}")
            raise
    
    async def delete_project(self, project_id: int) -> bool:
        """Delete a project from the vector database"""
        try:
            collection = self.get_or_create_collection(self.config.PROJECTS_COLLECTION)
            
            # Delete by ID
            collection.delete(ids=[f"project_{project_id}"])
            
            logger.info(f"Project {project_id} deleted from vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False
    
    async def update_project(self, project: RealEstateProject) -> bool:
        """Update a project in the vector database"""
        try:
            # First delete the old entry
            await self.delete_project(project.id)
            
            # Then add the updated entry
            return await self.index_project(project)
            
        except Exception as e:
            logger.error(f"Error updating project {project.id}: {e}")
            return False
    
    async def _get_project_owner(self, nit: str) -> Optional[ProjectOwner]:
        """Get project owner information from the project-owners-service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.PROJECT_OWNERS_SERVICE_URL}/project-owners/{nit}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return ProjectOwner(**data)
                else:
                    logger.warning(f"Project owner {nit} not found")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching project owner {nit}: {e}")
            return None
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection"""
        try:
            collection = self.get_or_create_collection(collection_name)
            count = collection.count()
            
            return {
                "name": collection_name,
                "count": count,
                "dimension": self.config.EMBEDDING_DIMENSION,
                "model": self.config.EMBEDDING_MODEL
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info for {collection_name}: {e}")
            raise
    
    async def sync_all_projects(self) -> Dict[str, Any]:
        """Sync all projects from projects-service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.PROJECTS_SERVICE_URL}/projects",
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    projects_data = response.json()
                    projects = [RealEstateProject(**project) for project in projects_data]
                    
                    indexed_count = 0
                    error_count = 0
                    
                    for project in projects:
                        if await self.index_project(project):
                            indexed_count += 1
                        else:
                            error_count += 1
                    
                    return {
                        "total_projects": len(projects),
                        "indexed_count": indexed_count,
                        "error_count": error_count,
                        "success": True
                    }
                else:
                    logger.error(f"Error fetching projects: {response.status_code}")
                    return {"success": False, "error": "Failed to fetch projects"}
                    
        except Exception as e:
            logger.error(f"Error syncing projects: {e}")
            return {"success": False, "error": str(e)} 