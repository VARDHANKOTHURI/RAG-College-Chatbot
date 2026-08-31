import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.app.config.settings import settings
from backend.app.config.database import db_manager
from backend.app.utils.file_utils import ensure_directories
from backend.app.utils.logger import logger
from backend.app.services.auth_service import auth_service
from backend.app.services.document_service import document_service
from backend.app.rag.vector_store import vector_store
from backend.app.middleware.error_handler import global_exception_handler
from backend.app.routes import (
    auth_router,
    chat_router,
    documents_router,
    collections_router,
    feedback_router,
    admin_router,
    health_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Initializing RAG-Based College Chatbot Server...")
    ensure_directories()
    await db_manager.connect()
    await auth_service.seed_default_users()

    # Seed sample documents if knowledge base is empty
    try:
        existing_docs = await document_service.list_documents()
        sample_path = "./data/sample_documents/College_Handbook_2026.txt"
        if not existing_docs and os.path.exists(sample_path):
            logger.info("Seeding initial College Handbook 2026 into knowledge base...")
            with open(sample_path, "rb") as f:
                content = f.read()
            await document_service.upload_and_process(
                file_content=content,
                filename="College_Handbook_2026.txt",
                title="Greenwood Institute of Technology — Official Student Handbook 2026",
                description="Comprehensive academic regulations, admissions, fees, hostel rules, exam guidelines, scholarships and club details.",
                category="General FAQ",
                department="All",
                academic_year="2026",
                version=1,
                uploaded_by="System Administrator"
            )
    except Exception as e:
        logger.warning(f"Initial sample document seeding skipped/failed: {e}")

    yield

    # Shutdown tasks
    logger.info("Shutting down College Chatbot server.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Exception Handler
app.add_exception_handler(Exception, global_exception_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(collections_router, prefix=settings.API_PREFIX)
app.include_router(feedback_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)

# Static & Upload file serving
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.STATIC_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

@app.get("/")
async def serve_index():
    index_path = os.path.join(settings.STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": f"Welcome to {settings.PROJECT_NAME} API. Visit /docs for Swagger UI or /api/health."}

# Catch-all for SPA client-side routes (e.g. /chat, /login, /admin, /documents)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("uploads/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        return JSONResponse(status_code=404, content={"code": "NOT_FOUND", "message": "API endpoint not found."})
    
    index_path = os.path.join(settings.STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"code": "NOT_FOUND", "message": "Page not found."})
