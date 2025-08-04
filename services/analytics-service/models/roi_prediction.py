import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ROIPredictionModel:
    """
    Modelo para predicción de ROI (Return on Investment) inmobiliario
    """
    
    def __init__(self):
        self.rental_yield_rates = {
            'chapinero': 0.085,  # 8.5% anual
            'usaquen': 0.078,    # 7.8% anual
            'zona_t': 0.092,     # 9.2% anual
            'suba': 0.075,       # 7.5% anual
            'engativa': 0.082,   # 8.2% anual
            'default': 0.080     # 8.0% anual
        }
        
        self.appreciation_rates = {
            'chapinero': 0.085,  # 8.5% anual
            'usaquen': 0.078,    # 7.8% anual
            'zona_t': 0.092,     # 9.2% anual
            'suba': 0.075,       # 7.5% anual
            'engativa': 0.082,   # 8.2% anual
            'default': 0.080     # 8.0% anual
        }
        
        self.operating_expenses = {
            'property_tax': 0.012,      # 1.2% del valor
            'insurance': 0.008,          # 0.8% del valor
            'maintenance': 0.015,        # 1.5% del valor
            'management_fee': 0.08,      # 8% del ingreso por renta
            'vacancy_rate': 0.05         # 5% de vacancia
        }
    
    def calculate_roi(self, property_data: Dict, investment_period: int = 5) -> Dict:
        """
        Calcula el ROI completo para un período de inversión
        """
        try:
            # Datos base
            purchase_price = property_data['purchase_price']
            location = property_data.get('location', 'default').lower()
            area_m2 = property_data.get('area_m2', 0)
            
            # Tasas específicas de la ubicación
            rental_yield = self.rental_yield_rates.get(location, self.rental_yield_rates['default'])
            appreciation_rate = self.appreciation_rates.get(location, self.appreciation_rates['default'])
            
            # Cálculos anuales
            annual_rental_income = purchase_price * rental_yield
            annual_appreciation = purchase_price * appreciation_rate
            
            # Gastos operativos anuales
            annual_expenses = self._calculate_annual_expenses(purchase_price, annual_rental_income)
            
            # Flujo de caja anual
            annual_cash_flow = annual_rental_income - annual_expenses
            
            # Proyección por años
            roi_projection = {}
            current_value = purchase_price
            total_cash_flow = 0
            total_appreciation = 0
            
            for year in range(1, investment_period + 1):
                # Valor de la propiedad
                current_value = purchase_price * ((1 + appreciation_rate) ** year)
                
                # Ingresos por renta (ajustados por inflación)
                inflation_adjusted_rent = annual_rental_income * ((1 + 0.03) ** (year - 1))
                
                # Gastos operativos (ajustados por inflación)
                inflation_adjusted_expenses = annual_expenses * ((1 + 0.03) ** (year - 1))
                
                # Flujo de caja
                year_cash_flow = inflation_adjusted_rent - inflation_adjusted_expenses
                total_cash_flow += year_cash_flow
                
                # Apreciación acumulada
                year_appreciation = current_value - purchase_price
                total_appreciation = year_appreciation
                
                # ROI total hasta este año
                total_investment_return = total_cash_flow + total_appreciation
                roi_percentage = (total_investment_return / purchase_price) * 100
                
                roi_projection[f"year_{year}"] = {
                    'property_value': round(current_value, 0),
                    'annual_rental_income': round(inflation_adjusted_rent, 0),
                    'annual_expenses': round(inflation_adjusted_expenses, 0),
                    'annual_cash_flow': round(year_cash_flow, 0),
                    'cumulative_cash_flow': round(total_cash_flow, 0),
                    'appreciation': round(year_appreciation, 0),
                    'total_return': round(total_investment_return, 0),
                    'roi_percentage': round(roi_percentage, 2),
                    'annual_roi': round((year_cash_flow + year_appreciation) / purchase_price * 100, 2)
                }
            
            # Métricas finales
            final_roi = (total_cash_flow + total_appreciation) / purchase_price
            annualized_roi = ((1 + final_roi) ** (1 / investment_period)) - 1
            
            return {
                'purchase_price': purchase_price,
                'investment_period': investment_period,
                'location': location,
                'rental_yield': rental_yield,
                'appreciation_rate': appreciation_rate,
                'projection': roi_projection,
                'summary': {
                    'total_cash_flow': round(total_cash_flow, 0),
                    'total_appreciation': round(total_appreciation, 0),
                    'total_return': round(total_cash_flow + total_appreciation, 0),
                    'final_roi_percentage': round(final_roi * 100, 2),
                    'annualized_roi_percentage': round(annualized_roi * 100, 2),
                    'break_even_year': self._calculate_break_even(roi_projection),
                    'risk_metrics': self._calculate_risk_metrics(roi_projection, purchase_price)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculando ROI: {e}")
            raise
    
    def calculate_roi_with_financing(self, property_data: Dict, financing_data: Dict) -> Dict:
        """
        Calcula ROI considerando financiamiento bancario
        """
        try:
            purchase_price = property_data['purchase_price']
            down_payment = financing_data['down_payment']
            loan_amount = purchase_price - down_payment
            interest_rate = financing_data['interest_rate']
            loan_term = financing_data['loan_term']
            
            # Cálculo de cuota mensual
            monthly_rate = interest_rate / 12
            num_payments = loan_term * 12
            
            if monthly_rate > 0:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
            else:
                monthly_payment = loan_amount / num_payments
            
            annual_payment = monthly_payment * 12
            
            # ROI con financiamiento
            roi_data = self.calculate_roi(property_data)
            
            # Ajustar flujo de caja por pagos del préstamo
            for year in range(1, len(roi_data['projection']) + 1):
                year_data = roi_data['projection'][f'year_{year}']
                
                # Restar pagos del préstamo del flujo de caja
                adjusted_cash_flow = year_data['annual_cash_flow'] - annual_payment
                year_data['annual_cash_flow_with_financing'] = round(adjusted_cash_flow, 0)
                year_data['annual_payment'] = round(annual_payment, 0)
                
                # Recalcular ROI
                total_investment_return = year_data['cumulative_cash_flow'] + year_data['appreciation'] - (annual_payment * year)
                roi_percentage = (total_investment_return / down_payment) * 100
                year_data['roi_percentage_with_financing'] = round(roi_percentage, 2)
            
            # Actualizar resumen
            final_year = len(roi_data['projection'])
            final_data = roi_data['projection'][f'year_{final_year}']
            
            roi_data['summary']['total_cash_flow_with_financing'] = round(final_data['cumulative_cash_flow'] - (annual_payment * final_year), 0)
            roi_data['summary']['final_roi_with_financing'] = round(((final_data['cumulative_cash_flow'] - (annual_payment * final_year) + final_data['appreciation']) / down_payment) * 100, 2)
            roi_data['summary']['monthly_payment'] = round(monthly_payment, 0)
            roi_data['summary']['annual_payment'] = round(annual_payment, 0)
            
            return roi_data
            
        except Exception as e:
            logger.error(f"Error calculando ROI con financiamiento: {e}")
            raise
    
    def _calculate_annual_expenses(self, property_value: float, annual_rental_income: float) -> float:
        """
        Calcula gastos operativos anuales
        """
        property_tax = property_value * self.operating_expenses['property_tax']
        insurance = property_value * self.operating_expenses['insurance']
        maintenance = property_value * self.operating_expenses['maintenance']
        management_fee = annual_rental_income * self.operating_expenses['management_fee']
        vacancy_loss = annual_rental_income * self.operating_expenses['vacancy_rate']
        
        return property_tax + insurance + maintenance + management_fee + vacancy_loss
    
    def _calculate_break_even(self, roi_projection: Dict) -> Optional[int]:
        """
        Calcula el año en que se recupera la inversión
        """
        for year, data in roi_projection.items():
            if data['cumulative_cash_flow'] >= 0:
                return int(year.split('_')[1])
        return None
    
    def _calculate_risk_metrics(self, roi_projection: Dict, purchase_price: float) -> Dict:
        """
        Calcula métricas de riesgo
        """
        cash_flows = [data['annual_cash_flow'] for data in roi_projection.values()]
        
        # Volatilidad del flujo de caja
        cash_flow_volatility = np.std(cash_flows) if len(cash_flows) > 1 else 0
        
        # Ratio de Sharpe (simplificado)
        avg_cash_flow = np.mean(cash_flows)
        sharpe_ratio = avg_cash_flow / cash_flow_volatility if cash_flow_volatility > 0 else 0
        
        # Máximo drawdown
        cumulative_cash_flows = [data['cumulative_cash_flow'] for data in roi_projection.values()]
        max_drawdown = min(cumulative_cash_flows) if cumulative_cash_flows else 0
        
        return {
            'cash_flow_volatility': round(cash_flow_volatility, 0),
            'sharpe_ratio': round(sharpe_ratio, 3),
            'max_drawdown': round(max_drawdown, 0),
            'risk_level': self._assess_risk_level(sharpe_ratio, max_drawdown, purchase_price)
        }
    
    def _assess_risk_level(self, sharpe_ratio: float, max_drawdown: float, purchase_price: float) -> str:
        """
        Evalúa el nivel de riesgo de la inversión
        """
        drawdown_ratio = abs(max_drawdown) / purchase_price
        
        if sharpe_ratio > 1.5 and drawdown_ratio < 0.1:
            return "BAJO"
        elif sharpe_ratio > 1.0 and drawdown_ratio < 0.2:
            return "MEDIO-BAJO"
        elif sharpe_ratio > 0.5 and drawdown_ratio < 0.3:
            return "MEDIO"
        elif sharpe_ratio > 0.0 and drawdown_ratio < 0.4:
            return "MEDIO-ALTO"
        else:
            return "ALTO"
    
    def compare_investments(self, properties: List[Dict]) -> Dict:
        """
        Compara múltiples inversiones
        """
        comparisons = {}
        
        for i, property_data in enumerate(properties):
            roi_data = self.calculate_roi(property_data)
            comparisons[f"property_{i+1}"] = {
                'name': property_data.get('name', f'Propiedad {i+1}'),
                'location': property_data.get('location', 'default'),
                'purchase_price': property_data['purchase_price'],
                'final_roi': roi_data['summary']['final_roi_percentage'],
                'annualized_roi': roi_data['summary']['annualized_roi_percentage'],
                'risk_level': roi_data['summary']['risk_metrics']['risk_level'],
                'break_even_year': roi_data['summary']['break_even_year']
            }
        
        # Ranking por ROI
        ranked_properties = sorted(
            comparisons.items(),
            key=lambda x: x[1]['final_roi'],
            reverse=True
        )
        
        return {
            'comparisons': comparisons,
            'ranking': ranked_properties,
            'best_investment': ranked_properties[0] if ranked_properties else None
        }

# Ejemplo de uso
if __name__ == "__main__":
    model = ROIPredictionModel()
    
    # Datos de ejemplo
    property_data = {
        'purchase_price': 420000000,  # $420M
        'location': 'chapinero',
        'area_m2': 85
    }
    
    financing_data = {
        'down_payment': 126000000,  # 30%
        'interest_rate': 0.12,      # 12% anual
        'loan_term': 20             # 20 años
    }
    
    # Calcular ROI
    roi_result = model.calculate_roi(property_data)
    roi_with_financing = model.calculate_roi_with_financing(property_data, financing_data)
    
    print("=== ANÁLISIS DE ROI ===")
    print(f"Precio de compra: ${roi_result['purchase_price']:,}")
    print(f"ROI final: {roi_result['summary']['final_roi_percentage']}%")
    print(f"ROI anualizado: {roi_result['summary']['annualized_roi_percentage']}%")
    print(f"Nivel de riesgo: {roi_result['summary']['risk_metrics']['risk_level']}")
    
    print("\n=== CON FINANCIAMIENTO ===")
    print(f"ROI con financiamiento: {roi_with_financing['summary']['final_roi_with_financing']}%")
    print(f"Cuota mensual: ${roi_with_financing['summary']['monthly_payment']:,}") 