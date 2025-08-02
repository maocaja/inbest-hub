import openai
import json
from typing import Dict, Any, Optional
from loguru import logger
from config import Config
from schemas.schemas import IntentAnalysis, IntentType

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.temperature = Config.OPENAI_TEMPERATURE
        self.max_tokens = Config.OPENAI_MAX_TOKENS
    
    async def analyze_intent(self, message: str) -> IntentAnalysis:
        """Analizar la intención del mensaje del usuario"""
        try:
            system_prompt = """
            Analiza la intención del mensaje del usuario. Clasifica en una de estas categorías:
            
            - search_projects: Buscar proyectos inmobiliarios
            - get_project_details: Obtener detalles de un proyecto específico
            - greeting: Saludo inicial
            - goodbye: Despedida
            - help: Solicitud de ayuda
            - unknown: No se puede determinar
            
            También extrae entidades como:
            - location: Ubicación (Bogotá, Chapinero, etc.)
            - price_range: Rango de precio
            - amenities: Amenities (piscina, gimnasio, etc.)
            - property_type: Tipo de propiedad
            
            Responde en formato JSON:
            {
                "type": "search_projects",
                "confidence": 0.95,
                "entities": {
                    "location": "Chapinero",
                    "price_range": {"min": 300000000, "max": 600000000},
                    "amenities": ["piscina", "gimnasio"]
                },
                "filters": {
                    "location": "Chapinero",
                    "price_min": 300000000,
                    "price_max": 600000000,
                    "amenities": ["piscina", "gimnasio"]
                }
            }
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,  # Baja temperatura para análisis preciso
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            intent_data = json.loads(content)
            
            return IntentAnalysis(
                type=IntentType(intent_data.get("type", "unknown")),
                confidence=float(intent_data.get("confidence", 0.0)),
                entities=intent_data.get("entities", {}),
                filters=intent_data.get("filters", {})
            )
            
        except Exception as e:
            logger.error(f"Error analizando intención: {e}")
            return IntentAnalysis(
                type=IntentType.UNKNOWN,
                confidence=0.0,
                entities={},
                filters={}
            )
    
    async def generate_response(self, context: str) -> str:
        """Generar respuesta natural basada en el contexto"""
        try:
            system_prompt = """
            Eres un asistente inmobiliario experto y amigable. Tu objetivo es ayudar a los usuarios a encontrar la propiedad perfecta.

            INSTRUCCIONES IMPORTANTES:
            - Responde de manera natural y conversacional, como un humano experto
            - NO uses frases típicas de bot como "¡Hola! Te ayudo a encontrar..."
            - Sé respetuoso, profesional pero cercano
            - Personaliza las respuestas según el contexto del usuario
            - Si no hay resultados, sugiere alternativas amablemente
            - Usa emojis ocasionalmente para ser más humano
            - Menciona detalles específicos de los proyectos
            - Haz preguntas de seguimiento naturales

            TONO:
            - Profesional pero amigable
            - Conocedor del mercado inmobiliario
            - Respetuoso del tiempo del usuario
            - Entusiasta pero no exagerado

            EJEMPLOS DE BUENAS RESPUESTAS:
            ✅ "Veo que buscas en Chapinero. El Residencial El Bosque podría ser perfecto para ti - tiene piscina, está en una zona excelente y el precio está en tu rango."
            ✅ "Encontré 3 opciones interesantes. El que más me llama la atención es la Torre Los Andes por su ubicación privilegiada."
            ✅ "No encontré exactamente lo que buscas en esa zona, pero tengo algunas alternativas en áreas cercanas que podrían interesarte."

            EJEMPLOS DE RESPUESTAS A EVITAR:
            ❌ "¡Hola! Te ayudo a encontrar tu propiedad ideal."
            ❌ "He encontrado las siguientes opciones para ti:"
            ❌ "Aquí tienes los resultados de tu búsqueda:"
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return "Lo siento, tuve un problema procesando tu solicitud. ¿Podrías intentar de nuevo?"
    
    async def generate_suggestions(self, intent: IntentAnalysis, projects: list, user_context: Dict) -> list:
        """Generar sugerencias basadas en el contexto"""
        try:
            if not projects:
                return [
                    "Explorar otras zonas",
                    "Ajustar el rango de precio",
                    "Ver todos los proyectos disponibles"
                ]
            
            suggestions = []
            
            if intent.type == IntentType.SEARCH_PROJECTS:
                if len(projects) > 0:
                    suggestions.append(f"Ver más detalles de {projects[0].get('name', 'este proyecto')}")
                suggestions.extend([
                    "Filtrar por amenities específicas",
                    "Comparar proyectos",
                    "Agendar visita"
                ])
            
            return suggestions[:5]  # Máximo 5 sugerencias
            
        except Exception as e:
            logger.error(f"Error generando sugerencias: {e}")
            return ["Ver todos los proyectos"] 