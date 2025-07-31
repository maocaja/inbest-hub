import logging
from typing import Dict, Any, List, Optional
import re
from datetime import datetime
from models.schemas import ValidationResult, RealEstateProject

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Servicio para validar información de proyectos inmobiliarios
    """
    
    def __init__(self):
        self.required_fields = [
            "name", "builder", "status"
        ]
        
        self.important_fields = [
            "location.city", "location.neighborhood",
            "price_info.price_min", "price_info.currency",
            "unit_info.area_m2_min", "unit_info.unit_types"
        ]
        
        self.validation_rules = {
            "delivery_date": self._validate_date_format,
            "price_info.price_min": self._validate_positive_number,
            "price_info.price_max": self._validate_positive_number,
            "unit_info.area_m2_min": self._validate_positive_number,
            "unit_info.area_m2_max": self._validate_positive_number,
            "location.latitude": self._validate_latitude,
            "location.longitude": self._validate_longitude
        }
    
    async def validate_project_data(self, project_data: Dict[str, Any]) -> ValidationResult:
        """
        Valida la información del proyecto inmobiliario
        """
        try:
            errors = []
            warnings = []
            suggestions = []
            
            # Validar campos requeridos
            missing_required = self._check_required_fields(project_data)
            errors.extend(missing_required)
            
            # Validar campos importantes
            missing_important = self._check_important_fields(project_data)
            warnings.extend(missing_important)
            
            # Validar reglas específicas
            validation_errors = self._validate_specific_rules(project_data)
            errors.extend(validation_errors)
            
            # Validar consistencia de datos
            consistency_errors = self._validate_data_consistency(project_data)
            errors.extend(consistency_errors)
            
            # Generar sugerencias
            suggestions = self._generate_suggestions(project_data)
            
            # Calcular score de completitud
            completeness_score = self._calculate_completeness_score(project_data)
            
            is_valid = len(errors) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                completeness_score=completeness_score,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error validando datos del proyecto: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Error en validación: {str(e)}"],
                warnings=[],
                completeness_score=0.0,
                suggestions=[]
            )
    
    def _check_required_fields(self, data: Dict[str, Any]) -> List[str]:
        """
        Verifica campos requeridos
        """
        errors = []
        
        for field in self.required_fields:
            if not self._get_nested_value(data, field):
                errors.append(f"Campo requerido faltante: {field}")
        
        return errors
    
    def _check_important_fields(self, data: Dict[str, Any]) -> List[str]:
        """
        Verifica campos importantes
        """
        warnings = []
        
        for field in self.important_fields:
            if not self._get_nested_value(data, field):
                warnings.append(f"Campo importante faltante: {field}")
        
        return warnings
    
    def _validate_specific_rules(self, data: Dict[str, Any]) -> List[str]:
        """
        Valida reglas específicas para campos
        """
        errors = []
        
        for field_path, validator_func in self.validation_rules.items():
            value = self._get_nested_value(data, field_path)
            if value is not None:
                try:
                    validator_func(value)
                except ValueError as e:
                    errors.append(f"Error en {field_path}: {str(e)}")
        
        return errors
    
    def _validate_data_consistency(self, data: Dict[str, Any]) -> List[str]:
        """
        Valida consistencia entre campos relacionados
        """
        errors = []
        
        # Validar precios
        price_min = self._get_nested_value(data, "price_info.price_min")
        price_max = self._get_nested_value(data, "price_info.price_max")
        
        if price_min and price_max and price_min > price_max:
            errors.append("El precio mínimo no puede ser mayor al precio máximo")
        
        # Validar áreas
        area_min = self._get_nested_value(data, "unit_info.area_m2_min")
        area_max = self._get_nested_value(data, "unit_info.area_m2_max")
        
        if area_min and area_max and area_min > area_max:
            errors.append("El área mínima no puede ser mayor al área máxima")
        
        # Validar habitaciones
        bedrooms_min = self._get_nested_value(data, "unit_info.bedrooms_min")
        bedrooms_max = self._get_nested_value(data, "unit_info.bedrooms_max")
        
        if bedrooms_min and bedrooms_max and bedrooms_min > bedrooms_max:
            errors.append("El número mínimo de habitaciones no puede ser mayor al máximo")
        
        # Validar coordenadas
        lat = self._get_nested_value(data, "location.latitude")
        lon = self._get_nested_value(data, "location.longitude")
        
        if lat is not None and lon is not None:
            if not (-90 <= lat <= 90):
                errors.append("Latitud debe estar entre -90 y 90")
            if not (-180 <= lon <= 180):
                errors.append("Longitud debe estar entre -180 y 180")
        
        return errors
    
    def _generate_suggestions(self, data: Dict[str, Any]) -> List[str]:
        """
        Genera sugerencias para mejorar los datos
        """
        suggestions = []
        
        # Sugerencias basadas en campos faltantes
        if not self._get_nested_value(data, "location.country"):
            suggestions.append("Agregar país para mejor geolocalización")
        
        if not self._get_nested_value(data, "price_info.currency"):
            suggestions.append("Especificar moneda para los precios")
        
        if not self._get_nested_value(data, "unit_info.unit_types"):
            suggestions.append("Especificar tipos de unidades disponibles")
        
        if not self._get_nested_value(data, "amenities.list"):
            suggestions.append("Listar amenidades disponibles")
        
        if not self._get_nested_value(data, "financial_info.offers_financing"):
            suggestions.append("Especificar si el proyecto ofrece financiación")
        
        # Sugerencias basadas en el contexto
        if self._get_nested_value(data, "status") == "preventa":
            if not self._get_nested_value(data, "delivery_date"):
                suggestions.append("Agregar fecha estimada de entrega para proyectos en preventa")
        
        if self._get_nested_value(data, "price_info.price_min"):
            if not self._get_nested_value(data, "price_info.price_per_m2"):
                suggestions.append("Calcular precio por m² para mejor comparación")
        
        return suggestions
    
    def _calculate_completeness_score(self, data: Dict[str, Any]) -> float:
        """
        Calcula el score de completitud del proyecto
        """
        total_fields = 0
        filled_fields = 0
        
        # Contar campos principales
        main_fields = [
            "name", "description", "builder", "status", "delivery_date"
        ]
        
        for field in main_fields:
            total_fields += 1
            if self._get_nested_value(data, field):
                filled_fields += 1
        
        # Contar campos de ubicación
        location_fields = [
            "location.country", "location.department", "location.city",
            "location.zone", "location.neighborhood"
        ]
        
        for field in location_fields:
            total_fields += 1
            if self._get_nested_value(data, field):
                filled_fields += 1
        
        # Contar campos de precios
        price_fields = [
            "price_info.currency", "price_info.price_min", "price_info.price_max"
        ]
        
        for field in price_fields:
            total_fields += 1
            if self._get_nested_value(data, field):
                filled_fields += 1
        
        # Contar campos de unidades
        unit_fields = [
            "unit_info.unit_types", "unit_info.area_m2_min", "unit_info.area_m2_max"
        ]
        
        for field in unit_fields:
            total_fields += 1
            if self._get_nested_value(data, field):
                filled_fields += 1
        
        if total_fields == 0:
            return 0.0
        
        return round((filled_fields / total_fields) * 100, 2)
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """
        Obtiene valor de un campo anidado usando notación de punto
        """
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _validate_date_format(self, value: str) -> None:
        """
        Valida formato de fecha YYYY-MM
        """
        if not re.match(r'^\d{4}-\d{2}$', value):
            raise ValueError("Fecha debe estar en formato YYYY-MM")
        
        try:
            datetime.strptime(value, "%Y-%m")
        except ValueError:
            raise ValueError("Fecha inválida")
    
    def _validate_positive_number(self, value: Any) -> None:
        """
        Valida que el valor sea un número positivo
        """
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Debe ser un número positivo")
    
    def _validate_latitude(self, value: float) -> None:
        """
        Valida latitud
        """
        if not (-90 <= value <= 90):
            raise ValueError("Latitud debe estar entre -90 y 90")
    
    def _validate_longitude(self, value: float) -> None:
        """
        Valida longitud
        """
        if not (-180 <= value <= 180):
            raise ValueError("Longitud debe estar entre -180 y 180") 