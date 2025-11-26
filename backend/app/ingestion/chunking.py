from typing import List, Dict


def chunk_text(
    text: str,
    max_chars: int = 1000,
    overlap: int = 200,
) -> List[str]:
    text = text.strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + max_chars, text_len)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_len:
            break
        start = end - overlap
        if start < 0:
            start = 0

    return chunks


def chunk_documents(
    docs: List[Dict],
    max_chars: int = 1000,
    overlap: int = 200,
) -> List[Dict]:
    all_chunks: List[Dict] = []
    for doc_idx, doc in enumerate(docs):
        content = doc["content"]
        path = doc["path"]
        doc_type = doc["type"]
        chunks = chunk_text(content, max_chars=max_chars, overlap=overlap)
        for chunk_idx, chunk in enumerate(chunks):
            all_chunks.append({
                "doc_id": doc_idx,
                "chunk_id": chunk_idx,
                "content": chunk,
                "source_path": str(path),
                "doc_type": doc_type,
            })

    print(f"[INFO] Created {len(all_chunks)} chunks from {len(docs)} docs")
    return all_chunks
