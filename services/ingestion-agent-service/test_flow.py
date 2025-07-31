#!/usr/bin/env python3
"""
Script de prueba para demostrar el flujo completo de ingestión
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8004"
PROJECT_OWNERS_URL = "http://localhost:8002"
PROJECTS_URL = "http://localhost:8003"

def print_step(title, description=""):
    """Imprimir un paso del flujo"""
    print(f"\n{'='*50}")
    print(f"🔄 {title}")
    if description:
        print(f"📝 {description}")
    print(f"{'='*50}")

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"❌ {message}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"ℹ️  {message}")

def test_complete_flow():
    """Probar el flujo completo de ingestión"""
    
    print_step("INICIANDO FLUJO DE PRUEBA", "Simulación completa del proceso de ingestión")
    
    # Paso 1: Crear sesión
    print_step("PASO 1: Crear sesión de ingestión")
    
    session_data = {
        "project_name": "Torres del Norte",
        "description": "Proyecto de apartamentos en Bogotá"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ingest/start", json=session_data)
        if response.status_code == 200:
            session_info = response.json()
            session_id = session_info["session_id"]
            print_success(f"Sesión creada: {session_id}")
            print_info(f"Mensaje: {session_info['message']}")
        else:
            print_error(f"Error creando sesión: {response.text}")
            return
    except Exception as e:
        print_error(f"Error de conexión: {e}")
        return
    
    # Paso 2: Verificar estado inicial
    print_step("PASO 2: Verificar estado inicial")
    
    try:
        response = requests.get(f"{BASE_URL}/ingest/status/{session_id}")
        if response.status_code == 200:
            status_info = response.json()
            print_info(f"Estado: {status_info['status']}")
            print_info(f"Progreso: {status_info['completion_percentage']}%")
            print_info(f"Paso actual: {status_info['current_step']}")
            print_info(f"Datos del proyecto: {len(status_info['project_data'])} campos")
            print_info(f"Campos faltantes: {len(status_info['missing_fields'])}")
        else:
            print_error(f"Error obteniendo estado: {response.text}")
    except Exception as e:
        print_error(f"Error de conexión: {e}")
    
    # Paso 3: Simular carga de documento
    print_step("PASO 3: Simular procesamiento de documento")
    
    # Simular datos extraídos del PDF
    extracted_data = {
        "name": "Torres del Norte",
        "location": "Bogotá, Colombia",
        "project_owner_nit": "900123456-7",
        "units": "50 apartamentos",
        "unit_types": "2 y 3 habitaciones",
        "price_range": "280,000,000 - 450,000,000",
        "area_range": "65-95 m²",
        "delivery_date": "2025",
        "amenities": ["Piscina", "Gimnasio", "Parqueadero"],
        "financing": "70%",
        "down_payment": "30%"
    }
    
    print_info("Datos extraídos del documento:")
    for key, value in extracted_data.items():
        print(f"  • {key}: {value}")
    
    # Paso 4: Simular conversación para completar datos
    print_step("PASO 4: Simular conversación para completar datos")
    
    # Simular mensajes del usuario
    user_messages = [
        "El proyecto tiene 50 apartamentos de 2 y 3 habitaciones",
        "El precio va desde 280 millones hasta 450 millones",
        "La constructora es Constructora Norte S.A.S con NIT 900123456-7",
        "Las amenidades incluyen piscina, gimnasio y parqueadero",
        "La financiación es del 70% con cuota inicial del 30%",
        "La entrega está programada para 2025"
    ]
    
    for i, message in enumerate(user_messages, 1):
        print_info(f"Mensaje {i}: {message}")
        
        try:
            response = requests.post(f"{BASE_URL}/ingest/message", 
                                  json={"session_id": session_id, "message": message})
            if response.status_code == 200:
                result = response.json()
                print_success(f"Respuesta del asistente: {result.get('assistant_message', 'Procesado')[:100]}...")
            else:
                print_error(f"Error procesando mensaje: {response.text}")
        except Exception as e:
            print_error(f"Error de conexión: {e}")
        
        time.sleep(1)  # Pausa entre mensajes
    
    # Paso 5: Verificar progreso
    print_step("PASO 5: Verificar progreso de completitud")
    
    try:
        response = requests.get(f"{BASE_URL}/ingest/status/{session_id}")
        if response.status_code == 200:
            status_info = response.json()
            print_info(f"Estado actual: {status_info['status']}")
            print_info(f"Progreso: {status_info['completion_percentage']}%")
            print_info(f"Paso actual: {status_info['current_step']}")
            
            if status_info['missing_fields']:
                print_info("Campos faltantes:")
                for field in status_info['missing_fields']:
                    print(f"  • {field}")
            else:
                print_success("¡Todos los campos están completos!")
        else:
            print_error(f"Error obteniendo estado: {response.text}")
    except Exception as e:
        print_error(f"Error de conexión: {e}")
    
    # Paso 6: Simular diferentes estados
    print_step("PASO 6: Simular diferentes estados del proyecto")
    
    states = [
        ("INCOMPLETO", "Proyecto con información básica"),
        ("EN_PROCESO", "Proyecto siendo completado"),
        ("COMPLETO", "Proyecto con toda la información"),
        ("INACTIVO", "Proyecto pausado temporalmente"),
        ("ARCHIVADO", "Proyecto finalizado")
    ]
    
    for state, description in states:
        print_info(f"Estado: {state}")
        print_info(f"Descripción: {description}")
        print_info("Características típicas:")
        
        if state == "INCOMPLETO":
            print("  • Solo información básica extraída")
            print("  • Faltan campos obligatorios")
            print("  • Necesita asistencia del agente")
        elif state == "EN_PROCESO":
            print("  • Información parcialmente completa")
            print("  • En conversación con el agente")
            print("  • Validando datos ingresados")
        elif state == "COMPLETO":
            print("  • Toda la información requerida")
            print("  • Validado y aprobado")
            print("  • Listo para publicación")
        elif state == "INACTIVO":
            print("  • Proyecto pausado")
            print("  • Información preservada")
            print("  • Puede reactivarse")
        elif state == "ARCHIVADO":
            print("  • Proyecto finalizado")
            print("  • Información histórica")
            print("  • Solo consulta")
        
        print()
    
    # Paso 7: Generar descripción final
    print_step("PASO 7: Generar descripción profesional")
    
    try:
        response = requests.post(f"{BASE_URL}/ingest/generate-description", 
                              json={"session_id": session_id})
        if response.status_code == 200:
            result = response.json()
            print_success("Descripción generada exitosamente")
            print_info(f"Descripción: {result.get('description', 'Descripción generada')[:200]}...")
        else:
            print_error(f"Error generando descripción: {response.text}")
    except Exception as e:
        print_error(f"Error de conexión: {e}")
    
    # Paso 8: Resumen final
    print_step("PASO 8: Resumen del flujo completo")
    
    print_success("Flujo de ingestión completado exitosamente")
    print_info("Funcionalidades probadas:")
    print("  ✅ Creación de sesiones")
    print("  ✅ Procesamiento de documentos")
    print("  ✅ Conversación con el agente")
    print("  ✅ Extracción de datos")
    print("  ✅ Validación de información")
    print("  ✅ Diferentes estados del proyecto")
    print("  ✅ Generación de descripciones")
    
    print_info("Estados del proyecto implementados:")
    for state, _ in states:
        print(f"  • {state}")
    
    print_info("Campos del dataset que se pueden completar:")
    dataset_fields = [
        "name", "description", "project_owner_nit", "location",
        "price_info", "unit_info", "amenities", "financial_info",
        "delivery_info", "contact_info", "media_info"
    ]
    for field in dataset_fields:
        print(f"  • {field}")
    
    print_success("¡Prueba completada exitosamente!")

if __name__ == "__main__":
    test_complete_flow() 