from .auth import router as auth_router
from .chat import router as chat_router
from .documents import router as documents_router
from .collections import router as collections_router
from .feedback import router as feedback_router
from .admin import router as admin_router
from .health import router as health_router

__all__ = [
    "auth_router",
    "chat_router",
    "documents_router",
    "collections_router",
    "feedback_router",
    "admin_router",
    "health_router"
]
