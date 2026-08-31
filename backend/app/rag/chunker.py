import uuid
from typing import List, Dict, Any
from backend.app.config.settings import settings
from backend.app.rag.document_loader import LoadedPage
from backend.app.rag.text_processor import TextProcessor

class Chunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        chunk_index: int,
        text: str,
        page_number: int,
        section: str,
        metadata: Dict[str, Any]
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.chunk_index = chunk_index
        self.text = text
        self.page_number = page_number
        self.section = section
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "page_number": self.page_number,
            "section": self.section,
            "metadata": self.metadata
        }

class DocumentChunker:
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        separators: List[str] = None
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.separators = separators or ["\n\n", "\n", ". ", "? ", "! ", " ", ""]

    def _split_text_recursively(self, text: str, separators: List[str]) -> List[str]:
        final_chunks = []
        if not separators:
            return [text] if text else []
        
        separator = separators[0]
        splits = text.split(separator) if separator else list(text)
        
        current_chunk = []
        current_length = 0
        
        for split in splits:
            item = split + (separator if separator else "")
            item_len = len(item)
            
            if current_length + item_len <= self.chunk_size:
                current_chunk.append(item)
                current_length += item_len
            else:
                if current_chunk:
                    chunk_text = "".join(current_chunk).strip()
                    if chunk_text:
                        final_chunks.append(chunk_text)
                    
                    # Handle overlap
                    overlap_items = []
                    overlap_len = 0
                    for prev_item in reversed(current_chunk):
                        if overlap_len + len(prev_item) <= self.chunk_overlap:
                            overlap_items.insert(0, prev_item)
                            overlap_len += len(prev_item)
                        else:
                            break
                    current_chunk = overlap_items
                    current_length = overlap_len
                
                if item_len > self.chunk_size and len(separators) > 1:
                    sub_chunks = self._split_text_recursively(split, separators[1:])
                    for sc in sub_chunks:
                        if sc.strip():
                            final_chunks.append(sc.strip())
                    current_chunk = []
                    current_length = 0
                else:
                    current_chunk.append(item)
                    current_length += item_len
        
        if current_chunk:
            chunk_text = "".join(current_chunk).strip()
            if chunk_text:
                final_chunks.append(chunk_text)
                
        return final_chunks

    def chunk_document(
        self,
        document_id: str,
        pages: List[LoadedPage],
        doc_metadata: Dict[str, Any] = None
    ) -> List[Chunk]:
        doc_metadata = doc_metadata or {}
        chunks: List[Chunk] = []
        chunk_idx = 0
        current_section = doc_metadata.get("title", "")

        for page in pages:
            cleaned_page_text = TextProcessor.clean_text(page.text)
            if not cleaned_page_text:
                continue

            extracted_section = TextProcessor.extract_section_title(cleaned_page_text)
            if extracted_section:
                current_section = extracted_section

            raw_chunks = self._split_text_recursively(cleaned_page_text, self.separators)

            for text_piece in raw_chunks:
                text_piece = text_piece.strip()
                if len(text_piece) < 20:  # Skip tiny fragments
                    continue

                chunk_id = str(uuid.uuid4())
                meta = {
                    "document_id": document_id,
                    "title": doc_metadata.get("title", ""),
                    "fileName": doc_metadata.get("fileName", ""),
                    "category": doc_metadata.get("category", "General FAQ"),
                    "department": doc_metadata.get("department", "All"),
                    "academicYear": doc_metadata.get("academicYear", "2026"),
                    "version": doc_metadata.get("version", 1),
                    "page_number": page.page_number,
                    "section": current_section
                }

                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        chunk_index=chunk_idx,
                        text=text_piece,
                        page_number=page.page_number,
                        section=current_section,
                        metadata=meta
                    )
                )
                chunk_idx += 1

        return chunks
