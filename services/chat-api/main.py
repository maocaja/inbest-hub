from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import uvicorn
from datetime import datetime
from typing import List, Dict, Any
import os

from config import Config
from services.chat_service import ChatService
from schemas.schemas import (
    ChatRequest, ChatResponse, ConversationInfo, MessageInfo,
    HealthResponse, SearchRequest, SearchResponse
)
from database.database import init_db

# Configurar logging
logger.add("chat_api.log", rotation="1 day", retention="7 days", level=Config.LOG_LEVEL)

# Crear aplicación FastAPI
app = FastAPI(
    title="Chat API",
    description="API de chat inteligente para proyectos inmobiliarios",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS de forma segura
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend local
        "https://inbest.com",      # Frontend producción
        "https://app.inbest.com"   # App producción
    ],
    allow_credentials=False,  # No permitir credenciales para APIs públicas
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["X-Total-Count"],
    max_age=3600,  # Cache CORS por 1 hora
)

# Middleware para Security Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Middleware para agregar headers de seguridad"""
    response = await call_next(request)
    
    # Security Headers según OWASP
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # Headers adicionales de seguridad
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

# Inicializar servicios
chat_service = ChatService()

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("Iniciando Chat API con configuración de seguridad...")
    
    try:
        # Validar configuración
        Config.validate()
        logger.info("Configuración validada correctamente")
        
        # Inicializar base de datos
        init_db()
        logger.info("Base de datos inicializada correctamente")
        
        # Verificar servicios externos
        try:
            health_status = await chat_service.health_check()
            logger.info(f"Estado de servicios: {health_status}")
        except Exception as e:
            logger.warning(f"No se pudo verificar servicios externos: {e}")
        
        logger.info("Chat API iniciado correctamente con headers de seguridad")
        
    except Exception as e:
        logger.error(f"Error iniciando Chat API: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("Cerrando Chat API...")

# Endpoints principales

@app.post("/chat/conversation", response_model=ChatResponse)
async def chat_conversation(request: ChatRequest):
    """
    Procesa un mensaje del usuario y genera una respuesta natural
    
    - **message**: Mensaje del usuario
    - **conversation_id**: ID de conversación existente (opcional)
    - **user_id**: ID del usuario (opcional)
    """
    try:
        logger.info(f"Procesando mensaje: {request.message[:50]}...")
        
        response = await chat_service.process_message(request)
        
        logger.info(f"Respuesta generada para conversación {response.conversation_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error procesando conversación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/chat/conversations/{user_id}", response_model=List[ConversationInfo])
async def get_user_conversations(user_id: str):
    """
    Obtiene todas las conversaciones de un usuario
    
    - **user_id**: ID del usuario
    """
    try:
        conversations = await chat_service.get_user_conversations(user_id)
        return conversations
        
    except Exception as e:
        logger.error(f"Error obteniendo conversaciones: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/chat/conversations/{conversation_id}/messages", response_model=List[MessageInfo])
async def get_conversation_messages(conversation_id: str):
    """
    Obtiene todos los mensajes de una conversación
    
    - **conversation_id**: ID de la conversación
    """
    try:
        messages = await chat_service.get_conversation_messages(conversation_id)
        return messages
        
    except Exception as e:
        logger.error(f"Error obteniendo mensajes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.delete("/chat/conversations/{conversation_id}")
async def close_conversation(conversation_id: str):
    """
    Cierra una conversación
    
    - **conversation_id**: ID de la conversación
    """
    try:
        success = await chat_service.close_conversation(conversation_id)
        
        if success:
            return {"message": f"Conversación {conversation_id} cerrada correctamente"}
        else:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
            
    except Exception as e:
        logger.error(f"Error cerrando conversación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/chat/search", response_model=SearchResponse)
async def search_projects(request: SearchRequest):
    """
    Búsqueda directa de proyectos
    
    - **query**: Query de búsqueda
    - **filters**: Filtros adicionales
    - **max_results**: Máximo número de resultados
    """
    try:
        from .services.search_service import SearchService
        search_service = SearchService()
        
        projects = await search_service.search_projects(request.filters or {})
        
        return SearchResponse(
            results=projects,
            total_results=len(projects),
            query=request.query,
            filters_applied=request.filters
        )
        
    except Exception as e:
        logger.error(f"Error en búsqueda directa: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Verificación de salud del servicio
    """
    try:
        health_status = await chat_service.health_check()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            services=health_status
        )
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            services={"error": str(e)}
        )

# Endpoints de utilidad

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Chat API - Servicio de chat inteligente para proyectos inmobiliarios",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/info")
async def get_info():
    """Información del servicio"""
    return {
        "service": "Chat API",
        "version": "1.0.0",
        "description": "API de chat inteligente para proyectos inmobiliarios",
        "features": [
            "Análisis de intención con OpenAI",
            "Búsqueda semántica de proyectos",
            "Respuestas naturales generadas por LLM",
            "Gestión de conversaciones",
            "Ranking inteligente de proyectos",
            "Detección de oportunidades de lead"
        ],
        "endpoints": {
            "chat": "/chat/conversation",
            "conversations": "/chat/conversations/{user_id}",
            "messages": "/chat/conversations/{conversation_id}/messages",
            "search": "/chat/search",
            "health": "/health"
        }
    }

# Manejo de errores global

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc)
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejador de excepciones HTTP"""
    logger.warning(f"Error HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True,
        log_level=Config.LOG_LEVEL.lower()
    )
