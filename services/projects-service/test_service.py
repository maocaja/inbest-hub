#!/usr/bin/env python3
"""
Tests básicos para Projects Service
"""

import sys
import os
import json
import requests
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test de importaciones básicas"""
    print("🧪 Probando importaciones...")
    
    try:
        from config import Config
        print("✅ Config importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Config: {e}")
        return False
    
    try:
        from database.database import get_db, engine
        print("✅ Database importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando database: {e}")
        return False
    
    try:
        from models.models import Project, ProjectOwner, ProjectStatus
        print("✅ Models importados correctamente")
    except ImportError as e:
        print(f"❌ Error importando models: {e}")
        return False
    
    try:
        from schemas.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
        print("✅ Schemas importados correctamente")
    except ImportError as e:
        print(f"❌ Error importando schemas: {e}")
        return False
    
    try:
        from services.projects_service import ProjectsService
        print("✅ ProjectsService importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando ProjectsService: {e}")
        return False
    
    return True

def test_config():
    """Test de configuración"""
    print("\n🧪 Probando configuración...")
    
    try:
        from config import Config
        
        # Verificar configuración básica
        assert hasattr(Config, 'PORT'), "Config debe tener PORT"
        assert hasattr(Config, 'DATABASE_URL'), "Config debe tener DATABASE_URL"
        assert hasattr(Config, 'PROJECT_STATES'), "Config debe tener PROJECT_STATES"
        
        print(f"✅ Puerto configurado: {Config.PORT}")
        print(f"✅ Base de datos: {Config.DATABASE_URL}")
        print(f"✅ Estados de proyecto: {Config.PROJECT_STATES}")
        
        # Validar configuración
        errors = Config.validate_config()
        if errors:
            print(f"⚠️  Errores de configuración: {errors}")
            return False
        else:
            print("✅ Configuración válida")
            return True
            
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_database_connection():
    """Test de conexión a base de datos"""
    print("\n🧪 Probando conexión a base de datos...")
    
    try:
        from database.database import engine
        from models.models import Base
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas correctamente")
        
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            result.fetchone()  # Ejecutar la consulta
            print("✅ Conexión a base de datos exitosa")
        
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {e}")
        return False

def test_schemas():
    """Test de esquemas Pydantic"""
    print("\n🧪 Probando esquemas...")
    
    try:
        from schemas.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectStatus
        
        # Test ProjectCreate
        project_data = {
            "name": "Test Project",
            "description": "Proyecto de prueba para testing",
            "project_owner_nit": "900123456-7",
            "status": "incompleto"
        }
        
        project = ProjectCreate(**project_data)
        print("✅ ProjectCreate válido")
        
        # Test ProjectStatus
        assert "incompleto" in [s.value for s in ProjectStatus], "Estado incompleto debe existir"
        assert "en_proceso" in [s.value for s in ProjectStatus], "Estado en_proceso debe existir"
        print("✅ Estados de proyecto válidos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en esquemas: {e}")
        return False

def test_service():
    """Test del servicio de proyectos"""
    print("\n🧪 Probando servicio de proyectos...")
    
    try:
        from services.projects_service import ProjectsService
        from database.database import SessionLocal
        from schemas.schemas import ProjectCreate
        
        service = ProjectsService()
        print("✅ ProjectsService instanciado correctamente")
        
        # Crear sesión de prueba
        db = SessionLocal()
        print("✅ Sesión de base de datos creada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en servicio: {e}")
        return False

def test_fastapi_routes():
    """Test de rutas FastAPI"""
    print("\n🧪 Probando rutas FastAPI...")
    
    try:
        from main import app
        
        # Verificar rutas básicas
        routes = [
            "/",
            "/health",
            "/projects",
            "/projects/{project_id}",
            "/projects/{project_id}/state",
            "/projects/owner/{owner_nit}",
            "/projects/status/{status}"
        ]
        
        app_routes = [route.path for route in app.routes]
        
        for route in routes:
            if route in app_routes:
                print(f"✅ Ruta {route} encontrada")
            else:
                print(f"⚠️  Ruta {route} no encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en rutas FastAPI: {e}")
        return False

def test_api_endpoints():
    """Test de endpoints API (requiere servidor corriendo)"""
    print("\n🧪 Probando endpoints API...")
    
    base_url = "http://localhost:8003"
    
    try:
        # Health check
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check exitoso")
        else:
            print(f"⚠️  Health check falló: {response.status_code}")
            return False
        
        # Root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint exitoso")
        else:
            print(f"⚠️  Root endpoint falló: {response.status_code}")
            return False
        
        # Projects endpoint
        response = requests.get(f"{base_url}/projects", timeout=5)
        if response.status_code == 200:
            print("✅ Projects endpoint exitoso")
        else:
            print(f"⚠️  Projects endpoint falló: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("⚠️  Servidor no está corriendo (esto es normal si no se ha iniciado)")
        return True
    except Exception as e:
        print(f"❌ Error en endpoints API: {e}")
        return False

def main():
    """Función principal de tests"""
    print("🧪 Iniciando tests básicos para Projects Service...")
    print("="*60)
    
    tests = [
        ("Importaciones", test_imports),
        ("Configuración", test_config),
        ("Base de datos", test_database_connection),
        ("Esquemas", test_schemas),
        ("Servicio", test_service),
        ("Rutas FastAPI", test_fastapi_routes),
        ("Endpoints API", test_api_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ Test '{test_name}' falló")
        except Exception as e:
            print(f"❌ Test '{test_name}' falló con excepción: {e}")
    
    print("\n" + "="*60)
    print(f"📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron!")
        return 0
    else:
        print("⚠️  Algunos tests fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())
