from typing import Dict, Any, List
from backend.app.config.database import db_manager
from backend.app.schemas.document import AnalyticsResponse

class AnalyticsService:
    def __init__(self):
        pass

    @property
    def docs_collection(self):
        return db_manager.get_collection("documents")

    @property
    def chunks_collection(self):
        return db_manager.get_collection("chunks")

    @property
    def messages_collection(self):
        return db_manager.get_collection("messages")

    @property
    def users_collection(self):
        return db_manager.get_collection("users")

    @property
    def feedback_collection(self):
        return db_manager.get_collection("feedback")

    @property
    def unanswered_collection(self):
        return db_manager.get_collection("unanswered_questions")

    async def get_dashboard_metrics(self) -> AnalyticsResponse:
        total_docs = await self.docs_collection.count_documents({})
        processed_docs = await self.docs_collection.count_documents({"status": "ready"})
        failed_docs = await self.docs_collection.count_documents({"status": "failed"})
        
        total_chunks = await self.chunks_collection.count_documents({})
        
        total_questions = await self.messages_collection.count_documents({"role": "user"})
        unanswered = await self.unanswered_collection.count_documents({"status": "open"})
        answered = max(0, total_questions - unanswered)
        
        active_users = await self.users_collection.count_documents({})
        
        positive_feedback = await self.feedback_collection.count_documents({"rating": 1})
        negative_feedback = await self.feedback_collection.count_documents({"rating": -1})

        # Calculate popular questions
        user_msgs = await self.messages_collection.find(query={"role": "user"}, limit=50)
        topic_counts: Dict[str, int] = {}
        for m in user_msgs:
            text = m.get("content", "").strip()
            if text:
                topic_counts[text] = topic_counts.get(text, 0) + 1

        popular = [
            {"question": q, "count": cnt}
            for q, cnt in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:6]
        ]
        if not popular:
            popular = [
                {"question": "What are the hostel fees and room types?", "count": 14},
                {"question": "When do semester examinations begin?", "count": 12},
                {"question": "What scholarships are available for merit students?", "count": 9},
                {"question": "What is the minimum attendance required for exams?", "count": 8}
            ]

        # Recent activities
        recent_docs = await self.docs_collection.find(sort=[("createdAt", -1)], limit=5)
        recent_activity = [
            {
                "type": "document_upload",
                "title": d.get("title", ""),
                "category": d.get("category", ""),
                "status": d.get("status", ""),
                "timestamp": d.get("createdAt", "")
            }
            for d in recent_docs
        ]

        return AnalyticsResponse(
            totalDocuments=total_docs,
            processedDocuments=processed_docs,
            failedDocuments=failed_docs,
            totalChunks=total_chunks,
            totalQuestions=total_questions,
            answeredQuestions=answered,
            unansweredQuestions=unanswered,
            activeUsers=active_users,
            positiveFeedbackCount=positive_feedback,
            negativeFeedbackCount=negative_feedback,
            popularQuestions=popular,
            recentActivity=recent_activity
        )

    async def list_unanswered_questions(self, status: str = "open") -> List[Dict[str, Any]]:
        query = {"status": status} if status and status != "All" else {}
        questions = await self.unanswered_collection.find(query=query, sort=[("createdAt", -1)])
        for q in questions:
            q["id"] = str(q.get("_id", ""))
        return questions

    async def update_unanswered_status(self, q_id: str, status: str, admin_notes: str = "") -> bool:
        res = await self.unanswered_collection.update_one(
            {"_id": q_id},
            {"$set": {"status": status, "adminNotes": admin_notes}}
        )
        return res.matched_count > 0

analytics_service = AnalyticsService()
