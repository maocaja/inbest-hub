#!/usr/bin/env python3
"""
Script de configuración para el Real Estate Data Extractor Agent
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Verifica la versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def check_pip():
    """Verifica que pip esté disponible"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✅ pip disponible - OK")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip no está disponible")
        return False

def install_dependencies():
    """Instala las dependencias del proyecto"""
    print("\n📦 Instalando dependencias...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def create_env_file():
    """Crea el archivo .env si no existe"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ Archivo .env ya existe")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Archivo .env creado desde env.example")
        print("💡 Recuerda configurar tu OPENAI_API_KEY en el archivo .env")
        return True
    else:
        print("❌ No se encontró env.example")
        return False

def check_openai_key():
    """Verifica si la API key de OpenAI está configurada"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key_here":
        print("✅ OPENAI_API_KEY configurada")
        return True
    else:
        print("⚠️  OPENAI_API_KEY no está configurada")
        print("   Edita el archivo .env y agrega tu API key de OpenAI")
        return False

def run_tests():
    """Ejecuta los tests del proyecto"""
    print("\n🧪 Ejecutando tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "-v"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tests pasaron correctamente")
            return True
        else:
            print("⚠️  Algunos tests fallaron:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        return False

def create_directories():
    """Crea directorios necesarios"""
    directories = [
        "logs",
        "uploads",
        "exports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directorios creados")

def show_usage_instructions():
    """Muestra instrucciones de uso"""
    print("\n" + "="*50)
    print("🚀 CONFIGURACIÓN COMPLETADA")
    print("="*50)
    
    print("\n📋 Para usar el agente:")
    print("1. Configura tu API key de OpenAI en el archivo .env")
    print("2. Ejecuta el servidor:")
    print("   python main.py")
    print("3. El agente estará disponible en: http://localhost:8012")
    
    print("\n📚 Documentación:")
    print("- README.md: Documentación completa")
    print("- examples/example_usage.py: Ejemplos de uso")
    
    print("\n🔧 Endpoints disponibles:")
    print("- POST /extract: Extraer datos de documentos")
    print("- POST /validate: Validar datos del proyecto")
    print("- POST /complete: Completar información faltante")
    print("- GET /schema: Obtener esquema JSON")
    print("- GET /health: Verificar estado del servidor")
    
    print("\n💡 Próximos pasos:")
    print("1. Configura tu OPENAI_API_KEY en .env")
    print("2. Ejecuta: python main.py")
    print("3. Prueba con: python examples/example_usage.py")

def main():
    """Función principal del setup"""
    print("🏠 REAL ESTATE DATA EXTRACTOR AGENT - SETUP")
    print("="*50)
    
    # Verificar requisitos básicos
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Crear directorios
    create_directories()
    
    # Instalar dependencias
    if not install_dependencies():
        return False
    
    # Crear archivo .env
    if not create_env_file():
        return False
    
    # Verificar configuración
    check_openai_key()
    
    # Ejecutar tests
    run_tests()
    
    # Mostrar instrucciones
    show_usage_instructions()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup falló. Revisa los errores arriba.")
        sys.exit(1)
    else:
        print("\n✅ Setup completado exitosamente!") 