from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from backend.app.schemas.document import DocumentResponse
from backend.app.controllers.document_controller import DocumentController
from backend.app.middleware.auth import get_current_user, require_admin

router = APIRouter(prefix="/documents", tags=["Document Management"])

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    category: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    return await DocumentController.list_documents(category=category, department=department, search=search)

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await DocumentController.get_document(document_id)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(""),
    category: Optional[str] = Form("General FAQ"),
    department: Optional[str] = Form("All"),
    academic_year: Optional[str] = Form("2026"),
    version: Optional[int] = Form(1),
    current_user: dict = Depends(require_admin)
):
    return await DocumentController.upload_document(
        user=current_user,
        file=file,
        title=title,
        description=description,
        category=category,
        department=department,
        academic_year=academic_year,
        version=version
    )

@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    current_user: dict = Depends(require_admin)
):
    return await DocumentController.reprocess_document(document_id)

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(require_admin)
):
    return await DocumentController.delete_document(document_id)
