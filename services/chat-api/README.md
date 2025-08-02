# Chat API

API de chat inteligente para proyectos inmobiliarios con análisis de intención, búsqueda semántica y respuestas naturales generadas por LLM.

## 🚀 Características

- **Análisis de Intención**: Detección automática de la intención del usuario usando OpenAI
- **Búsqueda Semántica**: Búsqueda inteligente de proyectos usando embeddings
- **Respuestas Naturales**: Respuestas generadas por LLM, no respuestas quemadas
- **Ranking Inteligente**: Sistema de ranking multi-criterio para proyectos
- **Gestión de Conversaciones**: Historial completo de conversaciones
- **Personalización**: Adaptación basada en preferencias del usuario
- **Detección de Leads**: Identificación automática de oportunidades de venta

## 📋 Requisitos

- Python 3.8+
- OpenAI API Key
- Servicios externos:
  - Embedding Service (puerto 8005)
  - Projects Service (puerto 8003)

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
cd services/chat-api
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

4. **Configurar OpenAI API Key**
```bash
# En .env
OPENAI_API_KEY=your_openai_api_key_here
```

## ⚙️ Configuración

### Variables de Entorno

```env
# Servidor
PORT=8006
HOST=0.0.0.0

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=500

# Base de datos
DATABASE_URL=sqlite:///./chat_api.db

# Servicios externos
EMBEDDING_SERVICE_URL=http://localhost:8005
PROJECTS_SERVICE_URL=http://localhost:8003

# Configuración
MAX_CONVERSATION_HISTORY=10
SEARCH_MAX_RESULTS=10
LOG_LEVEL=INFO
REQUEST_TIMEOUT=30.0
```

## 🚀 Uso

### Iniciar el servicio

```bash
python main.py
```

El servicio estará disponible en `http://localhost:8006`

### Documentación API

- **Swagger UI**: `http://localhost:8006/docs`
- **ReDoc**: `http://localhost:8006/redoc`

## 📚 Endpoints

### 1. Chat Conversation

**POST** `/chat/conversation`

Procesa un mensaje del usuario y genera una respuesta natural.

```json
{
  "message": "Busco apartamentos en Chapinero con piscina",
  "conversation_id": "conv_123",  // opcional
  "user_id": "user_456"           // opcional
}
```

**Respuesta:**
```json
{
  "conversation_id": "conv_123",
  "response": "¡Perfecto! Encontré 3 proyectos en Chapinero que podrían interesarte...",
  "projects": [
    {
      "id": 1,
      "name": "Residencial El Bosque",
      "location": {"city": "Chapinero", "department": "Cundinamarca"},
      "price_info": {"min_price": 350000000, "max_price": 550000000},
      "amenities": ["piscina", "gimnasio", "seguridad 24/7"],
      "final_score": 0.95
    }
  ],
  "suggestions": [
    "Ver más detalles del Residencial El Bosque",
    "Filtrar por amenities específicas",
    "Comparar proyectos"
  ],
  "metadata": {
    "intent": {"type": "search_projects", "confidence": 0.95},
    "lead_opportunity": true,
    "projects_count": 3
  }
}
```

### 2. Obtener Conversaciones

**GET** `/chat/conversations/{user_id}`

Obtiene todas las conversaciones de un usuario.

### 3. Obtener Mensajes

**GET** `/chat/conversations/{conversation_id}/messages`

Obtiene todos los mensajes de una conversación.

### 4. Cerrar Conversación

**DELETE** `/chat/conversations/{conversation_id}`

Cierra una conversación.

### 5. Búsqueda Directa

**POST** `/chat/search`

Búsqueda directa de proyectos.

```json
{
  "query": "apartamentos bogotá piscina",
  "filters": {
    "location": "Chapinero",
    "price_range": {"min": 300000000, "max": 600000000},
    "amenities": ["piscina"]
  },
  "max_results": 10
}
```

### 6. Health Check

**GET** `/health`

Verificación de salud del servicio.

## 🧠 Funcionalidades Avanzadas

### Análisis de Intención

El sistema analiza automáticamente la intención del usuario:

- `search_projects`: Búsqueda de proyectos
- `get_project_details`: Detalles de proyecto específico
- `greeting`: Saludo inicial
- `goodbye`: Despedida
- `help`: Solicitud de ayuda

### Ranking Inteligente

Sistema de ranking multi-criterio:

- **40%** - Score semántico (búsqueda vectorial)
- **25%** - Ubicación
- **20%** - Precio
- **10%** - Amenities
- **5%** - Disponibilidad

### Personalización

El sistema aprende de las preferencias del usuario:

- Zonas preferidas
- Rango de precio
- Tipo de propiedad
- Amenities favoritas

### Detección de Leads

Identifica automáticamente oportunidades de venta basado en:

- Palabras clave de interés
- Proyectos en resultados
- Conversación avanzada

## 🗄️ Base de Datos

### Tablas

- **conversations**: Gestión de conversaciones
- **messages**: Historial de mensajes
- **users**: Información de usuarios
- **project_interactions**: Interacciones con proyectos
- **leads**: Gestión de leads

### Estructura

```sql
-- Conversaciones
CREATE TABLE conversations (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    status VARCHAR DEFAULT 'active',
    metadata JSONB,
    message_count INTEGER DEFAULT 0
);

-- Mensajes
CREATE TABLE messages (
    id VARCHAR PRIMARY KEY,
    conversation_id VARCHAR REFERENCES conversations(id),
    role VARCHAR NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP,
    metadata JSONB
);
```

## 🔧 Desarrollo

### Estructura del Proyecto

```
chat-api/
├── main.py                    # Aplicación FastAPI
├── config.py                  # Configuración
├── requirements.txt           # Dependencias
├── env.example               # Variables de entorno
├── README.md                 # Documentación
├── schemas/
│   ├── __init__.py
│   └── schemas.py            # Esquemas Pydantic
├── services/
│   ├── __init__.py
│   ├── chat_service.py       # Servicio principal
│   ├── openai_service.py     # Integración OpenAI
│   ├── search_service.py     # Búsqueda semántica
│   ├── conversation_service.py # Gestión conversaciones
│   └── response_generator.py # Generador de respuestas
├── models/
│   └── __init__.py
├── database/
│   ├── __init__.py
│   ├── models.py             # Modelos SQLAlchemy
│   └── database.py           # Configuración BD
└── tests/
    └── __init__.py
```

### Testing

```bash
# Ejecutar tests
pytest tests/

# Test específico
pytest tests/test_chat_service.py
```

### Logs

Los logs se guardan en `chat_api.log` con rotación diaria.

## 🤝 Integración

### Servicios Externos

- **Embedding Service** (puerto 8005): Búsqueda semántica
- **Projects Service** (puerto 8003): Datos de proyectos

### Flujo de Integración

1. Usuario envía mensaje
2. Análisis de intención con OpenAI
3. Búsqueda semántica en Embedding Service
4. Obtención de detalles en Projects Service
5. Ranking y filtrado
6. Generación de respuesta natural
7. Guardado en base de datos

## 🚀 Deployment

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

```env
OPENAI_API_KEY=your_production_key
DATABASE_URL=postgresql://user:password@localhost/chat_api
LOG_LEVEL=WARNING
```

## 📊 Monitoreo

### Métricas

- Conversaciones activas
- Tasa de conversión de leads
- Tiempo de respuesta
- Errores por endpoint

### Health Check

```bash
curl http://localhost:8006/health
```

## 🔒 Seguridad

- Validación de entrada con Pydantic
- Manejo de errores robusto
- Timeouts en servicios externos
- Logging de errores

## 📝 Licencia

MIT License

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch
3. Commit cambios
4. Push al branch
5. Crear Pull Request

## 📞 Soporte

Para soporte técnico, contactar al equipo de desarrollo.
