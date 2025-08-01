#!/usr/bin/env python3
"""
Script de testing básico para Media Service
"""

import requests
import json
import os
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8005"
TEST_IMAGE_PATH = "test_image.jpg"
TEST_PDF_PATH = "test_document.pdf"

def create_test_files():
    """Crea archivos de prueba"""
    print("🔄 Creando archivos de prueba...")
    
    # Crear imagen de prueba usando PIL
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Crear imagen de prueba
        img = Image.new('RGB', (300, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Agregar texto
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((10, 10), "Test Image", fill='black', font=font)
        draw.text((10, 50), "Media Service", fill='blue', font=font)
        draw.text((10, 90), "Testing", fill='red', font=font)
        
        img.save(TEST_IMAGE_PATH)
        print(f"✅ Imagen de prueba creada: {TEST_IMAGE_PATH}")
        
    except ImportError:
        print("⚠️  PIL no disponible, creando imagen simple...")
        # Crear archivo de imagen simple
        with open(TEST_IMAGE_PATH, 'wb') as f:
            # Header de imagen PNG simple
            f.write(b'\x89PNG\r\n\x1a\n')
    
    # Crear PDF de prueba usando reportlab
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(TEST_PDF_PATH, pagesize=letter)
        c.drawString(100, 750, "Test Document")
        c.drawString(100, 700, "Media Service Testing")
        c.drawString(100, 650, "This is a test PDF file")
        c.save()
        print(f"✅ PDF de prueba creado: {TEST_PDF_PATH}")
        
    except ImportError:
        print("⚠️  reportlab no disponible, creando PDF simple...")
        # Crear archivo PDF simple
        with open(TEST_PDF_PATH, 'wb') as f:
            # Header de PDF simple
            f.write(b'%PDF-1.4\n')

def test_health_check():
    """Prueba el health check"""
    print("\n🔄 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check exitoso: {data['status']}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servicio")
        return False

def test_supported_formats():
    """Prueba el endpoint de formatos soportados"""
    print("\n🔄 Probando formatos soportados...")
    try:
        response = requests.get(f"{BASE_URL}/supported-formats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Formatos soportados obtenidos:")
            print(f"   - Imágenes: {len(data['image_formats'])} formatos")
            print(f"   - Documentos: {len(data['document_formats'])} formatos")
            print(f"   - Tamaño máximo: {data['max_file_size'] / (1024*1024):.1f}MB")
            return True
        else:
            print(f"❌ Error obteniendo formatos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_upload_file(file_path, file_type):
    """Prueba la subida de un archivo"""
    print(f"\n🔄 Probando subida de {file_type}...")
    
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return None
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
            data = {
                'uploaded_by': 'test_user',
                'service_source': 'test_service',
                'reference_id': 'test_123',
                'is_public': 'true'
            }
            
            response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    file_id = result['file']['id']
                    print(f"✅ Archivo subido exitosamente: ID {file_id}")
                    return file_id
                else:
                    print(f"❌ Error en subida: {result.get('error', 'Unknown error')}")
                    return None
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ Error subiendo archivo: {e}")
        return None

def test_get_file_info(file_id):
    """Prueba obtener información de un archivo"""
    print(f"\n🔄 Probando obtención de información del archivo {file_id}...")
    try:
        response = requests.get(f"{BASE_URL}/files/{file_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Información del archivo obtenida:")
            print(f"   - Nombre: {data['original_filename']}")
            print(f"   - Tipo: {data['file_type']}")
            print(f"   - Tamaño: {data['file_size']} bytes")
            print(f"   - Procesado: {data['is_processed']}")
            return True
        else:
            print(f"❌ Error obteniendo información: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_download_file(file_id):
    """Prueba la descarga de un archivo"""
    print(f"\n🔄 Probando descarga del archivo {file_id}...")
    try:
        response = requests.get(f"{BASE_URL}/files/{file_id}/download")
        if response.status_code == 200:
            print(f"✅ Descarga exitosa: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Error en descarga: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_list_files():
    """Prueba listar archivos"""
    print("\n🔄 Probando listado de archivos...")
    try:
        response = requests.get(f"{BASE_URL}/files?limit=10")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Listado exitoso: {data['total']} archivos")
            return True
        else:
            print(f"❌ Error en listado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def cleanup_test_files():
    """Limpia archivos de prueba"""
    print("\n🔄 Limpiando archivos de prueba...")
    for file_path in [TEST_IMAGE_PATH, TEST_PDF_PATH]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Archivo eliminado: {file_path}")

def main():
    """Función principal de testing"""
    print("🧪 Iniciando tests de Media Service...")
    
    # Verificar que el servicio esté corriendo
    if not test_health_check():
        print("\n❌ El servicio no está disponible. Asegúrate de que esté corriendo en http://localhost:8005")
        return
    
    # Crear archivos de prueba
    create_test_files()
    
    # Probar formatos soportados
    test_supported_formats()
    
    # Probar subida de imagen
    image_id = test_upload_file(TEST_IMAGE_PATH, "imagen")
    if image_id:
        test_get_file_info(image_id)
        test_download_file(image_id)
    
    # Probar subida de PDF
    pdf_id = test_upload_file(TEST_PDF_PATH, "documento")
    if pdf_id:
        test_get_file_info(pdf_id)
        test_download_file(pdf_id)
    
    # Probar listado
    test_list_files()
    
    # Limpiar archivos de prueba
    cleanup_test_files()
    
    print("\n🎉 ¡Tests completados!")

if __name__ == "__main__":
    main() 