#!/usr/bin/env python3
"""
Manejador de webhooks para recibir notificaciones de cambios de constructoras
"""

import logging
from typing import Dict, Any
from database.database import SessionLocal
from models.models import ProjectOwner
from datetime import datetime

logger = logging.getLogger(__name__)

class WebhookHandler:
    """Manejador de webhooks para constructoras"""
    
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