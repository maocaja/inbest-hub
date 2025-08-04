# Embedding Service

Servicio para generación de embeddings y búsqueda vectorial de proyectos inmobiliarios.

## 🚀 Características

- **Generación de Embeddings**: Utiliza sentence-transformers para generar embeddings de texto
- **Búsqueda Vectorial**: Búsqueda semántica de proyectos usando ChromaDB
- **Sincronización Automática**: Sincroniza proyectos desde projects-service
- **Webhooks**: Recibe notificaciones de cambios en proyectos
- **API REST**: Endpoints para todas las operaciones

## 📋 Requisitos

- Python 3.8+
- ChromaDB
- sentence-transformers
- FastAPI

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
cd services/embedding-service
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

4. **Ejecutar el servicio**
```bash
python main.py
```

## 🔧 Configuración

### Variables de Entorno

- `PORT`: Puerto del servicio (default: 8005)
- `EMBEDDING_MODEL`: Modelo de embeddings (default: sentence-transformers/all-MiniLM-L6-v2)
- `CHROMA_PERSIST_DIRECTORY`: Directorio para ChromaDB
- `PROJECTS_SERVICE_URL`: URL del projects-service
- `PROJECT_OWNERS_SERVICE_URL`: URL del project-owners-service

## 📚 API Endpoints

### Health Check
```http
GET /health
```

### Generar Embedding
```http
POST /embeddings/generate
Content-Type: application/json

{
  "text": "apartamento en bogota",
  "metadata": {}
}
```

### Búsqueda de Proyectos
```http
POST /search
Content-Type: application/json

{
  "query": "apartamentos en bogota",
  "collection": "real_estate_projects",
  "max_results": 10,
  "similarity_threshold": 0.7
}
```

### Indexar Proyecto
```http
POST /projects/index
Content-Type: application/json

{
  "id": 1,
  "name": "Torre Residencial",
  "description": "Apartamentos de lujo en Bogotá",
  "location": "Chapinero",
  "city": "Bogotá",
  "state": "Cundinamarca",
  "property_type": "Apartamento",
  "construction_company_nit": "12345678-9"
}
```

### Sincronizar Todos los Proyectos
```http
POST /sync/projects
```

### Información de Colección
```http
GET /collections/{collection_name}
```

### Webhook para Sincronización
```http
POST /webhook/project-sync
Content-Type: application/json

{
  "project_id": 1,
  "action": "create",
  "data": {
    "id": 1,
    "name": "Torre Residencial",
    "description": "Apartamentos de lujo en Bogotá",
    "location": "Chapinero",
    "city": "Bogotá",
    "state": "Cundinamarca",
    "property_type": "Apartamento",
    "construction_company_nit": "12345678-9"
  }
}
```

## 🔍 Funcionalidades

### 1. Generación de Embeddings
- Utiliza modelos pre-entrenados de sentence-transformers
- Soporte para diferentes modelos de embeddings
- Generación asíncrona de embeddings

### 2. Búsqueda Vectorial
- Búsqueda semántica de proyectos
- Filtros por metadatos
- Umbral de similitud configurable
- Resultados ordenados por relevancia

### 3. Indexación de Proyectos
- Indexación automática de proyectos
- Texto de búsqueda generado automáticamente
- Metadatos enriquecidos con información del propietario

### 4. Sincronización
- Sincronización completa desde projects-service
- Webhooks para actualizaciones en tiempo real
- Manejo de errores y reintentos

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Ejecutar con coverage
pytest --cov=.
```

## 📊 Monitoreo

- Logs detallados con loguru
- Health checks automáticos
- Métricas de rendimiento
- Información de colecciones

## 🔗 Integración

### Con Projects Service
- Recibe webhooks de cambios en proyectos
- Sincronización automática de datos
- Búsqueda enriquecida con metadatos

### Con Project Owners Service
- Obtiene información de propietarios
- Enriquece metadatos de proyectos
- Mejora la calidad de búsqueda

## 🚀 Despliegue

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Variables de Producción
```bash
PORT=8005
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_PERSIST_DIRECTORY=/data/chroma_db
PROJECTS_SERVICE_URL=https://projects-service.example.com
PROJECT_OWNERS_SERVICE_URL=https://project-owners-service.example.com
```

## 📈 Escalabilidad

- ChromaDB permite escalabilidad horizontal
- Modelos de embeddings optimizados
- Caché de embeddings
- Búsqueda distribuida

## 🔒 Seguridad

- Validación de entrada con Pydantic
- Sanitización de consultas
- Rate limiting
- Autenticación (futuro)

## 📝 Logs

Los logs se guardan en:
- `logs/embedding_service.log`
- Rotación diaria
- Retención de 7 días

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request 