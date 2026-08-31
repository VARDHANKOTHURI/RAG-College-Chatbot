import re
import unicodedata

class TextProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        
        # Normalize unicode
        text = unicodedata.normalize("NFKD", text)
        
        # Replace non-breaking spaces and irregular tabs
        text = text.replace("\u00a0", " ").replace("\t", " ")
        
        # Remove consecutive non-printable characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Replace multiple empty lines with double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace multiple consecutive spaces on the same line with single space
        lines = [re.sub(r'[ ]{2,}', ' ', line).strip() for line in text.split("\n")]
        
        # Reconstruct text
        cleaned_text = "\n".join(lines).strip()
        return cleaned_text

    @staticmethod
    def extract_section_title(text: str) -> str:
        """Heuristic to detect the topmost heading or section in a text block."""
        lines = text.split("\n")
        for line in lines[:3]:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#") or re.match(r'^(Section|Chapter|Article|Clause|\d+\.|\b[A-Z\s]{4,}\b)', line):
                return line.lstrip("#").strip()
            if len(line) < 60 and line.isupper():
                return line
        return ""
