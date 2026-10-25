"""Normalize resume text while preserving technical punctuation."""
import re

def clean_text(text: str) -> str:
    """Lowercase and normalize text while keeping paragraph breaks and technical symbols."""
    text = text.casefold()
    text = re.sub(r"[^\w+#.\-/\n ]+", " ", text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)
