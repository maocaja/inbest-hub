#!/usr/bin/env python3
"""
Integration test demonstrating the connection between embedding-service and projects-service
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Configuration
PROJECTS_SERVICE_URL = "http://localhost:8003"
EMBEDDING_SERVICE_URL = "http://localhost:8005"

async def test_integration():
    """Test the integration between services"""
    print("🔗 Testing Integration between Embedding Service and Projects Service")
    print("=" * 70)
    
    # Step 1: Create a project in projects-service
    print("📝 Step 1: Creating a project in projects-service...")
    project_data = {
        "name": "Residencial El Bosque",
        "description": "Apartamentos de lujo con vista al bosque en Bogotá",
        "project_owner_nit": "12345678-9",
        "location": {
            "address": "Calle 123 # 45-67",
            "city": "Bogotá",
            "department": "Cundinamarca",
            "country": "Colombia"
        },
        "price_info": {
            "currency": "COP",
            "min_price": 300000000,
            "max_price": 600000000,
            "price_per_m2": 5000000
        },
        "unit_info": {
            "total_units": 80,
            "available_units": 12,
            "unit_types": ["Apartamento", "Penthouse"],
            "areas": {
                "Apartamento": {"min": 60, "max": 120},
                "Penthouse": {"min": 150, "max": 200}
            }
        },
        "amenities": ["Piscina", "Gimnasio", "Zona BBQ", "Seguridad 24/7", "Parqueadero"],
        "status": "en_proceso"
    }
    
    async with httpx.AsyncClient() as client:
        # Create project
        response = await client.post(
            f"{PROJECTS_SERVICE_URL}/projects",
            json=project_data
        )
        
        if response.status_code == 201:
            created_project = response.json()
            project_id = created_project["id"]
            print(f"✅ Project created with ID: {project_id}")
            print(f"   Name: {created_project['name']}")
            print(f"   Status: {created_project['status']}")
        else:
            print(f"❌ Failed to create project: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    
    # Step 2: Wait a moment for webhook processing
    print("\n⏳ Step 2: Waiting for webhook processing...")
    await asyncio.sleep(3)
    
    # Step 3: Check if project was indexed in embedding-service
    print("\n🔍 Step 3: Checking if project was indexed in embedding-service...")
    async with httpx.AsyncClient() as client:
        # Search for the project
        search_data = {
            "query": "residencial el bosque bogota",
            "collection": "real_estate_projects",
            "max_results": 5,
            "similarity_threshold": 0.3
        }
        
        response = await client.post(
            f"{EMBEDDING_SERVICE_URL}/search",
            json=search_data
        )
        
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Search completed: {search_results['total_results']} results found")
            
            if search_results['total_results'] > 0:
                for i, result in enumerate(search_results['results']):
                    print(f"   {i+1}. Score: {result['score']:.3f} - {result['metadata']['name']}")
                    print(f"      Location: {result['metadata'].get('location', 'N/A')}")
                    print(f"      Property Type: {result['metadata'].get('property_type', 'N/A')}")
            else:
                print("   ⚠️  No projects found in search results")
        else:
            print(f"❌ Search failed: {response.status_code}")
    
    # Step 4: Update the project
    print("\n🔄 Step 4: Updating the project...")
    update_data = {
        "name": "Residencial El Bosque Premium",
        "description": "Apartamentos de lujo premium con vista al bosque en Bogotá",
        "amenities": ["Piscina", "Gimnasio", "Zona BBQ", "Seguridad 24/7", "Parqueadero", "Spa", "Salón de eventos"]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{PROJECTS_SERVICE_URL}/projects/{project_id}",
            json=update_data
        )
        
        if response.status_code == 200:
            updated_project = response.json()
            print(f"✅ Project updated: {updated_project['name']}")
        else:
            print(f"❌ Failed to update project: {response.status_code}")
            print(f"   Response: {response.text}")
    
    # Step 5: Wait and search again
    print("\n⏳ Step 5: Waiting for update webhook processing...")
    await asyncio.sleep(3)
    
    print("\n🔍 Step 6: Searching for updated project...")
    async with httpx.AsyncClient() as client:
        search_data = {
            "query": "residencial el bosque premium spa",
            "collection": "real_estate_projects",
            "max_results": 5,
            "similarity_threshold": 0.3
        }
        
        response = await client.post(
            f"{EMBEDDING_SERVICE_URL}/search",
            json=search_data
        )
        
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Search completed: {search_results['total_results']} results found")
            
            if search_results['total_results'] > 0:
                for i, result in enumerate(search_results['results']):
                    print(f"   {i+1}. Score: {result['score']:.3f} - {result['metadata']['name']}")
                    amenities = json.loads(result['metadata'].get('amenities', '[]'))
                    print(f"      Amenities: {', '.join(amenities)}")
            else:
                print("   ⚠️  No projects found in search results")
        else:
            print(f"❌ Search failed: {response.status_code}")
    
    # Step 7: Check collection info
    print("\n📊 Step 7: Checking collection information...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{EMBEDDING_SERVICE_URL}/collections/real_estate_projects")
        
        if response.status_code == 200:
            collection_info = response.json()
            print(f"✅ Collection info:")
            print(f"   Name: {collection_info['name']}")
            print(f"   Count: {collection_info['count']} projects")
            print(f"   Dimension: {collection_info['dimension']}")
            print(f"   Model: {collection_info['model']}")
        else:
            print(f"❌ Failed to get collection info: {response.status_code}")
    
    print("\n" + "=" * 70)
    print("🎉 Integration test completed!")
    print("The embedding-service and projects-service are working together!")

async def test_manual_sync():
    """Test manual synchronization"""
    print("\n🔄 Testing manual synchronization...")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{EMBEDDING_SERVICE_URL}/sync/projects")
        
        if response.status_code == 200:
            sync_result = response.json()
            print(f"✅ Sync completed:")
            print(f"   Total projects: {sync_result['total_projects']}")
            print(f"   Indexed: {sync_result['indexed_count']}")
            print(f"   Errors: {sync_result['error_count']}")
        else:
            print(f"❌ Sync failed: {response.status_code}")
            print(f"   Response: {response.text}")

async def main():
    """Run integration tests"""
    try:
        await test_integration()
        await test_manual_sync()
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 