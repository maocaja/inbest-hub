import openai
import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

from models.schemas import RealEstateProject, Location, PriceInfo, UnitInfo, Amenities, FinancialInfo, AudienceInfo, Media

logger = logging.getLogger(__name__)

class RealEstateDataExtractor:
    """
    Servicio para extraer información de proyectos inmobiliarios usando IA
    """
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """
        Retorna el prompt del sistema para la extracción de datos inmobiliarios
        """
        return """
        Eres un experto asesor inmobiliario especializado en extraer información detallada de proyectos inmobiliarios desde documentos.

        Tu tarea es analizar el contenido del documento y extraer toda la información relevante sobre el proyecto inmobiliario, organizándola en el siguiente esquema JSON:

        {
          "project_id": "string",                 // ID único del proyecto
          "name": "string",                       // Nombre del proyecto
          "description": "string",                // Descripción breve del proyecto
          "builder": "string",                    // Constructora o desarrollador
          "status": "preventa | construcción | entregado", // Estado actual
          "delivery_date": "YYYY-MM",            // Fecha estimada de entrega

          "location": {
            "country": "string",                 // País (ej. Colombia)
            "department": "string",              // Departamento o estado
            "city": "string",                    // Ciudad o municipio
            "zone": "string",                    // Zona dentro de la ciudad
            "neighborhood": "string",            // Barrio o sector
            "latitude": "float",
            "longitude": "float"
          },

          "price_info": {
            "currency": "COP | USD | ...",       // Moneda
            "price_min": "number",               // Precio más bajo de unidad
            "price_max": "number",               // Precio más alto
            "price_per_m2": "number",            // (opcional) Precio promedio por m²
            "maintenance_fee": "number"          // Cuota de administración mensual
          },

          "unit_info": {
            "unit_types": ["apartamento", "casa", "duplex"], // Tipos disponibles
            "area_m2_min": "number",
            "area_m2_max": "number",
            "bedrooms_min": "integer",
            "bedrooms_max": "integer",
            "bathrooms_min": "integer",
            "bathrooms_max": "integer",
            "parking_min": "integer",
            "parking_max": "integer",
            "balcony": true,
            "storage_room": true
          },

          "amenities": {
            "list": [
              "zona BBQ", 
              "piscina", 
              "coworking", 
              "juegos infantiles", 
              "gimnasio"
            ],
            "green_areas": true,
            "pet_friendly": true,
            "security_features": [
              "portería 24h", 
              "circuito cerrado", 
              "acceso biométrico"
            ]
          },

          "financial_info": {
            "offers_financing": true,            // ¿El proyecto tiene financiación?
            "down_payment_percent": "number",    // % cuota inicial
            "installment_months": "integer",     // Cuotas/plazo
            "expected_rent": "number",           // Renta esperada mensual
            "appreciation_rate": "float",        // % valorización anual esperada
            "investment_horizon_years": "integer"
          },

          "audience_info": {
            "target_audience": ["familias", "inversionistas", "estudiantes"],
            "usage_type": "vivienda | inversión | vacacional",
            "income_level": "bajo | medio | alto"
          },

          "media": {
            "images": ["url1", "url2", "url3"],
            "videos": ["video_url"],
            "brochure_url": "pdf_url",
            "virtual_tour_url": "tour_url"
          }
        }

        INSTRUCCIONES IMPORTANTES:
        1. Extrae SOLO la información que esté explícitamente mencionada en el documento
        2. Si no encuentras información para un campo, déjalo como null
        3. Para fechas, usa formato YYYY-MM
        4. Para precios, extrae solo números (sin símbolos de moneda)
        5. Para coordenadas, extrae solo números decimales
        6. Para listas, incluye solo elementos mencionados explícitamente
        7. Para booleanos, usa true/false basado en la información disponible
        8. Sé preciso y no inventes información

        Responde ÚNICAMENTE con el JSON válido, sin explicaciones adicionales.
        """
    
    async def extract_project_data(self, content: str) -> RealEstateProject:
        """
        Extrae información del proyecto inmobiliario desde el contenido del documento
        """
        try:
            # Preparar el prompt para el usuario
            user_prompt = f"""
            Analiza el siguiente contenido de un documento inmobiliario y extrae toda la información relevante sobre el proyecto:

            {content}

            Extrae la información en el formato JSON especificado, incluyendo solo datos que estén explícitamente mencionados en el documento.
            """
            
            # Llamar a OpenAI
            response = await self._call_openai(user_prompt)
            
            # Parsear la respuesta JSON
            project_data = self._parse_json_response(response)
            
            # Convertir a Pydantic model
            real_estate_project = RealEstateProject(**project_data)
            
            logger.info("Datos del proyecto extraídos exitosamente")
            return real_estate_project
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del proyecto: {str(e)}")
            raise
    
    async def complete_missing_data(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Completa información faltante en el proyecto usando IA
        """
        try:
            # Convertir el proyecto actual a JSON string
            current_data = json.dumps(project_data, ensure_ascii=False, indent=2)
            
            user_prompt = f"""
            Analiza el siguiente proyecto inmobiliario y completa la información faltante basándote en el contexto y patrones del mercado:

            {current_data}

            Completa los campos que estén como null o vacíos con información razonable basada en:
            1. El contexto del proyecto
            2. Patrones del mercado inmobiliario
            3. Información típica para proyectos similares
            4. Datos demográficos y de ubicación

            Mantén la información existente sin cambios y solo completa los campos faltantes.
            Responde ÚNICAMENTE con el JSON actualizado.
            """
            
            response = await self._call_openai(user_prompt)
            completed_data = self._parse_json_response(response)
            
            logger.info("Información faltante completada exitosamente")
            return completed_data
            
        except Exception as e:
            logger.error(f"Error completando información faltante: {str(e)}")
            raise
    
    async def _call_openai(self, user_prompt: str) -> str:
        """
        Realiza la llamada a OpenAI
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error en llamada a OpenAI: {str(e)}")
            raise
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parsea la respuesta JSON de OpenAI
        """
        try:
            # Limpiar la respuesta de posibles caracteres extra
            cleaned_response = response.strip()
            
            # Buscar el JSON en la respuesta
            json_start = cleaned_response.find('{')
            json_end = cleaned_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No se encontró JSON válido en la respuesta")
            
            json_str = cleaned_response[json_start:json_end]
            
            # Parsear el JSON
            data = json.loads(json_str)
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON: {str(e)}")
            logger.error(f"Respuesta recibida: {response}")
            raise
        except Exception as e:
            logger.error(f"Error procesando respuesta: {str(e)}")
            raise
    
    def extract_keywords(self, content: str) -> List[str]:
        """
        Extrae palabras clave relevantes del contenido
        """
        try:
            # Palabras clave comunes en proyectos inmobiliarios
            keywords = [
                "apartamento", "casa", "duplex", "penthouse", "studio",
                "preventa", "construcción", "entregado", "nuevo",
                "precio", "valor", "m2", "metros cuadrados",
                "habitaciones", "baños", "parqueadero", "balcón",
                "amenidades", "piscina", "gimnasio", "zona BBQ",
                "financiación", "cuota inicial", "crédito",
                "ubicación", "zona", "barrio", "ciudad",
                "constructora", "desarrollador", "inmobiliaria"
            ]
            
            found_keywords = []
            content_lower = content.lower()
            
            for keyword in keywords:
                if keyword in content_lower:
                    found_keywords.append(keyword)
            
            return found_keywords
            
        except Exception as e:
            logger.error(f"Error extrayendo palabras clave: {str(e)}")
            return [] 