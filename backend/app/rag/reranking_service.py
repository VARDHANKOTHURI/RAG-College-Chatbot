from typing import List
from backend.app.rag.retrieval_service import RetrievedChunk
from backend.app.utils.logger import logger

class RerankingService:
    def __init__(self):
        self._cross_encoder = None
        self._initialized = False

    def _init_model(self):
        if self._initialized:
            return
        try:
            from sentence_transformers import CrossEncoder
            self._cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("Loaded CrossEncoder re-ranking model.")
        except Exception:
            self._cross_encoder = None
        self._initialized = True

    def rerank(self, query: str, chunks: List[RetrievedChunk], top_n: int = 4) -> List[RetrievedChunk]:
        if not chunks or len(chunks) <= top_n:
            return chunks

        self._init_model()

        if self._cross_encoder:
            try:
                pairs = [[query, chunk.text] for chunk in chunks]
                scores = self._cross_encoder.predict(pairs)
                for chunk, score in zip(chunks, scores):
                    chunk.score = float(score)
                chunks.sort(key=lambda x: x.score, reverse=True)
                return chunks[:top_n]
            except Exception as e:
                logger.warning(f"CrossEncoder reranking failed: {e}")

        # Fallback heuristic: exact phrase & keyword density re-ranking
        q_lower = query.lower()
        for chunk in chunks:
            text_lower = chunk.text.lower()
            bonus = 0.0
            if q_lower in text_lower:
                bonus += 0.25
            if chunk.section and chunk.section.lower() in q_lower:
                bonus += 0.15
            chunk.score += bonus

        chunks.sort(key=lambda x: x.score, reverse=True)
        return chunks[:top_n]

reranking_service = RerankingService()
