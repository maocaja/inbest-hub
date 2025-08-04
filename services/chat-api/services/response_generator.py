from typing import List, Dict, Any, Optional
from loguru import logger
from .openai_service import OpenAIService
from .search_service import SearchService
from .conversation_service import ConversationService
from schemas.schemas import IntentAnalysis, IntentType

class ResponseGenerator:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.system_prompt = self.load_system_prompt()
    
    def load_system_prompt(self) -> str:
        """Carga el prompt del sistema para generar respuestas naturales"""
        return """
        Eres un asistente inmobiliario experto y amigable. Tu objetivo es ayudar a los usuarios a encontrar 
        propiedades que se ajusten a sus necesidades y preferencias.

        INSTRUCCIONES:
        1. SIEMPRE genera respuestas naturales y conversacionales, NO respuestas robóticas o genéricas
        2. Usa un tono amigable, profesional y empático
        3. Personaliza las respuestas basándote en el contexto del usuario
        4. Menciona detalles específicos de los proyectos cuando sea relevante
        5. Ofrece sugerencias útiles y contextuales
        6. Si no hay proyectos que coincidan, sugiere alternativas o ajustes en la búsqueda

        CONTEXTO DEL USUARIO:
        {user_context}

        PROYECTOS ENCONTRADOS:
        {projects_info}

        HISTORIAL DE CONVERSACIÓN:
        {conversation_history}

        INTENCIÓN DETECTADA:
        {intent_info}

        MENSAJE DEL USUARIO:
        {user_message}

        Genera una respuesta natural, conversacional y útil que:
        - Acknowledge el mensaje del usuario
        - Presente los proyectos encontrados de manera atractiva
        - Mencione características relevantes (ubicación, precio, amenities)
        - Ofrezca sugerencias para continuar la conversación
        - Mantenga un tono profesional pero amigable
        """
    
    async def generate_response(self, 
                              user_message: str,
                              projects: List[Dict[str, Any]], 
                              conversation_history: List[Dict[str, Any]], 
                              user_context: Dict[str, Any], 
                              intent: IntentAnalysis) -> str:
        """Genera una respuesta natural usando el LLM"""
        try:
            # Construir contexto completo
            context = self._build_context(
                user_message, projects, conversation_history, user_context, intent
            )
            
            # Generar respuesta con OpenAI
            response = await self.openai_service.generate_response(context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return self._generate_fallback_response(projects, intent)
    
    def _build_context(self, user_message: str, projects: List[Dict[str, Any]], 
                       conversation_history: List[Dict[str, Any]], user_context: Dict[str, Any],
                       intent: IntentAnalysis) -> str:
        """Construye el contexto completo para el LLM"""
        
        # Formatear información del usuario
        user_info = self._format_user_context(user_context)
        
        # Formatear proyectos
        projects_info = self._format_projects(projects)
        
        # Formatear historial de conversación
        history_info = self._format_conversation_history(conversation_history)
        
        # Formatear intención
        intent_info = self._format_intent(intent)
        
        # Construir contexto completo
        context = self.system_prompt.format(
            user_context=user_info,
            projects_info=projects_info,
            conversation_history=history_info,
            intent_info=intent_info,
            user_message=user_message
        )
        
        return context
    
    def _format_user_context(self, user_context: Dict[str, Any]) -> str:
        """Formatea el contexto del usuario para el LLM"""
        if not user_context:
            return "Sin información específica del usuario."
        
        preferences = user_context.get("preferences", {})
        
        context_parts = []
        
        # Zonas preferidas
        zones = preferences.get("zones", [])
        if zones:
            context_parts.append(f"Zonas de interés: {', '.join(zones)}")
        
        # Tipo de propiedad
        property_types = preferences.get("property_type", [])
        if property_types:
            context_parts.append(f"Tipos de propiedad: {', '.join(property_types)}")
        
        # Amenities
        amenities = preferences.get("amenities", [])
        if amenities:
            context_parts.append(f"Amenities de interés: {', '.join(amenities)}")
        
        # Rango de precio
        price_range = preferences.get("price_range", {})
        if price_range.get("min") or price_range.get("max"):
            min_price = price_range.get("min", 0)
            max_price = price_range.get("max", "sin límite")
            context_parts.append(f"Rango de precio: ${min_price:,} - ${max_price:,}")
        
        # Longitud de conversación
        conversation_length = user_context.get("conversation_length", 0)
        if conversation_length > 0:
            context_parts.append(f"Conversación activa con {conversation_length} mensajes")
        
        return "\n".join(context_parts) if context_parts else "Sin preferencias específicas detectadas."
    
    def _format_projects(self, projects: List[Dict[str, Any]]) -> str:
        """Formatea la información de proyectos para el LLM"""
        if not projects:
            return "No se encontraron proyectos que coincidan con la búsqueda."
        
        projects_info = []
        
        for i, project in enumerate(projects[:5], 1):  # Máximo 5 proyectos
            project_info = f"{i}. {project.get('name', 'Proyecto sin nombre')}"
            
            # Ubicación
            location = project.get("location", {})
            if isinstance(location, dict):
                city = location.get("city", "")
                department = location.get("department", "")
                if city:
                    project_info += f" - Ubicado en {city}"
                    if department and department != city:
                        project_info += f", {department}"
            
            # Precio
            price_info = project.get("price_info", {})
            if isinstance(price_info, dict):
                min_price = price_info.get("min_price")
                max_price = price_info.get("max_price")
                if min_price:
                    project_info += f" - Precio desde ${min_price:,}"
                    if max_price and max_price != min_price:
                        project_info += f" hasta ${max_price:,}"
            
            # Amenities
            amenities = project.get("amenities", [])
            if amenities and isinstance(amenities, list):
                project_info += f" - Amenities: {', '.join(amenities[:3])}"  # Máximo 3 amenities
            
            # Score
            score = project.get("final_score", 0)
            if score > 0:
                project_info += f" (Relevancia: {score:.1%})"
            
            projects_info.append(project_info)
        
        return "\n".join(projects_info)
    
    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Formatea el historial de conversación para el LLM"""
        if not history:
            return "Sin historial de conversación previo."
        
        # Tomar solo los últimos 5 mensajes para no sobrecargar el contexto
        recent_history = history[-5:]
        
        history_parts = []
        for msg in recent_history:
            role = "Usuario" if msg["role"] == "user" else "Asistente"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            history_parts.append(f"{role}: {content}")
        
        return "\n".join(history_parts)
    
    def _format_intent(self, intent: IntentAnalysis) -> str:
        """Formatea la información de intención para el LLM"""
        intent_type = intent.type.value
        confidence = intent.confidence
        
        intent_info = f"Tipo de intención: {intent_type} (confianza: {confidence:.1%})"
        
        if intent.entities:
            entities = ", ".join([f"{k}: {v}" for k, v in intent.entities.items()])
            intent_info += f"\nEntidades detectadas: {entities}"
        
        if intent.filters:
            filters = ", ".join([f"{k}: {v}" for k, v in intent.filters.items()])
            intent_info += f"\nFiltros aplicados: {filters}"
        
        return intent_info
    
    def _generate_fallback_response(self, projects: List[Dict[str, Any]], intent: IntentAnalysis) -> str:
        """Genera una respuesta de fallback cuando hay errores"""
        if intent.type == IntentType.SEARCH_PROJECTS:
            if projects:
                return f"Encontré {len(projects)} proyectos que podrían interesarte. ¿Te gustaría que te muestre más detalles de alguno en particular?"
            else:
                return "No encontré proyectos que coincidan exactamente con tu búsqueda. ¿Podrías ajustar algunos criterios o te ayudo a explorar otras opciones?"
        elif intent.type == IntentType.GREETING:
            return "¡Hola! Soy tu asistente inmobiliario. ¿En qué puedo ayudarte hoy? Puedo ayudarte a encontrar propiedades, comparar proyectos o responder cualquier pregunta sobre bienes raíces."
        elif intent.type == IntentType.GOODBYE:
            return "¡Ha sido un placer ayudarte! Si necesitas más información en el futuro, no dudes en volver. ¡Que tengas un excelente día!"
        else:
            return "Entiendo tu consulta. ¿En qué más puedo ayudarte con respecto a proyectos inmobiliarios?"
    
    async def generate_suggestions(self, intent: IntentAnalysis, projects: List[Dict[str, Any]], 
                                  user_context: Dict[str, Any]) -> List[str]:
        """Genera sugerencias contextuales para el usuario"""
        suggestions = []
        
        if intent.type == IntentType.SEARCH_PROJECTS:
            if projects:
                suggestions.extend([
                    "Ver más detalles del proyecto",
                    "Comparar proyectos encontrados",
                    "Filtrar por precio específico",
                    "Buscar en otras zonas"
                ])
            else:
                suggestions.extend([
                    "Ajustar criterios de búsqueda",
                    "Explorar otras zonas",
                    "Ver proyectos destacados",
                    "Contactar un asesor"
                ])
        elif intent.type == IntentType.GREETING:
            suggestions.extend([
                "Buscar apartamentos",
                "Ver proyectos en Chapinero",
                "Proyectos con piscina",
                "Precios desde $300M"
            ])
        elif intent.type == IntentType.HELP:
            suggestions.extend([
                "Cómo buscar proyectos",
                "Filtros disponibles",
                "Información de contacto",
                "Proyectos destacados"
            ])
        
        return suggestions[:4]  # Máximo 4 sugerencias
    
    async def detect_lead_opportunity(self, user_message: str, projects: List[Dict[str, Any]], 
                                    conversation_history: List[Dict[str, Any]]) -> bool:
        """Detecta si hay una oportunidad de lead"""
        # Palabras clave que indican interés
        interest_keywords = [
            "me interesa", "quiero", "déjame", "contacto", "información",
            "detalles", "visitar", "ver", "conocer", "agendar", "cita"
        ]
        
        # Verificar si el mensaje contiene palabras de interés
        message_lower = user_message.lower()
        has_interest_keywords = any(keyword in message_lower for keyword in interest_keywords)
        
        # Verificar si hay proyectos en los resultados
        has_projects = len(projects) > 0
        
        # Verificar si la conversación es avanzada (más de 3 mensajes)
        is_advanced_conversation = len(conversation_history) > 3
        
        # Oportunidad de lead si hay interés Y proyectos O conversación avanzada
        return (has_interest_keywords and has_projects) or is_advanced_conversation 