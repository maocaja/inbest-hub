import os
import shutil
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from models.models import MediaFile, FileProcessingLog
from schemas.schemas import MediaFileCreate, MediaFileUpdate
from utils.validators import (
    validate_file_extension, validate_file_size, validate_mime_type,
    get_file_type_from_extension, sanitize_filename, generate_unique_filename
)
from utils.optimizers import (
    optimize_image, extract_file_metadata, create_thumbnail
)
from config import Config

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, db: Session):
        self.db = db
    
    async def upload_file(
        self, 
        file: UploadFile, 
        uploaded_by: Optional[str] = None,
        service_source: Optional[str] = None,
        reference_id: Optional[str] = None,
        is_public: bool = True
    ) -> MediaFile:
        """
        Sube y procesa un archivo
        """
        try:
            # Validar extensión
            is_valid, error_msg = validate_file_extension(file.filename)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Validar tamaño
            file_content = await file.read()
            file_size = len(file_content)
            is_valid, error_msg = validate_file_size(file_size)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Obtener extensión y tipo
            _, extension = os.path.splitext(file.filename.lower())
            file_type = get_file_type_from_extension(extension)
            
            # Sanitizar nombre
            sanitized_filename = sanitize_filename(file.filename)
            
            # Determinar directorio de almacenamiento
            upload_dir = Config.get_upload_path(file_type)
            
            # Generar nombre único
            unique_filename = generate_unique_filename(sanitized_filename, upload_dir)
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Guardar archivo
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            # Validar tipo MIME
            is_valid, error_msg = validate_mime_type(file_path, extension)
            if not is_valid:
                os.remove(file_path)  # Limpiar archivo inválido
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Extraer metadatos
            metadata = extract_file_metadata(file_path, file_type)
            
            # Crear registro en BD
            media_file = MediaFile(
                filename=unique_filename,
                original_filename=sanitized_filename,
                file_path=file_path,
                file_type=file_type,
                mime_type=file.content_type,
                file_size=file_size,
                file_extension=extension,
                width=metadata.get('width'),
                height=metadata.get('height'),
                pages=metadata.get('pages'),
                duration=metadata.get('duration'),
                uploaded_by=uploaded_by,
                service_source=service_source,
                reference_id=reference_id,
                is_public=is_public,
                processing_metadata=metadata
            )
            
            self.db.add(media_file)
            self.db.commit()
            self.db.refresh(media_file)
            
            # Procesar archivo (optimizar imágenes, crear miniaturas, etc.)
            await self._process_file(media_file)
            
            logger.info(f"Archivo subido exitosamente: {unique_filename}")
            return media_file
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error subiendo archivo: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    
    async def _process_file(self, media_file: MediaFile) -> None:
        """
        Procesa un archivo después de subirlo
        """
        try:
            # Crear log de procesamiento
            log = FileProcessingLog(
                file_id=media_file.id,
                operation="upload",
                status="processing"
            )
            self.db.add(log)
            self.db.commit()
            
            # Procesar según el tipo
            if media_file.file_type == "image":
                await self._process_image(media_file)
            elif media_file.file_type == "document":
                await self._process_document(media_file)
            
            # Marcar como procesado
            media_file.is_processed = True
            self.db.commit()
            
            # Actualizar log
            log.status = "success"
            log.details = "Archivo procesado exitosamente"
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error procesando archivo {media_file.filename}: {str(e)}")
            
            # Actualizar log con error
            log.status = "failed"
            log.error_message = str(e)
            self.db.commit()
    
    async def _process_image(self, media_file: MediaFile) -> None:
        """
        Procesa una imagen (optimizar, crear miniatura)
        """
        try:
            # Optimizar imagen
            result = optimize_image(media_file.file_path)
            
            if result.get("success"):
                media_file.is_optimized = True
                # Actualizar metadatos con información de optimización
                current_metadata = media_file.processing_metadata or {}
                current_metadata["optimization"] = result
                media_file.processing_metadata = current_metadata
                
                # Crear miniatura
                thumbnail_dir = os.path.join(os.path.dirname(media_file.file_path), "thumbnails")
                os.makedirs(thumbnail_dir, exist_ok=True)
                thumbnail_path = os.path.join(thumbnail_dir, f"thumb_{media_file.filename}")
                
                if create_thumbnail(media_file.file_path, thumbnail_path):
                    current_metadata["thumbnail_path"] = thumbnail_path
                    media_file.processing_metadata = current_metadata
            
        except Exception as e:
            logger.error(f"Error procesando imagen {media_file.filename}: {str(e)}")
            raise
    
    async def _process_document(self, media_file: MediaFile) -> None:
        """
        Procesa un documento (extraer texto, metadatos)
        """
        try:
            # Por ahora solo extraemos metadatos básicos
            # En el futuro se puede agregar extracción de texto, OCR, etc.
            pass
            
        except Exception as e:
            logger.error(f"Error procesando documento {media_file.filename}: {str(e)}")
            raise
    
    def get_file_by_id(self, file_id: int) -> Optional[MediaFile]:
        """
        Obtiene un archivo por ID
        """
        return self.db.query(MediaFile).filter(MediaFile.id == file_id).first()
    
    def get_file_by_filename(self, filename: str) -> Optional[MediaFile]:
        """
        Obtiene un archivo por nombre
        """
        return self.db.query(MediaFile).filter(MediaFile.filename == filename).first()
    
    def list_files(
        self, 
        file_type: Optional[str] = None,
        service_source: Optional[str] = None,
        reference_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[MediaFile]:
        """
        Lista archivos con filtros opcionales
        """
        query = self.db.query(MediaFile)
        
        if file_type:
            query = query.filter(MediaFile.file_type == file_type)
        
        if service_source:
            query = query.filter(MediaFile.service_source == service_source)
        
        if reference_id:
            query = query.filter(MediaFile.reference_id == reference_id)
        
        return query.offset(offset).limit(limit).all()
    
    def update_file(self, file_id: int, update_data: MediaFileUpdate) -> Optional[MediaFile]:
        """
        Actualiza un archivo
        """
        media_file = self.get_file_by_id(file_id)
        if not media_file:
            return None
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(media_file, field, value)
        
        self.db.commit()
        self.db.refresh(media_file)
        return media_file
    
    def delete_file(self, file_id: int) -> bool:
        """
        Elimina un archivo (soft delete)
        """
        media_file = self.get_file_by_id(file_id)
        if not media_file:
            return False
        
        try:
            # Eliminar archivo físico
            if os.path.exists(media_file.file_path):
                os.remove(media_file.file_path)
            
            # Eliminar miniatura si existe
            if media_file.processing_metadata and "thumbnail_path" in media_file.processing_metadata:
                thumbnail_path = media_file.processing_metadata["thumbnail_path"]
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
            
            # Eliminar de BD
            self.db.delete(media_file)
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando archivo {file_id}: {str(e)}")
            return False
    
    def get_file_info(self, file_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información completa de un archivo
        """
        media_file = self.get_file_by_id(file_id)
        if not media_file:
            return None
        
        # Verificar si el archivo existe físicamente
        file_exists = os.path.exists(media_file.file_path)
        
        return {
            "id": media_file.id,
            "filename": media_file.filename,
            "original_filename": media_file.original_filename,
            "file_type": media_file.file_type,
            "mime_type": media_file.mime_type,
            "file_size": media_file.file_size,
            "file_extension": media_file.file_extension,
            "width": media_file.width,
            "height": media_file.height,
            "pages": media_file.pages,
            "duration": media_file.duration,
            "is_processed": media_file.is_processed,
            "is_optimized": media_file.is_optimized,
            "is_public": media_file.is_public,
            "uploaded_by": media_file.uploaded_by,
            "service_source": media_file.service_source,
            "reference_id": media_file.reference_id,
            "created_at": media_file.created_at,
            "updated_at": media_file.updated_at,
            "file_exists": file_exists,
            "download_url": f"/media/{file_id}/download" if file_exists else None
        } 