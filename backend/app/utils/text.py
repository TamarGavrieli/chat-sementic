import re

def normalize_hebrew(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def make_snippet(text: str, max_chars: int = 220) -> str:
    text = normalize_hebrew(text)
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    last_punct = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))
    if last_punct != -1 and last_punct > max_chars * 0.4:
        return cut[: last_punct + 1]
    return cut + "..."
