from abc import ABC, abstractmethod
from typing import List

from sentence_transformers import SentenceTransformer


class BaseEmbeddingModel(ABC):

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class LocalEmbeddingModel(BaseEmbeddingModel):
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=False)
        return [emb.tolist() if hasattr(emb, "tolist") else list(emb) for emb in embeddings]


class BaseChatModel(ABC):
    @abstractmethod
    def stream(self, prompt: str):
        raise NotImplementedError
