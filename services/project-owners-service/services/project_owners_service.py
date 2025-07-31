"""
Servicio de lógica de negocio para Project Owners
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging
import requests

from models.models import ProjectOwner
from schemas.schemas import ProjectOwnerCreate, ProjectOwnerUpdate, ProjectOwnerResponse
from config import Config

logger = logging.getLogger(__name__)

class ProjectOwnersService:
    """
    Servicio para gestionar constructoras/propietarios de proyectos
    """
    
    def create_project_owner(self, db: Session, project_owner: ProjectOwnerCreate) -> ProjectOwnerResponse:
        """
        Crear una nueva constructora/propietario
        """
        try:
            # Verificar si ya existe un NIT
            if Config.NIT_UNIQUE:
                existing_nit = db.query(ProjectOwner).filter(ProjectOwner.nit == project_owner.nit).first()
                if existing_nit:
                    raise ValueError(f"Ya existe una constructora con el NIT {project_owner.nit}")
            
            # Verificar si ya existe un email
            if Config.EMAIL_UNIQUE:
                existing_email = db.query(ProjectOwner).filter(ProjectOwner.email == project_owner.email).first()
                if existing_email:
                    raise ValueError(f"Ya existe una constructora con el email {project_owner.email}")
            
            # Crear el nuevo project owner
            db_project_owner = ProjectOwner(**project_owner.dict())
            db.add(db_project_owner)
            db.commit()
            db.refresh(db_project_owner)
            
            logger.info(f"Project owner created: {db_project_owner.name} (NIT: {db_project_owner.nit})")
            
            # Notificar vía webhook a otros servicios
            try:
                self._notify_webhook_created(db_project_owner)
            except Exception as e:
                logger.warning(f"Error enviando webhook: {e}")
            
            return ProjectOwnerResponse.from_orm(db_project_owner)
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error creating project owner: {str(e)}")
            raise ValueError("Error de integridad en la base de datos")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating project owner: {str(e)}")
            raise
    
    def _notify_webhook_created(self, project_owner):
        """Notificar creación vía webhook"""
        try:
            webhook_url = "http://localhost:8003/webhooks/project-owners/created"
            project_owner_data = {
                "nit": project_owner.nit,
                "name": project_owner.name,
                "email": project_owner.email,
                "phone": project_owner.phone,
                "address": project_owner.address,
                "city": project_owner.city,
                "department": project_owner.department,
                "country": project_owner.country,
                "website": project_owner.website,
                "contact_person": project_owner.contact_person,
                "contact_phone": project_owner.contact_phone,
                "contact_email": project_owner.contact_email,
                "is_active": project_owner.is_active,
                "is_verified": project_owner.is_verified,
                "created_at": project_owner.created_at.isoformat() if project_owner.created_at else None,
                "updated_at": project_owner.updated_at.isoformat() if project_owner.updated_at else None
            }
            
            response = requests.post(
                webhook_url,
                json=project_owner_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook enviado exitosamente para constructora {project_owner.nit}")
            else:
                logger.error(f"Error enviando webhook: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error enviando webhook: {e}")
    
    def get_project_owners(self, db: Session, skip: int = 0, limit: int = 100) -> List[ProjectOwnerResponse]:
        """
        Obtener lista de constructoras/propietarios
        """
        try:
            project_owners = db.query(ProjectOwner).offset(skip).limit(limit).all()
            return [ProjectOwnerResponse.from_orm(po) for po in project_owners]
        except Exception as e:
            logger.error(f"Error getting project owners: {str(e)}")
            raise
    
    def get_project_owner(self, db: Session, nit: str) -> Optional[ProjectOwnerResponse]:
        """
        Obtener una constructora/propietario por NIT
        """
        try:
            project_owner = db.query(ProjectOwner).filter(ProjectOwner.nit == nit).first()
            if project_owner:
                return ProjectOwnerResponse.from_orm(project_owner)
            return None
        except Exception as e:
            logger.error(f"Error getting project owner {nit}: {str(e)}")
            raise
    
    def get_project_owner_by_nit(self, db: Session, nit: str) -> Optional[ProjectOwnerResponse]:
        """
        Obtener una constructora/propietario por NIT
        """
        try:
            project_owner = db.query(ProjectOwner).filter(ProjectOwner.nit == nit).first()
            if project_owner:
                return ProjectOwnerResponse.from_orm(project_owner)
            return None
        except Exception as e:
            logger.error(f"Error getting project owner by NIT {nit}: {str(e)}")
            raise
    
    def update_project_owner(self, db: Session, nit: str, project_owner: ProjectOwnerUpdate) -> Optional[ProjectOwnerResponse]:
        """
        Actualizar una constructora/propietario
        """
        try:
            # Buscar el project owner
            db_project_owner = db.query(ProjectOwner).filter(ProjectOwner.nit == nit).first()
            if not db_project_owner:
                return None
            
            # Verificar NIT único si se está actualizando
            if project_owner.nit and Config.NIT_UNIQUE:
                existing_nit = db.query(ProjectOwner).filter(
                    ProjectOwner.nit == project_owner.nit,
                    ProjectOwner.nit != nit
                ).first()
                if existing_nit:
                    raise ValueError(f"Ya existe una constructora con el NIT {project_owner.nit}")
            
            # Verificar email único si se está actualizando
            if project_owner.email and Config.EMAIL_UNIQUE:
                existing_email = db.query(ProjectOwner).filter(
                    ProjectOwner.email == project_owner.email,
                    ProjectOwner.nit != nit
                ).first()
                if existing_email:
                    raise ValueError(f"Ya existe una constructora con el email {project_owner.email}")
            
            # Actualizar campos
            update_data = project_owner.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_project_owner, field, value)
            
            db.commit()
            db.refresh(db_project_owner)
            
            logger.info(f"Project owner updated: {db_project_owner.name} (NIT: {db_project_owner.nit})")
            return ProjectOwnerResponse.from_orm(db_project_owner)
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error updating project owner: {str(e)}")
            raise ValueError("Error de integridad en la base de datos")
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating project owner {project_owner_id}: {str(e)}")
            raise
    
    def delete_project_owner(self, db: Session, nit: str) -> bool:
        """
        Eliminar una constructora/propietario
        """
        try:
            project_owner = db.query(ProjectOwner).filter(ProjectOwner.nit == nit).first()
            if not project_owner:
                return False
            
            db.delete(project_owner)
            db.commit()
            
            logger.info(f"Project owner deleted: {project_owner.name} (NIT: {nit})")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting project owner {project_owner_id}: {str(e)}")
            raise
    
    def deactivate_project_owner(self, db: Session, nit: str) -> Optional[ProjectOwnerResponse]:
        """
        Desactivar una constructora/propietario (soft delete)
        """
        try:
            project_owner = db.query(ProjectOwner).filter(ProjectOwner.nit == nit).first()
            if not project_owner:
                return None
            
            project_owner.is_active = False
            db.commit()
            db.refresh(project_owner)
            
            logger.info(f"Project owner deactivated: {project_owner.name} (NIT: {nit})")
            return ProjectOwnerResponse.from_orm(project_owner)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deactivating project owner {project_owner_id}: {str(e)}")
            raise
    
    def activate_project_owner(self, db: Session, nit: str) -> Optional[ProjectOwnerResponse]:
        """
        Activar una constructora/propietario
        """
        try:
            project_owner = db.query(ProjectOwner).filter(ProjectOwner.nit == nit).first()
            if not project_owner:
                return None
            
            project_owner.is_active = True
            db.commit()
            db.refresh(project_owner)
            
            logger.info(f"Project owner activated: {project_owner.name} (NIT: {nit})")
            return ProjectOwnerResponse.from_orm(project_owner)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error activating project owner {project_owner_id}: {str(e)}")
            raise
    
    def verify_project_owner(self, db: Session, nit: str) -> Optional[ProjectOwnerResponse]:
        """
        Verificar una constructora/propietario
        """
        try:
            project_owner = db.query(ProjectOwner).filter(ProjectOwner.nit == nit).first()
            if not project_owner:
                return None
            
            project_owner.is_verified = True
            db.commit()
            db.refresh(project_owner)
            
            logger.info(f"Project owner verified: {project_owner.name} (NIT: {nit})")
            return ProjectOwnerResponse.from_orm(project_owner)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error verifying project owner {project_owner_id}: {str(e)}")
            raise 