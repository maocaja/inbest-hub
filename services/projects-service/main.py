"""
Aplicación principal de FastAPI para Projects Service
"""

import logging
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from database.database import get_db, engine
from models.models import Base
from schemas.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectStateUpdate,
    ProjectListResponse
)
from services.projects_service import ProjectsService
from webhook_handler import WebhookHandler
from config import Config

# Configurar logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Projects Service",
    description="Servicio para gestión de proyectos inmobiliarios",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciar servicios
projects_service = ProjectsService()
webhook_handler = WebhookHandler()

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("Projects Service starting up...")
    
    # Validar configuración
    config_errors = Config.validate_config()
    if config_errors:
        logger.error(f"Configuration errors: {config_errors}")
        raise ValueError(f"Configuration errors: {config_errors}")
    
    logger.info("Configuration validated successfully")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Projects Service API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "projects-service",
        "version": "1.0.0"
    }

@app.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo proyecto inmobiliario
    """
    try:
        result = projects_service.create_project(db, project)
        logger.info(f"Project created successfully: {result.name}")
        return result
    except ValueError as e:
        logger.error(f"Validation error creating project: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.get("/projects", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    owner_nit: Optional[str] = Query(None, description="Filtrar por NIT de constructora"),
    active_only: bool = Query(True, description="Solo proyectos activos")
):
    """
    Obtener lista de proyectos con filtros opcionales
    """
    try:
        projects = projects_service.get_projects(
            db=next(get_db()),
            skip=skip,
            limit=limit,
            status=status,
            owner_nit=owner_nit,
            active_only=active_only
        )
        return projects
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un proyecto específico por ID
    """
    try:
        project = projects_service.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un proyecto existente
    """
    try:
        result = projects_service.update_project(db, project_id, project)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")
        logger.info(f"Project updated: {result.name} (ID: {result.id})")
        return result
    except ValueError as e:
        logger.error(f"Validation error updating project: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.patch("/projects/{project_id}/state", response_model=ProjectResponse)
async def update_project_state(
    project_id: int,
    state_update: ProjectStateUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar el estado de un proyecto
    """
    try:
        result = projects_service.update_project_state(db, project_id, state_update)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")
        logger.info(f"Project state updated: {result.name} -> {state_update.status.value}")
        return result
    except ValueError as e:
        logger.error(f"Validation error updating project state: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project state {project_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar un proyecto (soft delete)
    """
    try:
        success = projects_service.delete_project(db, project_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")
        logger.info(f"Project deleted: ID {project_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.get("/projects/{project_id}/history")
async def get_project_history(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener historial de cambios de un proyecto
    """
    try:
        history = projects_service.get_project_history(db, project_id)
        return {"project_id": project_id, "history": history}
    except Exception as e:
        logger.error(f"Error getting project history {project_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.get("/projects/owner/{owner_nit}", response_model=List[ProjectResponse])
async def get_projects_by_owner(
    owner_nit: str,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: Session = Depends(get_db)
):
    """
    Obtener proyectos de una constructora específica
    """
    try:
        projects = projects_service.get_projects_by_owner(db, owner_nit, skip, limit)
        return projects
    except Exception as e:
        logger.error(f"Error getting projects by owner {owner_nit}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.get("/projects/status/{status}", response_model=List[ProjectResponse])
async def get_projects_by_status(
    status: str,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: Session = Depends(get_db)
):
    """
    Obtener proyectos por estado
    """
    try:
        projects = projects_service.get_projects_by_status(db, status, skip, limit)
        return projects
    except Exception as e:
        logger.error(f"Error getting projects by status {status}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

# Webhook endpoints para sincronización de constructoras
@app.post("/webhooks/project-owners/created")
async def webhook_project_owner_created(project_owner_data: dict):
    """
    Webhook para notificar creación de constructora
    """
    try:
        success = webhook_handler.handle_project_owner_created(project_owner_data)
        if success:
            return {"status": "success", "message": "Constructora creada exitosamente"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error procesando webhook")
    except Exception as e:
        logger.error(f"Error en webhook de creación: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.put("/webhooks/project-owners/updated")
async def webhook_project_owner_updated(project_owner_data: dict):
    """
    Webhook para notificar actualización de constructora
    """
    try:
        success = webhook_handler.handle_project_owner_updated(project_owner_data)
        if success:
            return {"status": "success", "message": "Constructora actualizada exitosamente"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error procesando webhook")
    except Exception as e:
        logger.error(f"Error en webhook de actualización: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@app.delete("/webhooks/project-owners/deleted/{nit}")
async def webhook_project_owner_deleted(nit: str):
    """
    Webhook para notificar eliminación de constructora
    """
    try:
        success = webhook_handler.handle_project_owner_deleted(nit)
        if success:
            return {"status": "success", "message": "Constructora eliminada exitosamente"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error procesando webhook")
    except Exception as e:
        logger.error(f"Error en webhook de eliminación: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    
    # Crear tablas en la base de datos
    Base.metadata.create_all(bind=engine)
    
    # Configuración del servidor
    server_config = Config.get_server_config()
    
    # Ejecutar servidor
    uvicorn.run(
        "main:app",
        host=server_config["host"],
        port=server_config["port"],
        reload=server_config["reload"],
        log_level=Config.LOG_LEVEL.lower()
    )
