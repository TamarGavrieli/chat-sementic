from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings


class SemanticVectorDB:
    
    def __init__(self, index_dir: Path, collection_name: str = "verdicts"):
        index_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(index_dir),
            settings=Settings(
                anonymized_telemetry=False
            ),
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def clear(self):
        
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ):
        
        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            ids.append(f"{chunk['doc_id']}_{chunk['chunk_id']}")
            documents.append(chunk["content"])
            metadatas.append({
                "source_path": chunk["source_path"],
                "doc_type": chunk["doc_type"],
                "doc_id": chunk["doc_id"],
                "chunk_id": chunk["chunk_id"],
            })

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def query(self, query_texts: List[str], n_results: int = 5):
        
        results = self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
        )
        return results
