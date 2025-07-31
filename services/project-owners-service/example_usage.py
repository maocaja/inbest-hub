#!/usr/bin/env python3
"""
Ejemplo de uso del Project Owners Service

Este script demuestra cómo usar la API del servicio de constructoras
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:8001"

def test_health_check():
    """Prueba el endpoint de health check"""
    print("🔍 Verificando estado del servicio...")
    
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

def create_project_owner():
    """Ejemplo de creación de una constructora"""
    print("\n🏗️ Creando constructora...")
    
    data = {
        "name": "Constructora ABC",
        "nit": "900123456-7",
        "email": "contacto@constructoraabc.com",
        "phone": "+57 300 123 4567",
        "city": "Medellín",
        "department": "Antioquia",
        "country": "Colombia",
        "website": "https://constructoraabc.com",
        "contact_person": "Juan Pérez",
        "contact_phone": "+57 300 987 6543",
        "contact_email": "juan.perez@constructoraabc.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/project-owners", json=data)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Constructora creada exitosamente!")
            print(f"   ID: {result['id']}")
            print(f"   Nombre: {result['name']}")
            print(f"   NIT: {result['nit']}")
            print(f"   Ciudad: {result['city']}")
            return result['id']
        else:
            print(f"❌ Error creando constructora: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def get_project_owners():
    """Ejemplo de obtención de constructoras"""
    print("\n📋 Obteniendo lista de constructoras...")
    
    try:
        response = requests.get(f"{BASE_URL}/project-owners")
        
        if response.status_code == 200:
            project_owners = response.json()
            print(f"✅ Se encontraron {len(project_owners)} constructoras")
            
            for po in project_owners:
                print(f"   - {po['name']} (ID: {po['id']}) - {po['city']}")
            
            return project_owners
        else:
            print(f"❌ Error obteniendo constructoras: {response.status_code}")
            print(response.text)
            return []
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def get_project_owner_by_id(owner_id):
    """Ejemplo de obtención de una constructora por ID"""
    print(f"\n🔍 Obteniendo constructora ID {owner_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/project-owners/{owner_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Constructora encontrada!")
            print(f"   Nombre: {result['name']}")
            print(f"   NIT: {result['nit']}")
            print(f"   Email: {result['email']}")
            print(f"   Ciudad: {result['city']}")
            print(f"   Activa: {result['is_active']}")
            print(f"   Verificada: {result['is_verified']}")
            return result
        else:
            print(f"❌ Error obteniendo constructora: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def update_project_owner(owner_id):
    """Ejemplo de actualización de una constructora"""
    print(f"\n✏️ Actualizando constructora ID {owner_id}...")
    
    data = {
        "name": "Constructora ABC Actualizada",
        "phone": "+57 300 111 2222",
        "website": "https://constructoraabc-actualizada.com"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/project-owners/{owner_id}", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Constructora actualizada exitosamente!")
            print(f"   Nombre: {result['name']}")
            print(f"   Teléfono: {result['phone']}")
            print(f"   Website: {result['website']}")
            return result
        else:
            print(f"❌ Error actualizando constructora: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def search_by_nit(nit):
    """Ejemplo de búsqueda por NIT"""
    print(f"\n🔍 Buscando constructora por NIT: {nit}...")
    
    try:
        response = requests.get(f"{BASE_URL}/project-owners/nit/{nit}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Constructora encontrada por NIT!")
            print(f"   Nombre: {result['name']}")
            print(f"   ID: {result['id']}")
            return result
        else:
            print(f"❌ Constructora no encontrada: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_validation_errors():
    """Prueba errores de validación"""
    print("\n🧪 Probando validaciones...")
    
    # Test NIT duplicado
    print("   Probando NIT duplicado...")
    data = {
        "name": "Constructora Duplicada",
        "nit": "900123456-7",  # NIT que ya existe
        "email": "duplicada@test.com",
        "city": "Bogotá",
        "country": "Colombia"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/project-owners", json=data)
        
        if response.status_code == 400:
            print("   ✅ Validación de NIT único funciona")
        else:
            print("   ❌ Debería haber fallado con NIT duplicado")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test email inválido
    print("   Probando email inválido...")
    data = {
        "name": "Constructora Test",
        "nit": "800987654-3",
        "email": "invalid-email",
        "city": "Cali",
        "country": "Colombia"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/project-owners", json=data)
        
        if response.status_code == 422:  # Validation error
            print("   ✅ Validación de email funciona")
        else:
            print("   ❌ Debería haber fallado con email inválido")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("🏗️ PROJECT OWNERS SERVICE - EJEMPLOS DE USO")
    print("="*50)
    
    # Verificar estado del servidor
    if not test_health_check():
        print("\n💡 Para ejecutar este ejemplo:")
        print("1. Asegúrate de que PostgreSQL esté ejecutándose")
        print("2. Configura DATABASE_URL en el archivo .env")
        print("3. Ejecuta: python main.py")
        return
    
    # Ejecutar ejemplos
    owner_id = create_project_owner()
    
    if owner_id:
        get_project_owner_by_id(owner_id)
        update_project_owner(owner_id)
        search_by_nit("900123456-7")
    
    get_project_owners()
    test_validation_errors()
    
    print("\n✅ Ejemplos completados!")

if __name__ == "__main__":
    main() 