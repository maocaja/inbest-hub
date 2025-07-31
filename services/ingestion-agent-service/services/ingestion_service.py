"""
Servicio principal de ingestión que coordina todos los componentes
"""

import logging
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from models.models import ConversationSession, ConversationMessage, DocumentUpload, IngestionTask, ProjectDraft
from schemas.schemas import SessionCreate, MessageCreate, TaskCreate, ProjectDraftCreate
from utils.document_processor import DocumentProcessor
from services.llm_service import LLMService
from config import Config
import requests

logger = logging.getLogger(__name__)

class IngestionService:
    """
    Servicio principal para coordinar la ingestión de proyectos
    """
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.llm_service = LLMService()
    
    def create_session(self, db: Session, session_data: SessionCreate) -> Dict[str, Any]:
        """
        Crear una nueva sesión de conversación
        """
        try:
            session_id = str(uuid.uuid4())
            
            # Crear sesión en base de datos
            db_session = ConversationSession(
                session_id=session_id,
                project_owner_nit=session_data.project_owner_nit,
                user_id=session_data.user_id,
                user_name=session_data.user_name,
                status="active",
                current_step="initialization"
            )
            
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            
            logger.info(f"Nueva sesión creada: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Sesión iniciada exitosamente. ¡Hola! Soy tu asistente para proyectos inmobiliarios. ¿En qué puedo ayudarte hoy?"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creando sesión: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_message(self, db: Session, session_id: str, message: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Procesar mensaje del usuario y generar respuesta
        """
        try:
            # Verificar que la sesión existe
            session = db.query(ConversationSession).filter(ConversationSession.session_id == session_id).first()
            if not session:
                return {
                    "success": False,
                    "error": "Sesión no encontrada"
                }
            
            # Guardar mensaje del usuario
            user_message = ConversationMessage(
                session_id=session_id,
                role="user",
                content=message,
                message_metadata=metadata
            )
            db.add(user_message)
            
            # Obtener historial de conversación
            conversation_history = self._get_conversation_history(db, session_id)
            
            # Obtener herramientas disponibles
            tools = self._get_available_tools()
            
            # Generar respuesta del LLM con herramientas
            llm_response = self.llm_service.generate_response(conversation_history, tools)
            
            if not llm_response["success"]:
                return llm_response
            
            # Debug: verificar respuesta del LLM
            logger.info(f"LLM Response: {llm_response}")
            
            # Guardar respuesta del asistente
            assistant_response = llm_response.get("response")
            if assistant_response is None and llm_response.get("tool_calls"):
                assistant_response = "Procesando información con herramientas disponibles..."
            elif assistant_response is None:
                assistant_response = "No se pudo generar una respuesta."
            
            logger.info(f"Assistant Response: {assistant_response}")
            
            assistant_message = ConversationMessage(
                session_id=session_id,
                role="assistant",
                content=assistant_response
            )
            db.add(assistant_message)
            
            # Actualizar última actividad
            session.last_activity = datetime.utcnow()
            
            db.commit()
            
            # Preparar respuesta
            response_data = {
                "session_id": session_id,
                "assistant_message": assistant_response,
                "status": "active"
            }
            
            # Agregar información adicional si hay tool calls
            if llm_response.get("tool_calls"):
                tool_results = self._process_tool_calls(db, session_id, llm_response["tool_calls"])
                response_data.update(tool_results)
            
            return {
                "success": True,
                **response_data
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error procesando mensaje: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_document(self, db: Session, session_id: str, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Subir y procesar documento
        """
        try:
            # Verificar que la sesión existe
            session = db.query(ConversationSession).filter(ConversationSession.session_id == session_id).first()
            if not session:
                return {
                    "success": False,
                    "error": "Sesión no encontrada"
                }
            
            # Validar archivo
            validation = self.document_processor.validate_file(file_path)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"]
                }
            
            # Crear registro de documento
            file_size = validation["file_info"]["size"]
            file_type = validation["file_info"]["type"]
            
            db_document = DocumentUpload(
                session_id=session_id,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                processing_status="processing"
            )
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            
            # Procesar documento
            processing_result = self.document_processor.process_document(file_path)
            
            if processing_result["success"]:
                # Actualizar documento con datos extraídos
                db_document.processing_status = "completed"
                db_document.extracted_data = processing_result["extracted_data"]
                db_document.processed_at = datetime.utcnow()
                
                # Extraer información del proyecto usando LLM
                if "text_content" in processing_result["extracted_data"]:
                    llm_extraction = self.llm_service.extract_project_info(
                        processing_result["extracted_data"]["text_content"]
                    )
                    
                    if llm_extraction["success"]:
                        # Combinar datos extraídos
                        combined_data = {
                            **processing_result["extracted_data"]["project_info"],
                            **llm_extraction["extracted_data"]
                        }
                        
                        # Crear o actualizar borrador del proyecto
                        self._update_project_draft(db, session_id, combined_data)
                        
                        # Generar mensaje de respuesta
                        extracted_info = llm_extraction["extracted_data"]
                        response_message = f"""
¡Excelente! He procesado tu documento y extraje la siguiente información:

📋 **Información extraída:**
"""
                        
                        if extracted_info.get("name"):
                            response_message += f"• **Nombre del proyecto:** {extracted_info['name']}\n"
                        if extracted_info.get("location"):
                            response_message += f"• **Ubicación:** {extracted_info['location']}\n"
                        if extracted_info.get("price"):
                            response_message += f"• **Precio:** {extracted_info['price']}\n"
                        if extracted_info.get("units"):
                            response_message += f"• **Unidades:** {extracted_info['units']}\n"
                        
                        response_message += f"""
¿Te gustaría que complete la información faltante o que corrija algún dato extraído?
"""
                        
                        # Guardar mensaje del sistema
                        system_message = ConversationMessage(
                            session_id=session_id,
                            role="assistant",
                            content=response_message,
                            message_metadata={"document_processed": True, "extracted_data": combined_data}
                        )
                        db.add(system_message)
                        
                        db.commit()
                        
                        return {
                            "success": True,
                            "upload_id": db_document.id,
                            "processing_status": "completed",
                            "extracted_data": combined_data,
                            "message": response_message
                        }
                
                # Si no se pudo extraer con LLM, usar datos básicos
                basic_data = processing_result["extracted_data"].get("project_info", {})
                self._update_project_draft(db, session_id, basic_data)
                
                response_message = f"""
He procesado tu documento '{filename}'. 

📄 **Información básica extraída:**
"""
                
                for key, value in basic_data.items():
                    if value:
                        response_message += f"• **{key.title()}:** {value}\n"
                
                response_message += """
¿Te gustaría que complete la información faltante del proyecto?
"""
                
                # Guardar mensaje del sistema
                system_message = ConversationMessage(
                    session_id=session_id,
                    role="assistant",
                    content=response_message,
                    message_metadata={"document_processed": True, "extracted_data": basic_data}
                )
                db.add(system_message)
                
                db.commit()
                
                return {
                    "success": True,
                    "upload_id": db_document.id,
                    "processing_status": "completed",
                    "extracted_data": basic_data,
                    "message": response_message
                }
            else:
                # Error en procesamiento
                db_document.processing_status = "failed"
                db.commit()
                
                return {
                    "success": False,
                    "error": processing_result["error"]
                }
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error procesando documento: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_session_status(self, db: Session, session_id: str) -> Dict[str, Any]:
        """
        Obtener estado de la sesión
        """
        try:
            session = db.query(ConversationSession).filter(ConversationSession.session_id == session_id).first()
            if not session:
                return {
                    "success": False,
                    "error": "Sesión no encontrada"
                }
            
            # Obtener borrador del proyecto
            project_draft = db.query(ProjectDraft).filter(ProjectDraft.session_id == session_id).first()
            
            # Calcular porcentaje de completitud
            completion_percentage = 0
            missing_fields = []
            
            if project_draft:
                completion_percentage = project_draft.completion_percentage
                # TODO: Calcular campos faltantes específicos
            
            return {
                "success": True,
                "session_id": session_id,
                "status": session.status,
                "completion_percentage": completion_percentage,
                "current_step": session.current_step,
                "project_data": project_draft.project_data if project_draft else {},
                "missing_fields": missing_fields,
                "created_at": session.created_at,
                "last_activity": session.last_activity
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de sesión: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_conversation_history(self, db: Session, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Obtener historial de conversación
        """
        messages = db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        ).order_by(ConversationMessage.timestamp.desc()).limit(limit).all()
        
        # Convertir a formato esperado por LLM
        history = []
        for message in reversed(messages):  # Ordenar cronológicamente
            history.append({
                "role": message.role,
                "content": message.content
            })
        
        return history
    
    def _update_project_draft(self, db: Session, session_id: str, project_data: Dict[str, Any]):
        """
        Actualizar borrador del proyecto
        """
        try:
            # Buscar borrador existente
            draft = db.query(ProjectDraft).filter(ProjectDraft.session_id == session_id).first()
            
            if draft:
                # Actualizar datos existentes
                current_data = draft.project_data
                current_data.update(project_data)
                draft.project_data = current_data
                draft.updated_at = datetime.utcnow()
            else:
                # Crear nuevo borrador
                draft = ProjectDraft(
                    session_id=session_id,
                    project_data=project_data,
                    completion_percentage=0,
                    status="draft"
                )
                db.add(draft)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error actualizando borrador: {e}")
            db.rollback()
    
    def _process_tool_calls(self, db: Session, session_id: str, tool_calls: List) -> Dict[str, Any]:
        """
        Procesar llamadas de herramientas
        """
        results = {}
        
        for tool_call in tool_calls:
            # Manejar tanto objetos ChatCompletionMessageToolCall como diccionarios
            if hasattr(tool_call, 'function'):
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
            else:
                tool_name = tool_call.get("function", {}).get("name")
                arguments = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
            
            if tool_name == "get_project_owner_info":
                result = self._call_project_owners_service("GET", f"/project-owners/nit/{arguments.get('nit')}")
            elif tool_name == "create_project":
                result = self._call_projects_service("POST", "/projects", arguments.get('project_data'))
            elif tool_name == "update_project":
                result = self._call_projects_service("PUT", f"/projects/{arguments.get('project_id')}", arguments.get('updates'))
            elif tool_name == "get_project":
                result = self._call_projects_service("GET", f"/projects/{arguments.get('project_id')}")
            elif tool_name == "list_missing_fields":
                result = self._get_missing_fields(db, session_id)
            elif tool_name == "generate_project_description":
                result = self._generate_description(db, session_id)
            else:
                result = {"success": False, "error": f"Herramienta no reconocida: {tool_name}"}
            
            results[f"tool_{tool_name}"] = result
        
        return results
    
    def _call_projects_service(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Llamar al servicio de proyectos
        """
        try:
            url = f"{Config.PROJECTS_SERVICE_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)
            else:
                return {"success": False, "error": f"Método no soportado: {method}"}
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Error {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_missing_fields(self, db: Session, session_id: str) -> Dict[str, Any]:
        """
        Obtener campos faltantes del proyecto
        """
        try:
            draft = db.query(ProjectDraft).filter(ProjectDraft.session_id == session_id).first()
            if not draft:
                return {"success": False, "error": "No hay borrador de proyecto"}
            
            project_data = draft.project_data
            required_fields = [
                "name", "description", "project_owner_nit", "location", 
                "price_info", "unit_info", "amenities", "financial_info"
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in project_data or not project_data[field]:
                    missing_fields.append(field)
            
            completion_percentage = int((len(required_fields) - len(missing_fields)) / len(required_fields) * 100)
            
            return {
                "success": True,
                "missing_fields": missing_fields,
                "completion_percentage": completion_percentage
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_description(self, db: Session, session_id: str) -> Dict[str, Any]:
        """
        Generar descripción del proyecto
        """
        try:
            draft = db.query(ProjectDraft).filter(ProjectDraft.session_id == session_id).first()
            if not draft:
                return {"success": False, "error": "No hay borrador de proyecto"}
            
            result = self.llm_service.generate_project_description(draft.project_data)
            
            if result["success"]:
                # Actualizar descripción en el borrador
                draft.project_data["description"] = result["description"]
                db.commit()
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)} 

    def _get_available_tools(self) -> List[Dict]:
        """
        Definir herramientas disponibles para el LLM
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_project_owner_info",
                    "description": "Obtener información de una constructora por NIT",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "nit": {
                                "type": "string",
                                "description": "NIT de la constructora"
                            }
                        },
                        "required": ["nit"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_project",
                    "description": "Crear un nuevo proyecto inmobiliario",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_data": {
                                "type": "object",
                                "description": "Datos completos del proyecto a crear"
                            }
                        },
                        "required": ["project_data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_project",
                    "description": "Actualizar datos de un proyecto existente",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "integer",
                                "description": "ID del proyecto"
                            },
                            "updates": {
                                "type": "object",
                                "description": "Datos a actualizar"
                            }
                        },
                        "required": ["project_id", "updates"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_project",
                    "description": "Obtener información de un proyecto por ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "integer",
                                "description": "ID del proyecto"
                            }
                        },
                        "required": ["project_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_missing_fields",
                    "description": "Listar campos faltantes del proyecto actual",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_project_description",
                    "description": "Generar descripción profesional del proyecto",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

    def _call_project_owners_service(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Llamar al servicio de project-owners
        """
        try:
            url = f"{Config.PROJECT_OWNERS_SERVICE_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)
            else:
                return {"success": False, "error": f"Método no soportado: {method}"}
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Error {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)} 