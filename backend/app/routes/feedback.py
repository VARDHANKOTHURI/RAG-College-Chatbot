from typing import List
from fastapi import APIRouter, Depends
from backend.app.schemas.document import FeedbackCreateRequest, FeedbackResponse
from backend.app.controllers.chat_controller import ChatController
from backend.app.controllers.admin_controller import AdminController
from backend.app.middleware.auth import get_current_user, require_admin

router = APIRouter(prefix="/feedback", tags=["Answer Feedback"])

@router.post("", response_model=FeedbackResponse)
async def submit_feedback(
    req: FeedbackCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    return await ChatController.submit_feedback(user=current_user, req=req)

@router.get("", response_model=List[FeedbackResponse])
async def list_feedback(current_user: dict = Depends(require_admin)):
    return await AdminController.list_feedback()
