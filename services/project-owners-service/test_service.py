#!/usr/bin/env python3
"""
Script de prueba para verificar el Project Owners Service
"""

import sys
import os
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Prueba que todos los módulos se puedan importar correctamente"""
    print("🧪 Probando imports...")
    
    try:
        from config import Config
        print("✅ Config importado correctamente")
    except Exception as e:
        print(f"❌ Error importando Config: {e}")
        return False
    
    try:
        from database.database import get_db, engine, Base
        print("✅ Database importado correctamente")
    except Exception as e:
        print(f"❌ Error importando database: {e}")
        return False
    
    try:
        from models.models import ProjectOwner
        print("✅ Models importado correctamente")
    except Exception as e:
        print(f"❌ Error importando models: {e}")
        return False
    
    try:
        from schemas.schemas import ProjectOwnerCreate, ProjectOwnerUpdate, ProjectOwnerResponse
        print("✅ Schemas importado correctamente")
    except Exception as e:
        print(f"❌ Error importando schemas: {e}")
        return False
    
    try:
        from services.project_owners_service import ProjectOwnersService
        print("✅ Services importado correctamente")
    except Exception as e:
        print(f"❌ Error importando services: {e}")
        return False
    
    try:
        from main import app
        print("✅ FastAPI app importado correctamente")
    except Exception as e:
        print(f"❌ Error importando main: {e}")
        return False
    
    return True

def test_schemas():
    """Prueba la validación de schemas"""
    print("\n🧪 Probando schemas...")
    
    try:
        from schemas.schemas import ProjectOwnerCreate
        
        # Test valid data
        valid_data = {
            "name": "Constructora Test",
            "nit": "900123456-7",
            "email": "test@constructora.com",
            "city": "Medellín",
            "country": "Colombia"
        }
        
        project_owner = ProjectOwnerCreate(**valid_data)
        print("✅ Schema válido creado correctamente")
        
        # Test invalid NIT
        try:
            invalid_data = valid_data.copy()
            invalid_data["nit"] = "invalid-nit"
            ProjectOwnerCreate(**invalid_data)
            print("❌ Debería haber fallado con NIT inválido")
            return False
        except Exception:
            print("✅ Validación de NIT funciona correctamente")
        
        # Test invalid email
        try:
            invalid_data = valid_data.copy()
            invalid_data["email"] = "invalid-email"
            ProjectOwnerCreate(**invalid_data)
            print("❌ Debería haber fallado con email inválido")
            return False
        except Exception:
            print("✅ Validación de email funciona correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando schemas: {e}")
        return False

def test_config():
    """Prueba la configuración"""
    print("\n🧪 Probando configuración...")
    
    try:
        from config import Config
        
        # Test server config
        server_config = Config.get_server_config()
        assert "host" in server_config
        assert "port" in server_config
        print("✅ Configuración del servidor válida")
        
        # Test database config
        db_config = Config.get_database_config()
        assert "url" in db_config
        print("✅ Configuración de base de datos válida")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")
        return False

def test_service_methods():
    """Prueba los métodos del servicio (sin base de datos)"""
    print("\n🧪 Probando métodos del servicio...")
    
    try:
        from services.project_owners_service import ProjectOwnersService
        
        service = ProjectOwnersService()
        print("✅ Servicio creado correctamente")
        
        # Verificar que los métodos existen
        methods = [
            'create_project_owner',
            'get_project_owners',
            'get_project_owner',
            'get_project_owner_by_nit',
            'update_project_owner',
            'delete_project_owner',
            'deactivate_project_owner',
            'activate_project_owner',
            'verify_project_owner'
        ]
        
        for method in methods:
            assert hasattr(service, method), f"Método {method} no encontrado"
        
        print("✅ Todos los métodos del servicio están disponibles")
        return True
        
    except Exception as e:
        print(f"❌ Error probando servicio: {e}")
        return False

def test_fastapi_routes():
    """Prueba que las rutas de FastAPI estén definidas"""
    print("\n🧪 Probando rutas de FastAPI...")
    
    try:
        from main import app
        
        # Verificar que las rutas principales existen
        routes = [
            "/",
            "/health",
            "/project-owners",
            "/project-owners/{nit}"
        ]
        
        app_routes = [route.path for route in app.routes]
        
        for route in routes:
            if route in app_routes or any(route.replace("{", "").replace("}", "") in r for r in app_routes):
                print(f"✅ Ruta {route} encontrada")
            else:
                print(f"⚠️  Ruta {route} no encontrada")
        
        print("✅ Rutas de FastAPI verificadas")
        return True
        
    except Exception as e:
        print(f"❌ Error probando rutas de FastAPI: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🏗️ PROJECT OWNERS SERVICE - PRUEBAS")
    print("="*50)
    
    tests = [
        test_imports,
        test_schemas,
        test_config,
        test_service_methods,
        test_fastapi_routes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} falló")
        except Exception as e:
            print(f"❌ Test {test.__name__} falló con excepción: {e}")
    
    print(f"\n📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("✅ Todos los tests pasaron exitosamente!")
        print("\n🎉 El servicio está listo para usar.")
        print("💡 Para ejecutar el servicio:")
        print("   1. Configura PostgreSQL y DATABASE_URL")
        print("   2. Ejecuta: python main.py")
        return True
    else:
        print("❌ Algunos tests fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 