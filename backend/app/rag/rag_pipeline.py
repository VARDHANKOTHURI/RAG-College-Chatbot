import uuid
from typing import List, Dict, Any, Optional, AsyncGenerator
from backend.app.config.settings import settings
from backend.app.rag.retrieval_service import retrieval_service, RetrievedChunk
from backend.app.rag.reranking_service import reranking_service
from backend.app.rag.prompt_builder import PromptBuilder, UNKNOWN_RESPONSE_TEMPLATE
from backend.app.rag.llm_service import llm_service
from backend.app.utils.logger import logger

class RAGPipelineResult:
    def __init__(
        self,
        answer: str,
        sources: List[Dict[str, Any]],
        is_unknown: bool,
        retrieval_score: float,
        retrieved_chunks: List[RetrievedChunk]
    ):
        self.answer = answer
        self.sources = sources
        self.is_unknown = is_unknown
        self.retrieval_score = retrieval_score
        self.retrieved_chunks = retrieved_chunks

class RAGPipeline:
    def __init__(self):
        self.top_k = settings.TOP_K
        self.enable_reranking = settings.ENABLE_RERANKING

    async def execute(
        self,
        query: str,
        conversation_history: List[Dict[str, str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        language: str = "English"
    ) -> RAGPipelineResult:
        logger.info(f"Executing RAG pipeline for query: '{query}'")

        # 1. Retrieve candidate chunks
        retrieved_chunks = await retrieval_service.retrieve(
            query=query,
            top_k=self.top_k,
            filters=filters
        )

        # 2. Check if relevant context is found
        if not retrieved_chunks:
            logger.info(f"No relevant chunks found above threshold for query: '{query}'")
            return RAGPipelineResult(
                answer=UNKNOWN_RESPONSE_TEMPLATE,
                sources=[],
                is_unknown=True,
                retrieval_score=0.0,
                retrieved_chunks=[]
            )

        # 3. Optional Re-ranking
        if self.enable_reranking and len(retrieved_chunks) > 1:
            final_chunks = reranking_service.rerank(query, retrieved_chunks, top_n=self.top_k)
        else:
            final_chunks = retrieved_chunks

        max_score = max(c.score for c in final_chunks) if final_chunks else 0.0

        # 4. Construct Grounded Prompt
        prompt = PromptBuilder.build_rag_prompt(
            query=query,
            chunks=final_chunks,
            conversation_history=conversation_history,
            language=language
        )

        # 5. Call LLM
        answer = await llm_service.generate_response(prompt)

        # 6. Format Sources for Student Inspection
        sources = []
        for c in final_chunks:
            sources.append({
                "documentId": c.document_id,
                "title": c.title,
                "fileName": c.file_name,
                "pageNumber": c.page_number,
                "section": c.section,
                "category": c.category,
                "department": c.department,
                "snippet": c.text[:280] + ("..." if len(c.text) > 280 else ""),
                "score": round(c.score, 4)
            })

        is_unknown = UNKNOWN_RESPONSE_TEMPLATE.lower() in answer.lower()

        return RAGPipelineResult(
            answer=answer,
            sources=sources if not is_unknown else [],
            is_unknown=is_unknown,
            retrieval_score=max_score,
            retrieved_chunks=final_chunks
        )

    async def execute_stream(
        self,
        query: str,
        conversation_history: List[Dict[str, str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        language: str = "English"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        # 1. Retrieve
        retrieved_chunks = await retrieval_service.retrieve(
            query=query,
            top_k=self.top_k,
            filters=filters
        )

        if not retrieved_chunks:
            yield {
                "type": "sources",
                "sources": [],
                "is_unknown": True,
                "retrieval_score": 0.0
            }
            yield {
                "type": "token",
                "token": UNKNOWN_RESPONSE_TEMPLATE
            }
            yield {"type": "done"}
            return

        # 2. Re-rank
        if self.enable_reranking and len(retrieved_chunks) > 1:
            final_chunks = reranking_service.rerank(query, retrieved_chunks, top_n=self.top_k)
        else:
            final_chunks = retrieved_chunks

        max_score = max(c.score for c in final_chunks) if final_chunks else 0.0

        sources = []
        for c in final_chunks:
            sources.append({
                "documentId": c.document_id,
                "title": c.title,
                "fileName": c.file_name,
                "pageNumber": c.page_number,
                "section": c.section,
                "category": c.category,
                "department": c.department,
                "snippet": c.text[:280] + ("..." if len(c.text) > 280 else ""),
                "score": round(c.score, 4)
            })

        # Yield sources first so the UI can display badges immediately
        yield {
            "type": "sources",
            "sources": sources,
            "is_unknown": False,
            "retrieval_score": max_score
        }

        # 3. Build Prompt & Stream LLM Output
        prompt = PromptBuilder.build_rag_prompt(
            query=query,
            chunks=final_chunks,
            conversation_history=conversation_history,
            language=language
        )

        async for token in llm_service.generate_response_stream(prompt):
            yield {
                "type": "token",
                "token": token
            }

        yield {"type": "done"}

rag_pipeline = RAGPipeline()
