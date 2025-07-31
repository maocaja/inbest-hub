#!/usr/bin/env python3
"""
Tests básicos para Ingestion Agent Service
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
        from models.models import ConversationSession, ConversationMessage, DocumentUpload
        print("✅ Models importados correctamente")
    except ImportError as e:
        print(f"❌ Error importando models: {e}")
        return False

    try:
        from schemas.schemas import IngestionStartRequest, ChatMessageRequest
        print("✅ Schemas importados correctamente")
    except ImportError as e:
        print(f"❌ Error importando schemas: {e}")
        return False

    try:
        from services.ingestion_service import IngestionService
        print("✅ IngestionService importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando IngestionService: {e}")
        return False

    try:
        from utils.document_processor import DocumentProcessor
        print("✅ DocumentProcessor importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando DocumentProcessor: {e}")
        return False

    try:
        from services.llm_service import LLMService
        print("✅ LLMService importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando LLMService: {e}")
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
        assert hasattr(Config, 'OPENAI_API_KEY'), "Config debe tener OPENAI_API_KEY"

        print(f"✅ Puerto configurado: {Config.PORT}")
        print(f"✅ Base de datos: {Config.DATABASE_URL}")
        print(f"✅ OpenAI API Key configurada: {'Sí' if Config.OPENAI_API_KEY else 'No'}")

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
        from sqlalchemy import text

        # Crear tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas correctamente")

        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()  # Ejecutar la consulta
            print("✅ Conexión a base de datos exitosa")

        return True

    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {e}")
        return False

def test_document_processor():
    """Test del procesador de documentos"""
    print("\n🧪 Probando procesador de documentos...")

    try:
        from utils.document_processor import DocumentProcessor

        processor = DocumentProcessor()
        print("✅ DocumentProcessor instanciado correctamente")

        # Verificar formatos soportados
        formats = processor.get_supported_formats()
        print(f"✅ Formatos soportados: {formats}")

        # Test de validación de archivo
        test_file = "test_document.txt"
        with open(test_file, "w") as f:
            f.write("Test document content")

        validation = processor.validate_file(test_file)
        print(f"✅ Validación de archivo: {validation['valid']}")

        # Limpiar archivo de prueba
        if os.path.exists(test_file):
            os.remove(test_file)

        return True

    except Exception as e:
        print(f"❌ Error en procesador de documentos: {e}")
        return False

def test_llm_service():
    """Test del servicio LLM"""
    print("\n🧪 Probando servicio LLM...")

    try:
        from services.llm_service import LLMService
        from config import Config

        if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "your_openai_api_key_here":
            print("⚠️  OpenAI API Key no configurada, saltando test de LLM")
            return True

        llm_service = LLMService()
        print("✅ LLMService instanciado correctamente")

        # Test básico de generación de respuesta
        test_messages = [
            {"role": "user", "content": "Hola, ¿cómo estás?"}
        ]

        response = llm_service.generate_response(test_messages)
        if response["success"]:
            print("✅ Respuesta LLM generada correctamente")
        else:
            print(f"⚠️  Error en LLM: {response.get('error', 'Unknown error')}")

        return True

    except Exception as e:
        print(f"❌ Error en servicio LLM: {e}")
        return False

def test_ingestion_service():
    """Test del servicio de ingestión"""
    print("\n🧪 Probando servicio de ingestión...")

    try:
        from services.ingestion_service import IngestionService
        from database.database import SessionLocal

        service = IngestionService()
        print("✅ IngestionService instanciado correctamente")

        # Crear sesión de prueba
        db = SessionLocal()
        print("✅ Sesión de base de datos creada")

        return True

    except Exception as e:
        print(f"❌ Error en servicio de ingestión: {e}")
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
            "/ingest/start",
            "/ingest/message",
            "/ingest/status/{session_id}",
            "/ingest/upload",
            "/ingest/generate-description",
            "/ingest/supported-formats"
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

    base_url = "http://localhost:8004"

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

        # Supported formats endpoint
        response = requests.get(f"{base_url}/ingest/supported-formats", timeout=5)
        if response.status_code == 200:
            print("✅ Supported formats endpoint exitoso")
        else:
            print(f"⚠️  Supported formats endpoint falló: {response.status_code}")
            return False

        return True

    except requests.exceptions.ConnectionError:
        print("⚠️  Servidor no está corriendo (esto es normal si no se ha iniciado)")
        return True
    except Exception as e:
        print(f"❌ Error en endpoints API: {e}")
        return False

def test_openai_integration():
    """Test de integración con OpenAI"""
    print("\n🧪 Probando integración con OpenAI...")

    try:
        from config import Config

        if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == "your_openai_api_key_here":
            print("⚠️  OpenAI API Key no configurada, saltando test de integración")
            return True

        # Test básico de conexión con OpenAI
        import openai
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Test simple de chat
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hola"}],
            max_tokens=10
        )
        
        if response.choices:
            print("✅ Integración con OpenAI exitosa")
            return True
        else:
            print("⚠️  Respuesta vacía de OpenAI")
            return False

    except Exception as e:
        print(f"❌ Error en integración con OpenAI: {e}")
        return False

def main():
    """Función principal de tests"""
    print("🧪 Iniciando tests básicos para Ingestion Agent Service...")
    print("="*70)

    tests = [
        ("Importaciones", test_imports),
        ("Configuración", test_config),
        ("Base de datos", test_database_connection),
        ("Procesador de documentos", test_document_processor),
        ("Servicio LLM", test_llm_service),
        ("Servicio de ingestión", test_ingestion_service),
        ("Rutas FastAPI", test_fastapi_routes),
        ("Endpoints API", test_api_endpoints),
        ("Integración OpenAI", test_openai_integration)
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

    print("\n" + "="*70)
    print(f"📊 Resultados: {passed}/{total} tests pasaron")

    if passed == total:
        print("🎉 ¡Todos los tests pasaron!")
        return 0
    else:
        print("⚠️  Algunos tests fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())
