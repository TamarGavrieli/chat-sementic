from pathlib import Path
import sys
from app.ingestion.loaders import load_all_documents
from app.ingestion.chunking import chunk_documents
from app.llm.base import LocalEmbeddingModel
from app.vectordb.vectordb import SemanticVectorDB

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.append(str(BACKEND_DIR))


def main():
    raw_dir = PROJECT_ROOT / "data" / "raw"
    index_dir = PROJECT_ROOT / "data" / "index"
    print(f"[INFO] Using raw_dir={raw_dir}")
    print(f"[INFO] Using index_dir={index_dir}")
    docs = load_all_documents(raw_dir)
    if not docs:
        print("[!] No documents found in raw_dir. Aborting.")
        return
    print(f"[INFO] Loaded {len(docs)} documents")
    chunks = chunk_documents(docs, max_chars=800, overlap=200)
    if not chunks:
        print("[!] No chunks created. Aborting.")
        return
    print(f"[INFO] Created {len(chunks)} chunks")
    print("[INFO] Initializing embedding model (this may take a few seconds)...")
    embed_model = LocalEmbeddingModel()
    texts = [c["content"] for c in chunks]
    print(f"[INFO] Computing embeddings for {len(texts)} chunks...")
    embeddings = embed_model.embed_texts(texts)
    print("[INFO] Embeddings computed")
    print("[INFO] Initializing vector database...")
    vectordb = SemanticVectorDB(index_dir=index_dir, collection_name="verdicts")
    vectordb.clear()
    print("[INFO] Index cleared")
    print("[INFO] Adding chunks to vector database...")
    vectordb.add_chunks(chunks, embeddings)
    print("[✓] Index built successfully!")


if __name__ == "__main__":
    main()
