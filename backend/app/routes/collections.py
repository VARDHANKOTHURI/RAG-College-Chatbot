import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.document import CollectionCreateRequest, CollectionResponse
from backend.app.config.database import db_manager
from backend.app.middleware.auth import get_current_user, require_admin

router = APIRouter(prefix="/collections", tags=["Knowledge Collections"])

@router.get("", response_model=List[CollectionResponse])
async def list_collections(current_user: dict = Depends(get_current_user)):
    col = db_manager.get_collection("collections")
    items = await col.find()
    if not items:
        # Seed default collections
        default_cols = [
            {"_id": "col-general", "name": "General College Knowledge", "description": "Campus policies, calendar, hostel, FAQs", "department": "All", "accessRules": ["student", "admin"], "createdAt": datetime.utcnow().isoformat()},
            {"_id": "col-cse", "name": "Computer Science & Engineering", "description": "CSE syllabus, lab manuals, faculty list", "department": "CSE", "accessRules": ["student", "admin"], "createdAt": datetime.utcnow().isoformat()},
            {"_id": "col-admissions", "name": "Admissions & Scholarships", "description": "Eligibility criteria, cutoff ranks, fee waiver notices", "department": "Admissions", "accessRules": ["student", "admin"], "createdAt": datetime.utcnow().isoformat()},
            {"_id": "col-exams", "name": "Examination Cell", "description": "Exam schedules, hall ticket rules, revaluation guidelines", "department": "Exams", "accessRules": ["student", "admin"], "createdAt": datetime.utcnow().isoformat()}
        ]
        for dc in default_cols:
            await col.insert_one(dc)
        items = default_cols
    
    for it in items:
        it["id"] = str(it.get("_id", ""))
    return [CollectionResponse(**it) for it in items]

@router.post("", response_model=CollectionResponse)
async def create_collection(
    req: CollectionCreateRequest,
    current_user: dict = Depends(require_admin)
):
    col = db_manager.get_collection("collections")
    col_id = str(uuid.uuid4())
    record = {
        "_id": col_id,
        "name": req.name,
        "description": req.description,
        "department": req.department,
        "accessRules": req.accessRules,
        "createdAt": datetime.utcnow().isoformat()
    }
    await col.insert_one(record)
    record["id"] = col_id
    return CollectionResponse(**record)

@router.delete("/{collection_id}")
async def delete_collection(
    collection_id: str,
    current_user: dict = Depends(require_admin)
):
    col = db_manager.get_collection("collections")
    res = await col.delete_one({"_id": collection_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "Collection not found."})
    return {"message": "Collection deleted successfully."}
