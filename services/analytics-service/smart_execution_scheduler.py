import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from loguru import logger
import json
import redis
from dataclasses import dataclass

@dataclass
class ExecutionTrigger:
    """Triggers para ejecutar recolección de datos"""
    market_key: str
    trigger_type: str  # 'scheduled', 'demand', 'change_detected'
    priority: int  # 1-5 (5 = más alta)
    last_execution: datetime
    next_execution: datetime
    data_freshness: int  # horas que los datos siguen siendo válidos

class SmartExecutionScheduler:
    """
    Scheduler inteligente que determina cuándo ejecutar recolección de datos
    """
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.execution_triggers = {}
        self.data_cache = {}
        self.cache_ttl = {
            'rental_yields': 24,      # 24 horas
            'operating_expenses': 168, # 1 semana
            'market_trends': 72,       # 3 días
            'property_prices': 12,     # 12 horas
            'vacancy_rates': 48        # 2 días
        }
        
    async def get_market_data(self, country: str, city: str, data_type: str = None) -> Dict:
        """
        Obtiene datos de mercado de forma inteligente
        """
        try:
            market_key = f"{country.lower()}_{city.lower()}"
            
            # 1. Verificar si hay datos en cache
            cached_data = await self._get_cached_data(market_key, data_type)
            if cached_data and self._is_data_fresh(cached_data, data_type):
                logger.info(f"Datos en cache válidos para {market_key}")
                return cached_data
            
            # 2. Verificar si necesitamos ejecutar recolección
            should_execute = await self._should_execute_collection(market_key, data_type)
            
            if should_execute:
                # 3. Ejecutar recolección
                logger.info(f"Ejecutando recolección para {market_key}")
                new_data = await self._execute_data_collection(country, city, data_type)
                
                # 4. Guardar en cache
                await self._cache_data(market_key, new_data, data_type)
                
                return new_data
            else:
                # 5. Usar datos de respaldo si no hay cache
                logger.info(f"Usando datos de respaldo para {market_key}")
                return await self._get_fallback_data(country, city, data_type)
                
        except Exception as e:
            logger.error(f"Error obteniendo datos: {e}")
            return await self._get_fallback_data(country, city, data_type)
    
    async def _should_execute_collection(self, market_key: str, data_type: str = None) -> bool:
        """
        Determina si debe ejecutar recolección de datos
        """
        try:
            # 1. Verificar si es la primera vez
            if not await self._has_cached_data(market_key):
                logger.info(f"Primera vez para {market_key} - ejecutando recolección")
                return True
            
            # 2. Verificar si los datos están expirados
            if await self._is_data_expired(market_key, data_type):
                logger.info(f"Datos expirados para {market_key} - ejecutando recolección")
                return True
            
            # 3. Verificar si hay demanda alta
            if await self._has_high_demand(market_key):
                logger.info(f"Alta demanda para {market_key} - ejecutando recolección")
                return True
            
            # 4. Verificar si hay cambios significativos en el mercado
            if await self._detect_market_changes(market_key):
                logger.info(f"Cambios detectados para {market_key} - ejecutando recolección")
                return True
            
            # 5. Verificar horario de ejecución programada
            if await self._is_scheduled_execution_time(market_key):
                logger.info(f"Ejecución programada para {market_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando ejecución: {e}")
            return False
    
    async def _has_cached_data(self, market_key: str) -> bool:
        """
        Verifica si hay datos en cache
        """
        try:
            cached_data = self.redis_client.get(f"market_data:{market_key}")
            return cached_data is not None
            
        except Exception as e:
            logger.error(f"Error verificando cache: {e}")
            return False
    
    async def _is_data_expired(self, market_key: str, data_type: str = None) -> bool:
        """
        Verifica si los datos han expirado
        """
        try:
            # Obtener timestamp de última actualización
            last_update_key = f"last_update:{market_key}"
            last_update_str = self.redis_client.get(last_update_key)
            
            if not last_update_str:
                return True
            
            last_update = datetime.fromisoformat(last_update_str.decode())
            current_time = datetime.utcnow()
            
            # Determinar TTL basado en tipo de datos
            ttl_hours = self.cache_ttl.get(data_type, 24)
            
            return (current_time - last_update).total_seconds() > (ttl_hours * 3600)
            
        except Exception as e:
            logger.error(f"Error verificando expiración: {e}")
            return True
    
    async def _has_high_demand(self, market_key: str) -> bool:
        """
        Verifica si hay alta demanda para este mercado
        """
        try:
            # Contar consultas en las últimas horas
            demand_key = f"demand:{market_key}"
            recent_queries = self.redis_client.zcount(
                demand_key, 
                datetime.utcnow().timestamp() - 3600,  # Última hora
                datetime.utcnow().timestamp()
            )
            
            # Si hay más de 10 consultas en la última hora, es alta demanda
            return recent_queries > 10
            
        except Exception as e:
            logger.error(f"Error verificando demanda: {e}")
            return False
    
    async def _detect_market_changes(self, market_key: str) -> bool:
        """
        Detecta cambios significativos en el mercado
        """
        try:
            # Obtener datos históricos
            historical_data = await self._get_historical_data(market_key)
            
            if not historical_data:
                return False
            
            # Calcular cambios en indicadores clave
            changes = {
                'rental_yield_change': self._calculate_change(historical_data, 'rental_yield'),
                'price_change': self._calculate_change(historical_data, 'avg_price'),
                'vacancy_change': self._calculate_change(historical_data, 'vacancy_rate')
            }
            
            # Si hay cambios significativos (>5%), ejecutar recolección
            significant_changes = [
                abs(change) > 0.05 for change in changes.values()
            ]
            
            return any(significant_changes)
            
        except Exception as e:
            logger.error(f"Error detectando cambios: {e}")
            return False
    
    async def _is_scheduled_execution_time(self, market_key: str) -> bool:
        """
        Verifica si es hora de ejecución programada
        """
        try:
            # Obtener configuración de horario
            schedule_config = await self._get_schedule_config(market_key)
            
            current_time = datetime.utcnow()
            
            # Verificar horarios programados
            for schedule_type, schedule_time in schedule_config.items():
                if schedule_type == 'daily' and current_time.hour == schedule_time:
                    return True
                elif schedule_type == 'weekly' and current_time.weekday() == schedule_time:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando horario: {e}")
            return False
    
    async def _execute_data_collection(self, country: str, city: str, data_type: str = None) -> Dict:
        """
        Ejecuta recolección de datos
        """
        try:
            # Importar el recolector automático
            from automated_data_collector import AutomatedDataCollector
            from adaptive_learning_system import AdaptiveLearningSystem
            
            collector = AutomatedDataCollector()
            learning_system = AdaptiveLearningSystem()
            
            # Recolectar datos
            market_data = await collector.collect_market_data(country, city)
            
            # Aprender patrones
            patterns = await learning_system.learn_market_patterns(market_data)
            
            # Combinar resultados
            result = {
                'market_data': market_data,
                'patterns': patterns,
                'collected_at': datetime.utcnow().isoformat(),
                'data_type': data_type
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error ejecutando recolección: {e}")
            return await self._get_fallback_data(country, city, data_type)
    
    async def _cache_data(self, market_key: str, data: Dict, data_type: str = None):
        """
        Guarda datos en cache
        """
        try:
            # Guardar datos
            cache_key = f"market_data:{market_key}"
            self.redis_client.setex(
                cache_key,
                self.cache_ttl.get(data_type, 24) * 3600,  # TTL en segundos
                json.dumps(data)
            )
            
            # Guardar timestamp de actualización
            update_key = f"last_update:{market_key}"
            self.redis_client.set(update_key, datetime.utcnow().isoformat())
            
            logger.info(f"Datos guardados en cache para {market_key}")
            
        except Exception as e:
            logger.error(f"Error guardando en cache: {e}")
    
    async def _get_cached_data(self, market_key: str, data_type: str = None) -> Optional[Dict]:
        """
        Obtiene datos del cache
        """
        try:
            cache_key = f"market_data:{market_key}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data.decode())
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo cache: {e}")
            return None
    
    def _is_data_fresh(self, data: Dict, data_type: str = None) -> bool:
        """
        Verifica si los datos están frescos
        """
        try:
            if 'collected_at' not in data:
                return False
            
            collected_at = datetime.fromisoformat(data['collected_at'])
            current_time = datetime.utcnow()
            
            ttl_hours = self.cache_ttl.get(data_type, 24)
            max_age = timedelta(hours=ttl_hours)
            
            return (current_time - collected_at) < max_age
            
        except Exception as e:
            logger.error(f"Error verificando frescura: {e}")
            return False
    
    async def _get_fallback_data(self, country: str, city: str, data_type: str = None) -> Dict:
        """
        Obtiene datos de respaldo
        """
        try:
            # Datos de respaldo basados en investigación global
            fallback_data = {
                'rental_yields': {
                    'chapinero': 0.085,
                    'usaquen': 0.078,
                    'zona_t': 0.092,
                    'default': 0.075
                },
                'operating_expenses': {
                    'property_tax': 0.012,
                    'insurance': 0.008,
                    'maintenance': 0.015,
                    'management_fee': 0.08,
                    'vacancy_rate': 0.05
                }
            }
            
            return {
                'market_data': fallback_data,
                'source': 'fallback',
                'collected_at': datetime.utcnow().isoformat(),
                'confidence': 0.6
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de respaldo: {e}")
            return {}
    
    def _calculate_change(self, historical_data: List[Dict], metric: str) -> float:
        """
        Calcula cambio en una métrica
        """
        try:
            if len(historical_data) < 2:
                return 0.0
            
            current_value = historical_data[-1].get(metric, 0)
            previous_value = historical_data[-2].get(metric, 0)
            
            if previous_value == 0:
                return 0.0
            
            return (current_value - previous_value) / previous_value
            
        except Exception as e:
            logger.error(f"Error calculando cambio: {e}")
            return 0.0
    
    async def _get_schedule_config(self, market_key: str) -> Dict:
        """
        Obtiene configuración de horarios
        """
        # Horarios de ejecución programada
        return {
            'daily': 6,      # 6:00 AM UTC
            'weekly': 0,     # Lunes
            'monthly': 1     # Primer día del mes
        }
    
    async def _get_historical_data(self, market_key: str) -> List[Dict]:
        """
        Obtiene datos históricos
        """
        try:
            # En producción, esto vendría de una base de datos
            # Por ahora, simulamos datos históricos
            return [
                {'rental_yield': 0.085, 'avg_price': 450000000, 'vacancy_rate': 0.04},
                {'rental_yield': 0.083, 'avg_price': 445000000, 'vacancy_rate': 0.045}
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos: {e}")
            return []

# Ejemplo de uso
if __name__ == "__main__":
    scheduler = SmartExecutionScheduler()
    
    print("=== SCHEDULER INTELIGENTE ===")
    print("Estrategias de ejecución:")
    print("1. Cache inteligente (24h-1 semana)")
    print("2. Ejecución bajo demanda")
    print("3. Detección de cambios de mercado")
    print("4. Horarios programados")
    print("5. Datos de respaldo")
    print("\nOptimizado para velocidad y eficiencia") 