#!/usr/bin/env python3
"""
Script de configuración automática para Ingestion Agent Service
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Verificar versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")

def check_pip():
    """Verificar que pip esté disponible"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      check=True, capture_output=True)
        print("✅ pip detectado")
    except subprocess.CalledProcessError:
        print("❌ Error: pip no está disponible")
        sys.exit(1)

def create_directories():
    """Crear directorios necesarios"""
    directories = [
        "uploads",
        "logs",
        "tests",
        "examples"
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directorio {directory} creado/verificado")

def install_dependencies():
    """Instalar dependencias"""
    print("📦 Instalando dependencias...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        sys.exit(1)

def create_env_file():
    """Crear archivo .env si no existe"""
    env_file = Path(".env")
    env_example = Path("env.example")

    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Archivo .env creado desde env.example")
            print("⚠️  IMPORTANTE: Configura tu OPENAI_API_KEY en el archivo .env")
        else:
            print("⚠️  No se encontró env.example, creando .env básico")
            with open(env_file, "w") as f:
                f.write("# Ingestion Agent Service Configuration\n")
                f.write("PORT=8004\n")
                f.write("HOST=0.0.0.0\n")
                f.write("DEBUG=True\n")
                f.write("RELOAD=True\n")
                f.write("LOG_LEVEL=INFO\n")
                f.write("DATABASE_URL=sqlite:///./ingestion_agent.db\n")
                f.write("ENVIRONMENT=development\n")
                f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
                f.write("PROJECT_OWNERS_SERVICE_URL=http://localhost:8002\n")
                f.write("PROJECTS_SERVICE_URL=http://localhost:8003\n")
            print("✅ Archivo .env básico creado")
            print("⚠️  IMPORTANTE: Configura tu OPENAI_API_KEY en el archivo .env")
    else:
        print("✅ Archivo .env ya existe")

def check_openai_config():
    """Verificar configuración de OpenAI"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            content = f.read()
            if "OPENAI_API_KEY" in content:
                if "your_openai_api_key_here" in content:
                    print("⚠️  OPENAI_API_KEY no configurada - configúrala en .env")
                else:
                    print("✅ OPENAI_API_KEY configurada")
            else:
                print("⚠️  OPENAI_API_KEY no encontrada en .env")
    else:
        print("⚠️  Archivo .env no encontrado")

def check_external_services():
    """Verificar servicios externos"""
    print("🔍 Verificando servicios externos...")
    
    services = [
        ("Project Owners Service", "http://localhost:8002/health"),
        ("Projects Service", "http://localhost:8003/health")
    ]
    
    import requests
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} disponible")
            else:
                print(f"⚠️  {service_name} no responde correctamente")
        except requests.exceptions.ConnectionError:
            print(f"⚠️  {service_name} no disponible (esto es normal si no está corriendo)")
        except Exception as e:
            print(f"⚠️  Error verificando {service_name}: {e}")

def run_tests():
    """Ejecutar tests básicos"""
    print("🧪 Ejecutando tests básicos...")
    try:
        subprocess.run([sys.executable, "test_service.py"], check=True)
        print("✅ Tests ejecutados correctamente")
    except subprocess.CalledProcessError:
        print("⚠️  Algunos tests fallaron (esto es normal en la primera ejecución)")
    except FileNotFoundError:
        print("⚠️  Archivo test_service.py no encontrado")

def display_usage():
    """Mostrar instrucciones de uso"""
    print("\n" + "="*60)
    print("🤖 Ingestion Agent Service - Configuración Completada")
    print("="*60)
    print("\n📋 Para ejecutar el servicio:")
    print("   python main.py")
    print("\n📋 Para ejecutar con uvicorn:")
    print("   uvicorn main:app --host 0.0.0.0 --port 8004 --reload")
    print("\n📋 Para ver la documentación API:")
    print("   http://localhost:8004/docs")
    print("\n📋 Para health check:")
    print("   curl http://localhost:8004/health")
    print("\n📋 Para iniciar una sesión de ingestión:")
    print("   curl -X POST http://localhost:8004/ingest/start \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "project_owner_nit": "900123456-7",')
    print('       "user_name": "Asesor Ejemplo"')
    print("     }'")
    print("\n📋 Para enviar un mensaje:")
    print("   curl -X POST http://localhost:8004/ingest/message \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "session_id": "tu_session_id",')
    print('       "message": "Hola, quiero crear un proyecto"')
    print("     }'")
    print("\n📋 Para subir un documento:")
    print("   curl -X POST http://localhost:8004/ingest/upload \\")
    print("     -F 'session_id=tu_session_id' \\")
    print("     -F 'file=@documento.pdf'")
    print("\n📋 Para obtener formatos soportados:")
    print("   curl http://localhost:8004/ingest/supported-formats")
    print("\n" + "="*60)
    print("⚠️  IMPORTANTE: Asegúrate de configurar OPENAI_API_KEY en .env")
    print("="*60)

def main():
    """Función principal"""
    print("🤖 Configurando Ingestion Agent Service...")
    print("="*60)

    # Verificaciones básicas
    check_python_version()
    check_pip()

    # Crear estructura
    create_directories()

    # Instalar dependencias
    install_dependencies()

    # Configurar entorno
    create_env_file()
    check_openai_config()

    # Verificar servicios externos
    check_external_services()

    # Ejecutar tests
    run_tests()

    # Mostrar instrucciones
    display_usage()

if __name__ == "__main__":
    main()
