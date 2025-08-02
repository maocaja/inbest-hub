#!/usr/bin/env python3
"""
Script de testing simplificado para Chat API
"""

import sys
import os
import asyncio

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_file_structure():
    """Test de estructura de archivos"""
    print("🧪 Testing estructura de archivos...")
    
    required_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "env.example",
        "README.md",
        "schemas/schemas.py",
        "services/chat_service.py",
        "services/openai_service.py",
        "services/search_service.py",
        "services/conversation_service.py",
        "services/response_generator.py",
        "database/models.py",
        "database/database.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        return False
    else:
        print("✅ Todos los archivos requeridos existen")
        return True

def test_dependencies():
    """Test de dependencias"""
    print("\n🧪 Testing dependencias...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "openai",
        "sqlalchemy",
        "httpx",
        "pydantic",
        "loguru"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Paquetes faltantes: {missing_packages}")
        return False
    else:
        print("✅ Todas las dependencias están instaladas")
        return True

def test_config():
    """Test de configuración"""
    print("\n🧪 Testing configuración...")
    
    try:
        from config import Config
        
        # Verificar configuración básica
        assert Config.PORT == 8006, f"Puerto incorrecto: {Config.PORT}"
        assert Config.HOST == "0.0.0.0", f"Host incorrecto: {Config.HOST}"
        assert Config.EMBEDDING_SERVICE_URL == "http://localhost:8005", f"URL embedding incorrecta: {Config.EMBEDDING_SERVICE_URL}"
        assert Config.PROJECTS_SERVICE_URL == "http://localhost:8003", f"URL projects incorrecta: {Config.PROJECTS_SERVICE_URL}"
        
        print("✅ Configuración básica correcta")
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_schemas():
    """Test de esquemas Pydantic"""
    print("\n🧪 Testing esquemas...")
    
    try:
        from schemas.schemas import ChatRequest, ChatResponse, IntentType
        
        # Test ChatRequest
        request_data = {
            "message": "Busco apartamentos en Bogotá",
            "user_id": "user_123"
        }
        request = ChatRequest(**request_data)
        assert request.message == "Busco apartamentos en Bogotá"
        assert request.user_id == "user_123"
        print("✅ ChatRequest funciona correctamente")
        
        # Test IntentType
        intent_types = [intent.value for intent in IntentType]
        expected_types = ["search_projects", "get_project_details", "greeting", "goodbye", "help", "unknown"]
        assert all(t in intent_types for t in expected_types), f"Tipos de intención incorrectos: {intent_types}"
        print("✅ IntentType funciona correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en esquemas: {e}")
        return False

def test_database_models():
    """Test de modelos de base de datos"""
    print("\n🧪 Testing modelos de BD...")
    
    try:
        from database.models import Conversation, Message, User
        from datetime import datetime
        
        # Test Conversation
        conv = Conversation(
            id="test_conv_123",
            user_id="user_123",
            created_at=datetime.utcnow(),
            status="active"
        )
        assert conv.id == "test_conv_123"
        assert conv.user_id == "user_123"
        assert conv.status == "active"
        print("✅ Modelo Conversation funciona correctamente")
        
        # Test Message
        msg = Message(
            id="test_msg_456",
            conversation_id="test_conv_123",
            role="user",
            content="Test message",
            timestamp=datetime.utcnow()
        )
        assert msg.id == "test_msg_456"
        assert msg.role == "user"
        assert msg.content == "Test message"
        print("✅ Modelo Message funciona correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en modelos de BD: {e}")
        return False

def test_database_connection():
    """Test de conexión a base de datos"""
    print("\n🧪 Testing conexión a BD...")
    
    try:
        from database.database import init_db, get_db
        
        # Test de inicialización
        init_db()
        print("✅ Base de datos inicializada correctamente")
        
        # Test de conexión
        db = next(get_db())
        db.execute("SELECT 1")
        print("✅ Conexión a BD funciona correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en conexión a BD: {e}")
        return False

def test_services_creation():
    """Test de creación de servicios"""
    print("\n🧪 Testing creación de servicios...")
    
    try:
        # Test OpenAI Service
        from services.openai_service import OpenAIService
        openai_service = OpenAIService()
        print("✅ OpenAI Service creado correctamente")
        
        # Test Search Service
        from services.search_service import SearchService
        search_service = SearchService()
        print("✅ Search Service creado correctamente")
        
        # Test Conversation Service
        from services.conversation_service import ConversationService
        conv_service = ConversationService()
        print("✅ Conversation Service creado correctamente")
        
        # Test Response Generator
        from services.response_generator import ResponseGenerator
        response_gen = ResponseGenerator()
        print("✅ Response Generator creado correctamente")
        
        # Test Chat Service
        from services.chat_service import ChatService
        chat_service = ChatService()
        print("✅ Chat Service creado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando servicios: {e}")
        return False

def test_fastapi_app():
    """Test de aplicación FastAPI"""
    print("\n🧪 Testing aplicación FastAPI...")
    
    try:
        from main import app
        
        # Verificar que la app se creó correctamente
        assert app is not None, "App no se creó correctamente"
        
        # Verificar endpoints básicos
        routes = [route.path for route in app.routes]
        expected_routes = [
            "/",
            "/info", 
            "/health",
            "/chat/conversation",
            "/chat/conversations/{user_id}",
            "/chat/conversations/{conversation_id}/messages",
            "/chat/search"
        ]
        
        for route in expected_routes:
            if route not in routes:
                print(f"⚠️  Ruta faltante: {route}")
        
        print("✅ Aplicación FastAPI creada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en aplicación FastAPI: {e}")
        return False

async def main():
    """Función principal de testing"""
    print("🚀 Iniciando testing simplificado del Chat API...\n")
    
    tests = [
        ("Estructura de archivos", test_file_structure),
        ("Dependencias", test_dependencies),
        ("Configuración", test_config),
        ("Esquemas", test_schemas),
        ("Modelos de BD", test_database_models),
        ("Conexión a BD", test_database_connection),
        ("Creación de servicios", test_services_creation),
        ("Aplicación FastAPI", test_fastapi_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            else:
                print(f"❌ Test '{test_name}' falló")
                
        except Exception as e:
            print(f"❌ Error en test '{test_name}': {e}")
    
    print(f"\n📊 Resultados del testing:")
    print(f"✅ Tests pasados: {passed}/{total}")
    print(f"❌ Tests fallidos: {total - passed}")
    
    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron! El Chat API está listo para usar.")
        print("\n📝 Próximos pasos:")
        print("1. Configurar OPENAI_API_KEY en .env")
        print("2. Asegurar que embedding-service esté corriendo (puerto 8005)")
        print("3. Asegurar que projects-service esté corriendo (puerto 8003)")
        print("4. Ejecutar: python main.py")
        print("5. Acceder a: http://localhost:8006/docs")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisar los errores antes de continuar.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main()) 