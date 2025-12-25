import requests
import json
from typing import Generator
from .base import BaseChatModel


class OllamaChatModel(BaseChatModel):
    def __init__(self, model: str = "llama3.1:8b-instruct-q4_K_M"):
        self.model_name = model
        self.base_url = "http://localhost:11434"
    
    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream response from Ollama (local LLM)."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "num_predict": 150,  # תשובה קצרה = מהר יותר
                        "temperature": 0.2,
                        "top_p": 0.9
                    }
                },
                stream=True,
                timeout=600  #10 דק
            )
            
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                data = json.loads(line)

                if data.get("done"):
                    break  
                
                chunk = data.get("response")
                if chunk:
                    yield chunk

        except requests.exceptions.Timeout:
            yield "הזמן הקצוב לתשובה עבר. נסה שאלה קצרה יותר."
        except Exception as e:
            yield f"שגיאה בחיבור ל-Ollama: {str(e)}"