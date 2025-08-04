#!/usr/bin/env python3
"""
Manejador de webhooks para recibir notificaciones de cambios de constructoras
"""

import httpx
import logging
from typing import Dict, Any, Optional
from database.database import SessionLocal
from models.models import ProjectOwner
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class WebhookHandler:
    """Manejador de webhooks para constructoras"""
    
    def __init__(self):
        self.embedding_service_url = Config.EMBEDDING_SERVICE_URL
        
    async def notify_embedding_service(self, action: str, project_data: Dict[str, Any], project_id: int):
        """
        Notificar al embedding-service sobre cambios en proyectos
        
        Args:
            action: 'create', 'update', o 'delete'
            project_data: Datos del proyecto
            project_id: ID del proyecto
        """
        try:
            webhook_data = {
                "project_id": project_id,
                "action": action,
                "data": project_data if action != "delete" else None
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.embedding_service_url}/webhook/project-sync",
                    json=webhook_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully notified embedding-service about project {project_id} {action}")
                else:
                    logger.warning(f"Failed to notify embedding-service: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error notifying embedding-service: {e}")
    
    async def notify_project_owners_service(self, action: str, project_data: Dict[str, Any]):
        """
        Notificar al project-owners-service sobre cambios en proyectos
        """
        try:
            # Obtener el NIT de la constructora
            construction_company_nit = project_data.get("construction_company_nit")
            if not construction_company_nit:
                logger.warning("No construction_company_nit found in project data")
                return
            
            webhook_url = f"{Config.PROJECT_OWNERS_SERVICE_URL}/webhooks/projects/{action}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=project_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully notified project-owners-service about project {action}")
                else:
                    logger.warning(f"Failed to notify project-owners-service: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error notifying project-owners-service: {e}")
    
    async def handle_project_created(self, project_data: Dict[str, Any], project_id: int):
        """Manejar la creación de un proyecto"""
        await self.notify_embedding_service("create", project_data, project_id)
        await self.notify_project_owners_service("created", project_data)
    
    async def handle_project_updated(self, project_data: Dict[str, Any], project_id: int):
        """Manejar la actualización de un proyecto"""
        await self.notify_embedding_service("update", project_data, project_id)
        await self.notify_project_owners_service("updated", project_data)
    
    async def handle_project_deleted(self, project_id: int):
        """Manejar la eliminación de un proyecto"""
        await self.notify_embedding_service("delete", {}, project_id)
        await self.notify_project_owners_service("deleted", {"project_id": project_id})
    
    def handle_project_owner_created(self, project_owner_data: Dict[str, Any]) -> bool:
        """Manejar creación de constructora"""
        db = SessionLocal()
        try:
            # Verificar si ya existe
            existing = db.query(ProjectOwner).filter(ProjectOwner.nit == project_owner_data['nit']).first()
            if existing:
                logger.info(f"Constructora {project_owner_data['name']} ya existe")
                return True
            
            # Convertir fechas
            if 'created_at' in project_owner_data and isinstance(project_owner_data['created_at'], str):
                project_owner_data['created_at'] = datetime.fromisoformat(project_owner_data['created_at'].replace('Z', '+00:00'))
            if 'updated_at' in project_owner_data and isinstance(project_owner_data['updated_at'], str):
                project_owner_data['updated_at'] = datetime.fromisoformat(project_owner_data['updated_at'].replace('Z', '+00:00'))
            
            # Crear nueva constructora
            new_owner = ProjectOwner(**project_owner_data)
            db.add(new_owner)
            db.commit()
            
            logger.info(f"Constructora {project_owner_data['name']} creada vía webhook")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creando constructora vía webhook: {e}")
            return False
        finally:
            db.close()
    
    def handle_project_owner_updated(self, project_owner_data: Dict[str, Any]) -> bool:
        """Manejar actualización de constructora"""
        db = SessionLocal()
        try:
            # Buscar constructora existente
            existing = db.query(ProjectOwner).filter(ProjectOwner.nit == project_owner_data['nit']).first()
            if not existing:
                logger.warning(f"Constructora {project_owner_data['nit']} no encontrada para actualizar")
                return False
            
            # Convertir fechas
            if 'updated_at' in project_owner_data and isinstance(project_owner_data['updated_at'], str):
                project_owner_data['updated_at'] = datetime.fromisoformat(project_owner_data['updated_at'].replace('Z', '+00:00'))
            
            # Actualizar campos
            for field, value in project_owner_data.items():
                if hasattr(existing, field):
                    setattr(existing, field, value)
            
            db.commit()
            logger.info(f"Constructora {project_owner_data['name']} actualizada vía webhook")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error actualizando constructora vía webhook: {e}")
            return False
        finally:
            db.close()
    
    def handle_project_owner_deleted(self, nit: str) -> bool:
        """Manejar eliminación de constructora"""
        db = SessionLocal()
        try:
            # Buscar constructora
            existing = db.query(ProjectOwner).filter(ProjectOwner.nit == nit).first()
            if not existing:
                logger.warning(f"Constructora {nit} no encontrada para eliminar")
                return False
            
            # Soft delete (marcar como inactiva)
            existing.is_active = False
            db.commit()
            
            logger.info(f"Constructora {nit} marcada como inactiva vía webhook")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error eliminando constructora vía webhook: {e}")
            return False
        finally:
            db.close() 