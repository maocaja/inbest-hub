# 📁 Media Service

Servicio de gestión de archivos multimedia para el backend inmobiliario.

## 🎯 Funcionalidades

- **Subida y descarga** de archivos multimedia
- **Validación** de formatos y tamaños
- **Optimización** automática de imágenes
- **Creación de miniaturas** para imágenes
- **Extracción de metadatos** de documentos
- **Almacenamiento organizado** por tipo de archivo
- **API REST** completa con documentación automática

## 📋 Formatos Soportados

### Imágenes
- JPG, JPEG, PNG, GIF, BMP, WebP

### Documentos
- PDF, DOCX, DOC, XLSX, XLS, TXT

## 🚀 Instalación

### 1. Configuración inicial
```bash
cd services/media-service
python setup.py
```

### 2. Crear archivo .env
```bash
cp env.example .env
# Editar variables según necesidad
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Iniciar servicio
```bash
python main.py
```

## 📡 API Endpoints

### Health Check
- `GET /health` - Estado del servicio

### Información
- `GET /supported-formats` - Formatos soportados

### Gestión de Archivos
- `POST /upload` - Subir archivo
- `GET /files/{file_id}` - Información del archivo
- `GET /files` - Listar archivos
- `GET /files/{file_id}/download` - Descargar archivo
- `GET /files/{file_id}/thumbnail` - Obtener miniatura
- `PUT /files/{file_id}` - Actualizar archivo
- `DELETE /files/{file_id}` - Eliminar archivo

### Logs
- `GET /processing-logs` - Logs de procesamiento

## 🔧 Configuración

### Variables de Entorno

```env
# Servidor
HOST=0.0.0.0
PORT=8005
DEBUG=True

# Base de datos
DATABASE_URL=sqlite:///./media_service.db

# Almacenamiento
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800  # 50MB

# Procesamiento de imágenes
MAX_IMAGE_WIDTH=1920
MAX_IMAGE_HEIGHT=1080
IMAGE_QUALITY=85

# Seguridad
ALLOWED_ORIGINS=*

# Logging
LOG_LEVEL=INFO
```

## 📁 Estructura de Archivos

```
media-service/
├── main.py                 # Aplicación FastAPI
├── config.py              # Configuración
├── requirements.txt        # Dependencias
├── setup.py               # Script de configuración
├── test_service.py        # Tests básicos
├── env.example            # Variables de entorno
├── README.md              # Documentación
├── database/
│   └── database.py        # Configuración de BD
├── models/
│   └── models.py          # Modelos SQLAlchemy
├── schemas/
│   └── schemas.py         # Esquemas Pydantic
├── services/
│   └── file_service.py    # Lógica de negocio
├── utils/
│   ├── validators.py      # Validaciones
│   └── optimizers.py      # Optimización
├── tests/
│   └── test_media.py      # Tests unitarios
└── uploads/               # Archivos subidos
    ├── image/
    │   └── thumbnails/
    └── document/
```

## 🧪 Testing

### Tests básicos
```bash
python test_service.py
```

### Tests unitarios
```bash
python -m pytest tests/
```

## 🔗 Integración con Otros Servicios

### Ingestion Agent Service
```python
# Subir documento para procesamiento
response = requests.post(
    "http://localhost:8005/upload",
    files={"file": open("document.pdf", "rb")},
    data={
        "service_source": "ingestion-agent",
        "reference_id": "session_123"
    }
)
```

### Projects Service
```python
# Subir imagen de proyecto
response = requests.post(
    "http://localhost:8005/upload",
    files={"file": open("project_image.jpg", "rb")},
    data={
        "service_source": "projects",
        "reference_id": "project_456"
    }
)
```

## 📊 Características Técnicas

### Validaciones
- **Formato de archivo** según extensión
- **Tamaño máximo** configurable
- **Tipo MIME** real del archivo
- **Sanitización** de nombres de archivo

### Procesamiento
- **Optimización automática** de imágenes
- **Creación de miniaturas** (150x150px)
- **Extracción de metadatos** de documentos
- **Logs de procesamiento** detallados

### Seguridad
- **Validación de tipos MIME** reales
- **Sanitización** de nombres de archivo
- **Control de acceso** por archivo
- **Tokens de acceso** opcionales

### Almacenamiento
- **Organización por tipo** (image/document)
- **Nombres únicos** con timestamp y UUID
- **Metadatos completos** en base de datos
- **Limpieza automática** al eliminar

## 🚀 Despliegue

### Desarrollo
```bash
python main.py
```

### Producción
```bash
uvicorn main:app --host 0.0.0.0 --port 8005
```

### Docker (futuro)
```bash
docker build -t media-service .
docker run -p 8005:8005 media-service
```

## 📈 Monitoreo

### Health Check
```bash
curl http://localhost:8005/health
```

### Métricas
- Archivos subidos por tipo
- Tiempo de procesamiento
- Errores de validación
- Uso de almacenamiento

## 🔄 Próximas Mejoras

- [ ] **OCR** para documentos
- [ ] **Compresión** de videos
- [ ] **CDN** para archivos públicos
- [ ] **Backup automático** de archivos
- [ ] **Migración** a PostgreSQL
- [ ] **Docker** containerización
- [ ] **CI/CD** pipeline

## 📞 Soporte

Para reportar problemas o solicitar nuevas funcionalidades, crear un issue en el repositorio del proyecto. 