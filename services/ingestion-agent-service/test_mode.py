#!/usr/bin/env python3
"""
Modo de prueba para simular respuestas del LLM sin usar OpenAI
"""

import json
import random
from typing import List, Dict, Any

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
    
    def generate_response(self, messages: List[Dict[str, str]], tools: List[Dict] = None) -> Dict[str, Any]:
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

def test_mock_llm():
    """
    Probar el servicio LLM simulado
    """
    print("🧪 Probando LLM simulado...")
    
    mock_llm = MockLLMService()
    
    # Test 1: Respuesta de saludo
    messages = [{"role": "user", "content": "Hola, necesito ayuda"}]
    response = mock_llm.generate_response(messages)
    print(f"✅ Respuesta de saludo: {response['response'][:50]}...")
    
    # Test 2: Información del proyecto
    messages = [{"role": "user", "content": "El proyecto tiene 50 apartamentos"}]
    response = mock_llm.generate_response(messages)
    print(f"✅ Respuesta de proyecto: {response['response'][:50]}...")
    
    # Test 3: Tool calling
    messages = [{"role": "user", "content": "El NIT es 900123456-7"}]
    response = mock_llm.generate_response(messages)
    if response.get('tool_calls'):
        print(f"✅ Tool calling simulado: {response['tool_calls'][0]['function']['name']}")
    else:
        print("ℹ️  No se activó tool calling")
    
    print("✅ LLM simulado funcionando correctamente")

if __name__ == "__main__":
    test_mock_llm() 