import os
from typing import List
from pydantic_settings import BaseSettings

IS_SERVERLESS = os.environ.get("VERCEL") == "1" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None

class Settings(BaseSettings):
    PROJECT_NAME: str = "Greenwood Institute of Technology — RAG College Chatbot"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "college_rag_chatbot"

    # JWT
    JWT_SECRET: str = "greenwood-college-super-secret-jwt-key-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Vector DB (Qdrant)
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "college_knowledge_base"
    QDRANT_PATH: str = "/tmp/qdrant_storage" if IS_SERVERLESS else "./data/qdrant_storage"

    # LLM Providers
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.2

    # Embeddings & RAG
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100
    TOP_K: int = 4
    SIMILARITY_THRESHOLD: float = 0.28
    ENABLE_RERANKING: bool = True

    # Storage Paths
    UPLOAD_DIR: str = "/tmp/uploads" if IS_SERVERLESS else "./data/uploads"
    STATIC_DIR: str = "./static"
    MAX_UPLOAD_SIZE_MB: int = 25

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"

settings = Settings()
