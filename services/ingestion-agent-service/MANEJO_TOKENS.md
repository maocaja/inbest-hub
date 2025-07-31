# 🔄 Manejo de Tokens y Modos del LLM

## 📊 **¿Qué son los tokens?**

Los **tokens** son unidades de texto que OpenAI usa para procesar:
- **1 token** ≈ 4 caracteres en inglés
- **1 token** ≈ 3-4 caracteres en español
- **Límite GPT-3.5**: 4,096 tokens por conversación
- **Límite GPT-4**: 8,192 tokens por conversación

### **Ejemplos de uso de tokens:**
- **Mensaje corto**: "Hola" = ~1 token
- **Mensaje medio**: "El proyecto tiene 50 apartamentos" = ~8 tokens
- **Documento PDF**: 1 página = ~500-1000 tokens
- **Conversación larga**: 50 mensajes = ~2000-3000 tokens

## ⚠️ **¿Qué pasa si se alcanza el límite?**

### **Error típico:**
```
Error: Maximum context length exceeded
```

### **Soluciones automáticas implementadas:**

#### **1. Truncamiento inteligente**
```python
# El sistema automáticamente:
# - Mantiene los últimos N mensajes
# - Elimina mensajes antiguos
# - Preserva el contexto importante
```

#### **2. Resumen de conversación**
```python
# Cuando se acerca al límite:
# - Genera resumen de la conversación
# - Mantiene solo puntos clave
# - Continúa con contexto resumido
```

#### **3. Reinicio de sesión**
```python
# Si no se puede continuar:
# - Sugiere crear nueva sesión
# - Guarda progreso actual
# - Permite continuar desde donde se quedó
```

## 🔧 **Cómo cambiar entre modos**

### **Modo Simulado (Sin costos)**
```bash
# Activar modo simulado
python3 switch_mode.py simulado

# Verificar modo actual
python3 switch_mode.py status

# Reiniciar servicio
pkill -f "python3 main.py"
python3 main.py &
```

### **Modo Real (Con OpenAI)**
```bash
# Activar modo real
python3 switch_mode.py real

# Verificar modo actual
python3 switch_mode.py status

# Reiniciar servicio
pkill -f "python3 main.py"
python3 main.py &
```

## 📈 **Monitoreo de uso de tokens**

### **En modo real:**
```json
{
  "usage": {
    "prompt_tokens": 1500,
    "completion_tokens": 200,
    "total_tokens": 1700
  }
}
```

### **En modo simulado:**
```json
{
  "usage": {
    "prompt_tokens": 1500,
    "completion_tokens": 200,
    "total_tokens": 1700
  }
}
```

## 🎯 **Estrategias para optimizar tokens**

### **1. Mensajes concisos**
```bash
# ❌ Mal: Muy largo
"El proyecto inmobiliario que estamos desarrollando en la ciudad de Bogotá, específicamente en la localidad de Chapinero, tiene un total de 50 apartamentos distribuidos en 2 torres de 25 pisos cada una, con amenidades que incluyen piscina, gimnasio, parqueadero, zona de BBQ, salón comunal, y áreas verdes..."

# ✅ Bien: Conciso
"Proyecto: 50 apartamentos en Chapinero, Bogotá. Amenidades: piscina, gimnasio, parqueadero."
```

### **2. Limpiar historial periódicamente**
```bash
# El sistema automáticamente:
# - Mantiene últimos 10 mensajes
# - Elimina contexto antiguo
# - Preserva información clave
```

### **3. Usar modo simulado para desarrollo**
```bash
# Para pruebas extensas:
python3 switch_mode.py simulado
# Sin límites de tokens
# Sin costos
# Respuestas predefinidas
```

## 🔄 **Comandos útiles**

### **Verificar modo actual:**
```bash
python3 switch_mode.py status
```

### **Cambiar a modo simulado:**
```bash
python3 switch_mode.py simulado
```

### **Cambiar a modo real:**
```bash
python3 switch_mode.py real
```

### **Ver uso de tokens en tiempo real:**
```bash
# En los logs del servicio verás:
# "total_tokens": 1700
```

## 💡 **Recomendaciones**

### **Para desarrollo:**
- ✅ Usar **modo simulado**
- ✅ Sin límites de tokens
- ✅ Sin costos
- ✅ Respuestas predecibles

### **Para producción:**
- ✅ Usar **modo real**
- ✅ Configurar límite de gasto
- ✅ Monitorear uso de tokens
- ✅ Optimizar mensajes

### **Para pruebas extensas:**
- ✅ Usar **modo simulado**
- ✅ Probar flujos completos
- ✅ Validar funcionalidades
- ✅ Sin preocuparse por límites

## 🚨 **Alertas automáticas**

El sistema detecta automáticamente:
- ⚠️ **80% del límite alcanzado**: Aviso preventivo
- 🚨 **90% del límite alcanzado**: Sugerencia de limpiar historial
- ❌ **100% del límite alcanzado**: Error con opciones de recuperación

## 📝 **Ejemplo de manejo de límite**

```python
# Cuando se alcanza el límite:
if total_tokens > max_tokens * 0.9:
    # Limpiar historial antiguo
    messages = messages[-5:]  # Mantener solo últimos 5
    
    # Agregar resumen
    summary = "Conversación anterior resumida..."
    messages.insert(0, {"role": "system", "content": summary})
    
    # Continuar normalmente
    continue_conversation()
```

---

**🎯 Con estas estrategias, puedes usar el sistema sin preocuparte por límites de tokens.** 