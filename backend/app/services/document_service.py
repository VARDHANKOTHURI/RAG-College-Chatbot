import os
import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.app.config.database import db_manager
from backend.app.config.settings import settings
from backend.app.rag.document_loader import DocumentLoader
from backend.app.rag.chunker import DocumentChunker
from backend.app.rag.embedding_service import embedding_service
from backend.app.rag.vector_store import vector_store
from backend.app.utils.file_utils import save_uploaded_file
from backend.app.utils.logger import logger

class DocumentService:
    def __init__(self):
        self.chunker = DocumentChunker()

    @property
    def docs_collection(self):
        return db_manager.get_collection("documents")

    @property
    def chunks_collection(self):
        return db_manager.get_collection("chunks")

    async def list_documents(
        self,
        category: Optional[str] = None,
        department: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = {}
        if category and category != "All":
            query["category"] = category
        if department and department != "All":
            query["department"] = department
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"fileName": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        docs = await self.docs_collection.find(query=query, sort=[("createdAt", -1)])
        # Normalize _id to id
        for d in docs:
            d["id"] = str(d.get("_id", ""))
        return docs

    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.docs_collection.find_one({"_id": doc_id})
        if doc:
            doc["id"] = str(doc.get("_id", ""))
        return doc

    async def process_document_pipeline(self, doc_id: str, file_path: str, metadata: Dict[str, Any]):
        """Complete asynchronous ingestion pipeline."""
        logger.info(f"Starting ingestion pipeline for document: {doc_id} ({file_path})")
        try:
            # Step 1: Text extraction
            pages = DocumentLoader.load(file_path)
            total_pages = len(pages)
            if total_pages == 0:
                raise ValueError("No text could be extracted from document.")

            # Step 2 & 3: Cleaning & Chunking
            chunks = self.chunker.chunk_document(
                document_id=doc_id,
                pages=pages,
                doc_metadata=metadata
            )
            
            if not chunks:
                raise ValueError("Document yielded 0 valid text chunks.")

            # Step 4: Generate Embeddings
            chunk_texts = [c.text for c in chunks]
            embeddings = await embedding_service.get_embeddings_batch(chunk_texts)

            # Step 5: Store in Qdrant Vector Store
            vector_store.upsert_chunks(chunks, embeddings)

            # Step 6: Store Chunks in DB
            # First remove existing chunks if reprocessing
            await self.chunks_collection.delete_many({"documentId": doc_id})
            for c in chunks:
                chunk_dict = c.to_dict()
                chunk_dict["_id"] = c.chunk_id
                chunk_dict["documentId"] = doc_id
                await self.chunks_collection.insert_one(chunk_dict)

            # Step 7: Update document status to ready
            await self.docs_collection.update_one(
                {"_id": doc_id},
                {"$set": {
                    "status": "ready",
                    "totalPages": total_pages,
                    "totalChunks": len(chunks),
                    "errorMessage": None,
                    "updatedAt": datetime.utcnow().isoformat()
                }}
            )
            logger.info(f"Successfully processed document {doc_id}. Chunks: {len(chunks)}, Pages: {total_pages}")

        except Exception as e:
            logger.error(f"Ingestion pipeline failed for document {doc_id}: {e}", exc_info=True)
            await self.docs_collection.update_one(
                {"_id": doc_id},
                {"$set": {
                    "status": "failed",
                    "errorMessage": str(e),
                    "updatedAt": datetime.utcnow().isoformat()
                }}
            )

    async def upload_and_process(
        self,
        file_content: bytes,
        filename: str,
        title: str,
        description: str = "",
        category: str = "General FAQ",
        department: str = "All",
        academic_year: str = "2026",
        version: int = 1,
        uploaded_by: str = "admin"
    ) -> Dict[str, Any]:
        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id}_{filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
        save_uploaded_file(file_content, file_path)

        doc_record = {
            "_id": doc_id,
            "title": title or filename,
            "fileName": filename,
            "description": description,
            "category": category,
            "department": department,
            "academicYear": academic_year,
            "version": version,
            "status": "processing",
            "uploadedBy": uploaded_by,
            "fileUrl": f"/uploads/{safe_filename}",
            "totalPages": 1,
            "totalChunks": 0,
            "errorMessage": None,
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat()
        }

        await self.docs_collection.insert_one(doc_record)

        # Process in background task
        asyncio.create_task(
            self.process_document_pipeline(
                doc_id=doc_id,
                file_path=file_path,
                metadata={
                    "title": doc_record["title"],
                    "fileName": filename,
                    "category": category,
                    "department": department,
                    "academicYear": academic_year,
                    "version": version
                }
            )
        )

        doc_record["id"] = doc_id
        return doc_record

    async def reprocess_document(self, doc_id: str) -> Dict[str, Any]:
        doc = await self.get_document(doc_id)
        if not doc:
            raise ValueError("Document not found.")

        safe_filename = os.path.basename(doc["fileUrl"])
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Underlying file {safe_filename} not found on disk.")

        await self.docs_collection.update_one(
            {"_id": doc_id},
            {"$set": {"status": "processing", "errorMessage": None}}
        )

        asyncio.create_task(
            self.process_document_pipeline(
                doc_id=doc_id,
                file_path=file_path,
                metadata={
                    "title": doc["title"],
                    "fileName": doc["fileName"],
                    "category": doc.get("category", "General FAQ"),
                    "department": doc.get("department", "All"),
                    "academicYear": doc.get("academicYear", "2026"),
                    "version": doc.get("version", 1)
                }
            )
        )
        return {"message": "Reprocessing started in background.", "id": doc_id}

    async def delete_document(self, doc_id: str) -> bool:
        doc = await self.get_document(doc_id)
        if not doc:
            return False

        # Delete vectors from Qdrant
        vector_store.delete_by_document_id(doc_id)

        # Delete chunks from DB
        await self.chunks_collection.delete_many({"documentId": doc_id})

        # Delete document record
        await self.docs_collection.delete_one({"_id": doc_id})

        # Remove local file if exists
        try:
            safe_filename = os.path.basename(doc.get("fileUrl", ""))
            file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"Could not remove file on disk: {e}")

        return True

document_service = DocumentService()
