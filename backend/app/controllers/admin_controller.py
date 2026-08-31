from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from backend.app.schemas.document import AnalyticsResponse, FeedbackResponse
from backend.app.services.analytics_service import analytics_service
from backend.app.config.database import db_manager

class AdminController:
    @staticmethod
    async def get_analytics() -> AnalyticsResponse:
        return await analytics_service.get_dashboard_metrics()

    @staticmethod
    async def get_unanswered(status: Optional[str] = "open") -> List[Dict[str, Any]]:
        return await analytics_service.list_unanswered_questions(status=status)

    @staticmethod
    async def update_unanswered_status(q_id: str, payload: dict) -> Dict[str, str]:
        status_val = payload.get("status", "resolved")
        admin_notes = payload.get("adminNotes", "")
        success = await analytics_service.update_unanswered_status(q_id, status_val, admin_notes)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "Question not found."})
        return {"message": "Status updated successfully."}

    @staticmethod
    async def list_feedback() -> List[FeedbackResponse]:
        col = db_manager.get_collection("feedback")
        items = await col.find(sort=[("createdAt", -1)], limit=100)
        for it in items:
            it["id"] = str(it.get("_id", ""))
        return [FeedbackResponse(**it) for it in items]
