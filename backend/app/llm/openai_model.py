from openai import OpenAI
from typing import Generator
from .base import BaseChatModel  # ייבוא המחלקה הבסיסית


class OpenAIChatModel(BaseChatModel):  # ← חשוב! צריך לרשת מהמחלקה הבסיסית
    def __init__(self, model: str):
        self.client = OpenAI()  # או עם api_key אם צריך
        self.model_name = model
    
    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream response from OpenAI."""
        stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content