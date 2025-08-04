import httpx
from typing import List, Dict, Any, Optional
from loguru import logger
from schemas.schemas import ChatRequest, ChatResponse, IntentAnalysis, IntentType
from services.openai_service import OpenAIService
from services.search_service import SearchService
from services.conversation_service import ConversationService
from services.response_generator import ResponseGenerator

class ChatService:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.search_service = SearchService()
        self.conversation_service = ConversationService()
        self.response_generator = ResponseGenerator()
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Procesa un mensaje del usuario y genera una respuesta natural"""
        try:
            # 1. Obtener o crear conversación
            conversation_id = await self.conversation_service.get_or_create_conversation(
                request.conversation_id, request.user_id
            )
            
            # 2. Analizar intención del mensaje
            intent = await self.openai_service.analyze_intent(request.message)
            
            # 3. Buscar proyectos si es necesario
            projects = []
            if intent.type == IntentType.SEARCH_PROJECTS:
                projects = await self.search_service.search_projects(intent.filters or {})
            
            # 4. Obtener contexto de la conversación
            conversation_history = await self.conversation_service.get_conversation_history(conversation_id)
            user_context = await self.conversation_service.get_user_context(conversation_id)
            
            # 5. Generar respuesta natural
            natural_response = await self.response_generator.generate_response(
                user_message=request.message,
                projects=projects,
                conversation_history=conversation_history,
                user_context=user_context,
                intent=intent
            )
            
            # 6. Generar sugerencias
            suggestions = await self.response_generator.generate_suggestions(
                intent, projects, user_context
            )
            
            # 7. Guardar mensajes en historial
            await self.conversation_service.add_message(
                conversation_id, "user", request.message,
                metadata={"intent": intent.dict()}
            )
            await self.conversation_service.add_message(
                conversation_id, "assistant", natural_response,
                metadata={"projects_count": len(projects)}
            )
            
            # 8. Detectar oportunidad de lead
            lead_opportunity = await self.response_generator.detect_lead_opportunity(
                request.message, projects, conversation_history
            )
            
            return ChatResponse(
                conversation_id=conversation_id,
                response=natural_response,
                projects=projects,
                suggestions=suggestions,
                metadata={
                    "intent": intent.dict(),
                    "lead_opportunity": lead_opportunity,
                    "projects_count": len(projects)
                }
            )
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            return ChatResponse(
                conversation_id=request.conversation_id or "error",
                response="Lo siento, tuve un problema procesando tu solicitud. ¿Podrías intentar de nuevo?",
                projects=[],
                suggestions=["Intentar de nuevo", "Contactar soporte"],
                metadata={"error": str(e)}
            )
    
    async def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtener todas las conversaciones de un usuario"""
        try:
            conversations = await self.conversation_service.get_user_conversations(user_id)
            return [conv.dict() for conv in conversations]
        except Exception as e:
            logger.error(f"Error obteniendo conversaciones: {e}")
            return []
    
    async def get_conversation_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Obtener todos los mensajes de una conversación"""
        try:
            messages = await self.conversation_service.get_conversation_messages(conversation_id)
            return [msg.dict() for msg in messages]
        except Exception as e:
            logger.error(f"Error obteniendo mensajes: {e}")
            return []
    
    async def close_conversation(self, conversation_id: str) -> bool:
        """Cerrar una conversación"""
        try:
            await self.conversation_service.close_conversation(conversation_id)
            return True
        except Exception as e:
            logger.error(f"Error cerrando conversación: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar salud de todos los servicios"""
        health_status = {
            "chat_service": "healthy",
            "openai_service": "unknown",
            "search_service": "unknown",
            "database": "unknown"
        }
        
        try:
            # Verificar OpenAI
            test_intent = await self.openai_service.analyze_intent("test")
            if test_intent:
                health_status["openai_service"] = "healthy"
        except Exception as e:
            health_status["openai_service"] = f"error: {str(e)}"
        
        try:
            # Verificar servicios externos
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Verificar embedding-service
                embedding_response = await client.get(f"{self.search_service.embedding_service_url}/health")
                if embedding_response.status_code == 200:
                    health_status["embedding_service"] = "healthy"
                else:
                    health_status["embedding_service"] = "unhealthy"
                
                # Verificar projects-service
                projects_response = await client.get(f"{self.search_service.projects_service_url}/health")
                if projects_response.status_code == 200:
                    health_status["projects_service"] = "healthy"
                else:
                    health_status["projects_service"] = "unhealthy"
        except Exception as e:
            health_status["external_services"] = f"error: {str(e)}"
        
        try:
            # Verificar base de datos
            from database.database import get_db
            db = next(get_db())
            db.execute("SELECT 1")
            health_status["database"] = "healthy"
        except Exception as e:
            health_status["database"] = f"error: {str(e)}"
        
        return health_status 