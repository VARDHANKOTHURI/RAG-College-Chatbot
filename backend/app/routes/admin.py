from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, Body
from backend.app.schemas.document import AnalyticsResponse
from backend.app.controllers.admin_controller import AdminController
from backend.app.middleware.auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin & Analytics"])

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(current_user: dict = Depends(require_admin)):
    return await AdminController.get_analytics()

@router.get("/unanswered", response_model=List[Dict[str, Any]])
async def get_unanswered_questions(
    status: Optional[str] = Query("open"),
    current_user: dict = Depends(require_admin)
):
    return await AdminController.get_unanswered(status=status)

@router.put("/unanswered/{question_id}")
async def update_unanswered_status(
    question_id: str,
    payload: dict = Body(...),
    current_user: dict = Depends(require_admin)
):
    return await AdminController.update_unanswered_status(question_id, payload)

@router.get("/popular-questions")
async def get_popular_questions(current_user: dict = Depends(require_admin)):
    analytics = await AdminController.get_analytics()
    return {"popularQuestions": analytics.popularQuestions}
