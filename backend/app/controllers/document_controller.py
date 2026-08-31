from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status, UploadFile
from backend.app.schemas.document import DocumentResponse, DocumentUpdateRequest
from backend.app.services.document_service import document_service
from backend.app.utils.file_utils import validate_file

class DocumentController:
    @staticmethod
    async def list_documents(
        category: Optional[str] = None,
        department: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[DocumentResponse]:
        docs = await document_service.list_documents(category=category, department=department, search=search)
        return [DocumentResponse(**d) for d in docs]

    @staticmethod
    async def get_document(doc_id: str) -> DocumentResponse:
        doc = await document_service.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found."})
        return DocumentResponse(**doc)

    @staticmethod
    async def upload_document(
        user: dict,
        file: UploadFile,
        title: Optional[str] = None,
        description: Optional[str] = "",
        category: Optional[str] = "General FAQ",
        department: Optional[str] = "All",
        academic_year: Optional[str] = "2026",
        version: Optional[int] = 1
    ) -> DocumentResponse:
        content = await file.read()
        is_valid, err = validate_file(file.filename, len(content))
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"code": "INVALID_FILE", "message": err})

        res = await document_service.upload_and_process(
            file_content=content,
            filename=file.filename,
            title=title or file.filename,
            description=description or "",
            category=category or "General FAQ",
            department=department or "All",
            academic_year=academic_year or "2026",
            version=version or 1,
            uploaded_by=user.get("name", "admin")
        )
        return DocumentResponse(**res)

    @staticmethod
    async def reprocess_document(doc_id: str) -> Dict[str, Any]:
        try:
            return await document_service.reprocess_document(doc_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "DOCUMENT_NOT_FOUND", "message": str(e)})

    @staticmethod
    async def delete_document(doc_id: str) -> Dict[str, str]:
        success = await document_service.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found."})
        return {"message": "Document and associated vectors deleted successfully."}
