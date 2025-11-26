from typing import List, Dict
from pathlib import Path

from .vectordb.vectordb import SemanticVectorDB   
from .llm.base import LocalEmbeddingModel     


class SemanticSearchService:
    def __init__(self, index_dir: Path):
        self.vectordb = SemanticVectorDB(index_dir=index_dir, collection_name="verdicts")
        self.embed_model = LocalEmbeddingModel()

    def search(self, question: str, k: int = 5) -> List[Dict]:
        query_embedding = self.embed_model.embed_texts([question])

        results = self.vectordb.collection.query(
            query_embeddings=query_embedding,
            n_results=k,
        )

        documents = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            documents.append({
                "content": doc,
                "source": meta["source_path"],
            })

        return documents
