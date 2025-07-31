# Project Owners Service

Servicio para gestionar constructoras y propietarios de proyectos inmobiliarios. Este es el primer microservicio del backend inmobiliario que maneja el CRUD básico de constructoras.

## Características

- **CRUD completo** de constructoras/propietarios de proyectos
- **Validaciones** de NIT único y email único
- **Base de datos PostgreSQL** con SQLAlchemy
- **API REST** con FastAPI
- **Validación de datos** con Pydantic
- **Logging** detallado para debugging

## Estructura del Proyecto

```
services/project-owners-service/
├── main.py                 # Aplicación FastAPI principal
├── config.py              # Configuración del servicio
├── requirements.txt       # Dependencias
├── env.example           # Variables de entorno de ejemplo
├── README.md             # Documentación
├── database/
│   └── database.py       # Configuración de base de datos
├── models/
│   └── models.py         # Modelos SQLAlchemy
├── schemas/
│   └── schemas.py        # Esquemas Pydantic
└── services/
    └── project_owners_service.py  # Lógica de negocio
```

## Instalación

1. **Clonar el repositorio**:
```bash
cd services/project-owners-service
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar base de datos PostgreSQL**:
```bash
# Crear base de datos
createdb project_owners_db

# O usar Docker
docker run --name postgres-project-owners \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=project_owners_db \
  -p 5432:5432 \
  -d postgres:13
```

4. **Configurar variables de entorno**:
```bash
cp env.example .env
# Editar .env con tu configuración de base de datos
```

5. **Ejecutar el servicio**:
```bash
python main.py
```

El servicio estará disponible en `http://localhost:8001`

## API Endpoints

### 1. Health Check
```http
GET /health
```

### 2. Crear Constructora
```http
POST /project-owners
Content-Type: application/json

{
  "name": "Constructora ABC",
  "nit": "900123456-7",
  "email": "contacto@constructoraabc.com",
  "phone": "+57 300 123 4567",
  "city": "Medellín",
  "department": "Antioquia",
  "country": "Colombia",
  "website": "https://constructoraabc.com",
  "contact_person": "Juan Pérez",
  "contact_phone": "+57 300 987 6543",
  "contact_email": "juan.perez@constructoraabc.com"
}
```

### 3. Obtener Constructoras
```http
GET /project-owners?skip=0&limit=10
```

### 4. Obtener Constructora por ID
```http
GET /project-owners/{id}
```

### 5. Actualizar Constructora
```http
PUT /project-owners/{id}
Content-Type: application/json

{
  "name": "Constructora ABC Actualizada",
  "phone": "+57 300 111 2222"
}
```

### 6. Eliminar Constructora
```http
DELETE /project-owners/{id}
```

### 7. Buscar por NIT
```http
GET /project-owners/nit/{nit}
```

## Modelo de Datos

### ProjectOwner

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| id | Integer | Sí | ID único (auto-increment) |
| name | String(100) | Sí | Nombre de la constructora |
| nit | String(20) | Sí | NIT único |
| email | String(255) | Sí | Email único |
| phone | String(20) | No | Teléfono principal |
| address | Text | No | Dirección física |
| city | String(100) | Sí | Ciudad |
| department | String(100) | No | Departamento |
| country | String(100) | Sí | País (default: Colombia) |
| website | String(255) | No | Sitio web |
| contact_person | String(100) | No | Persona de contacto |
| contact_phone | String(20) | No | Teléfono de contacto |
| contact_email | String(255) | No | Email de contacto |
| is_active | Boolean | Sí | Estado activo (default: true) |
| is_verified | Boolean | Sí | Estado verificado (default: false) |
| created_at | DateTime | Sí | Fecha de creación |
| updated_at | DateTime | Sí | Fecha de actualización |

## Validaciones

### NIT
- Debe contener solo números, guiones y puntos
- Longitud mínima: 8 caracteres
- Longitud máxima: 20 caracteres
- Debe ser único en la base de datos

### Email
- Debe ser un email válido
- Debe ser único en la base de datos

### Teléfono
- Debe contener solo números, espacios, guiones y +
- Longitud máxima: 20 caracteres

### Nombre
- Longitud mínima: 2 caracteres
- Longitud máxima: 100 caracteres

## Estados

### is_active
- `true`: Constructora activa
- `false`: Constructora inactiva (soft delete)

### is_verified
- `true`: Constructora verificada
- `false`: Constructora pendiente de verificación

## Ejemplos de Uso

### Crear una constructora
```python
import requests

url = "http://localhost:8001/project-owners"
data = {
    "name": "Constructora XYZ",
    "nit": "800987654-3",
    "email": "info@constructoraXYZ.com",
    "city": "Bogotá",
    "department": "Cundinamarca",
    "country": "Colombia"
}

response = requests.post(url, json=data)
print(response.json())
```

### Obtener constructoras
```python
import requests

url = "http://localhost:8001/project-owners"
response = requests.get(url)
project_owners = response.json()
print(f"Total constructoras: {len(project_owners)}")
```

### Buscar por NIT
```python
import requests

nit = "900123456-7"
url = f"http://localhost:8001/project-owners/nit/{nit}"
response = requests.get(url)

if response.status_code == 200:
    constructora = response.json()
    print(f"Constructora encontrada: {constructora['name']}")
else:
    print("Constructora no encontrada")
```

## Configuración

### Variables de Entorno (.env)

```env
# Server Configuration
PORT=8001
HOST=0.0.0.0
DEBUG=True
RELOAD=True

# Logging Configuration
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/project_owners_db

# Development Configuration
ENVIRONMENT=development
```

### Configuración de Base de Datos

El servicio usa PostgreSQL con las siguientes configuraciones:

- **Pool de conexiones**: Configurado para reciclar conexiones cada 300 segundos
- **Echo**: Habilitado en modo debug para ver queries SQL
- **Timezone**: Configurado para usar timezone del servidor

## Logging

El servicio incluye logging detallado para:

- Creación, actualización y eliminación de constructoras
- Errores de validación
- Errores de base de datos
- Operaciones de búsqueda

## Próximos Pasos

Este servicio es la base para:

1. **projects-service**: CRUD de proyectos inmobiliarios
2. **ingestion-agent-service**: Agente conversacional para completar proyectos
3. **media-service**: Gestión de archivos multimedia
4. **embedding-service**: Búsqueda semántica

## Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear una rama para tu feature
3. Implementar cambios
4. Agregar tests
5. Crear Pull Request

## Licencia

MIT License 