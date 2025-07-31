from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn
import os
from dotenv import load_dotenv
import logging

from database.database import get_db, engine
from models.models import Base
from schemas.schemas import ProjectOwnerCreate, ProjectOwnerUpdate, ProjectOwnerResponse
from services.project_owners_service import ProjectOwnersService
from config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables (only when running the app)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Project Owners Service",
    description="Servicio para gestionar constructoras y propietarios de proyectos inmobiliarios",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service
project_owners_service = ProjectOwnersService()

@app.get("/")
async def root():
    return {
        "message": "Project Owners Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "project-owners-service"}

@app.post("/project-owners", response_model=ProjectOwnerResponse, status_code=status.HTTP_201_CREATED)
async def create_project_owner(
    project_owner: ProjectOwnerCreate,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva constructora/propietario de proyecto
    """
    try:
        result = project_owners_service.create_project_owner(db, project_owner)
        logger.info(f"Project owner created: {result.name} (NIT: {result.nit})")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating project owner: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating project owner: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.get("/project-owners", response_model=List[ProjectOwnerResponse])
async def get_project_owners(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtener lista de constructoras/propietarios de proyectos
    """
    try:
        project_owners = project_owners_service.get_project_owners(db, skip=skip, limit=limit)
        return project_owners
    except Exception as e:
        logger.error(f"Error getting project owners: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.get("/project-owners/{nit}", response_model=ProjectOwnerResponse)
async def get_project_owner(
    nit: str,
    db: Session = Depends(get_db)
):
    """
    Obtener una constructora/propietario específico por NIT
    """
    try:
        project_owner = project_owners_service.get_project_owner(db, nit)
        if not project_owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Constructora no encontrada")
        return project_owner
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project owner {nit}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.put("/project-owners/{nit}", response_model=ProjectOwnerResponse)
async def update_project_owner(
    nit: str,
    project_owner: ProjectOwnerUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar una constructora/propietario existente
    """
    try:
        result = project_owners_service.update_project_owner(db, nit, project_owner)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Constructora no encontrada")
        logger.info(f"Project owner updated: {result.name} (NIT: {result.nit})")
        return result
    except ValueError as e:
        logger.error(f"Validation error updating project owner: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project owner {nit}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.delete("/project-owners/{nit}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_owner(
    nit: str,
    db: Session = Depends(get_db)
):
    """
    Eliminar una constructora/propietario
    """
    try:
        success = project_owners_service.delete_project_owner(db, nit)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Constructora no encontrada")
        logger.info(f"Project owner deleted: NIT {nit}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project owner {nit}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")



if __name__ == "__main__":
    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        logger.error("Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        exit(1)
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        logger.info("Make sure PostgreSQL is running and DATABASE_URL is correct")
        exit(1)
    
    server_config = Config.get_server_config()
    logger.info(f"Starting server on {server_config['host']}:{server_config['port']}")
    
    uvicorn.run(
        "main:app",
        host=server_config['host'],
        port=server_config['port'],
        reload=server_config['reload']
    ) 