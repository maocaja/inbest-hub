#!/usr/bin/env python3
"""
Script de configuración para Media Service
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Error: {e.stderr}")
        return False

def create_directories():
    """Crea los directorios necesarios"""
    directories = [
        "uploads",
        "uploads/image",
        "uploads/document",
        "uploads/image/thumbnails",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio creado: {directory}")

def install_dependencies():
    """Instala las dependencias"""
    return run_command("pip install -r requirements.txt", "Instalando dependencias")

def create_env_file():
    """Crea el archivo .env si no existe"""
    if not os.path.exists(".env"):
        shutil.copy("env.example", ".env")
        print("✅ Archivo .env creado desde env.example")
    else:
        print("ℹ️  Archivo .env ya existe")

def test_database():
    """Prueba la conexión a la base de datos"""
    try:
        from database.database import engine
        from models.models import Base
        from sqlalchemy import text
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("✅ Conexión a base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {e}")
        return False

def main():
    """Función principal de configuración"""
    print("🚀 Configurando Media Service...")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    # Crear directorios
    create_directories()
    
    # Instalar dependencias
    if not install_dependencies():
        print("❌ Error instalando dependencias")
        sys.exit(1)
    
    # Crear archivo .env
    create_env_file()
    
    # Probar base de datos
    if not test_database():
        print("❌ Error configurando base de datos")
        sys.exit(1)
    
    print("\n🎉 ¡Configuración completada exitosamente!")
    print("\n📋 Para iniciar el servicio:")
    print("   python main.py")
    print("\n📋 Para ver la documentación:")
    print("   http://localhost:8005/docs")
    print("\n📋 Para health check:")
    print("   http://localhost:8005/health")

if __name__ == "__main__":
    main() 