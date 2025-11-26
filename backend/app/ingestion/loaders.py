from pathlib import Path
from typing import List, Dict

from docx import Document as DocxDocument
from pypdf import PdfReader


def load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        texts.append(text)
    return "\n".join(texts)


def load_docx(path: Path) -> str:
    doc = DocxDocument(str(path))
    texts = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            texts.append(text)
    return "\n".join(texts)


def load_all_documents(raw_dir: Path) -> List[Dict]:
    docs = []
    for path in raw_dir.iterdir():
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                content = load_pdf(path)
                doc_type = "pdf"
            elif suffix == ".docx":
                content = load_docx(path)
                doc_type = "docx"
            else:
                continue

            if content.strip():
                docs.append({
                    "path": path,
                    "content": content,
                    "type": doc_type,
                })
        except Exception as e:
            print(f"[WARN] Failed to load {path.name}: {e}")

    print(f"[INFO] Loaded {len(docs)} documents from {raw_dir}")
    return docs
