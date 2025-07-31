import pytest
import json
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from main import app
from services.document_processor import DocumentProcessor
from services.data_extractor import RealEstateDataExtractor
from services.data_validator import DataValidator

client = TestClient(app)

class TestDocumentProcessor:
    """Tests para el procesador de documentos"""
    
    def test_supported_formats(self):
        processor = DocumentProcessor()
        assert '.pdf' in processor.supported_formats
        assert '.docx' in processor.supported_formats
        assert '.xlsx' in processor.supported_formats
        assert '.xls' in processor.supported_formats

class TestDataValidator:
    """Tests para el validador de datos"""
    
    def test_validate_required_fields(self):
        validator = DataValidator()
        
        # Test con datos completos
        complete_data = {
            "name": "Proyecto Test",
            "builder": "Constructora Test",
            "status": "preventa"
        }
        
        result = validator._check_required_fields(complete_data)
        assert len(result) == 0
        
        # Test con datos incompletos
        incomplete_data = {
            "name": "Proyecto Test"
            # Falta builder y status
        }
        
        result = validator._check_required_fields(incomplete_data)
        assert len(result) == 2
        assert "builder" in result[0]
        assert "status" in result[1]
    
    def test_validate_date_format(self):
        validator = DataValidator()
        
        # Test fecha válida
        try:
            validator._validate_date_format("2024-12")
        except ValueError:
            pytest.fail("Fecha válida no debería fallar")
        
        # Test fecha inválida
        with pytest.raises(ValueError):
            validator._validate_date_format("2024-13")
        
        with pytest.raises(ValueError):
            validator._validate_date_format("2024")
    
    def test_validate_positive_number(self):
        validator = DataValidator()
        
        # Test números válidos
        try:
            validator._validate_positive_number(100)
            validator._validate_positive_number(100.5)
        except ValueError:
            pytest.fail("Números positivos no deberían fallar")
        
        # Test números inválidos
        with pytest.raises(ValueError):
            validator._validate_positive_number(0)
        
        with pytest.raises(ValueError):
            validator._validate_positive_number(-10)
    
    def test_calculate_completeness_score(self):
        validator = DataValidator()
        
        # Test con datos completos
        complete_data = {
            "name": "Proyecto Test",
            "description": "Descripción test",
            "builder": "Constructora Test",
            "status": "preventa",
            "delivery_date": "2024-12",
            "location": {
                "country": "Colombia",
                "department": "Antioquia",
                "city": "Medellín",
                "zone": "Centro",
                "neighborhood": "El Poblado"
            },
            "price_info": {
                "currency": "COP",
                "price_min": 100000000,
                "price_max": 200000000
            },
            "unit_info": {
                "unit_types": ["apartamento"],
                "area_m2_min": 50,
                "area_m2_max": 120
            }
        }
        
        score = validator._calculate_completeness_score(complete_data)
        assert score > 80  # Debería tener un score alto
    
    def test_get_nested_value(self):
        validator = DataValidator()
        
        data = {
            "location": {
                "city": "Medellín",
                "country": "Colombia"
            },
            "price_info": {
                "currency": "COP"
            }
        }
        
        # Test valores existentes
        assert validator._get_nested_value(data, "location.city") == "Medellín"
        assert validator._get_nested_value(data, "price_info.currency") == "COP"
        
        # Test valores inexistentes
        assert validator._get_nested_value(data, "location.latitude") is None
        assert validator._get_nested_value(data, "nonexistent.field") is None

class TestAPIEndpoints:
    """Tests para los endpoints de la API"""
    
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Real Estate Data Extractor Agent" in data["message"]
    
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_schema_endpoint(self):
        response = client.get("/schema")
        assert response.status_code == 200
        data = response.json()
        assert "properties" in data
    
    @patch('services.document_processor.DocumentProcessor.process_document')
    @patch('services.data_extractor.RealEstateDataExtractor.extract_project_data')
    @patch('services.data_validator.DataValidator.validate_project_data')
    def test_extract_endpoint_success(self, mock_validate, mock_extract, mock_process):
        # Mock responses
        mock_process.return_value = "Contenido del documento"
        
        mock_project_data = {
            "name": "Proyecto Test",
            "builder": "Constructora Test",
            "status": "preventa"
        }
        mock_extract.return_value = Mock(**mock_project_data)
        
        mock_validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "completeness_score": 85.5,
            "suggestions": []
        }
        mock_validate.return_value = Mock(**mock_validation)
        
        # Test file upload
        test_file_content = b"test content"
        response = client.post(
            "/extract",
            files={"file": ("test.pdf", test_file_content, "application/pdf")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Datos extraídos exitosamente" in data["message"]
    
    def test_extract_endpoint_invalid_file_type(self):
        test_file_content = b"test content"
        response = client.post(
            "/extract",
            files={"file": ("test.txt", test_file_content, "text/plain")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Tipo de archivo no soportado" in data["detail"]

if __name__ == "__main__":
    pytest.main([__file__]) 