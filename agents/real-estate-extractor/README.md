# Real Estate Data Extractor Agent

Agente especializado en extraer información de proyectos inmobiliarios desde documentos PDF, DOCX y Excel, y completar datasets estructurados.

## Características

- **Procesamiento de documentos**: PDF, DOCX, Excel (XLSX, XLS)
- **Extracción inteligente**: Usa IA para extraer información relevante
- **Validación de datos**: Verifica completitud y consistencia
- **Completado automático**: Completa información faltante usando IA
- **Esquema estructurado**: Dataset completo de proyectos inmobiliarios

## Estructura del Dataset

El agente extrae información en el siguiente esquema JSON:

```json
{
  "project_id": "string",                 // ID único del proyecto
  "name": "string",                       // Nombre del proyecto
  "description": "string",                // Descripción breve del proyecto
  "builder": "string",                    // Constructora o desarrollador
  "status": "preventa | construcción | entregado", // Estado actual
  "delivery_date": "YYYY-MM",            // Fecha estimada de entrega

  "location": {
    "country": "string",                 // País (ej. Colombia)
    "department": "string",              // Departamento o estado
    "city": "string",                    // Ciudad o municipio
    "zone": "string",                    // Zona dentro de la ciudad
    "neighborhood": "string",            // Barrio o sector
    "latitude": "float",
    "longitude": "float"
  },

  "price_info": {
    "currency": "COP | USD | ...",       // Moneda
    "price_min": "number",               // Precio más bajo de unidad
    "price_max": "number",               // Precio más alto
    "price_per_m2": "number",            // (opcional) Precio promedio por m²
    "maintenance_fee": "number"          // Cuota de administración mensual
  },

  "unit_info": {
    "unit_types": ["apartamento", "casa", "duplex"], // Tipos disponibles
    "area_m2_min": "number",
    "area_m2_max": "number",
    "bedrooms_min": "integer",
    "bedrooms_max": "integer",
    "bathrooms_min": "integer",
    "bathrooms_max": "integer",
    "parking_min": "integer",
    "parking_max": "integer",
    "balcony": true,
    "storage_room": true
  },

  "amenities": {
    "list": [
      "zona BBQ", 
      "piscina", 
      "coworking", 
      "juegos infantiles", 
      "gimnasio"
    ],
    "green_areas": true,
    "pet_friendly": true,
    "security_features": [
      "portería 24h", 
      "circuito cerrado", 
      "acceso biométrico"
    ]
  },

  "financial_info": {
    "offers_financing": true,            // ¿El proyecto tiene financiación?
    "down_payment_percent": "number",    // % cuota inicial
    "installment_months": "integer",     // Cuotas/plazo
    "expected_rent": "number",           // Renta esperada mensual
    "appreciation_rate": "float",        // % valorización anual esperada
    "investment_horizon_years": "integer"
  },

  "audience_info": {
    "target_audience": ["familias", "inversionistas", "estudiantes"],
    "usage_type": "vivienda | inversión | vacacional",
    "income_level": "bajo | medio | alto"
  },

  "media": {
    "images": ["url1", "url2", "url3"],
    "videos": ["video_url"],
    "brochure_url": "pdf_url",
    "virtual_tour_url": "tour_url"
  }
}
```

## Instalación

1. **Clonar el repositorio**:
```bash
cd agents/real-estate-extractor
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tu API key de OpenAI
```

4. **Ejecutar el agente**:
```bash
python main.py
```

El agente estará disponible en `http://localhost:8012`

## API Endpoints

### 1. Extraer datos de documento
```http
POST /extract
Content-Type: multipart/form-data

file: [archivo PDF/DOCX/Excel]
```

**Respuesta**:
```json
{
  "success": true,
  "project_data": {
    // Datos del proyecto extraídos
  },
  "validation_result": {
    "is_valid": true,
    "errors": [],
    "warnings": [],
    "completeness_score": 85.5,
    "suggestions": []
  },
  "message": "Datos extraídos exitosamente"
}
```

### 2. Validar datos del proyecto
```http
POST /validate
Content-Type: application/json

{
  // Datos del proyecto a validar
}
```

### 3. Completar información faltante
```http
POST /complete
Content-Type: application/json

{
  // Datos del proyecto con campos faltantes
}
```

### 4. Obtener esquema JSON
```http
GET /schema
```

## Uso como Asesor Inmobiliario

El agente actúa como un asistente especializado que:

1. **Extrae información precisa** de documentos inmobiliarios
2. **Valida la completitud** de los datos
3. **Sugiere mejoras** para completar información faltante
4. **Mantiene consistencia** en el formato de datos
5. **Proporciona feedback** sobre la calidad de la información

### Flujo de trabajo recomendado:

1. **Cargar documento**: Subir PDF, DOCX o Excel con información del proyecto
2. **Revisar extracción**: Verificar datos extraídos y validación
3. **Completar información**: Usar el endpoint `/complete` para llenar campos faltantes
4. **Validar final**: Verificar que todos los datos sean correctos
5. **Exportar dataset**: Obtener JSON estructurado para análisis

## Configuración

### Variables de entorno (.env):
```env
OPENAI_API_KEY=tu_api_key_aqui
PORT=8012
LOG_LEVEL=INFO
```

### Configuración de logging:
El agente incluye logging detallado para debugging y monitoreo.

## Dependencias principales

- **FastAPI**: Framework web para la API
- **PyPDF2**: Procesamiento de PDFs
- **python-docx**: Procesamiento de documentos Word
- **openpyxl/pandas**: Procesamiento de Excel
- **OpenAI**: IA para extracción y completado de datos
- **Pydantic**: Validación de esquemas

## Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear una rama para tu feature
3. Implementar cambios
4. Agregar tests
5. Crear Pull Request

## Licencia

MIT License 