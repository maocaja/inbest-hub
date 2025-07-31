# 🤖 Ingestion Agent Service

Servicio de agente conversacional inteligente para asistir en la ingestión y completado de información de proyectos inmobiliarios.

## 🎯 Descripción

El **Ingestion Agent Service** es un microservicio que proporciona un asistente conversacional tipo ChatGPT para ayudar a los asesores inmobiliarios a completar la información de proyectos de manera eficiente y estructurada.

### ✨ Características Principales

- **💬 Chat Conversacional**: Interfaz de chat natural en español
- **📄 Procesamiento de Documentos**: Extracción automática de PDF, DOCX, Excel
- **🧠 IA Inteligente**: Integración con OpenAI GPT-4
- **🔗 Integración con Servicios**: Comunicación con project-owners-service y projects-service
- **📊 Seguimiento de Progreso**: Monitoreo de completitud de proyectos
- **🔄 Tool Calling**: Llamadas automáticas a APIs externas
- **📝 Generación de Descripciones**: Creación automática de descripciones profesionales

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                Ingestion Agent Service                     │
├─────────────────────────────────────────────────────────────┤
│  📄 Document Processor  │  💬 Chat Interface  │  🧠 LLM   │
│  - PDF/DOCX/Excel      │  - REST API         │  - GPT-4  │
│  - Data Extraction     │  - WebSocket        │  - Tools  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Tool Calling                            │
├─────────────────────────────────────────────────────────────┤
│  🔍 get_project_by_id()     │  📝 update_project_fields() │
│  📋 list_missing_fields()    │  📄 generate_description()  │
│  🏗️ create_project()        │  ✅ validate_project()      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                       │
├─────────────────────────────────────────────────────────────┤
│  project-owners-service  │  projects-service              │
│  (puerto 8002)          │  (puerto 8003)                │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Instalación

### Prerrequisitos

- Python 3.8+
- OpenAI API Key
- Servicios externos corriendo (project-owners-service, projects-service)

### Configuración Rápida

1. **Clonar y navegar al directorio**:
```bash
cd services/ingestion-agent-service
```

2. **Ejecutar configuración automática**:
```bash
python3 setup.py
```

3. **Configurar OpenAI API Key**:
```bash
# Editar archivo .env
OPENAI_API_KEY=tu_api_key_aqui
```

4. **Ejecutar el servicio**:
```bash
python3 main.py
```

### Configuración Manual

1. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

2. **Crear archivo .env**:
```bash
cp env.example .env
# Editar .env con tu configuración
```

3. **Crear directorios**:
```bash
mkdir -p uploads logs tests examples
```

## 📋 Endpoints API

### Sesiones de Ingestión

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/ingest/start` | Iniciar nueva sesión |
| `POST` | `/ingest/message` | Enviar mensaje al agente |
| `GET` | `/ingest/status/{session_id}` | Estado de la sesión |

### Documentos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/ingest/upload` | Subir y procesar documento |
| `GET` | `/ingest/supported-formats` | Formatos soportados |

### Utilidades

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/ingest/generate-description` | Generar descripción |
| `GET` | `/ingest/sessions/{session_id}/history` | Historial de chat |
| `GET` | `/ingest/sessions/{session_id}/documents` | Documentos de sesión |

## 💬 Ejemplos de Uso

### 1. Iniciar Sesión

```bash
curl -X POST http://localhost:8004/ingest/start \
  -H 'Content-Type: application/json' \
  -d '{
    "project_owner_nit": "900123456-7",
    "user_name": "Asesor Ejemplo"
  }'
```

**Respuesta**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "message": "Sesión iniciada exitosamente. ¡Hola! Soy tu asistente para proyectos inmobiliarios. ¿En qué puedo ayudarte hoy?"
}
```

### 2. Enviar Mensaje

```bash
curl -X POST http://localhost:8004/ingest/message \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Hola, quiero crear un proyecto residencial"
  }'
```

**Respuesta**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "assistant_message": "¡Hola! Me alegra ayudarte a crear un proyecto residencial. Para empezar, necesito algunos datos básicos:\n\n1. ¿Cuál es el nombre del proyecto?\n2. ¿En qué ciudad se ubicará?\n3. ¿Tienes algún documento con información del proyecto que puedas compartir?",
  "status": "active",
  "missing_fields": ["name", "location", "description"]
}
```

### 3. Subir Documento

```bash
curl -X POST http://localhost:8004/ingest/upload \
  -F 'session_id=550e8400-e29b-41d4-a716-446655440000' \
  -F 'file=@proyecto.pdf'
```

**Respuesta**:
```json
{
  "upload_id": 1,
  "processing_status": "completed",
  "extracted_data": {
    "name": "Residencial Los Pinos",
    "location": "Medellín, Antioquia",
    "price": "Desde $150,000,000"
  },
  "message": "¡Excelente! He procesado tu documento y extraje la siguiente información:\n\n📋 **Información extraída:**\n• **Nombre del proyecto:** Residencial Los Pinos\n• **Ubicación:** Medellín, Antioquia\n• **Precio:** Desde $150,000,000\n\n¿Te gustaría que complete la información faltante o que corrija algún dato extraído?"
}
```

### 4. Obtener Estado

```bash
curl http://localhost:8004/ingest/status/550e8400-e29b-41d4-a716-446655440000
```

**Respuesta**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "completion_percentage": 65,
  "current_step": "collecting_amenities",
  "project_data": {
    "name": "Residencial Los Pinos",
    "location": "Medellín, Antioquia",
    "price_info": {"min_price": 150000000}
  },
  "missing_fields": ["amenities", "delivery_date", "contact_info"]
}
```

## 📄 Formatos de Documento Soportados

- **PDF** (`.pdf`): Documentos de texto e imágenes
- **Word** (`.docx`): Documentos de Microsoft Word
- **Excel** (`.xlsx`, `.xls`): Hojas de cálculo
- **Imágenes** (`.jpg`, `.jpeg`, `.png`): Imágenes (OCR futuro)

## 🧠 Integración con LLM

### Prompt Base del Agente

```
Eres un asistente experto en proyectos inmobiliarios. Tu trabajo es asistir a un asesor humano para completar toda la información de un proyecto nuevo de vivienda basado en documentos o conversación.

Tu comportamiento debe ser:
- Amable, profesional y centrado en la tarea
- Capaz de interpretar respuestas ambiguas del usuario
- Capaz de ignorar o redirigir temas irrelevantes de forma educada
- Siempre enfocado en completar todos los campos requeridos del proyecto

Tienes acceso a herramientas como:
- get_project_by_id(project_id)
- update_project_fields(project_id, fields)
- list_missing_fields(project_id)
- generate_project_description(project_id)

Nunca inventes información. Siempre valida el estado actual del proyecto con list_missing_fields.
Cuando todos los campos estén completos, informa al usuario y sugiere generar la descripción final automáticamente.

Responde en español de manera natural y conversacional.
```

### Tool Calling

El agente puede llamar automáticamente a las siguientes herramientas:

- **`get_project_by_id(project_id)`**: Obtener datos de un proyecto
- **`update_project_fields(project_id, fields)`**: Actualizar campos del proyecto
- **`list_missing_fields(project_id)`**: Listar campos faltantes
- **`generate_project_description(project_id)`**: Generar descripción automática

## 🗄️ Modelos de Base de Datos

### ConversationSession
- `session_id`: Identificador único de la sesión
- `project_owner_nit`: NIT de la constructora asociada
- `status`: Estado de la sesión (active, paused, completed, cancelled)
- `current_step`: Paso actual del proceso
- `user_id`, `user_name`: Información del usuario

### ConversationMessage
- `session_id`: Referencia a la sesión
- `role`: Rol del mensaje (user, assistant, system)
- `content`: Contenido del mensaje
- `timestamp`: Fecha y hora del mensaje
- `message_type`: Tipo de mensaje (text, file, action)

### DocumentUpload
- `session_id`: Referencia a la sesión
- `filename`, `file_path`: Información del archivo
- `processing_status`: Estado del procesamiento
- `extracted_data`: Datos extraídos del documento

### ProjectDraft
- `session_id`: Referencia a la sesión
- `project_data`: Datos completos del proyecto (JSON)
- `completion_percentage`: Porcentaje de completitud
- `status`: Estado del borrador (draft, ready, published)

## ⚙️ Configuración

### Variables de Entorno

```bash
# Server Configuration
PORT=8004
HOST=0.0.0.0
DEBUG=True
RELOAD=True

# Database Configuration
DATABASE_URL=sqlite:///./ingestion_agent.db

# OpenAI Configuration
OPENAI_API_KEY=tu_api_key_aqui
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7

# External Services
PROJECT_OWNERS_SERVICE_URL=http://localhost:8002
PROJECTS_SERVICE_URL=http://localhost:8003

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB
```

## 🧪 Testing

### Ejecutar Tests Básicos

```bash
python3 test_service.py
```

### Tests Incluidos

- ✅ Importaciones de módulos
- ✅ Configuración del sistema
- ✅ Conexión a base de datos
- ✅ Procesador de documentos
- ✅ Servicio LLM
- ✅ Servicio de ingestión
- ✅ Rutas FastAPI
- ✅ Endpoints API
- ✅ Integración con OpenAI

## 📊 Monitoreo y Logs

### Niveles de Log

- **INFO**: Operaciones normales
- **WARNING**: Advertencias no críticas
- **ERROR**: Errores que requieren atención
- **DEBUG**: Información detallada para desarrollo

### Métricas Importantes

- Tiempo de respuesta del LLM
- Tasa de éxito en procesamiento de documentos
- Porcentaje de completitud promedio
- Número de sesiones activas

## 🔧 Desarrollo

### Estructura del Proyecto

```
ingestion-agent-service/
├── main.py                 # Aplicación principal FastAPI
├── config.py              # Configuración centralizada
├── requirements.txt       # Dependencias Python
├── setup.py              # Script de configuración automática
├── test_service.py       # Tests básicos
├── env.example           # Variables de entorno de ejemplo
├── README.md             # Documentación
├── database/
│   └── database.py       # Configuración de base de datos
├── models/
│   └── models.py         # Modelos SQLAlchemy
├── schemas/
│   └── schemas.py        # Esquemas Pydantic
├── services/
│   ├── ingestion_service.py  # Servicio principal
│   └── llm_service.py       # Servicio LLM
├── utils/
│   └── document_processor.py # Procesador de documentos
├── uploads/              # Directorio para archivos temporales
├── logs/                 # Directorio para logs
├── tests/                # Tests adicionales
└── examples/             # Ejemplos de uso
```

### Comandos de Desarrollo

```bash
# Ejecutar en modo desarrollo
python3 main.py

# Ejecutar con uvicorn
uvicorn main:app --host 0.0.0.0 --port 8004 --reload

# Ejecutar tests
python3 test_service.py

# Ver documentación API
# Abrir http://localhost:8004/docs
```

## 🤝 Integración con Otros Servicios

### Comunicación con project-owners-service

```python
# Verificar existencia de constructora
response = requests.get(f"{PROJECT_OWNERS_SERVICE_URL}/project-owners/nit/{nit}")
```

### Comunicación con projects-service

```python
# Crear proyecto
response = requests.post(f"{PROJECTS_SERVICE_URL}/projects", json=project_data)

# Actualizar proyecto
response = requests.put(f"{PROJECTS_SERVICE_URL}/projects/{project_id}", json=updates)
```

## 🚨 Troubleshooting

### Problemas Comunes

1. **Error de OpenAI API Key**:
   - Verificar que la API key esté configurada en `.env`
   - Verificar que la API key sea válida

2. **Error de conexión a servicios externos**:
   - Verificar que project-owners-service esté corriendo en puerto 8002
   - Verificar que projects-service esté corriendo en puerto 8003

3. **Error de procesamiento de documentos**:
   - Verificar que el archivo no exceda el tamaño máximo (10MB)
   - Verificar que el formato sea soportado

4. **Error de base de datos**:
   - Verificar que el directorio tenga permisos de escritura
   - Verificar que SQLite esté disponible

### Logs de Debug

```bash
# Cambiar nivel de log a DEBUG en .env
LOG_LEVEL=DEBUG

# Ver logs en tiempo real
tail -f logs/ingestion_agent.log
```

## 📈 Roadmap

### Próximas Funcionalidades

- [ ] **WebSocket para chat en tiempo real**
- [ ] **OCR para imágenes**
- [ ] **Validación avanzada de datos**
- [ ] **Templates de proyectos**
- [ ] **Exportación de datos**
- [ ] **Analytics y métricas**
- [ ] **Multiidioma**
- [ ] **Integración con CRM**

### Mejoras Técnicas

- [ ] **Caché Redis**
- [ ] **Queue para procesamiento asíncrono**
- [ ] **Métricas Prometheus**
- [ ] **Health checks avanzados**
- [ ] **Rate limiting**
- [ ] **Autenticación JWT**

## 📄 Licencia

Este proyecto es parte del backend inmobiliario y está sujeto a los términos de la licencia del proyecto principal.

## 🤝 Contribución

Para contribuir al desarrollo:

1. Crear una rama para tu feature
2. Implementar los cambios
3. Ejecutar tests
4. Crear pull request

## 📞 Soporte

Para soporte técnico o preguntas sobre el servicio:

- Crear un issue en el repositorio
- Revisar la documentación en `/docs`
- Verificar los logs del servicio
