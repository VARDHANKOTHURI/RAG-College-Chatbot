import re
from typing import List, Dict, Any, Optional
from backend.app.config.settings import settings
from backend.app.rag.embedding_service import embedding_service, STOP_WORDS
from backend.app.rag.vector_store import vector_store
from backend.app.utils.logger import logger

class RetrievedChunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        text: str,
        page_number: int,
        section: str,
        title: str,
        file_name: str,
        category: str,
        department: str,
        academic_year: str,
        score: float
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.text = text
        self.page_number = page_number
        self.section = section
        self.title = title
        self.file_name = file_name
        self.category = category
        self.department = department
        self.academic_year = academic_year
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "page_number": self.page_number,
            "section": self.section,
            "title": self.title,
            "file_name": self.file_name,
            "category": self.category,
            "department": self.department,
            "academic_year": self.academic_year,
            "score": round(self.score, 4)
        }

class RetrievalService:
    def __init__(self):
        self.top_k = settings.TOP_K
        self.threshold = settings.SIMILARITY_THRESHOLD

    def _keyword_overlap_score(self, query: str, text: str) -> float:
        """Computes keyword term match boost with stop word removal and phrase matching."""
        raw_words = re.findall(r'\b[a-zA-Z0-9_\-\.]{2,}\b', query.lower())
        informative_words = [w for w in raw_words if w not in STOP_WORDS]
        if not informative_words:
            return 0.0
        
        text_lower = text.lower()
        matched = 0
        for w in informative_words:
            if w in text_lower:
                matched += 1.0

        score = matched / len(informative_words)
        if len(informative_words) >= 2:
            phrase = " ".join(informative_words[:3])
            if phrase in text_lower:
                score += 0.2
        return min(1.0, score)

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        threshold: Optional[float] = None
    ) -> List[RetrievedChunk]:
        k = top_k or self.top_k
        min_threshold = threshold if threshold is not None else settings.SIMILARITY_THRESHOLD

        # 1. Embed query
        query_vector = await embedding_service.get_embedding(query)

        # 2. Search in Qdrant (fetch candidate pool of 3*k for hybrid scoring)
        raw_results = vector_store.search(
            query_vector=query_vector,
            top_k=k * 3,
            filters=filters
        )

        if not raw_results:
            return []

        # 3. Hybrid search combination with out-of-domain safeguard
        retrieved_items: List[RetrievedChunk] = []
        for res in raw_results:
            payload = res.get("payload", {})
            semantic_score = res.get("score", 0.0)
            chunk_text = payload.get("text", "")

            # Keyword match boost
            kw_score = self._keyword_overlap_score(query, chunk_text)
            
            # Combined hybrid score (60% semantic + 40% keyword)
            hybrid_score = (0.6 * semantic_score) + (0.4 * kw_score)

            # Relevance criteria:
            # - If at least 1 informative query keyword matched: requires hybrid_score >= min_threshold
            # - If 0 keywords matched: requires a strong semantic match (>= 0.60) to prevent hallucinated context
            is_relevant = (kw_score > 0 and hybrid_score >= min_threshold) or (kw_score == 0 and semantic_score >= 0.60)

            if is_relevant:
                retrieved_items.append(
                    RetrievedChunk(
                        chunk_id=payload.get("chunk_id", res.get("id")),
                        document_id=payload.get("document_id", ""),
                        text=chunk_text,
                        page_number=payload.get("page_number", 1),
                        section=payload.get("section", ""),
                        title=payload.get("title", "College Document"),
                        file_name=payload.get("fileName", ""),
                        category=payload.get("category", "General"),
                        department=payload.get("department", "All"),
                        academic_year=payload.get("academicYear", "2026"),
                        score=hybrid_score
                    )
                )

        # Sort by hybrid score descending
        retrieved_items.sort(key=lambda x: x.score, reverse=True)
        return retrieved_items[:k]

retrieval_service = RetrievalService()
