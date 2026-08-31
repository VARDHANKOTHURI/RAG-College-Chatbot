import json
import asyncio
from typing import AsyncGenerator, Optional
import httpx
from backend.app.config.settings import settings
from backend.app.utils.logger import logger
from backend.app.rag.prompt_builder import UNKNOWN_RESPONSE_TEMPLATE

class LLMService:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.openrouter_key = settings.OPENROUTER_API_KEY
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE

    async def generate_response(self, prompt: str) -> str:
        if settings.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={settings.GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": self.temperature,
                        "maxOutputTokens": 1024
                    }
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts:
                                return parts[0].get("text", "")
                    else:
                        logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"Gemini API error: {e}")

        if settings.OPENROUTER_API_KEY:
            try:
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "google/gemini-flash-1.5",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"OpenRouter API error: {e}")

        return self._extractive_fallback(prompt)

    async def generate_response_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        if settings.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent?alt=sse&key={settings.GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": self.temperature,
                        "maxOutputTokens": 1024
                    }
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    async with client.stream("POST", url, json=payload, headers={"Content-Type": "application/json"}) as resp:
                        if resp.status_code == 200:
                            async for line in resp.aiter_lines():
                                if line.startswith("data: "):
                                    try:
                                        chunk_data = json.loads(line[6:])
                                        candidates = chunk_data.get("candidates", [])
                                        if candidates and "content" in candidates[0]:
                                            parts = candidates[0]["content"].get("parts", [])
                                            for part in parts:
                                                text = part.get("text", "")
                                                if text:
                                                    yield text
                                    except Exception:
                                        continue
                            return
            except Exception as e:
                logger.warning(f"Gemini streaming failed: {e}. Falling back to simulated streaming.")

        full_text = await self.generate_response(prompt)
        words = full_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield chunk
            await asyncio.sleep(0.015)

    def _extractive_fallback(self, prompt: str) -> str:
        if "College Knowledge Base Context:" not in prompt:
            return "Information retrieved successfully from college documents."

        try:
            context_part = prompt.split("College Knowledge Base Context:\n===============================\n")[1]
            context_part = context_part.split("\n===============================\n")[0]
            
            question_part = prompt.split("Student Question: ")[1].split("\n")[0].strip().lower()
            
            sources = context_part.split("\n\n---\n\n")
            if not sources or not sources[0].strip():
                return UNKNOWN_RESPONSE_TEMPLATE

            from backend.app.rag.embedding_service import STOP_WORDS
            import re
            q_tokens = [w for w in re.findall(r'\b[a-zA-Z0-9_\-\.]{3,}\b', question_part) if w not in STOP_WORDS]

            context_lower = context_part.lower()
            matched_terms = [t for t in q_tokens if t in context_lower]
            
            if not matched_terms or (len(q_tokens) >= 2 and len(matched_terms) / len(q_tokens) < 0.60):
                return UNKNOWN_RESPONSE_TEMPLATE

            relevant_lines = []
            for src in sources[:3]:
                lines = src.split("\n")
                content = lines[2:] if len(lines) > 2 else lines
                
                matching_in_src = []
                for line in content:
                    line_clean = line.strip()
                    if not line_clean or line_clean.startswith("==="):
                        continue
                    if any(t in line_clean.lower() for t in matched_terms):
                        matching_in_src.append(line_clean)

                if matching_in_src:
                    relevant_lines.extend(matching_in_src)

            if relevant_lines:
                seen = set()
                deduped = []
                for l in relevant_lines:
                    if l not in seen:
                        seen.add(l)
                        deduped.append(l)
                body = "\n".join(deduped[:8])
                return f"Based on the official college documents:\n\n{body}"
            
            return UNKNOWN_RESPONSE_TEMPLATE
        except Exception:
            return UNKNOWN_RESPONSE_TEMPLATE

llm_service = LLMService()
