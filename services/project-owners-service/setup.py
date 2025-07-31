#!/usr/bin/env python3
"""
Script de configuración para el Project Owners Service
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
        print("💡 Recuerda configurar tu DATABASE_URL en el archivo .env")
        return True
    else:
        print("❌ No se encontró env.example")
        return False

def check_database_config():
    """Verifica si la configuración de base de datos está configurada"""
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url != "postgresql://postgres:password@localhost:5432/project_owners_db":
        print("✅ DATABASE_URL configurada")
        return True
    else:
        print("⚠️  DATABASE_URL no está configurada")
        print("   Edita el archivo .env y configura tu conexión a PostgreSQL")
        return False

def create_directories():
    """Crea directorios necesarios"""
    directories = [
        "logs",
        "migrations"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directorios creados")

def show_usage_instructions():
    """Muestra instrucciones de uso"""
    print("\n" + "="*50)
    print("🚀 CONFIGURACIÓN COMPLETADA")
    print("="*50)
    
    print("\n📋 Para usar el servicio:")
    print("1. Configura tu DATABASE_URL en el archivo .env")
    print("2. Asegúrate de que PostgreSQL esté ejecutándose")
    print("3. Ejecuta el servidor:")
    print("   python main.py")
    print("4. El servicio estará disponible en: http://localhost:8001")
    
    print("\n📚 Documentación:")
    print("- README.md: Documentación completa")
    print("- /docs: Documentación de API")
    
    print("\n🔧 Endpoints disponibles:")
    print("- POST /project-owners: Crear constructora")
    print("- GET /project-owners: Listar constructoras")
    print("- GET /project-owners/{id}: Obtener constructora")
    print("- PUT /project-owners/{id}: Actualizar constructora")
    print("- DELETE /project-owners/{id}: Eliminar constructora")
    print("- GET /project-owners/nit/{nit}: Buscar por NIT")
    print("- GET /health: Verificar estado del servidor")
    
    print("\n💡 Próximos pasos:")
    print("1. Configura tu DATABASE_URL en .env")
    print("2. Ejecuta: python main.py")
    print("3. Prueba los endpoints con curl o Postman")

def main():
    """Función principal del setup"""
    print("🏗️ PROJECT OWNERS SERVICE - SETUP")
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
    check_database_config()
    
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