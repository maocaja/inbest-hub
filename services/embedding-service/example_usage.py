#!/usr/bin/env python3
"""
Example usage of Embedding Service
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8005"

async def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False

async def test_generate_embedding():
    """Test embedding generation"""
    print("🧠 Testing embedding generation...")
    async with httpx.AsyncClient() as client:
        data = {
            "text": "apartamento en bogota con piscina",
            "metadata": {"source": "test"}
        }
        response = await client.post(f"{BASE_URL}/embeddings/generate", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Embedding generated: dimension={result['dimension']}, model={result['model']}")
            return True
        else:
            print(f"❌ Embedding generation failed: {response.status_code}")
            return False

async def test_index_project():
    """Test project indexing"""
    print("📝 Testing project indexing...")
    async with httpx.AsyncClient() as client:
        project_data = {
            "id": 1,
            "name": "Torre Residencial Los Andes",
            "description": "Apartamentos de lujo en el corazón de Bogotá con amenidades premium",
            "location": "Chapinero",
            "city": "Bogotá",
            "state": "Cundinamarca",
            "country": "Colombia",
            "property_type": "Apartamento",
            "total_units": 120,
            "available_units": 15,
            "price_range_min": 250000000,
            "price_range_max": 450000000,
            "area_range_min": 45,
            "area_range_max": 120,
            "amenities": ["Piscina", "Gimnasio", "Zona BBQ", "Seguridad 24/7"],
            "construction_company_nit": "12345678-9",
            "state": "in_progress"
        }
        response = await client.post(f"{BASE_URL}/projects/index", json=project_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Project indexed: {result['message']}")
            return True
        else:
            print(f"❌ Project indexing failed: {response.status_code}")
            return False

async def test_search_projects():
    """Test project search"""
    print("🔍 Testing project search...")
    async with httpx.AsyncClient() as client:
        search_data = {
            "query": "apartamentos en bogota con piscina",
            "collection": "real_estate_projects",
            "max_results": 5,
            "similarity_threshold": 0.5
        }
        response = await client.post(f"{BASE_URL}/search", json=search_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search completed: {result['total_results']} results found")
            for i, res in enumerate(result['results']):
                print(f"  {i+1}. Score: {res['score']:.3f} - {res['metadata']['name']}")
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False

async def test_sync_projects():
    """Test project synchronization"""
    print("🔄 Testing project synchronization...")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/sync/projects")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sync completed: {result['total_projects']} projects, {result['indexed_count']} indexed")
            return True
        else:
            print(f"❌ Sync failed: {response.status_code}")
            return False

async def test_collection_info():
    """Test collection information"""
    print("📊 Testing collection info...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/collections/real_estate_projects")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Collection info: {result['name']} - {result['count']} items")
            return True
        else:
            print(f"❌ Collection info failed: {response.status_code}")
            return False

async def test_webhook():
    """Test webhook endpoint"""
    print("🔗 Testing webhook...")
    async with httpx.AsyncClient() as client:
        webhook_data = {
            "project_id": 2,
            "action": "create",
            "data": {
                "id": 2,
                "name": "Conjunto Residencial El Prado",
                "description": "Apartamentos familiares con áreas verdes",
                "location": "Suba",
                "city": "Bogotá",
                "state": "Cundinamarca",
                "property_type": "Apartamento",
                "construction_company_nit": "98765432-1"
            }
        }
        response = await client.post(f"{BASE_URL}/webhook/project-sync", json=webhook_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook processed: {result['message']}")
            return True
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            return False

async def main():
    """Run all tests"""
    print("🚀 Starting Embedding Service tests...")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Generate Embedding", test_generate_embedding),
        ("Index Project", test_index_project),
        ("Search Projects", test_search_projects),
        ("Collection Info", test_collection_info),
        ("Webhook", test_webhook),
        ("Sync Projects", test_sync_projects),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("=" * 60)
    print("📋 Test Results:")
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Embedding Service is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the service configuration.")

if __name__ == "__main__":
    asyncio.run(main()) 