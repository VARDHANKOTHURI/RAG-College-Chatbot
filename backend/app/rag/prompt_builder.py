from typing import List, Dict, Any
from backend.app.rag.retrieval_service import RetrievedChunk

UNKNOWN_RESPONSE_TEMPLATE = (
    "I couldn't find this information in the available college documents. "
    "Please contact the concerned department or administrator for accurate information."
)

class PromptBuilder:
    @staticmethod
    def build_rag_prompt(
        query: str,
        chunks: List[RetrievedChunk],
        conversation_history: List[Dict[str, str]] = None,
        language: str = "English"
    ) -> str:
        # Build context blocks with clear source citations
        context_blocks = []
        for i, chunk in enumerate(chunks, 1):
            block = (
                f"[Source {i}]: Document: \"{chunk.title}\" | Page: {chunk.page_number} | Category: {chunk.category} | Department: {chunk.department}\n"
                f"Content:\n{chunk.text}"
            )
            context_blocks.append(block)
        
        full_context = "\n\n---\n\n".join(context_blocks)

        # Build recent conversation history
        history_text = ""
        if conversation_history:
            formatted_turns = []
            for turn in conversation_history[-4:]:  # last 4 turns
                role = "Student" if turn.get("role") == "user" else "Assistant"
                formatted_turns.append(f"{role}: {turn.get('content', '')}")
            history_text = "\nRecent Conversation:\n" + "\n".join(formatted_turns) + "\n"

        language_instruction = f"Respond in {language}." if language and language.lower() != "english" else ""

        system_instructions = f"""You are the official AI Academic and College Information Assistant.
Your job is to provide accurate, helpful, and concise answers to student inquiries based SOLELY on the authorized College Knowledge Base documents provided below.

CRITICAL RULES:
1. Grounding Rule: Answer strictly using facts and information from the provided College Knowledge Base context.
2. No Hallucination: If the requested information cannot be found in or directly inferred from the provided context, you MUST explicitly respond with:
   "{UNKNOWN_RESPONSE_TEMPLATE}"
3. Do not make up dates, fees, rules, or contact details not present in the context.
4. Source Attribution: When providing details, naturally reference the document title and page number where appropriate.
5. Formatting: Use clean Markdown with bullet points, bold key terms, and readable paragraphs.
{language_instruction}
"""

        user_prompt = f"""{history_text}
College Knowledge Base Context:
===============================
{full_context}
===============================

Student Question: {query}

Please provide a clear, accurate, and well-structured answer based strictly on the context above:"""

        return f"{system_instructions}\n\n{user_prompt}"
