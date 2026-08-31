import os
import shutil
from typing import Tuple
from backend.app.config.settings import settings

def ensure_directories():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.QDRANT_PATH, exist_ok=True)
    os.makedirs("./data/local_db", exist_ok=True)
    os.makedirs("./data/sample_documents", exist_ok=True)

def validate_file(filename: str, file_size_bytes: int) -> Tuple[bool, str]:
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        return False, f"File extension '{ext}' is not supported. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
    
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        return False, f"File size exceeds the limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
    
    return True, ""

def save_uploaded_file(file_content: bytes, destination_path: str) -> str:
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    with open(destination_path, "wb") as f:
        f.write(file_content)
    return destination_path
