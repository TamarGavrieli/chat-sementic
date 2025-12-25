from typing import List, Dict
from pathlib import Path
from .vectordb.vectordb import SemanticVectorDB   
from .llm.base import LocalEmbeddingModel     


class SemanticSearchService:
    MAX_DISTANCE_THRESHOLD = 0.5

    def __init__(self, index_dir: Path):
        self.vectordb = SemanticVectorDB(
            index_dir=index_dir,
            collection_name="verdicts"
        )
        self.embed_model = LocalEmbeddingModel()

    def search(self, question: str, k: int = 2) -> List[Dict]:
        query_embedding = self.embed_model.embed_texts([question])

        results = self.vectordb.collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )


        if not results["documents"] or not results["documents"][0]:
            return []
        best_distance = results["distances"][0][0]
        print("[DEBUG] Best distance:", best_distance) 
        if best_distance > self.MAX_DISTANCE_THRESHOLD:
            return []

        documents = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            documents.append({
                "content": doc,
                "source": meta["source_path"],
                "distance": dist
            })

        return documents
