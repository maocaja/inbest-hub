from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from config import Config
from .models import Base
from loguru import logger

# Crear engine
engine = create_engine(
    Config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {}
)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Inicializar la base de datos"""
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        raise

def get_db() -> Session:
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crear todas las tablas"""
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas creadas correctamente")

def drop_tables():
    """Eliminar todas las tablas"""
    Base.metadata.drop_all(bind=engine)
    logger.info("Tablas eliminadas correctamente") 