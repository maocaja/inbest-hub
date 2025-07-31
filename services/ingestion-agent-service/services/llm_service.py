"""
Servicio de LLM para comunicación con OpenAI
"""

import logging
import json
import random
from typing import Dict, Any, List, Optional
import openai
from config import Config

logger = logging.getLogger(__name__)

class MockLLMService:
    """
    Servicio LLM simulado para pruebas sin OpenAI
    """
    
    def __init__(self):
        self.responses = {
            "greeting": [
                "¡Hola! Soy tu asistente para proyectos inmobiliarios. ¿En qué puedo ayudarte hoy?",
                "Hola, estoy aquí para ayudarte a completar la información de tu proyecto. ¿Qué necesitas?",
                "¡Bienvenido! Soy tu asistente inmobiliario. ¿Cómo puedo ayudarte?"
            ],
            "project_info": [
                "Perfecto, he anotado la información del proyecto. ¿Podrías darme más detalles sobre la ubicación?",
                "Excelente, he registrado los datos. ¿Sabes cuál es el precio por unidad?",
                "Muy bien, he guardado esa información. ¿Cuáles son las amenidades del proyecto?"
            ],
            "missing_fields": [
                "Veo que faltan algunos campos importantes. Necesitamos completar: precio, ubicación exacta, y amenidades.",
                "Para completar el proyecto necesitamos: información de contacto, detalles financieros, y fecha de entrega.",
                "Faltan algunos datos clave: NIT de la constructora, área de las unidades, y opciones de financiación."
            ],
            "completion": [
                "¡Excelente! El proyecto está casi completo. Solo faltan algunos detalles menores.",
                "Muy bien, hemos completado la mayoría de la información. ¿Quieres que genere una descripción profesional?",
                "Perfecto, el proyecto está completo. ¿Te gustaría que lo guarde en el sistema?"
            ]
        }
    
    def generate_response(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generar respuesta simulada del LLM
        """
        try:
            # Simular procesamiento
            last_message = messages[-1]["content"].lower() if messages else ""
            
            # Determinar tipo de respuesta basado en el mensaje
            if "hola" in last_message or "ayuda" in last_message:
                response_type = "greeting"
            elif "proyecto" in last_message and ("tiene" in last_message or "es" in last_message):
                response_type = "project_info"
            elif "falta" in last_message or "completar" in last_message:
                response_type = "missing_fields"
            elif "completo" in last_message or "terminado" in last_message:
                response_type = "completion"
            else:
                response_type = "project_info"
            
            # Seleccionar respuesta aleatoria
            response = random.choice(self.responses[response_type])
            
            # Simular tool calls ocasionalmente
            tool_calls = None
            if "nit" in last_message and "900123456-7" in last_message:
                tool_calls = [{
                    "id": f"call_{random.randint(1000, 9999)}",
                    "function": {
                        "name": "get_project_owner_info",
                        "arguments": json.dumps({"nit": "900123456-7"})
                    },
                    "type": "function"
                }]
            
            return {
                "success": True,
                "response": response,
                "tool_calls": tool_calls,
                "usage": {
                    "prompt_tokens": len(str(messages)),
                    "completion_tokens": len(response),
                    "total_tokens": len(str(messages)) + len(response)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en LLM simulado: {str(e)}"
            }
    
    def extract_project_info(self, document_text: str) -> Dict[str, Any]:
        """
        Extraer información del proyecto de manera simulada
        """
        # Simular extracción de datos
        extracted_data = {
            "name": "Proyecto Extraído",
            "location": "Ubicación Detectada",
            "price": "Precio Estimado",
            "units": "Número de Unidades"
        }
        
        return {
            "success": True,
            "extracted_data": extracted_data
        }
    
    def validate_project_data(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar datos del proyecto de manera simulada
        """
        return {
            "success": True,
            "is_valid": True,
            "validation_errors": []
        }
    
    def generate_project_description(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generar descripción del proyecto de manera simulada
        """
        description = f"""
        Proyecto inmobiliario {project_data.get('name', '')} ubicado en {project_data.get('location', '')}.
        Este desarrollo ofrece {project_data.get('units', '')} con precios desde {project_data.get('price', '')}.
        Incluye amenidades como piscina, gimnasio y parqueadero. Entrega programada para 2025.
        """
        
        return {
            "success": True,
            "description": description.strip()
        }

class LLMService:
    """
    Servicio para comunicación con OpenAI GPT
    """
    
    def __init__(self):
        # Verificar si usar LLM simulado
        if Config.USE_MOCK_LLM:
            self.mock_service = MockLLMService()
            self.use_mock = True
            logger.info("Usando LLM simulado (modo de prueba)")
        else:
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            self.use_mock = False
            logger.info("Usando OpenAI GPT real")
        
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.OPENAI_MAX_TOKENS
        self.temperature = Config.OPENAI_TEMPERATURE
        
        # Prompt base del agente
        self.base_prompt = """
Eres un asistente experto en proyectos inmobiliarios. Tu trabajo es asistir a un asesor humano para completar toda la información de un proyecto nuevo de vivienda basado en documentos o conversación.

Tu comportamiento debe ser:
- Amable, profesional y centrado en la tarea
- Capaz de interpretar respuestas ambiguas del usuario
- Capaz de ignorar o redirigir temas irrelevantes de forma educada
- Siempre enfocado en completar todos los campos requeridos del proyecto

Tienes acceso a herramientas como:
- get_project_by_id(project_id)
- update_project_fields(project_id, fields)
- list_missing_fields(project_id)
- generate_project_description(project_id)

Nunca inventes información. Siempre valida el estado actual del proyecto con list_missing_fields.
Cuando todos los campos estén completos, informa al usuario y sugiere generar la descripción final automáticamente.

Responde en español de manera natural y conversacional.
"""
    
    def generate_response(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generar respuesta del LLM
        """
        # Si está en modo simulado, usar el servicio mock
        if self.use_mock:
            return self.mock_service.generate_response(messages, tools)
        
        try:
            # Preparar mensajes con el prompt base
            system_message = {"role": "system", "content": self.base_prompt}
            all_messages = [system_message] + messages
            
            # Configurar parámetros
            params = {
                "model": self.model,
                "messages": all_messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # Agregar herramientas si están disponibles
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"
            
            # Llamar a OpenAI
            response = self.client.chat.completions.create(**params)
            
            # Procesar respuesta
            assistant_message = response.choices[0].message
            
            result = {
                "success": True,
                "response": assistant_message.content,
                "tool_calls": assistant_message.tool_calls if hasattr(assistant_message, 'tool_calls') else None,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            logger.info(f"Respuesta LLM generada exitosamente (tokens: {result['usage']['total_tokens']})")
            return result
            
        except Exception as e:
            logger.error(f"Error generando respuesta LLM: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Lo siento, tuve un problema procesando tu solicitud. ¿Podrías intentar de nuevo?"
            }
    
    def extract_project_info(self, document_text: str) -> Dict[str, Any]:
        """
        Extraer información del proyecto del texto del documento
        """
        try:
            prompt = f"""
Analiza el siguiente texto de un documento inmobiliario y extrae la información del proyecto en formato JSON.

Texto del documento:
{document_text}

Extrae la siguiente información si está disponible:
- name: Nombre del proyecto
- description: Descripción del proyecto
- location: Ubicación (dirección, ciudad, barrio)
- price_info: Información de precios (rango, moneda)
- unit_info: Información de unidades (tipos, cantidades)
- amenities: Amenidades disponibles
- delivery_date: Fecha de entrega
- contact_info: Información de contacto

Responde solo con el JSON válido, sin texto adicional.
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.generate_response(messages)
            
            if response["success"]:
                try:
                    # Intentar parsear JSON de la respuesta
                    import re
                    json_match = re.search(r'\{.*\}', response["response"], re.DOTALL)
                    if json_match:
                        extracted_data = json.loads(json_match.group())
                        return {
                            "success": True,
                            "extracted_data": extracted_data
                        }
                    else:
                        return {
                            "success": False,
                            "error": "No se pudo extraer JSON de la respuesta",
                            "raw_response": response["response"]
                        }
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": f"Error parseando JSON: {e}",
                        "raw_response": response["response"]
                    }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Error extrayendo información del proyecto: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_project_data(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar datos del proyecto usando LLM
        """
        try:
            prompt = f"""
Valida los siguientes datos de un proyecto inmobiliario y proporciona feedback:

Datos del proyecto:
{json.dumps(project_data, indent=2, ensure_ascii=False)}

Verifica:
1. ¿Los datos son coherentes y realistas?
2. ¿Faltan campos importantes?
3. ¿Hay inconsistencias en precios, ubicación, etc.?
4. ¿La información de contacto es válida?

Responde en formato JSON con:
- is_valid: boolean
- errors: lista de errores
- warnings: lista de advertencias
- missing_fields: lista de campos faltantes
- suggestions: sugerencias de mejora
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.generate_response(messages)
            
            if response["success"]:
                try:
                    # Intentar parsear JSON de la respuesta
                    import re
                    json_match = re.search(r'\{.*\}', response["response"], re.DOTALL)
                    if json_match:
                        validation_result = json.loads(json_match.group())
                        return {
                            "success": True,
                            "validation": validation_result
                        }
                    else:
                        return {
                            "success": False,
                            "error": "No se pudo extraer JSON de la respuesta",
                            "raw_response": response["response"]
                        }
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": f"Error parseando JSON: {e}",
                        "raw_response": response["response"]
                    }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Error validando datos del proyecto: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_project_description(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generar descripción del proyecto usando LLM
        """
        try:
            prompt = f"""
Genera una descripción profesional y atractiva para el siguiente proyecto inmobiliario:

Datos del proyecto:
{json.dumps(project_data, indent=2, ensure_ascii=False)}

La descripción debe:
- Ser profesional y comercial
- Destacar las características principales
- Incluir información de ubicación y precios
- Ser atractiva para potenciales compradores
- Tener entre 100-200 palabras

Responde solo con la descripción, sin formato adicional.
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.generate_response(messages)
            
            if response["success"]:
                return {
                    "success": True,
                    "description": response["response"].strip()
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Error generando descripción del proyecto: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_conversation_suggestions(self, conversation_history: List[Dict], current_project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generar sugerencias para la conversación basadas en el historial y datos actuales
        """
        try:
            # Analizar campos faltantes
            required_fields = [
                "name", "description", "project_owner_nit", "location", 
                "price_info", "unit_info", "amenities", "financial_info"
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in current_project_data or not current_project_data[field]:
                    missing_fields.append(field)
            
            prompt = f"""
Basándote en el historial de conversación y los datos actuales del proyecto, sugiere las próximas preguntas para completar la información faltante.

Historial de conversación (últimos 5 mensajes):
{json.dumps(conversation_history[-5:], indent=2, ensure_ascii=False)}

Datos actuales del proyecto:
{json.dumps(current_project_data, indent=2, ensure_ascii=False)}

Campos faltantes: {missing_fields}

Sugiere 2-3 preguntas específicas para completar la información faltante.
Responde en formato JSON con:
- next_questions: lista de preguntas sugeridas
- priority_field: campo más importante a completar
- estimated_completion: porcentaje estimado de completitud
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.generate_response(messages)
            
            if response["success"]:
                try:
                    import re
                    json_match = re.search(r'\{.*\}', response["response"], re.DOTALL)
                    if json_match:
                        suggestions = json.loads(json_match.group())
                        return {
                            "success": True,
                            "suggestions": suggestions
                        }
                    else:
                        return {
                            "success": False,
                            "error": "No se pudo extraer JSON de la respuesta"
                        }
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": f"Error parseando JSON: {e}"
                    }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Error generando sugerencias: {e}")
            return {
                "success": False,
                "error": str(e)
            } 