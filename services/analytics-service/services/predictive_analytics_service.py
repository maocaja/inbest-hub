import httpx
from typing import Dict, List, Optional, Any
from loguru import logger
from datetime import datetime, timedelta
import json

from models.price_prediction import PricePredictionModel
from models.roi_prediction import ROIPredictionModel

class PredictiveAnalyticsService:
    """
    Servicio de analytics predictivo que combina predicción de precios y ROI
    """
    
    def __init__(self):
        self.price_model = PricePredictionModel()
        self.roi_model = ROIPredictionModel()
        self.market_data_cache = {}
        self.cache_ttl = 3600  # 1 hora
    
    async def get_comprehensive_analysis(self, property_data: Dict) -> Dict:
        """
        Análisis completo: predicción de precios + ROI + recomendaciones
        """
        try:
            # 1. Predicción de precios
            price_analysis = await self._get_price_prediction(property_data)
            
            # 2. Análisis de ROI
            roi_analysis = await self._get_roi_analysis(property_data)
            
            # 3. Análisis de mercado
            market_analysis = await self._get_market_analysis(property_data)
            
            # 4. Recomendaciones de inversión
            investment_recommendations = await self._generate_investment_recommendations(
                price_analysis, roi_analysis, market_analysis
            )
            
            return {
                'property_info': property_data,
                'price_analysis': price_analysis,
                'roi_analysis': roi_analysis,
                'market_analysis': market_analysis,
                'investment_recommendations': investment_recommendations,
                'summary': self._generate_summary(price_analysis, roi_analysis, market_analysis),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en análisis comprehensivo: {e}")
            raise
    
    async def get_price_prediction(self, property_data: Dict, years_ahead: int = 5) -> Dict:
        """
        Predicción de precios con análisis detallado
        """
        try:
            # Enriquecer datos con información de mercado
            enriched_data = await self._enrich_property_data(property_data)
            
            # Predicción base
            prediction = self.price_model.predict_price(enriched_data, years_ahead)
            
            # Análisis de factores
            factor_analysis = await self._analyze_price_factors(enriched_data)
            
            # Comparación con mercado
            market_comparison = await self._compare_with_market(enriched_data)
            
            return {
                'prediction': prediction,
                'factor_analysis': factor_analysis,
                'market_comparison': market_comparison,
                'confidence_level': self._calculate_confidence_level(prediction, factor_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error en predicción de precios: {e}")
            raise
    
    async def get_roi_analysis(self, property_data: Dict, financing_data: Optional[Dict] = None) -> Dict:
        """
        Análisis completo de ROI
        """
        try:
            # ROI sin financiamiento
            roi_basic = self.roi_model.calculate_roi(property_data)
            
            # ROI con financiamiento (si se proporciona)
            roi_with_financing = None
            if financing_data:
                roi_with_financing = self.roi_model.calculate_roi_with_financing(
                    property_data, financing_data
                )
            
            # Análisis de escenarios
            scenarios = await self._analyze_roi_scenarios(property_data)
            
            # Comparación con otras inversiones
            investment_comparison = await self._compare_with_other_investments(property_data)
            
            return {
                'roi_basic': roi_basic,
                'roi_with_financing': roi_with_financing,
                'scenarios': scenarios,
                'investment_comparison': investment_comparison,
                'recommendation': self._generate_roi_recommendation(roi_basic, scenarios)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de ROI: {e}")
            raise
    
    async def get_market_analysis(self, location: str) -> Dict:
        """
        Análisis de mercado para una ubicación específica
        """
        try:
            # Obtener datos de mercado
            market_data = await self._fetch_market_data(location)
            
            # Análisis de tendencias
            trends = await self._analyze_market_trends(location)
            
            # Predicciones de mercado
            market_predictions = await self._predict_market_movement(location)
            
            # Análisis de competencia
            competition = await self._analyze_competition(location)
            
            return {
                'location': location,
                'market_data': market_data,
                'trends': trends,
                'predictions': market_predictions,
                'competition': competition,
                'risk_assessment': self._assess_market_risk(market_data, trends)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de mercado: {e}")
            raise
    
    async def compare_properties(self, properties: List[Dict]) -> Dict:
        """
        Compara múltiples propiedades
        """
        try:
            comparisons = []
            
            for property_data in properties:
                # Análisis individual
                analysis = await self.get_comprehensive_analysis(property_data)
                comparisons.append(analysis)
            
            # Ranking por diferentes criterios
            rankings = {
                'by_roi': sorted(comparisons, key=lambda x: x['roi_analysis']['roi_basic']['summary']['final_roi_percentage'], reverse=True),
                'by_price_potential': sorted(comparisons, key=lambda x: x['price_analysis']['prediction']['predictions']['year_5']['growth_rate'], reverse=True),
                'by_risk': sorted(comparisons, key=lambda x: x['roi_analysis']['roi_basic']['summary']['risk_metrics']['risk_level']),
                'by_market_position': sorted(comparisons, key=lambda x: x['market_analysis']['risk_assessment']['score'], reverse=True)
            }
            
            # Análisis de portafolio
            portfolio_analysis = await self._analyze_portfolio(comparisons)
            
            return {
                'comparisons': comparisons,
                'rankings': rankings,
                'portfolio_analysis': portfolio_analysis,
                'best_overall': self._select_best_overall(rankings)
            }
            
        except Exception as e:
            logger.error(f"Error comparando propiedades: {e}")
            raise
    
    async def _enrich_property_data(self, property_data: Dict) -> Dict:
        """
        Enriquece los datos de la propiedad con información de mercado
        """
        try:
            location = property_data.get('location', 'default')
            
            # Obtener datos de mercado
            market_data = await self._fetch_market_data(location)
            
            # Combinar datos
            enriched_data = property_data.copy()
            enriched_data.update({
                'gdp_growth': market_data.get('gdp_growth', 0.025),
                'inflation_rate': market_data.get('inflation_rate', 0.03),
                'interest_rate': market_data.get('interest_rate', 0.08),
                'metro_construction': market_data.get('metro_construction', 0.02),
                'new_commercial_centers': market_data.get('new_commercial_centers', 0.01),
                'population_growth': market_data.get('population_growth', 0.015),
                'income_growth': market_data.get('income_growth', 0.03),
                'employment_rate': market_data.get('employment_rate', 0.95),
                'crime_rate': market_data.get('crime_rate', 0.02),
                'school_quality': market_data.get('school_quality', 0.8)
            })
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Error enriqueciendo datos: {e}")
            return property_data
    
    async def _analyze_price_factors(self, property_data: Dict) -> Dict:
        """
        Analiza los factores que influyen en el precio
        """
        try:
            factors = {
                'location_impact': self._calculate_location_impact(property_data),
                'amenities_impact': self._calculate_amenities_impact(property_data),
                'market_conditions': self._calculate_market_conditions_impact(property_data),
                'development_impact': self._calculate_development_impact(property_data)
            }
            
            # Calcular impacto total
            total_impact = sum(factors.values())
            
            return {
                'factors': factors,
                'total_impact': total_impact,
                'primary_drivers': self._identify_primary_drivers(factors)
            }
            
        except Exception as e:
            logger.error(f"Error analizando factores: {e}")
            return {}
    
    async def _compare_with_market(self, property_data: Dict) -> Dict:
        """
        Compara la propiedad con el mercado
        """
        try:
            location = property_data.get('location', 'default')
            market_data = await self._fetch_market_data(location)
            
            current_price = property_data.get('purchase_price', 0)
            market_average = market_data.get('average_price', current_price)
            
            comparison = {
                'price_vs_market': (current_price - market_average) / market_average,
                'market_position': 'above' if current_price > market_average else 'below',
                'price_per_m2': current_price / property_data.get('area_m2', 1),
                'market_price_per_m2': market_data.get('price_per_m2', 0),
                'value_proposition': self._assess_value_proposition(property_data, market_data)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparando con mercado: {e}")
            return {}
    
    async def _analyze_roi_scenarios(self, property_data: Dict) -> Dict:
        """
        Analiza diferentes escenarios de ROI
        """
        try:
            scenarios = {}
            
            # Escenario optimista
            optimistic_data = property_data.copy()
            optimistic_data['appreciation_rate'] = property_data.get('appreciation_rate', 0.08) * 1.2
            scenarios['optimistic'] = self.roi_model.calculate_roi(optimistic_data)
            
            # Escenario pesimista
            pessimistic_data = property_data.copy()
            pessimistic_data['appreciation_rate'] = property_data.get('appreciation_rate', 0.08) * 0.8
            scenarios['pessimistic'] = self.roi_model.calculate_roi(pessimistic_data)
            
            # Escenario base
            scenarios['base'] = self.roi_model.calculate_roi(property_data)
            
            return scenarios
            
        except Exception as e:
            logger.error(f"Error analizando escenarios: {e}")
            return {}
    
    async def _fetch_market_data(self, location: str) -> Dict:
        """
        Obtiene datos de mercado (simulado)
        """
        try:
            # En producción, esto vendría de APIs externas o base de datos
            market_data = {
                'chapinero': {
                    'average_price': 450000000,
                    'price_per_m2': 5000000,
                    'gdp_growth': 0.025,
                    'inflation_rate': 0.03,
                    'interest_rate': 0.08,
                    'metro_construction': 0.02,
                    'new_commercial_centers': 0.01,
                    'population_growth': 0.015,
                    'income_growth': 0.03,
                    'employment_rate': 0.95,
                    'crime_rate': 0.02,
                    'school_quality': 0.8
                },
                'usaquen': {
                    'average_price': 380000000,
                    'price_per_m2': 4200000,
                    'gdp_growth': 0.025,
                    'inflation_rate': 0.03,
                    'interest_rate': 0.08,
                    'metro_construction': 0.01,
                    'new_commercial_centers': 0.005,
                    'population_growth': 0.012,
                    'income_growth': 0.025,
                    'employment_rate': 0.93,
                    'crime_rate': 0.015,
                    'school_quality': 0.85
                }
            }
            
            return market_data.get(location.lower(), market_data['chapinero'])
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de mercado: {e}")
            return {}
    
    def _calculate_confidence_level(self, prediction: Dict, factor_analysis: Dict) -> float:
        """
        Calcula el nivel de confianza de la predicción
        """
        try:
            # Factores que afectan la confianza
            model_accuracy = prediction.get('model_accuracy', 0.87)
            data_quality = 0.9  # Calidad de los datos
            market_stability = 0.85  # Estabilidad del mercado
            
            # Cálculo ponderado
            confidence = (model_accuracy * 0.5 + data_quality * 0.3 + market_stability * 0.2)
            
            return min(confidence, 0.95)  # Máximo 95%
            
        except Exception as e:
            logger.error(f"Error calculando confianza: {e}")
            return 0.8
    
    def _generate_investment_recommendations(self, price_analysis: Dict, roi_analysis: Dict, market_analysis: Dict) -> Dict:
        """
        Genera recomendaciones de inversión
        """
        try:
            roi_percentage = roi_analysis['roi_basic']['summary']['final_roi_percentage']
            price_growth = price_analysis['prediction']['predictions']['year_5']['growth_rate']
            risk_level = roi_analysis['roi_basic']['summary']['risk_metrics']['risk_level']
            
            recommendations = {
                'action': self._determine_action(roi_percentage, price_growth, risk_level),
                'timing': self._determine_timing(market_analysis),
                'strategy': self._determine_strategy(roi_analysis),
                'risk_mitigation': self._suggest_risk_mitigation(risk_level),
                'monitoring_points': self._suggest_monitoring_points(price_analysis, roi_analysis)
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {e}")
            return {}
    
    def _determine_action(self, roi: float, price_growth: float, risk_level: str) -> str:
        """
        Determina la acción recomendada
        """
        if roi > 50 and price_growth > 30 and risk_level in ['BAJO', 'MEDIO-BAJO']:
            return "COMPRAR AHORA"
        elif roi > 30 and price_growth > 20:
            return "COMPRAR CON CAUTELA"
        elif roi > 15 and price_growth > 10:
            return "MANTENER EN OBSERVACIÓN"
        else:
            return "NO RECOMENDADO"
    
    def _determine_timing(self, market_analysis: Dict) -> str:
        """
        Determina el timing óptimo
        """
        market_trend = market_analysis.get('trends', {}).get('direction', 'stable')
        
        if market_trend == 'bullish':
            return "COMPRAR PRONTO - Mercado en alza"
        elif market_trend == 'bearish':
            return "ESPERAR - Mercado en baja"
        else:
            return "TIMING NEUTRAL - Mercado estable"
    
    def _generate_summary(self, price_analysis: Dict, roi_analysis: Dict, market_analysis: Dict) -> Dict:
        """
        Genera un resumen ejecutivo
        """
        try:
            price_prediction = price_analysis['prediction']
            roi_summary = roi_analysis['roi_basic']['summary']
            
            return {
                'investment_score': self._calculate_investment_score(price_analysis, roi_analysis),
                'key_highlights': [
                    f"ROI esperado: {roi_summary['final_roi_percentage']}% en 5 años",
                    f"Crecimiento de precio: {price_prediction['predictions']['year_5']['growth_rate']}% en 5 años",
                    f"Nivel de riesgo: {roi_summary['risk_metrics']['risk_level']}",
                    f"Break-even: Año {roi_summary['break_even_year'] or 'N/A'}"
                ],
                'risk_reward_ratio': roi_summary['final_roi_percentage'] / (100 - roi_summary['risk_metrics']['sharpe_ratio'] * 100),
                'market_outlook': market_analysis.get('predictions', {}).get('outlook', 'neutral')
            }
            
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return {}

# Ejemplo de uso
if __name__ == "__main__":
    service = PredictiveAnalyticsService()
    
    # Datos de ejemplo
    property_data = {
        'purchase_price': 420000000,
        'location': 'chapinero',
        'area_m2': 85,
        'bedrooms': 2,
        'bathrooms': 2,
        'amenities': ['piscina', 'gimnasio', 'seguridad']
    }
    
    print("=== SERVICIO DE ANALYTICS PREDICTIVO ===")
    print("Modelo de predicción de precios y ROI")
    print("Listo para análisis comprehensivo de inversiones") 