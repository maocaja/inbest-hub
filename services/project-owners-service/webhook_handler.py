#!/usr/bin/env python3
"""
Manejador de webhooks para notificar cambios de constructoras
"""

import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WebhookNotifier:
    """Notificador de cambios vía webhooks"""
    
    def __init__(self):
        self.webhook_urls = {
            "projects_service": "http://localhost:8003/webhooks/project-owners"
        }
    
    def notify_project_owner_created(self, project_owner_data: Dict[str, Any]):
        """Notificar creación de constructora"""
        try:
            response = requests.post(
                f"{self.webhook_urls['projects_service']}/created",
                json=project_owner_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Webhook enviado exitosamente para constructora {project_owner_data.get('nit')}")
            else:
                logger.error(f"Error enviando webhook: {response.status_code}")
        except Exception as e:
            logger.error(f"Error enviando webhook: {e}")
    
    def notify_project_owner_updated(self, project_owner_data: Dict[str, Any]):
        """Notificar actualización de constructora"""
        try:
            response = requests.put(
                f"{self.webhook_urls['projects_service']}/updated",
                json=project_owner_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Webhook de actualización enviado para constructora {project_owner_data.get('nit')}")
            else:
                logger.error(f"Error enviando webhook de actualización: {response.status_code}")
        except Exception as e:
            logger.error(f"Error enviando webhook de actualización: {e}")
    
    def notify_project_owner_deleted(self, nit: str):
        """Notificar eliminación de constructora"""
        try:
            response = requests.delete(
                f"{self.webhook_urls['projects_service']}/deleted/{nit}",
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Webhook de eliminación enviado para constructora {nit}")
            else:
                logger.error(f"Error enviando webhook de eliminación: {response.status_code}")
        except Exception as e:
            logger.error(f"Error enviando webhook de eliminación: {e}") 