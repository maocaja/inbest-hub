#!/usr/bin/env python3
"""
Script para sincronizar constructoras del project-owners-service al projects-service
"""

import requests
import sys
from datetime import datetime
from database.database import SessionLocal
from models.models import ProjectOwner

def get_owners_from_service():
    """Obtener constructoras del project-owners-service"""
    try:
        response = requests.get("http://localhost:8002/project-owners")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error obteniendo constructoras: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error conectando al service: {e}")
        return []

def sync_owners_to_db(owners):
    """Sincronizar constructoras a la base de datos local"""
    db = SessionLocal()
    try:
        for owner_data in owners:
            # Verificar si ya existe
            existing = db.query(ProjectOwner).filter(ProjectOwner.nit == owner_data['nit']).first()
            if existing:
                print(f"✅ Constructora {owner_data['name']} ya existe")
                continue
            
            # Crear nueva constructora
            # Convertir fechas de string a datetime
            if 'created_at' in owner_data and isinstance(owner_data['created_at'], str):
                owner_data['created_at'] = datetime.fromisoformat(owner_data['created_at'].replace('Z', '+00:00'))
            if 'updated_at' in owner_data and isinstance(owner_data['updated_at'], str):
                owner_data['updated_at'] = datetime.fromisoformat(owner_data['updated_at'].replace('Z', '+00:00'))
            
            new_owner = ProjectOwner(**owner_data)
            db.add(new_owner)
            print(f"✅ Constructora {owner_data['name']} creada")
        
        db.commit()
        print(f"✅ Sincronización completada: {len(owners)} constructoras")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error en sincronización: {e}")
    finally:
        db.close()

def main():
    """Función principal"""
    print("🔄 Sincronizando constructoras...")
    
    # Obtener constructoras del service
    owners = get_owners_from_service()
    if not owners:
        print("❌ No se pudieron obtener constructoras")
        return
    
    print(f"📋 Encontradas {len(owners)} constructoras:")
    for owner in owners:
        print(f"   - {owner['name']} (NIT: {owner['nit']})")
    
    # Sincronizar a base de datos local
    sync_owners_to_db(owners)

if __name__ == "__main__":
    main() 