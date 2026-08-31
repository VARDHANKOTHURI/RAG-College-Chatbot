import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from backend.app.schemas.chat import ChatRequest, ChatResponse, ConversationCreateRequest, ConversationDetailResponse
from backend.app.controllers.chat_controller import ChatController
from backend.app.middleware.auth import get_current_user
from backend.app.rag.rag_pipeline import rag_pipeline
from backend.app.services.chat_service import chat_service
from backend.app.config.database import db_manager

router = APIRouter(prefix="/chat", tags=["Chat & RAG"])

@router.post("", response_model=ChatResponse)
async def ask_question(
    req: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    return await ChatController.ask_question(user=current_user, req=req)

@router.post("/stream")
async def ask_question_stream(
    req: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    # Ensure conversation exists
    conv_id = req.conversationId
    if not conv_id:
        title = " ".join(req.message.split()[:5]) + "..."
        new_conv = await chat_service.create_conversation(
            user_id=current_user["id"],
            title=title,
            collection_id=req.collectionId
        )
        conv_id = new_conv["id"]

    # Fetch recent history
    msgs_col = db_manager.get_collection("messages")
    recent_msgs = await msgs_col.find(
        query={"conversationId": conv_id},
        sort=[("createdAt", -1)],
        limit=6
    )
    history = [{"role": m["role"], "content": m["content"]} for m in reversed(recent_msgs)]

    # Store user message
    await msgs_col.insert_one({
        "_id": str(uuid.uuid4()) if 'uuid' in globals() else str(__import__('uuid').uuid4()),
        "conversationId": conv_id,
        "role": "user",
        "content": req.message,
        "createdAt": __import__('datetime').datetime.utcnow().isoformat()
    })

    filters = {}
    if req.department:
        filters["department"] = req.department
    if req.category:
        filters["category"] = req.category

    async def event_generator():
        # First send conversationId event
        yield f"data: {json.dumps({'type': 'init', 'conversationId': conv_id})}\n\n"
        
        full_tokens = []
        sources = []
        is_unknown = False
        retrieval_score = 0.0

        async for chunk in rag_pipeline.execute_stream(
            query=req.message,
            conversation_history=history,
            filters=filters,
            language=req.language or "English"
        ):
            if chunk.get("type") == "sources":
                sources = chunk.get("sources", [])
                is_unknown = chunk.get("is_unknown", False)
                retrieval_score = chunk.get("retrieval_score", 0.0)
            elif chunk.get("type") == "token":
                full_tokens.append(chunk.get("token", ""))
            
            yield f"data: {json.dumps(chunk)}\n\n"

        # Record assistant answer in DB
        assistant_content = "".join(full_tokens)
        msg_id = str(__import__('uuid').uuid4())
        await msgs_col.insert_one({
            "_id": msg_id,
            "conversationId": conv_id,
            "role": "assistant",
            "content": assistant_content,
            "sources": sources,
            "retrievalMetadata": {
                "score": retrieval_score,
                "isUnknown": is_unknown,
                "language": req.language
            },
            "feedback": None,
            "createdAt": __import__('datetime').datetime.utcnow().isoformat()
        })

        # If unknown, log to unanswered
        if is_unknown:
            unanswered_col = db_manager.get_collection("unanswered_questions")
            await unanswered_col.insert_one({
                "_id": str(__import__('uuid').uuid4()),
                "userId": current_user["id"],
                "question": req.message,
                "conversationId": conv_id,
                "retrievalScore": retrieval_score,
                "status": "open",
                "adminNotes": "",
                "createdAt": __import__('datetime').datetime.utcnow().isoformat()
            })

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/conversations", response_model=List[Dict[str, Any]])
async def list_conversations(current_user: dict = Depends(get_current_user)):
    return await ChatController.list_conversations(user=current_user)

@router.post("/conversations", response_model=Dict[str, Any])
async def create_conversation(
    req: ConversationCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    return await ChatController.create_conversation(user=current_user, req=req)

@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await ChatController.get_conversation(user=current_user, conversation_id=conversation_id)

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await ChatController.delete_conversation(user=current_user, conversation_id=conversation_id)

@router.get("/messages/{message_id}/sources")
async def get_message_sources(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    msgs_col = db_manager.get_collection("messages")
    msg = await msgs_col.find_one({"_id": message_id})
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "MESSAGE_NOT_FOUND", "message": "Message not found."})
    return {"sources": msg.get("sources", [])}
