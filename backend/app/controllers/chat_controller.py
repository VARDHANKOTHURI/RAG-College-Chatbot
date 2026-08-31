from typing import List, Dict, Any
from fastapi import HTTPException, status
from backend.app.schemas.chat import ChatRequest, ChatResponse, ConversationCreateRequest, ConversationDetailResponse, MessageResponse
from backend.app.services.chat_service import chat_service
from backend.app.schemas.document import FeedbackCreateRequest, FeedbackResponse

class ChatController:
    @staticmethod
    async def ask_question(user: dict, req: ChatRequest) -> ChatResponse:
        return await chat_service.ask_question(user_id=user["id"], req=req)

    @staticmethod
    async def list_conversations(user: dict) -> List[Dict[str, Any]]:
        return await chat_service.list_conversations(user_id=user["id"])

    @staticmethod
    async def create_conversation(user: dict, req: ConversationCreateRequest) -> Dict[str, Any]:
        return await chat_service.create_conversation(user_id=user["id"], title=req.title, collection_id=req.collectionId)

    @staticmethod
    async def get_conversation(user: dict, conversation_id: str) -> ConversationDetailResponse:
        conv = await chat_service.get_conversation_details(conv_id=conversation_id, user_id=user["id"])
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "CONVERSATION_NOT_FOUND", "message": "Conversation not found."})
        return ConversationDetailResponse(**conv)

    @staticmethod
    async def delete_conversation(user: dict, conversation_id: str) -> Dict[str, str]:
        success = await chat_service.delete_conversation(conv_id=conversation_id, user_id=user["id"])
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "CONVERSATION_NOT_FOUND", "message": "Conversation not found."})
        return {"message": "Conversation deleted successfully."}

    @staticmethod
    async def submit_feedback(user: dict, req: FeedbackCreateRequest) -> FeedbackResponse:
        res = await chat_service.submit_feedback(
            user_id=user["id"],
            message_id=req.messageId,
            rating=req.rating,
            reason=req.reason or "",
            comment=req.comment or ""
        )
        return FeedbackResponse(**res)
