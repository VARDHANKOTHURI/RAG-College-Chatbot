from fastapi import APIRouter
from backend.app.config.settings import settings
from backend.app.config.database import db_manager
from backend.app.rag.vector_store import vector_store

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": {
            "connected": db_manager.is_connected,
            "is_fallback": db_manager.is_fallback
        },
        "vector_store": {
            "collection": settings.QDRANT_COLLECTION_NAME,
            "total_vectors": vector_store.get_total_vectors()
        },
        "llm": {
            "model": settings.LLM_MODEL,
            "has_gemini_key": bool(settings.GEMINI_API_KEY),
            "has_openrouter_key": bool(settings.OPENROUTER_API_KEY)
        }
    }
