import openai
import json
from typing import Dict, List, Optional, Any
from loguru import logger
from datetime import datetime
import asyncio

class LLMIntegrationSystem:
    """
    Sistema de integración de LLMs para automatización inteligente
    """
    
    def __init__(self):
        self.openai_client = openai.OpenAI()
        self.models = {
            'gpt-4': 'gpt-4',
            'gpt-3.5-turbo': 'gpt-3.5-turbo',
            'claude-3': 'claude-3-sonnet-20240229'
        }
        
    async def analyze_market_data(self, raw_data: Dict, country: str, city: str) -> Dict:
        """
        Analiza datos de mercado usando LLM
        """
        try:
            # Preparar prompt para análisis
            prompt = self._build_market_analysis_prompt(raw_data, country, city)
            
            # Llamar a LLM
            response = await self._call_llm(prompt, model='gpt-4')
            
            # Parsear respuesta
            analysis = self._parse_market_analysis(response)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando datos con LLM: {e}")
            return self._get_fallback_analysis()
    
    async def extract_data_from_text(self, html_content: str, data_type: str) -> Dict:
        """
        Extrae datos estructurados de texto usando LLM
        """
        try:
            # Preparar prompt para extracción
            prompt = self._build_extraction_prompt(html_content, data_type)
            
            # Llamar a LLM
            response = await self._call_llm(prompt, model='gpt-3.5-turbo')
            
            # Parsear datos extraídos
            extracted_data = self._parse_extracted_data(response)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extrayendo datos con LLM: {e}")
            return {}
    
    async def detect_market_patterns(self, historical_data: List[Dict]) -> Dict:
        """
        Detecta patrones de mercado usando LLM
        """
        try:
            # Preparar prompt para detección de patrones
            prompt = self._build_pattern_detection_prompt(historical_data)
            
            # Llamar a LLM
            response = await self._call_llm(prompt, model='gpt-4')
            
            # Parsear patrones detectados
            patterns = self._parse_detected_patterns(response)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detectando patrones con LLM: {e}")
            return {}
    
    async def predict_market_changes(self, current_data: Dict, market_context: Dict) -> Dict:
        """
        Predice cambios de mercado usando LLM
        """
        try:
            # Preparar prompt para predicción
            prompt = self._build_prediction_prompt(current_data, market_context)
            
            # Llamar a LLM
            response = await self._call_llm(prompt, model='gpt-4')
            
            # Parsear predicciones
            predictions = self._parse_predictions(response)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error prediciendo cambios con LLM: {e}")
            return {}
    
    async def generate_investment_recommendations(self, market_data: Dict, user_profile: Dict) -> Dict:
        """
        Genera recomendaciones de inversión usando LLM
        """
        try:
            # Preparar prompt para recomendaciones
            prompt = self._build_recommendation_prompt(market_data, user_profile)
            
            # Llamar a LLM
            response = await self._call_llm(prompt, model='gpt-4')
            
            # Parsear recomendaciones
            recommendations = self._parse_recommendations(response)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones con LLM: {e}")
            return self._get_fallback_recommendations()
    
    async def adapt_to_new_market(self, country: str, city: str, available_data: Dict) -> Dict:
        """
        Adapta el sistema a un nuevo mercado usando LLM
        """
        try:
            # Preparar prompt para adaptación
            prompt = self._build_adaptation_prompt(country, city, available_data)
            
            # Llamar a LLM
            response = await self._call_llm(prompt, model='gpt-4')
            
            # Parsear adaptaciones
            adaptations = self._parse_adaptations(response)
            
            return adaptations
            
        except Exception as e:
            logger.error(f"Error adaptando a nuevo mercado con LLM: {e}")
            return self._get_default_adaptations()
    
    def _build_market_analysis_prompt(self, raw_data: Dict, country: str, city: str) -> str:
        """
        Construye prompt para análisis de mercado
        """
        return f"""
        Eres un experto analista inmobiliario. Analiza los siguientes datos del mercado de {city}, {country}:

        DATOS DEL MERCADO:
        {json.dumps(raw_data, indent=2)}

        TAREA:
        1. Analiza la salud del mercado inmobiliario
        2. Identifica tendencias clave
        3. Calcula métricas de rentabilidad
        4. Evalúa riesgos y oportunidades
        5. Proporciona insights accionables

        RESPONDE EN FORMATO JSON:
        {{
            "market_health": "excellent|good|fair|poor",
            "key_trends": ["tendencia1", "tendencia2"],
            "profitability_metrics": {{
                "rental_yield": 0.085,
                "price_appreciation": 0.08,
                "total_return": 0.165
            }},
            "risk_assessment": {{
                "market_risk": "low|medium|high",
                "liquidity_risk": "low|medium|high",
                "regulatory_risk": "low|medium|high"
            }},
            "opportunities": ["oportunidad1", "oportunidad2"],
            "recommendations": ["recomendación1", "recomendación2"]
        }}
        """
    
    def _build_extraction_prompt(self, html_content: str, data_type: str) -> str:
        """
        Construye prompt para extracción de datos
        """
        return f"""
        Eres un experto en extracción de datos inmobiliarios. Extrae información de {data_type} del siguiente HTML:

        HTML:
        {html_content[:2000]}...

        TAREA:
        Extrae todos los datos relevantes de {data_type} en formato JSON.

        PARA PRECIOS DE VENTA:
        - Busca precios en diferentes monedas
        - Identifica rangos de precios
        - Extrae precios por m²

        PARA RENTAS:
        - Busca precios de alquiler
        - Identifica rentas mensuales/anuales
        - Extrae rentas por m²

        PARA AMENITIES:
        - Lista todas las amenidades mencionadas
        - Categoriza por tipo

        RESPONDE EN FORMATO JSON:
        {{
            "prices": [{{"value": 450000000, "currency": "COP", "type": "sale"}}],
            "rents": [{{"value": 3200000, "currency": "COP", "type": "monthly"}}],
            "amenities": ["piscina", "gimnasio", "seguridad"],
            "location": "{{city}}",
            "confidence": 0.85
        }}
        """
    
    def _build_pattern_detection_prompt(self, historical_data: List[Dict]) -> str:
        """
        Construye prompt para detección de patrones
        """
        return f"""
        Eres un experto en análisis de patrones inmobiliarios. Analiza los siguientes datos históricos:

        DATOS HISTÓRICOS:
        {json.dumps(historical_data, indent=2)}

        TAREA:
        1. Identifica patrones de precios
        2. Detecta ciclos de mercado
        3. Analiza correlaciones
        4. Predice tendencias futuras
        5. Identifica anomalías

        RESPONDE EN FORMATO JSON:
        {{
            "price_patterns": {{
                "trend": "increasing|decreasing|stable",
                "seasonality": "yes|no",
                "volatility": "low|medium|high"
            }},
            "market_cycles": {{
                "current_phase": "expansion|peak|contraction|trough",
                "cycle_duration": "months",
                "next_phase_prediction": "date"
            }},
            "correlations": {{
                "gdp_correlation": 0.75,
                "interest_rate_correlation": -0.60,
                "inflation_correlation": 0.45
            }},
            "anomalies": ["anomalía1", "anomalía2"],
            "predictions": {{
                "short_term": "predicción 3 meses",
                "medium_term": "predicción 1 año",
                "long_term": "predicción 5 años"
            }}
        }}
        """
    
    def _build_prediction_prompt(self, current_data: Dict, market_context: Dict) -> str:
        """
        Construye prompt para predicciones
        """
        return f"""
        Eres un experto en predicción de mercados inmobiliarios. Predice cambios basado en:

        DATOS ACTUALES:
        {json.dumps(current_data, indent=2)}

        CONTEXTO DEL MERCADO:
        {json.dumps(market_context, indent=2)}

        TAREA:
        1. Predice cambios en precios
        2. Predice cambios en rentas
        3. Predice cambios en demanda
        4. Identifica factores de riesgo
        5. Sugiere timing de inversión

        RESPONDE EN FORMATO JSON:
        {{
            "price_predictions": {{
                "3_months": {{"change": 0.05, "confidence": 0.8}},
                "6_months": {{"change": 0.08, "confidence": 0.7}},
                "12_months": {{"change": 0.12, "confidence": 0.6}}
            }},
            "rental_predictions": {{
                "3_months": {{"change": 0.03, "confidence": 0.8}},
                "6_months": {{"change": 0.05, "confidence": 0.7}},
                "12_months": {{"change": 0.08, "confidence": 0.6}}
            }},
            "demand_predictions": {{
                "trend": "increasing|decreasing|stable",
                "drivers": ["factor1", "factor2"],
                "confidence": 0.75
            }},
            "risk_factors": ["riesgo1", "riesgo2"],
            "investment_timing": "buy_now|wait|sell"
        }}
        """
    
    def _build_recommendation_prompt(self, market_data: Dict, user_profile: Dict) -> str:
        """
        Construye prompt para recomendaciones
        """
        return f"""
        Eres un asesor inmobiliario experto. Genera recomendaciones personalizadas basado en:

        DATOS DEL MERCADO:
        {json.dumps(market_data, indent=2)}

        PERFIL DEL USUARIO:
        {json.dumps(user_profile, indent=2)}

        TAREA:
        1. Analiza el perfil de riesgo del usuario
        2. Identifica oportunidades específicas
        3. Genera recomendaciones personalizadas
        4. Calcula ROI esperado
        5. Sugiere estrategias de inversión

        RESPONDE EN FORMATO JSON:
        {{
            "risk_profile": "conservative|moderate|aggressive",
            "recommended_properties": [
                {{
                    "type": "apartment|house|commercial",
                    "location": "zona específica",
                    "price_range": "rango de precios",
                    "expected_roi": 0.085,
                    "risk_level": "low|medium|high"
                }}
            ],
            "investment_strategy": {{
                "approach": "buy_and_hold|flip|rental",
                "timeline": "short|medium|long",
                "diversification": "recommendations"
            }},
            "roi_projections": {{
                "1_year": 0.085,
                "3_years": 0.25,
                "5_years": 0.45
            }},
            "risk_mitigation": ["estrategia1", "estrategia2"],
            "next_steps": ["paso1", "paso2", "paso3"]
        }}
        """
    
    def _build_adaptation_prompt(self, country: str, city: str, available_data: Dict) -> str:
        """
        Construye prompt para adaptación a nuevo mercado
        """
        return f"""
        Eres un experto en adaptación de sistemas inmobiliarios. Adapta el sistema para {city}, {country}:

        DATOS DISPONIBLES:
        {json.dumps(available_data, indent=2)}

        TAREA:
        1. Identifica fuentes de datos específicas del país
        2. Adapta métricas a la cultura local
        3. Ajusta algoritmos a regulaciones locales
        4. Optimiza para patrones de mercado locales
        5. Sugiere configuraciones específicas

        RESPONDE EN FORMATO JSON:
        {{
            "data_sources": {{
                "portals": ["portal1", "portal2"],
                "official": ["fuente1", "fuente2"],
                "regulatory": ["autoridad1", "autoridad2"]
            }},
            "local_adaptations": {{
                "currency": "moneda local",
                "tax_structure": "estructura fiscal",
                "legal_requirements": ["requisito1", "requisito2"]
            }},
            "market_specifics": {{
                "typical_yields": 0.075,
                "price_volatility": "low|medium|high",
                "rental_demand": "high|medium|low"
            }},
            "algorithm_adjustments": {{
                "weight_factors": {{"location": 0.3, "price": 0.4, "amenities": 0.3}},
                "thresholds": {{"min_yield": 0.05, "max_risk": 0.7}},
                "filters": ["filtro1", "filtro2"]
            }},
            "recommended_config": {{
                "update_frequency": "daily|weekly|monthly",
                "confidence_thresholds": {{"low": 0.6, "medium": 0.8, "high": 0.9}},
                "fallback_strategies": ["estrategia1", "estrategia2"]
            }}
        }}
        """
    
    async def _call_llm(self, prompt: str, model: str = 'gpt-4') -> str:
        """
        Llama al LLM de forma asíncrona
        """
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=model,
                messages=[
                    {"role": "system", "content": "Eres un experto analista inmobiliario con acceso a datos de mercado globales."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error llamando LLM: {e}")
            return "{}"
    
    def _parse_market_analysis(self, response: str) -> Dict:
        """
        Parsea respuesta de análisis de mercado
        """
        try:
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error parseando análisis: {e}")
            return self._get_fallback_analysis()
    
    def _parse_extracted_data(self, response: str) -> Dict:
        """
        Parsea datos extraídos
        """
        try:
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error parseando datos extraídos: {e}")
            return {}
    
    def _parse_detected_patterns(self, response: str) -> Dict:
        """
        Parsea patrones detectados
        """
        try:
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error parseando patrones: {e}")
            return {}
    
    def _parse_predictions(self, response: str) -> Dict:
        """
        Parsea predicciones
        """
        try:
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error parseando predicciones: {e}")
            return {}
    
    def _parse_recommendations(self, response: str) -> Dict:
        """
        Parsea recomendaciones
        """
        try:
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error parseando recomendaciones: {e}")
            return self._get_fallback_recommendations()
    
    def _parse_adaptations(self, response: str) -> Dict:
        """
        Parsea adaptaciones
        """
        try:
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error parseando adaptaciones: {e}")
            return self._get_default_adaptations()
    
    def _get_fallback_analysis(self) -> Dict:
        """
        Análisis de respaldo
        """
        return {
            "market_health": "good",
            "key_trends": ["estable", "crecimiento moderado"],
            "profitability_metrics": {
                "rental_yield": 0.075,
                "price_appreciation": 0.06,
                "total_return": 0.135
            },
            "risk_assessment": {
                "market_risk": "medium",
                "liquidity_risk": "low",
                "regulatory_risk": "low"
            },
            "opportunities": ["inversión a largo plazo"],
            "recommendations": ["diversificar portafolio"]
        }
    
    def _get_fallback_recommendations(self) -> Dict:
        """
        Recomendaciones de respaldo
        """
        return {
            "risk_profile": "moderate",
            "recommended_properties": [
                {
                    "type": "apartment",
                    "location": "zona consolidada",
                    "price_range": "medio-alto",
                    "expected_roi": 0.075,
                    "risk_level": "medium"
                }
            ],
            "investment_strategy": {
                "approach": "buy_and_hold",
                "timeline": "medium",
                "diversification": "recomendada"
            },
            "roi_projections": {
                "1_year": 0.075,
                "3_years": 0.22,
                "5_years": 0.40
            },
            "risk_mitigation": ["diversificación", "análisis detallado"],
            "next_steps": ["investigar más", "consultar asesor"]
        }
    
    def _get_default_adaptations(self) -> Dict:
        """
        Adaptaciones por defecto
        """
        return {
            "data_sources": {
                "portals": ["default-portal.com"],
                "official": ["official-data.gov"],
                "regulatory": ["tax-authority.gov"]
            },
            "local_adaptations": {
                "currency": "USD",
                "tax_structure": "standard",
                "legal_requirements": ["basic_requirements"]
            },
            "market_specifics": {
                "typical_yields": 0.075,
                "price_volatility": "medium",
                "rental_demand": "medium"
            },
            "algorithm_adjustments": {
                "weight_factors": {"location": 0.3, "price": 0.4, "amenities": 0.3},
                "thresholds": {"min_yield": 0.05, "max_risk": 0.7},
                "filters": ["basic_filters"]
            },
            "recommended_config": {
                "update_frequency": "weekly",
                "confidence_thresholds": {"low": 0.6, "medium": 0.8, "high": 0.9},
                "fallback_strategies": ["global_averages", "similar_markets"]
            }
        }

# Ejemplo de uso
if __name__ == "__main__":
    llm_system = LLMIntegrationSystem()
    
    print("=== INTEGRACIÓN DE LLMs ===")
    print("Funciones principales:")
    print("1. Análisis de datos de mercado")
    print("2. Extracción de datos de texto")
    print("3. Detección de patrones")
    print("4. Predicciones de mercado")
    print("5. Recomendaciones personalizadas")
    print("6. Adaptación a nuevos mercados")
    print("\nSistema inteligente y automatizado") 