# API Usage Guide - Real Estate Data Extractor Agent

## Overview

El Real Estate Data Extractor Agent es un servicio especializado en extraer información estructurada de proyectos inmobiliarios desde documentos PDF, DOCX y Excel. Utiliza IA para identificar y organizar datos relevantes en un esquema JSON estandarizado.

## Base URL

```
http://localhost:8012
```

## Endpoints

### 1. Health Check

**GET** `/health`

Verifica el estado del servicio.

**Response:**
```json
{
  "status": "healthy",
  "service": "real-estate-extractor"
}
```

### 2. Extract Data from Document

**POST** `/extract`

Extrae información de proyectos inmobiliarios desde documentos.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF, DOCX, XLSX, XLS)

**Example with cURL:**
```bash
curl -X POST "http://localhost:8012/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@proyecto_inmobiliario.pdf"
```

**Response:**
```json
{
  "success": true,
  "project_data": {
    "name": "Residencial Los Pinos",
    "builder": "Constructora ABC",
    "status": "preventa",
    "delivery_date": "2024-12",
    "location": {
      "country": "Colombia",
      "city": "Medellín",
      "neighborhood": "El Poblado"
    },
    "price_info": {
      "currency": "COP",
      "price_min": 150000000,
      "price_max": 300000000
    },
    "unit_info": {
      "unit_types": ["apartamento"],
      "area_m2_min": 60,
      "area_m2_max": 120
    }
  },
  "validation_result": {
    "is_valid": true,
    "errors": [],
    "warnings": ["Campo importante faltante: location.zone"],
    "completeness_score": 85.5,
    "suggestions": [
      "Agregar zona para mejor geolocalización",
      "Especificar tipos de unidades disponibles"
    ]
  },
  "message": "Datos extraídos exitosamente"
}
```

### 3. Validate Project Data

**POST** `/validate`

Valida la información de un proyecto inmobiliario.

**Request:**
```json
{
  "name": "Residencial Los Pinos",
  "builder": "Constructora ABC",
  "status": "preventa",
  "delivery_date": "2024-12",
  "location": {
    "country": "Colombia",
    "city": "Medellín",
    "neighborhood": "El Poblado"
  },
  "price_info": {
    "currency": "COP",
    "price_min": 150000000,
    "price_max": 300000000
  }
}
```

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [
    "Campo importante faltante: unit_info.area_m2_min",
    "Campo importante faltante: unit_info.unit_types"
  ],
  "completeness_score": 75.0,
  "suggestions": [
    "Especificar tipos de unidades disponibles",
    "Agregar área mínima de unidades"
  ]
}
```

### 4. Complete Missing Data

**POST** `/complete`

Completa información faltante usando IA.

**Request:**
```json
{
  "name": "Residencial Los Pinos",
  "builder": "Constructora ABC",
  "status": "preventa",
  "location": {
    "city": "Medellín"
  }
}
```

**Response:**
```json
{
  "name": "Residencial Los Pinos",
  "builder": "Constructora ABC",
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
    "price_min": 120000000,
    "price_max": 250000000,
    "price_per_m2": 2500000
  },
  "unit_info": {
    "unit_types": ["apartamento"],
    "area_m2_min": 50,
    "area_m2_max": 120,
    "bedrooms_min": 1,
    "bedrooms_max": 3,
    "bathrooms_min": 1,
    "bathrooms_max": 2
  }
}
```

### 5. Get JSON Schema

**GET** `/schema`

Obtiene el esquema JSON del proyecto inmobiliario.

**Response:**
```json
{
  "title": "RealEstateProject",
  "type": "object",
  "properties": {
    "project_id": {
      "title": "Project Id",
      "type": "string",
      "description": "ID único del proyecto"
    },
    "name": {
      "title": "Name",
      "type": "string",
      "description": "Nombre del proyecto"
    }
    // ... más propiedades
  }
}
```

## Error Responses

### File Type Error
```json
{
  "detail": "Tipo de archivo no soportado. Formatos permitidos: .pdf, .docx, .xlsx, .xls"
}
```

### File Size Error
```json
{
  "detail": "Archivo demasiado grande. Tamaño máximo: 50MB"
}
```

### Validation Error
```json
{
  "detail": "Error en validación: Fecha debe estar en formato YYYY-MM"
}
```

## Python Client Example

```python
import requests
import json

class RealEstateExtractorClient:
    def __init__(self, base_url="http://localhost:8012"):
        self.base_url = base_url
    
    def extract_from_file(self, file_path):
        """Extrae datos desde un archivo"""
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(f"{self.base_url}/extract", files=files)
            return response.json()
    
    def validate_project(self, project_data):
        """Valida datos del proyecto"""
        response = requests.post(f"{self.base_url}/validate", json=project_data)
        return response.json()
    
    def complete_project(self, project_data):
        """Completa información faltante"""
        response = requests.post(f"{self.base_url}/complete", json=project_data)
        return response.json()
    
    def get_schema(self):
        """Obtiene el esquema JSON"""
        response = requests.get(f"{self.base_url}/schema")
        return response.json()

# Uso del cliente
client = RealEstateExtractorClient()

# Extraer datos
result = client.extract_from_file("proyecto.pdf")
if result['success']:
    print(f"Score de completitud: {result['validation_result']['completeness_score']}%")

# Validar datos
validation = client.validate_project(result['project_data'])
print(f"Válido: {validation['is_valid']}")

# Completar datos
completed = client.complete_project(result['project_data'])
print(f"Datos completados: {completed['name']}")
```

## JavaScript/Node.js Client Example

```javascript
const FormData = require('form-data');
const fs = require('fs');

class RealEstateExtractorClient {
    constructor(baseUrl = 'http://localhost:8012') {
        this.baseUrl = baseUrl;
    }

    async extractFromFile(filePath) {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        
        const response = await fetch(`${this.baseUrl}/extract`, {
            method: 'POST',
            body: form
        });
        
        return await response.json();
    }

    async validateProject(projectData) {
        const response = await fetch(`${this.baseUrl}/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(projectData)
        });
        
        return await response.json();
    }

    async completeProject(projectData) {
        const response = await fetch(`${this.baseUrl}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(projectData)
        });
        
        return await response.json();
    }
}

// Uso del cliente
const client = new RealEstateExtractorClient();

client.extractFromFile('proyecto.pdf')
    .then(result => {
        if (result.success) {
            console.log(`Score: ${result.validation_result.completeness_score}%`);
        }
    })
    .catch(error => console.error('Error:', error));
```

## Best Practices

### 1. File Preparation
- Asegúrate de que los documentos estén en formato legible
- Para PDFs, usa documentos con texto (no solo imágenes)
- Para Excel, organiza los datos en tablas claras

### 2. Data Validation
- Siempre valida los datos extraídos antes de usarlos
- Revisa las sugerencias para mejorar la completitud
- Corrige errores antes de completar información faltante

### 3. Error Handling
- Maneja errores de red y timeouts
- Verifica el tamaño de archivo antes de subir
- Implementa retry logic para fallos temporales

### 4. Performance
- Los archivos grandes pueden tomar más tiempo
- Considera procesar archivos en background
- Cachea resultados cuando sea apropiado

## Rate Limits

- Máximo 10MB por archivo
- Máximo 50MB total por minuto
- Máximo 100 requests por minuto por IP

## Support

Para soporte técnico o preguntas sobre la API:
- Revisa la documentación completa en README.md
- Ejecuta los tests para verificar la instalación
- Consulta los logs del servidor para debugging 