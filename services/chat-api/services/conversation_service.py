import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger
from database.database import get_db
from database.models import Conversation, Message, User
from schemas.schemas import ConversationInfo, MessageInfo, MessageRole

class ConversationService:
    def __init__(self):
        pass
    
    async def get_or_create_conversation(self, conversation_id: Optional[str], user_id: Optional[str]) -> str:
        """Obtiene una conversación existente o crea una nueva"""
        try:
            if not user_id:
                user_id = f"user_{uuid.uuid4().hex[:8]}"
            
            if conversation_id:
                # Verificar si la conversación existe
                db = next(get_db())
                existing_conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
                if existing_conv:
                    return conversation_id
            
            # Crear nueva conversación
            conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
            await self._ensure_user_exists(user_id)
            await self._create_conversation(conversation_id, user_id)
            
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error obteniendo/creando conversación: {e}")
            return f"conv_{uuid.uuid4().hex[:8]}"
    
    async def _ensure_user_exists(self, user_id: str):
        """Asegura que el usuario existe en la base de datos"""
        try:
            db = next(get_db())
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                user = User(
                    id=user_id,
                    created_at=datetime.utcnow(),
                    last_active=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                logger.info(f"Usuario {user_id} creado")
                
        except Exception as e:
            logger.error(f"Error asegurando existencia de usuario: {e}")
    
    async def _create_conversation(self, conversation_id: str, user_id: str):
        """Crea una nueva conversación"""
        try:
            db = next(get_db())
            conversation = Conversation(
                id=conversation_id,
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                status="active",
                message_count=0
            )
            db.add(conversation)
            db.commit()
            logger.info(f"Conversación {conversation_id} creada")
            
        except Exception as e:
            logger.error(f"Error creando conversación: {e}")
    
    async def add_message(self, conversation_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Agrega un mensaje a la conversación"""
        try:
            db = next(get_db())
            
            # Crear mensaje
            message = Message(
                id=f"msg_{uuid.uuid4().hex[:8]}",
                conversation_id=conversation_id,
                role=role,
                content=content,
                timestamp=datetime.utcnow(),
                metadata_json=metadata or {}
            )
            db.add(message)
            
            # Actualizar conversación
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.updated_at = datetime.utcnow()
                conversation.message_count += 1
            
            db.commit()
            logger.info(f"Mensaje agregado a conversación {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error agregando mensaje: {e}")
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene el historial reciente de una conversación"""
        try:
            db = next(get_db())
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata_json
                }
                for msg in reversed(messages)  # Orden cronológico
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []
    
    async def get_user_conversations(self, user_id: str) -> List[ConversationInfo]:
        """Obtiene todas las conversaciones de un usuario"""
        try:
            db = next(get_db())
            conversations = db.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(Conversation.updated_at.desc()).all()
            
            return [
                ConversationInfo(
                    id=conv.id,
                    user_id=conv.user_id,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=conv.message_count,
                    last_message="",  # TODO: Implementar
                    status=conv.status
                )
                for conv in conversations
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo conversaciones: {e}")
            return []
    
    async def get_conversation_messages(self, conversation_id: str) -> List[MessageInfo]:
        """Obtiene todos los mensajes de una conversación"""
        try:
            db = next(get_db())
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp.asc()).all()
            
            return [
                MessageInfo(
                    id=msg.id,
                    role=MessageRole(msg.role),
                    content=msg.content,
                    timestamp=msg.timestamp,
                    metadata=msg.metadata_json
                )
                for msg in messages
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo mensajes: {e}")
            return []
    
    async def get_user_context(self, conversation_id: str) -> Dict[str, Any]:
        """Extrae contexto del usuario basado en el historial de conversación"""
        try:
            # Obtener historial reciente
            history = await self.get_conversation_history(conversation_id, limit=20)
            
            # Extraer preferencias del historial
            preferences = self._extract_preferences_from_history(history)
            
            return {
                "preferences": preferences,
                "conversation_length": len(history),
                "last_interaction": history[-1]["timestamp"] if history else None
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo contexto: {e}")
            return {"preferences": {}, "conversation_length": 0}
    
    def _extract_preferences_from_history(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrae preferencias del usuario del historial de mensajes"""
        preferences = {
            "zones": [],
            "price_range": {"min": 0, "max": float('inf')},
            "property_type": [],
            "amenities": []
        }
        
        # Palabras clave para detectar preferencias
        zone_keywords = ["chapinero", "usaquén", "suba", "engativá", "bogotá", "medellín", "cali"]
        property_keywords = ["apartamento", "casa", "duplex", "penthouse", "estudio"]
        amenity_keywords = ["piscina", "gimnasio", "seguridad", "parqueadero", "ascensor"]
        
        for message in messages:
            if message["role"] == "user":
                content = message["content"].lower()
                
                # Detectar zonas
                for zone in zone_keywords:
                    if zone in content:
                        if zone not in preferences["zones"]:
                            preferences["zones"].append(zone)
                
                # Detectar tipo de propiedad
                for prop_type in property_keywords:
                    if prop_type in content:
                        if prop_type not in preferences["property_type"]:
                            preferences["property_type"].append(prop_type)
                
                # Detectar amenities
                for amenity in amenity_keywords:
                    if amenity in content:
                        if amenity not in preferences["amenities"]:
                            preferences["amenities"].append(amenity)
        
        return preferences
    
    async def close_conversation(self, conversation_id: str):
        """Cierra una conversación"""
        try:
            db = next(get_db())
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            
            if conversation:
                conversation.status = "closed"
                conversation.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Conversación {conversation_id} cerrada")
                return True
            else:
                logger.warning(f"Conversación {conversation_id} no encontrada")
                return False
                
        except Exception as e:
            logger.error(f"Error cerrando conversación: {e}")
            return False 