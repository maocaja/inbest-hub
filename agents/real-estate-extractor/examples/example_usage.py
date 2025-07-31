#!/usr/bin/env python3
"""
Ejemplo de uso del Real Estate Data Extractor Agent

Este script demuestra cómo usar el agente para extraer información
de proyectos inmobiliarios desde documentos.
"""

import requests
import json
import os
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8012"

def test_extract_from_document(file_path: str):
    """
    Ejemplo de extracción de datos desde un documento
    """
    print(f"🔍 Extrayendo datos desde: {file_path}")
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file, 'application/octet-stream')}
            
            response = requests.post(f"{BASE_URL}/extract", files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                if result['success']:
                    print("✅ Extracción exitosa!")
                    print(f"📊 Score de completitud: {result['validation_result']['completeness_score']}%")
                    
                    # Mostrar datos extraídos
                    project_data = result['project_data']
                    print("\n📋 DATOS EXTRAÍDOS:")
                    print(f"   Nombre: {project_data.get('name', 'N/A')}")
                    print(f"   Constructora: {project_data.get('builder', 'N/A')}")
                    print(f"   Estado: {project_data.get('status', 'N/A')}")
                    
                    if project_data.get('location'):
                        loc = project_data['location']
                        print(f"   Ubicación: {loc.get('city', 'N/A')}, {loc.get('neighborhood', 'N/A')}")
                    
                    if project_data.get('price_info'):
                        price = project_data['price_info']
                        print(f"   Precio: {price.get('price_min', 'N/A')} - {price.get('price_max', 'N/A')} {price.get('currency', '')}")
                    
                    # Mostrar validación
                    validation = result['validation_result']
                    if validation['errors']:
                        print("\n❌ ERRORES:")
                        for error in validation['errors']:
                            print(f"   - {error}")
                    
                    if validation['warnings']:
                        print("\n⚠️ ADVERTENCIAS:")
                        for warning in validation['warnings']:
                            print(f"   - {warning}")
                    
                    if validation['suggestions']:
                        print("\n💡 SUGERENCIAS:")
                        for suggestion in validation['suggestions']:
                            print(f"   - {suggestion}")
                    
                else:
                    print("❌ Error en la extracción:")
                    print(result['message'])
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                print(response.text)
                
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {file_path}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_validate_project_data():
    """
    Ejemplo de validación de datos del proyecto
    """
    print("\n🔍 Validando datos del proyecto...")
    
    # Datos de ejemplo para validar
    project_data = {
        "name": "Residencial Los Pinos",
        "builder": "Constructora ABC",
        "status": "preventa",
        "delivery_date": "2024-12",
        "location": {
            "country": "Colombia",
            "city": "Medellín",
            "neighborhood": "El Poblado"
        },
        "price_info": {
            "currency": "COP",
            "price_min": 150000000,
            "price_max": 300000000
        },
        "unit_info": {
            "unit_types": ["apartamento"],
            "area_m2_min": 60,
            "area_m2_max": 120
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/validate", json=project_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Validación completada!")
            print(f"📊 Score de completitud: {result['completeness_score']}%")
            print(f"✅ Válido: {result['is_valid']}")
            
            if result['errors']:
                print("\n❌ ERRORES:")
                for error in result['errors']:
                    print(f"   - {error}")
            
            if result['warnings']:
                print("\n⚠️ ADVERTENCIAS:")
                for warning in result['warnings']:
                    print(f"   - {warning}")
            
            if result['suggestions']:
                print("\n💡 SUGERENCIAS:")
                for suggestion in result['suggestions']:
                    print(f"   - {suggestion}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_complete_missing_data():
    """
    Ejemplo de completado de información faltante
    """
    print("\n🔧 Completando información faltante...")
    
    # Datos incompletos de ejemplo
    incomplete_data = {
        "name": "Residencial Los Pinos",
        "builder": "Constructora ABC",
        "status": "preventa",
        "location": {
            "city": "Medellín"
        }
        # Faltan muchos campos
    }
    
    try:
        response = requests.post(f"{BASE_URL}/complete", json=incomplete_data)
        
        if response.status_code == 200:
            completed_data = response.json()
            
            print("✅ Información completada!")
            print("\n📋 DATOS COMPLETADOS:")
            print(f"   Nombre: {completed_data.get('name', 'N/A')}")
            print(f"   Constructora: {completed_data.get('builder', 'N/A')}")
            print(f"   Estado: {completed_data.get('status', 'N/A')}")
            
            if completed_data.get('location'):
                loc = completed_data['location']
                print(f"   País: {loc.get('country', 'N/A')}")
                print(f"   Ciudad: {loc.get('city', 'N/A')}")
                print(f"   Zona: {loc.get('zone', 'N/A')}")
            
            if completed_data.get('price_info'):
                price = completed_data['price_info']
                print(f"   Moneda: {price.get('currency', 'N/A')}")
                print(f"   Precio mínimo: {price.get('price_min', 'N/A')}")
                print(f"   Precio máximo: {price.get('price_max', 'N/A')}")
            
            if completed_data.get('unit_info'):
                unit = completed_data['unit_info']
                print(f"   Tipos de unidad: {unit.get('unit_types', 'N/A')}")
                print(f"   Área mínima: {unit.get('area_m2_min', 'N/A')} m²")
                print(f"   Área máxima: {unit.get('area_m2_max', 'N/A')} m²")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_get_schema():
    """
    Ejemplo de obtención del esquema JSON
    """
    print("\n📋 Obteniendo esquema JSON...")
    
    try:
        response = requests.get(f"{BASE_URL}/schema")
        
        if response.status_code == 200:
            schema = response.json()
            
            print("✅ Esquema obtenido!")
            print(f"📊 Título: {schema.get('title', 'N/A')}")
            print(f"📝 Descripción: {schema.get('description', 'N/A')}")
            print(f"🔢 Versión: {schema.get('version', 'N/A')}")
            
            # Mostrar propiedades principales
            properties = schema.get('properties', {})
            print(f"\n📋 Propiedades principales ({len(properties)}):")
            for prop_name in list(properties.keys())[:5]:  # Mostrar solo las primeras 5
                print(f"   - {prop_name}")
            
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_server_status():
    """
    Verifica el estado del servidor
    """
    print("🔍 Verificando estado del servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Servidor funcionando: {result['status']}")
            return True
        else:
            print(f"❌ Servidor no disponible: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. Asegúrate de que esté ejecutándose.")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """
    Función principal que ejecuta todos los ejemplos
    """
    print("🏠 REAL ESTATE DATA EXTRACTOR AGENT - EJEMPLOS")
    print("=" * 50)
    
    # Verificar estado del servidor
    if not check_server_status():
        print("\n💡 Para ejecutar este ejemplo:")
        print("1. Asegúrate de que el agente esté ejecutándose:")
        print("   cd agents/real-estate-extractor")
        print("   python main.py")
        print("2. Configura tu API key de OpenAI en el archivo .env")
        return
    
    # Ejecutar ejemplos
    test_get_schema()
    test_validate_project_data()
    test_complete_missing_data()
    
    # Ejemplo con archivo (si existe)
    example_file = Path("examples/sample_project.pdf")
    if example_file.exists():
        test_extract_from_document(str(example_file))
    else:
        print(f"\n📄 Para probar la extracción de documentos:")
        print(f"   Coloca un archivo PDF/DOCX/Excel en: {example_file}")
        print(f"   O usa el endpoint /extract directamente")
    
    print("\n✅ Ejemplos completados!")

if __name__ == "__main__":
    main() 