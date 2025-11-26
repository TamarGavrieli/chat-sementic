from pathlib import Path
import sys
from app.ingestion.loaders import load_all_documents
from app.ingestion.chunking import chunk_documents

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.append(str(BACKEND_DIR))




def main():
    raw_dir = PROJECT_ROOT / "data" / "raw"
    docs = load_all_documents(raw_dir)
    print(f"[INFO] Loaded {len(docs)} docs")
    chunks = chunk_documents(docs, max_chars=800, overlap=200)
    print(f"[INFO] Total chunks: {len(chunks)}")
    for c in chunks[:3]:
        print("----")
        print(f"Source: {c['source_path']} (doc_id={c['doc_id']}, chunk_id={c['chunk_id']})")
        print(c["content"][:400])
        print("...")


if __name__ == "__main__":
    main()
