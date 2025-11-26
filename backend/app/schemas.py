from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    question: str


class SourceChunk(BaseModel):
    source: str
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
