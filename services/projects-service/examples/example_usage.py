#!/usr/bin/env python3
"""
Ejemplo de uso del Projects Service
"""

import requests
import json
import time

BASE_URL = "http://localhost:8003"

def health_check():
    """Verificar que el servicio esté funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servicio funcionando correctamente")
            return True
        else:
            print(f"❌ Servicio no responde: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servicio")
        return False

def create_project_owner():
    """Crear una constructora de prueba (requiere project-owners-service)"""
    print("\n🏗️  Creando constructora de prueba...")
    
    # Primero intentar crear en project-owners-service
    owner_data = {
        "name": "Constructora Ejemplo",
        "nit": "900123456-7",
        "email": "contacto@constructoraejemplo.com",
        "city": "Medellín",
        "country": "Colombia"
    }
    
    try:
        response = requests.post(
            "http://localhost:8002/project-owners",
            json=owner_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ Constructora creada en project-owners-service")
            return True
        elif response.status_code == 400 and "Ya existe" in response.text:
            print("✅ Constructora ya existe")
            return True
        else:
            print(f"⚠️  Error creando constructora: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  project-owners-service no disponible, continuando...")
        return True

def create_project():
    """Crear un proyecto de prueba"""
    print("\n🏗️  Creando proyecto de prueba...")
    
    project_data = {
        "name": "Residencial Los Pinos",
        "description": "Proyecto residencial de lujo en zona exclusiva de Medellín",
        "project_owner_nit": "900123456-7",
        "status": "incompleto",
        "location": {
            "address": "Calle 123 #45-67",
            "city": "Medellín",
            "department": "Antioquia",
            "country": "Colombia",
            "coordinates": {"lat": 6.2442, "lng": -75.5812}
        },
        "price_info": {
            "currency": "COP",
            "min_price": 150000000,
            "max_price": 450000000,
            "price_per_m2": 2500000
        },
        "unit_info": {
            "total_units": 120,
            "available_units": 45,
            "unit_types": ["Apartamento 2BR", "Apartamento 3BR", "Penthouse"],
            "areas": {
                "Apartamento 2BR": {"min": 65, "max": 85},
                "Apartamento 3BR": {"min": 95, "max": 120},
                "Penthouse": {"min": 150, "max": 200}
            }
        },
        "amenities": [
            "Piscina", "Gimnasio", "Zona BBQ", "Parqueadero cubierto",
            "Seguridad 24/7", "Área de juegos infantiles"
        ],
        "financial_info": {
            "delivery_date": "2024-12-31",
            "payment_plans": [
                {"name": "Plan 70/30", "description": "70% cuota inicial, 30% a 12 meses"}
            ],
            "financing_options": ["Banco A", "Banco B", "Leasing"]
        },
        "audience_info": {
            "target_audience": ["Familias", "Profesionales", "Inversionistas"],
            "income_levels": ["Medio-alto", "Alto"]
        },
        "media": {
            "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
            "videos": ["https://example.com/video.mp4"],
            "documents": ["https://example.com/brochure.pdf"]
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/projects",
            json=project_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            project = response.json()
            print(f"✅ Proyecto creado: {project['name']} (ID: {project['id']})")
            return project['id']
        else:
            print(f"❌ Error creando proyecto: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return None

def get_project(project_id):
    """Obtener un proyecto específico"""
    print(f"\n📋 Obteniendo proyecto {project_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/projects/{project_id}")
        
        if response.status_code == 200:
            project = response.json()
            print(f"✅ Proyecto obtenido: {project['name']}")
            print(f"   Estado: {project['status']}")
            print(f"   Constructora: {project['project_owner_nit']}")
            return project
        else:
            print(f"❌ Error obteniendo proyecto: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return None

def update_project_state(project_id, new_status):
    """Actualizar el estado de un proyecto"""
    print(f"\n🔄 Actualizando estado del proyecto {project_id} a '{new_status}'...")
    
    state_data = {"status": new_status}
    
    try:
        response = requests.patch(
            f"{BASE_URL}/projects/{project_id}/state",
            json=state_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            project = response.json()
            print(f"✅ Estado actualizado: {project['name']} -> {project['status']}")
            return True
        else:
            print(f"❌ Error actualizando estado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def list_projects():
    """Listar todos los proyectos"""
    print("\n📋 Listando proyectos...")
    
    try:
        response = requests.get(f"{BASE_URL}/projects")
        
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Encontrados {len(projects)} proyectos:")
            
            for project in projects:
                print(f"   - {project['name']} (ID: {project['id']}, Estado: {project['status']})")
            
            return projects
        else:
            print(f"❌ Error listando proyectos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return []

def get_projects_by_owner(owner_nit):
    """Obtener proyectos de una constructora específica"""
    print(f"\n🏢 Obteniendo proyectos de la constructora {owner_nit}...")
    
    try:
        response = requests.get(f"{BASE_URL}/projects/owner/{owner_nit}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Encontrados {len(projects)} proyectos de la constructora:")
            
            for project in projects:
                print(f"   - {project['name']} (ID: {project['id']})")
            
            return projects
        else:
            print(f"❌ Error obteniendo proyectos por constructora: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return []

def get_project_history(project_id):
    """Obtener historial de un proyecto"""
    print(f"\n📜 Obteniendo historial del proyecto {project_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/projects/{project_id}/history")
        
        if response.status_code == 200:
            history = response.json()
            print(f"✅ Historial obtenido:")
            
            for entry in history['history']:
                print(f"   - {entry['action']}: {entry['details']} ({entry['timestamp']})")
            
            return history
        else:
            print(f"❌ Error obteniendo historial: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return None

def test_validation_errors():
    """Probar validaciones de errores"""
    print("\n🧪 Probando validaciones de errores...")
    
    # Proyecto con NIT inválido
    invalid_project = {
        "name": "Proyecto Inválido",
        "description": "Proyecto con datos inválidos",
        "project_owner_nit": "NIT-INVALIDO",
        "status": "incompleto"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/projects",
            json=invalid_project,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ Validación de NIT funcionando correctamente")
        else:
            print(f"⚠️  Validación de NIT no funcionó como esperado: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en validación: {e}")

def main():
    """Función principal"""
    print("🚀 Ejemplo de uso del Projects Service")
    print("="*50)
    
    # Verificar que el servicio esté funcionando
    if not health_check():
        print("❌ El servicio no está disponible")
        return
    
    # Crear constructora de prueba
    create_project_owner()
    
    # Crear proyecto de prueba
    project_id = create_project()
    if not project_id:
        print("❌ No se pudo crear el proyecto de prueba")
        return
    
    # Obtener el proyecto creado
    get_project(project_id)
    
    # Actualizar estado del proyecto
    update_project_state(project_id, "en_proceso")
    
    # Listar todos los proyectos
    list_projects()
    
    # Obtener proyectos por constructora
    get_projects_by_owner("900123456-7")
    
    # Obtener historial del proyecto
    get_project_history(project_id)
    
    # Probar validaciones
    test_validation_errors()
    
    print("\n" + "="*50)
    print("✅ Ejemplo completado exitosamente")
    print("📋 Para más información, consulta la documentación API en:")
    print(f"   {BASE_URL}/docs")

if __name__ == "__main__":
    main() 