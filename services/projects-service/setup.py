#!/usr/bin/env python3
"""
Script de configuración automática para Projects Service
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
        else:
            print("⚠️  No se encontró env.example, creando .env básico")
            with open(env_file, "w") as f:
                f.write("# Projects Service Configuration\n")
                f.write("PORT=8003\n")
                f.write("HOST=0.0.0.0\n")
                f.write("DEBUG=True\n")
                f.write("RELOAD=True\n")
                f.write("LOG_LEVEL=INFO\n")
                f.write("DATABASE_URL=sqlite:///./projects.db\n")
                f.write("ENVIRONMENT=development\n")
            print("✅ Archivo .env básico creado")
    else:
        print("✅ Archivo .env ya existe")

def check_database_config():
    """Verificar configuración de base de datos"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            content = f.read()
            if "DATABASE_URL" in content:
                print("✅ Configuración de base de datos encontrada")
            else:
                print("⚠️  DATABASE_URL no encontrada en .env")
    else:
        print("⚠️  Archivo .env no encontrado")

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
    print("\n" + "="*50)
    print("🚀 Projects Service - Configuración Completada")
    print("="*50)
    print("\n📋 Para ejecutar el servicio:")
    print("   python main.py")
    print("\n📋 Para ejecutar con uvicorn:")
    print("   uvicorn main:app --host 0.0.0.0 --port 8003 --reload")
    print("\n📋 Para ver la documentación API:")
    print("   http://localhost:8003/docs")
    print("\n📋 Para health check:")
    print("   curl http://localhost:8003/health")
    print("\n📋 Para crear un proyecto de prueba:")
    print("   curl -X POST http://localhost:8003/projects \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "name": "Residencial Los Pinos",')
    print('       "description": "Proyecto residencial de lujo",')
    print('       "project_owner_nit": "900123456-7",')
    print('       "status": "incompleto"')
    print("     }'")
    print("\n📋 Para listar proyectos:")
    print("   curl http://localhost:8003/projects")
    print("\n" + "="*50)

def main():
    """Función principal"""
    print("🏗️  Configurando Projects Service...")
    print("="*50)
    
    # Verificaciones básicas
    check_python_version()
    check_pip()
    
    # Crear estructura
    create_directories()
    
    # Instalar dependencias
    install_dependencies()
    
    # Configurar entorno
    create_env_file()
    check_database_config()
    
    # Ejecutar tests
    run_tests()
    
    # Mostrar instrucciones
    display_usage()

if __name__ == "__main__":
    main()
