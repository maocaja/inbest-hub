import os
import magic
from typing import Tuple, Optional
from config import Config

def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """
    Valida la extensión del archivo
    Returns: (is_valid, error_message)
    """
    if not filename:
        return False, "Nombre de archivo vacío"
    
    # Obtener la extensión
    _, extension = os.path.splitext(filename.lower())
    
    if not extension:
        return False, "Archivo sin extensión"
    
    if extension not in Config.SUPPORTED_FORMATS:
        return False, f"Formato no soportado: {extension}. Formatos soportados: {', '.join(Config.SUPPORTED_FORMATS)}"
    
    return True, ""

def validate_file_size(file_size: int) -> Tuple[bool, str]:
    """
    Valida el tamaño del archivo
    Returns: (is_valid, error_message)
    """
    if file_size <= 0:
        return False, "Archivo vacío"
    
    if file_size > Config.MAX_FILE_SIZE:
        max_size_mb = Config.MAX_FILE_SIZE / (1024 * 1024)
        return False, f"Archivo demasiado grande. Tamaño máximo: {max_size_mb}MB"
    
    return True, ""

def validate_mime_type(file_path: str, expected_extension: str) -> Tuple[bool, str]:
    """
    Valida el tipo MIME del archivo usando python-magic
    Returns: (is_valid, error_message)
    """
    try:
        # Detectar el tipo MIME real del archivo
        mime_type = magic.from_file(file_path, mime=True)
        
        # Mapeo de extensiones a tipos MIME esperados
        mime_mapping = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.txt': 'text/plain'
        }
        
        expected_mime = mime_mapping.get(expected_extension.lower())
        if expected_mime and mime_type != expected_mime:
            return False, f"Tipo MIME no coincide. Esperado: {expected_mime}, Detectado: {mime_type}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Error al validar tipo MIME: {str(e)}"

def get_file_type_from_extension(extension: str) -> str:
    """
    Determina el tipo de archivo basado en la extensión
    """
    extension = extension.lower()
    
    if extension in Config.SUPPORTED_IMAGE_FORMATS:
        return "image"
    elif extension in Config.SUPPORTED_DOCUMENT_FORMATS:
        return "document"
    else:
        return "unknown"

def sanitize_filename(filename: str) -> str:
    """
    Sanitiza el nombre del archivo para evitar problemas de seguridad
    """
    # Caracteres no permitidos
    invalid_chars = '<>:"/\\|?*'
    
    # Reemplazar caracteres no válidos
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limitar longitud
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def generate_unique_filename(original_filename: str, upload_dir: str) -> str:
    """
    Genera un nombre único para el archivo
    """
    import uuid
    from datetime import datetime
    
    # Obtener extensión
    name, extension = os.path.splitext(original_filename)
    
    # Generar nombre único con timestamp y UUID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    new_filename = f"{timestamp}_{unique_id}{extension}"
    
    # Verificar que no exista
    counter = 1
    while os.path.exists(os.path.join(upload_dir, new_filename)):
        new_filename = f"{timestamp}_{unique_id}_{counter}{extension}"
        counter += 1
    
    return new_filename 