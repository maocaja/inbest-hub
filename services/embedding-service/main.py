from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import httpx
from loguru import logger
import sys
from datetime import datetime

from config import Config
from services.embedding_service import EmbeddingService
from schemas.schemas import (
    EmbeddingRequest, EmbeddingResponse, SearchRequest, SearchResponse,
    HealthResponse, SyncRequest, CollectionInfo, RealEstateProject
)

# Configure logging
logger.remove()
logger.add(sys.stderr, level=Config.LOG_LEVEL)
logger.add("logs/embedding_service.log", rotation="1 day", retention="7 days")

app = FastAPI(
    title="Embedding Service",
    description="Service for generating embeddings and vector search of real estate projects",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embedding service
embedding_service = EmbeddingService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Embedding Service...")
    try:
        # Test embedding service initialization
        test_embedding = embedding_service.generate_embedding("test")
        logger.info(f"Embedding service initialized successfully. Test embedding dimension: {len(test_embedding)}")
    except Exception as e:
        logger.error(f"Error initializing embedding service: {e}")
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check embedding service
        test_embedding = embedding_service.generate_embedding("health check")
        
        # Check vector database
        collection_info = embedding_service.get_collection_info(Config.PROJECTS_COLLECTION)
        
        services_status = {
            "embedding_service": "healthy",
            "vector_database": "healthy",
            "model": Config.EMBEDDING_MODEL
        }
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            services=services_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")

@app.post("/embeddings/generate", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest):
    """Generate embedding for given text"""
    try:
        embedding = embedding_service.generate_embedding(request.text)
        
        return EmbeddingResponse(
            embedding=embedding,
            dimension=len(embedding),
            model=Config.EMBEDDING_MODEL
        )
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

@app.post("/search", response_model=SearchResponse)
async def search_projects(request: SearchRequest):
    """Search projects using vector similarity"""
    try:
        result = await embedding_service.search_projects(request)
        return result
    except Exception as e:
        logger.error(f"Error searching projects: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching projects: {str(e)}")

@app.post("/projects/index")
async def index_project(project: RealEstateProject):
    """Index a single project"""
    try:
        success = await embedding_service.index_project(project)
        if success:
            return {"message": f"Project {project.id} indexed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to index project")
    except Exception as e:
        logger.error(f"Error indexing project: {e}")
        raise HTTPException(status_code=500, detail=f"Error indexing project: {str(e)}")

@app.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    """Delete a project from the vector database"""
    try:
        success = await embedding_service.delete_project(project_id)
        if success:
            return {"message": f"Project {project_id} deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete project")
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")

@app.put("/projects/{project_id}")
async def update_project(project_id: int, project: RealEstateProject):
    """Update a project in the vector database"""
    try:
        project.id = project_id
        success = await embedding_service.update_project(project)
        if success:
            return {"message": f"Project {project_id} updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update project")
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")

@app.post("/sync/projects")
async def sync_projects(background_tasks: BackgroundTasks):
    """Sync all projects from projects-service"""
    try:
        result = await embedding_service.sync_all_projects()
        if result["success"]:
            return {
                "message": "Projects sync completed",
                "total_projects": result["total_projects"],
                "indexed_count": result["indexed_count"],
                "error_count": result["error_count"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        logger.error(f"Error syncing projects: {e}")
        raise HTTPException(status_code=500, detail=f"Error syncing projects: {str(e)}")

@app.get("/collections/{collection_name}", response_model=CollectionInfo)
async def get_collection_info(collection_name: str):
    """Get information about a collection"""
    try:
        info = embedding_service.get_collection_info(collection_name)
        return CollectionInfo(**info)
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting collection info: {str(e)}")

@app.post("/webhook/project-sync")
async def webhook_project_sync(request: SyncRequest):
    """Webhook endpoint for project synchronization"""
    try:
        if request.action == "create":
            if request.data:
                success = await embedding_service.index_project(request.data)
                if success:
                    return {"message": f"Project {request.project_id} indexed via webhook"}
                else:
                    raise HTTPException(status_code=500, detail="Failed to index project via webhook")
            else:
                raise HTTPException(status_code=400, detail="Project data required for create action")
                
        elif request.action == "update":
            if request.data:
                request.data.id = request.project_id
                success = await embedding_service.update_project(request.data)
                if success:
                    return {"message": f"Project {request.project_id} updated via webhook"}
                else:
                    raise HTTPException(status_code=500, detail="Failed to update project via webhook")
            else:
                raise HTTPException(status_code=400, detail="Project data required for update action")
                
        elif request.action == "delete":
            success = await embedding_service.delete_project(request.project_id)
            if success:
                return {"message": f"Project {request.project_id} deleted via webhook"}
            else:
                raise HTTPException(status_code=500, detail="Failed to delete project via webhook")
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {request.action}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Embedding Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate_embedding": "/embeddings/generate",
            "search": "/search",
            "index_project": "/projects/index",
            "sync_projects": "/sync/projects",
            "collection_info": "/collections/{collection_name}",
            "webhook": "/webhook/project-sync"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level=Config.LOG_LEVEL.lower()
    ) 