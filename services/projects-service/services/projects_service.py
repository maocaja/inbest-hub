"""
Servicio de lógica de negocio para Projects
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
import logging

from models.models import Project, ProjectOwner, ProjectStatus
from schemas.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectStateUpdate
from config import Config

logger = logging.getLogger(__name__)

class ProjectsService:
    """
    Servicio para gestionar proyectos inmobiliarios
    """
    
    def create_project(self, db: Session, project: ProjectCreate) -> ProjectResponse:
        """
        Crear un nuevo proyecto
        """
        try:
            # Verificar que la constructora existe
            project_owner = db.query(ProjectOwner).filter(ProjectOwner.nit == project.project_owner_nit).first()
            if not project_owner:
                raise ValueError(f"No existe una constructora con el NIT {project.project_owner_nit}")
            
            # Verificar que la constructora está activa
            if not project_owner.is_active:
                raise ValueError(f"La constructora {project_owner.name} no está activa")
            
            # Crear el nuevo proyecto
            db_project = Project(**project.dict())
            db.add(db_project)
            db.commit()
            db.refresh(db_project)
            
            logger.info(f"Project created: {db_project.name} (ID: {db_project.id})")
            return ProjectResponse.from_orm(db_project)
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error creating project: {str(e)}")
            raise ValueError("Error de integridad en la base de datos")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating project: {str(e)}")
            raise
    
    def get_projects(self, db: Session, skip: int = 0, limit: int = 100, 
                    status: Optional[str] = None, owner_nit: Optional[str] = None,
                    active_only: bool = True) -> List[ProjectResponse]:
        """
        Obtener lista de proyectos con filtros opcionales
        """
        try:
            query = db.query(Project)
            
            # Filtros
            if active_only:
                query = query.filter(Project.is_active == True)
            
            if status:
                query = query.filter(Project.status == status)
            
            if owner_nit:
                query = query.filter(Project.project_owner_nit == owner_nit)
            
            projects = query.offset(skip).limit(limit).all()
            return [ProjectResponse.from_orm(p) for p in projects]
        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
            raise
    
    def get_project(self, db: Session, project_id: int) -> Optional[ProjectResponse]:
        """
        Obtener un proyecto específico por ID
        """
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                return ProjectResponse.from_orm(project)
            return None
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {str(e)}")
            raise
    
    def update_project(self, db: Session, project_id: int, project: ProjectUpdate) -> Optional[ProjectResponse]:
        """
        Actualizar un proyecto
        """
        try:
            # Buscar el proyecto
            db_project = db.query(Project).filter(Project.id == project_id).first()
            if not db_project:
                return None
            
            # Verificar constructora si se está actualizando
            if project.project_owner_nit:
                project_owner = db.query(ProjectOwner).filter(ProjectOwner.nit == project.project_owner_nit).first()
                if not project_owner:
                    raise ValueError(f"No existe una constructora con el NIT {project.project_owner_nit}")
                if not project_owner.is_active:
                    raise ValueError(f"La constructora {project_owner.name} no está activa")
            
            # Actualizar campos
            update_data = project.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_project, field, value)
            
            db.commit()
            db.refresh(db_project)
            
            logger.info(f"Project updated: {db_project.name} (ID: {db_project.id})")
            return ProjectResponse.from_orm(db_project)
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error updating project: {str(e)}")
            raise ValueError("Error de integridad en la base de datos")
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating project {project_id}: {str(e)}")
            raise
    
    def update_project_state(self, db: Session, project_id: int, state_update: ProjectStateUpdate) -> Optional[ProjectResponse]:
        """
        Actualizar el estado de un proyecto
        """
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return None
            
            project.status = state_update.status
            db.commit()
            db.refresh(project)
            
            logger.info(f"Project state updated: {project.name} -> {state_update.status.value}")
            return ProjectResponse.from_orm(project)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating project state {project_id}: {str(e)}")
            raise
    
    def delete_project(self, db: Session, project_id: int) -> bool:
        """
        Eliminar un proyecto (soft delete)
        """
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False
            
            project.is_active = False
            project.status = ProjectStatus.ARCHIVADO
            db.commit()
            
            logger.info(f"Project deleted: {project.name} (ID: {project_id})")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting project {project_id}: {str(e)}")
            raise
    
    def get_project_history(self, db: Session, project_id: int) -> List[Dict[str, Any]]:
        """
        Obtener historial de cambios de un proyecto
        """
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return []
            
            # En una implementación real, esto se manejaría con una tabla de historial
            # Por ahora, retornamos información básica
            return [
                {
                    "action": "created",
                    "timestamp": project.created_at.isoformat(),
                    "details": f"Proyecto creado: {project.name}"
                },
                {
                    "action": "updated",
                    "timestamp": project.updated_at.isoformat(),
                    "details": f"Última actualización: {project.name}"
                }
            ]
        except Exception as e:
            logger.error(f"Error getting project history {project_id}: {str(e)}")
            raise
    
    def get_projects_by_owner(self, db: Session, owner_nit: str, skip: int = 0, limit: int = 100) -> List[ProjectResponse]:
        """
        Obtener proyectos de una constructora específica
        """
        try:
            projects = db.query(Project).filter(
                Project.project_owner_nit == owner_nit,
                Project.is_active == True
            ).offset(skip).limit(limit).all()
            
            return [ProjectResponse.from_orm(p) for p in projects]
        except Exception as e:
            logger.error(f"Error getting projects by owner {owner_nit}: {str(e)}")
            raise
    
    def get_projects_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[ProjectResponse]:
        """
        Obtener proyectos por estado
        """
        try:
            projects = db.query(Project).filter(
                Project.status == status,
                Project.is_active == True
            ).offset(skip).limit(limit).all()
            
            return [ProjectResponse.from_orm(p) for p in projects]
        except Exception as e:
            logger.error(f"Error getting projects by status {status}: {str(e)}")
            raise 