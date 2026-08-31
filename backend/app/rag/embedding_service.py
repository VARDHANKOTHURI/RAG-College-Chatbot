import math
import hashlib
import re
from typing import List, Optional
import numpy as np
from backend.app.config.settings import settings
from backend.app.utils.logger import logger

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "can", "did", "do", "does", "doing", "don", "down", "during", "each", "few", "for", 
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", 
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", 
    "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", 
    "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", 
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", 
    "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", 
    "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", 
    "why", "will", "with", "you", "your", "yours", "yourself", "yourselves", "book", "get", "tell"
}

class EmbeddingService:
    def __init__(self, dimension: int = None):
        self.dimension = dimension or settings.EMBEDDING_DIMENSION
        self._hf_model = None
        self._initialized = False

    def _init_model(self):
        if self._initialized:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._hf_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"Loaded SentenceTransformer: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.info(f"Using deterministic TF-IDF semantic embedding engine ({e})")
            self._hf_model = None
        self._initialized = True

    def _deterministic_semantic_vector(self, text: str) -> List[float]:
        vec = np.zeros(self.dimension, dtype=np.float32)
        raw_words = re.findall(r'\b[a-zA-Z0-9_\-\.]{2,}\b', text.lower())
        if not raw_words:
            return vec.tolist()
        
        word_freq = {}
        for w in raw_words:
            word_freq[w] = word_freq.get(w, 0) + 1

        for word, count in word_freq.items():
            is_stop = word in STOP_WORDS
            base_weight = 0.1 if is_stop else 2.5
            tf_weight = (1.0 + math.log(count)) * base_weight
            
            if re.search(r'\d', word):
                tf_weight *= 3.0

            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            for k in range(3):
                idx = (h >> (k * 10)) % self.dimension
                sign = 1.0 if ((h >> (k * 4)) & 1) else -1.0
                vec[idx] += sign * tf_weight

            if not is_stop and len(word) >= 3:
                for j in range(len(word) - 2):
                    ng = word[j:j+3]
                    h_ng = int(hashlib.sha256(ng.encode('utf-8')).hexdigest(), 16)
                    idx_ng = h_ng % self.dimension
                    sign_ng = 1.0 if ((h_ng >> 8) & 1) else -1.0
                    vec[idx_ng] += sign_ng * 0.8

        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        return vec.tolist()

    async def get_embedding(self, text: str) -> List[float]:
        embeddings = await self.get_embeddings_batch([text])
        return embeddings[0]

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        self._init_model()

        if settings.GEMINI_API_KEY:
            try:
                import httpx
                headers = {"Content-Type": "application/json"}
                url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents?key={settings.GEMINI_API_KEY}"
                requests_payload = [{"model": "models/text-embedding-004", "content": {"parts": [{"text": t}]}} for t in texts[:20]]
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(url, json={"requests": requests_payload}, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        embeddings = [item["values"] for item in data.get("embeddings", [])]
                        if len(embeddings) == len(texts):
                            return embeddings
            except Exception as e:
                logger.warning(f"Gemini embedding API call failed: {e}. Falling back.")

        if self._hf_model is not None:
            try:
                embeddings = self._hf_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return embeddings.tolist()
            except Exception as e:
                logger.warning(f"SentenceTransformer encoding failed: {e}. Falling back to internal engine.")

        return [self._deterministic_semantic_vector(t) for t in texts]

embedding_service = EmbeddingService()
