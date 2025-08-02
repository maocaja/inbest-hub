#!/usr/bin/env python3
"""
Basic tests for Embedding Service
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Import the app
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Embedding Service"
    assert data["version"] == "1.0.0"

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "version" in data

def test_generate_embedding():
    """Test embedding generation"""
    with patch('services.embedding_service.EmbeddingService.generate_embedding') as mock_generate:
        mock_generate.return_value = [0.1] * 384  # Mock embedding
        
        response = client.post("/embeddings/generate", json={
            "text": "test text",
            "metadata": {}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "embedding" in data
        assert "dimension" in data
        assert "model" in data

def test_search_projects():
    """Test project search"""
    with patch('services.embedding_service.EmbeddingService.search_projects') as mock_search:
        mock_search.return_value = Mock(
            results=[],
            total_results=0,
            query="test",
            collection="test"
        )
        
        response = client.post("/search", json={
            "query": "test query",
            "collection": "real_estate_projects",
            "max_results": 10,
            "similarity_threshold": 0.7
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_results" in data
        assert "query" in data

def test_index_project():
    """Test project indexing"""
    with patch('services.embedding_service.EmbeddingService.index_project') as mock_index:
        mock_index.return_value = True
        
        project_data = {
            "id": 1,
            "name": "Test Project",
            "location": "Test Location",
            "city": "Test City",
            "state": "Test State",
            "property_type": "Apartamento",
            "construction_company_nit": "12345678-9"
        }
        
        response = client.post("/projects/index", json=project_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

def test_delete_project():
    """Test project deletion"""
    with patch('services.embedding_service.EmbeddingService.delete_project') as mock_delete:
        mock_delete.return_value = True
        
        response = client.delete("/projects/1")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

def test_update_project():
    """Test project update"""
    with patch('services.embedding_service.EmbeddingService.update_project') as mock_update:
        mock_update.return_value = True
        
        project_data = {
            "id": 1,
            "name": "Updated Project",
            "location": "Updated Location",
            "city": "Updated City",
            "state": "Updated State",
            "property_type": "Apartamento",
            "construction_company_nit": "12345678-9"
        }
        
        response = client.put("/projects/1", json=project_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

def test_sync_projects():
    """Test project synchronization"""
    with patch('services.embedding_service.EmbeddingService.sync_all_projects') as mock_sync:
        mock_sync.return_value = {
            "success": True,
            "total_projects": 5,
            "indexed_count": 5,
            "error_count": 0
        }
        
        response = client.post("/sync/projects")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "total_projects" in data

def test_collection_info():
    """Test collection information"""
    with patch('services.embedding_service.EmbeddingService.get_collection_info') as mock_info:
        mock_info.return_value = {
            "name": "test_collection",
            "count": 10,
            "dimension": 384,
            "model": "test_model"
        }
        
        response = client.get("/collections/test_collection")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "count" in data
        assert "dimension" in data

def test_webhook_project_sync():
    """Test webhook project sync"""
    with patch('services.embedding_service.EmbeddingService.index_project') as mock_index:
        mock_index.return_value = True
        
        webhook_data = {
            "project_id": 1,
            "action": "create",
            "data": {
                "id": 1,
                "name": "Test Project",
                "location": "Test Location",
                "city": "Test City",
                "state": "Test State",
                "property_type": "Apartamento",
                "construction_company_nit": "12345678-9"
            }
        }
        
        response = client.post("/webhook/project-sync", json=webhook_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

def test_webhook_invalid_action():
    """Test webhook with invalid action"""
    webhook_data = {
        "project_id": 1,
        "action": "invalid_action",
        "data": {}
    }
    
    response = client.post("/webhook/project-sync", json=webhook_data)
    assert response.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__]) 