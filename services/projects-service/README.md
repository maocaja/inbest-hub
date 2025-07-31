# 🏗️ Projects Service

Servicio para gestión de proyectos inmobiliarios en el backend inmobiliario.

## 📋 Características

- **CRUD completo** para proyectos inmobiliarios
- **Estados de proyecto**: incompleto, en_proceso, completo, inactivo, archivado
- **Relación con constructoras** (project-owners-service)
- **Estructura de datos compleja** con información detallada de proyectos
- **Validaciones robustas** y manejo de errores
- **API RESTful** con documentación automática
- **Base de datos SQLite/PostgreSQL** con SQLAlchemy ORM

## 🏗️ Estructura del Proyecto

```
services/projects-service/
├── database/
│   ├── __init__.py
│   └── database.py          # Configuración de base de datos
├── models/
│   ├── __init__.py
│   └── models.py            # Modelos SQLAlchemy
├── schemas/
│   ├── __init__.py
│   └── schemas.py           # Esquemas Pydantic
├── services/
│   ├── __init__.py
│   └── projects_service.py  # Lógica de negocio
├── tests/
│   └── __init__.py
├── examples/
│   └── __init__.py
├── main.py                  # Aplicación FastAPI
├── config.py                # Configuración centralizada
├── requirements.txt         # Dependencias
├── setup.py                # Script de configuración
├── test_service.py         # Tests básicos
├── env.example             # Variables de entorno
└── README.md               # Documentación
```

## 🚀 Instalación y Configuración

### 1. Clonar y configurar entorno

```bash
# Activar entorno virtual
source ../../venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar variables según necesidad
nano .env
```

### 3. Ejecutar el servicio

```bash
# Ejecutar directamente
python main.py

# O con uvicorn
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

## 📊 Modelo de Datos

### Project (Proyecto Inmobiliario)

```json
{
  "id": 1,
  "name": "Residencial Los Pinos",
  "description": "Proyecto residencial de lujo en zona exclusiva",
  "status": "en_proceso",
  "project_owner_nit": "900123456-7",
  "location": {
    "address": "Calle 123 #45-67",
    "city": "Medellín",
    "department": "Antioquia",
    "country": "Colombia",
    "coordinates": {"lat": 6.2442, "lng": -75.5812}
  },
  "price_info": {
    "currency": "COP",
    "min_price": 150000000,
    "max_price": 450000000,
    "price_per_m2": 2500000
  },
  "unit_info": {
    "total_units": 120,
    "available_units": 45,
    "unit_types": ["Apartamento 2BR", "Apartamento 3BR", "Penthouse"],
    "areas": {
      "Apartamento 2BR": {"min": 65, "max": 85},
      "Apartamento 3BR": {"min": 95, "max": 120},
      "Penthouse": {"min": 150, "max": 200}
    }
  },
  "amenities": [
    "Piscina", "Gimnasio", "Zona BBQ", "Parqueadero cubierto",
    "Seguridad 24/7", "Área de juegos infantiles"
  ],
  "financial_info": {
    "delivery_date": "2024-12-31",
    "payment_plans": [
      {"name": "Plan 70/30", "description": "70% cuota inicial, 30% a 12 meses"}
    ],
    "financing_options": ["Banco A", "Banco B", "Leasing"]
  },
  "audience_info": {
    "target_audience": ["Familias", "Profesionales", "Inversionistas"],
    "income_levels": ["Medio-alto", "Alto"]
  },
  "media": {
    "images": ["url1", "url2"],
    "videos": ["url_video"],
    "documents": ["brochure.pdf"]
  },
  "is_active": true,
  "is_featured": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z"
}
```

## 🔌 Endpoints API

### Proyectos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/projects` | Crear nuevo proyecto |
| `GET` | `/projects` | Listar proyectos (con filtros) |
| `GET` | `/projects/{id}` | Obtener proyecto específico |
| `PUT` | `/projects/{id}` | Actualizar proyecto |
| `PATCH` | `/projects/{id}/state` | Cambiar estado del proyecto |
| `DELETE` | `/projects/{id}` | Eliminar proyecto (soft delete) |
| `GET` | `/projects/{id}/history` | Historial de cambios |
| `GET` | `/projects/owner/{nit}` | Proyectos por constructora |
| `GET` | `/projects/status/{status}` | Proyectos por estado |

### Utilidades

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Información del servicio |
| `GET` | `/health` | Health check |

## 🔍 Filtros Disponibles

### GET /projects

- `skip`: Número de registros a saltar (paginación)
- `limit`: Número máximo de registros (máx. 1000)
- `status`: Filtrar por estado (incompleto, en_proceso, completo, inactivo, archivado)
- `owner_nit`: Filtrar por NIT de constructora
- `active_only`: Solo proyectos activos (true/false)

### Ejemplos

```bash
# Todos los proyectos
curl http://localhost:8003/projects

# Proyectos en proceso
curl http://localhost:8003/projects?status=en_proceso

# Proyectos de una constructora específica
curl http://localhost:8003/projects?owner_nit=900123456-7

# Con paginación
curl http://localhost:8003/projects?skip=20&limit=10
```

## 📝 Estados de Proyecto

1. **incompleto**: Proyecto recién creado, faltan datos
2. **en_proceso**: Proyecto siendo completado
3. **completo**: Proyecto con toda la información
4. **inactivo**: Proyecto temporalmente desactivado
5. **archivado**: Proyecto eliminado (soft delete)

## 🔗 Relación con Project Owners

Cada proyecto debe estar asociado a una constructora válida:

- El `project_owner_nit` debe existir en la tabla `project_owners`
- La constructora debe estar activa (`is_active = true`)
- Se valida la existencia antes de crear/actualizar proyectos

## 🧪 Testing

### Tests básicos

```bash
# Ejecutar tests
python test_service.py
```

### Tests con curl

```bash
# Health check
curl http://localhost:8003/health

# Crear proyecto
curl -X POST http://localhost:8003/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Residencial Los Pinos",
    "description": "Proyecto residencial de lujo",
    "project_owner_nit": "900123456-7",
    "status": "incompleto"
  }'

# Listar proyectos
curl http://localhost:8003/projects

# Obtener proyecto específico
curl http://localhost:8003/projects/1

# Actualizar estado
curl -X PATCH http://localhost:8003/projects/1/state \
  -H "Content-Type: application/json" \
  -d '{"status": "en_proceso"}'
```

## ⚙️ Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `PORT` | Puerto del servidor | `8003` |
| `HOST` | Host del servidor | `0.0.0.0` |
| `DEBUG` | Modo debug | `True` |
| `RELOAD` | Auto-reload | `True` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `DATABASE_URL` | URL de base de datos | `sqlite:///./projects.db` |
| `ENVIRONMENT` | Entorno | `development` |

### Base de Datos

- **SQLite**: Para desarrollo local (`sqlite:///./projects.db`)
- **PostgreSQL**: Para producción (`postgresql://user:password@localhost:5432/projects_db`)

## 📊 Logging

El servicio incluye logging detallado:

- **INFO**: Operaciones exitosas
- **ERROR**: Errores y excepciones
- **DEBUG**: Información detallada (solo en modo debug)

## 🔒 Validaciones

### Proyecto

- **Nombre**: 2-100 caracteres
- **Descripción**: 10-2000 caracteres (opcional)
- **NIT**: Formato válido (números, guiones, puntos)
- **Precios**: Valores positivos
- **Unidades**: Números positivos

### Estados

- Solo estados válidos permitidos
- Transiciones controladas
- Validación de constructora activa

## 🚀 Próximos Pasos

1. **Integración con project-owners-service**
2. **Implementación de historial detallado**
3. **Sistema de búsqueda avanzada**
4. **API de estadísticas**
5. **Integración con media-service**
6. **Sistema de notificaciones**

## 📞 Soporte

Para soporte técnico o preguntas sobre el servicio, contactar al equipo de desarrollo.
