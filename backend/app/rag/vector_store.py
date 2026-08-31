import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from backend.app.config.settings import settings
from backend.app.rag.chunker import Chunk
from backend.app.utils.logger import logger

class VectorStoreService:
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.client: Optional[QdrantClient] = None
        self._init_client()

    def _init_client(self):
        try:
            if settings.QDRANT_URL:
                logger.info(f"Connecting to Qdrant at {settings.QDRANT_URL}")
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=10.0
                )
            else:
                os.makedirs(settings.QDRANT_PATH, exist_ok=True)
                logger.info(f"Initializing local persistent Qdrant at {settings.QDRANT_PATH}")
                self.client = QdrantClient(path=settings.QDRANT_PATH)
            
            self._ensure_collection()
        except Exception as e:
            logger.warning(f"Could not initialize disk-backed Qdrant ({e}), falling back to in-memory Qdrant instance.")
            self.client = QdrantClient(":memory:")
            self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            existing_names = [c.name for c in collections]
            if self.collection_name not in existing_names:
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest_models.VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=rest_models.Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection: {e}")

    def upsert_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> bool:
        if not chunks or not embeddings:
            return True
        
        points = []
        for chunk, emb in zip(chunks, embeddings):
            payload = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "page_number": chunk.page_number,
                "section": chunk.section,
                "title": chunk.metadata.get("title", ""),
                "fileName": chunk.metadata.get("fileName", ""),
                "category": chunk.metadata.get("category", ""),
                "department": chunk.metadata.get("department", "All"),
                "academicYear": chunk.metadata.get("academicYear", "2026"),
                "version": chunk.metadata.get("version", 1)
            }
            
            points.append(
                rest_models.PointStruct(
                    id=chunk.chunk_id,
                    vector=emb,
                    payload=payload
                )
            )

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Upserted {len(points)} vectors to Qdrant collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert points to Qdrant: {e}")
            return False

    def search(
        self,
        query_vector: List[float],
        top_k: int = 4,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        try:
            qdrant_filter = None
            if filters:
                conditions = []
                for key, val in filters.items():
                    if val and val != "All":
                        conditions.append(
                            rest_models.FieldCondition(
                                key=key,
                                match=rest_models.MatchValue(value=val)
                            )
                        )
                if conditions:
                    qdrant_filter = rest_models.Filter(must=conditions)

            # Check if query_points method is available in newer Qdrant or fall back to search
            if hasattr(self.client, "query_points"):
                search_result = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k,
                    query_filter=qdrant_filter,
                    with_payload=True
                )
                points = search_result.points
            else:
                points = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    query_filter=qdrant_filter,
                    with_payload=True
                )

            results = []
            for hit in points:
                results.append({
                    "id": hit.id,
                    "score": float(hit.score),
                    "payload": hit.payload or {}
                })
            return results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    def delete_by_document_id(self, document_id: str) -> bool:
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=rest_models.FilterSelector(
                    filter=rest_models.Filter(
                        must=[
                            rest_models.FieldCondition(
                                key="document_id",
                                match=rest_models.MatchValue(value=document_id)
                            )
                        ]
                    )
                )
            )
            logger.info(f"Deleted vectors for document_id {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors for document_id {document_id}: {e}")
            return False

    def get_total_vectors(self) -> int:
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count or 0
        except Exception:
            return 0

vector_store = VectorStoreService()
