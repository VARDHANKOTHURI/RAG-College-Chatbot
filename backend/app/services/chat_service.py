import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, AsyncGenerator
from backend.app.config.database import db_manager
from backend.app.rag.rag_pipeline import rag_pipeline
from backend.app.schemas.chat import ChatRequest, ChatResponse, SourceResponse
from backend.app.utils.logger import logger

class ChatService:
    def __init__(self):
        pass

    @property
    def conversations_collection(self):
        return db_manager.get_collection("conversations")

    @property
    def messages_collection(self):
        return db_manager.get_collection("messages")

    @property
    def unanswered_collection(self):
        return db_manager.get_collection("unanswered_questions")

    @property
    def feedback_collection(self):
        return db_manager.get_collection("feedback")

    async def list_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        convs = await self.conversations_collection.find(
            query={"userId": user_id},
            sort=[("updatedAt", -1)]
        )
        for c in convs:
            c["id"] = str(c.get("_id", ""))
        return convs

    async def create_conversation(self, user_id: str, title: str = "New Conversation", collection_id: str = None) -> Dict[str, Any]:
        conv_id = str(uuid.uuid4())
        record = {
            "_id": conv_id,
            "userId": user_id,
            "title": title,
            "collectionId": collection_id,
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat()
        }
        await self.conversations_collection.insert_one(record)
        record["id"] = conv_id
        return record

    async def get_conversation_details(self, conv_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        conv = await self.conversations_collection.find_one({"_id": conv_id, "userId": user_id})
        if not conv:
            return None
        
        messages = await self.messages_collection.find(
            query={"conversationId": conv_id},
            sort=[("createdAt", 1)]
        )
        for m in messages:
            m["id"] = str(m.get("_id", ""))

        conv["id"] = str(conv.get("_id", ""))
        conv["messages"] = messages
        return conv

    async def delete_conversation(self, conv_id: str, user_id: str) -> bool:
        conv = await self.conversations_collection.find_one({"_id": conv_id, "userId": user_id})
        if not conv:
            return False

        await self.messages_collection.delete_many({"conversationId": conv_id})
        await self.conversations_collection.delete_one({"_id": conv_id})
        return True

    async def ask_question(self, user_id: str, req: ChatRequest) -> ChatResponse:
        conv_id = req.conversationId
        if not conv_id:
            # Create a title based on first 5 words of message
            title = " ".join(req.message.split()[:5]) + "..."
            new_conv = await self.create_conversation(user_id=user_id, title=title, collection_id=req.collectionId)
            conv_id = new_conv["id"]

        # Fetch recent history
        recent_msgs = await self.messages_collection.find(
            query={"conversationId": conv_id},
            sort=[("createdAt", -1)],
            limit=6
        )
        history = []
        for m in reversed(recent_msgs):
            history.append({"role": m["role"], "content": m["content"]})

        # Save user message
        user_msg_id = str(uuid.uuid4())
        await self.messages_collection.insert_one({
            "_id": user_msg_id,
            "conversationId": conv_id,
            "role": "user",
            "content": req.message,
            "createdAt": datetime.utcnow().isoformat()
        })

        # Prepare filters
        filters = {}
        if req.department:
            filters["department"] = req.department
        if req.category:
            filters["category"] = req.category

        # Execute RAG
        rag_result = await rag_pipeline.execute(
            query=req.message,
            conversation_history=history,
            filters=filters,
            language=req.language or "English"
        )

        # If question is unknown / unanswered, record in knowledge gaps
        if rag_result.is_unknown:
            await self.unanswered_collection.insert_one({
                "_id": str(uuid.uuid4()),
                "userId": user_id,
                "question": req.message,
                "conversationId": conv_id,
                "retrievalScore": rag_result.retrieval_score,
                "status": "open",
                "adminNotes": "",
                "createdAt": datetime.utcnow().isoformat()
            })

        # Save assistant message
        asst_msg_id = str(uuid.uuid4())
        await self.messages_collection.insert_one({
            "_id": asst_msg_id,
            "conversationId": conv_id,
            "role": "assistant",
            "content": rag_result.answer,
            "sources": rag_result.sources,
            "retrievalMetadata": {
                "score": rag_result.retrieval_score,
                "isUnknown": rag_result.is_unknown,
                "language": req.language
            },
            "feedback": None,
            "createdAt": datetime.utcnow().isoformat()
        })

        # Update conversation timestamp
        await self.conversations_collection.update_one(
            {"_id": conv_id},
            {"$set": {"updatedAt": datetime.utcnow().isoformat()}}
        )

        return ChatResponse(
            conversationId=conv_id,
            messageId=asst_msg_id,
            answer=rag_result.answer,
            sources=[SourceResponse(**s) for s in rag_result.sources],
            isUnknown=rag_result.is_unknown,
            retrievalScore=rag_result.retrieval_score
        )

    async def submit_feedback(self, user_id: str, message_id: str, rating: int, reason: str = "", comment: str = "") -> Dict[str, Any]:
        feedback_id = str(uuid.uuid4())
        record = {
            "_id": feedback_id,
            "userId": user_id,
            "messageId": message_id,
            "rating": rating,
            "reason": reason,
            "comment": comment,
            "createdAt": datetime.utcnow().isoformat()
        }
        await self.feedback_collection.insert_one(record)
        
        # Attach feedback directly to the message record
        await self.messages_collection.update_one(
            {"_id": message_id},
            {"$set": {"feedback": {"rating": rating, "reason": reason, "comment": comment}}}
        )
        record["id"] = feedback_id
        return record

chat_service = ChatService()
