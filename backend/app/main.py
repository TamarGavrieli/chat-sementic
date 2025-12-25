from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import time
import os

from .schemas import ChatRequest
from .services import SemanticSearchService

# 🔹 RAG + LLM
from .llm.rag import build_prompt
from .llm.ollama_model import OllamaChatModel

app = FastAPI(title="Semantic Verdict Chat")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM 
chat_model = OllamaChatModel(model="llama3.1:8b-instruct-q4_K_M")

# Vector DB
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_DIR = PROJECT_ROOT / "data" / "index"
search_service = SemanticSearchService(index_dir=INDEX_DIR)

# Debug mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


# ======================
# Warm-up (קריטי למהירות)
# ======================

@app.on_event("startup")
def warmup_llm():
    print("[INFO] Warming up LLM...")
    try:
        tokens = []
        for token in chat_model.stream("שלום, מה שלומך?"):
            tokens.append(token)
            if len(tokens) >= 10:  # 10 tokens מספיק
                break
        print(f"[INFO] LLM warm-up completed ({len(tokens)} tokens)")
    except Exception as e:
        print("[WARN] LLM warm-up failed:", e)


# ======================
# Streaming Answer Logic
# ======================

def stream_answer(question: str):
    total_start = time.time()
    
    # 🔍 Retrieval (RAG)
    print(f"[TIME] Starting search...")
    results = search_service.search(question, k=2)
    print(f"[TIME] Search done: {time.time() - total_start:.2f}s")
    
    if not results:
        msg = "לא נמצאו קטעים רלוונטיים במסמכים עבור השאלה הזו."
        for ch in msg:
            yield ch
            time.sleep(0.01)
        return
    
    # Build prompt
    prompt = build_prompt(question, results)
    print(f"[TIME] Prompt built: {time.time() - total_start:.2f}s")
    
    # Debug: print prompt preview
    if DEBUG:
        print("==== PROMPT SENT TO LLM ====")
        print(prompt)
        print("================================")
    else:
        print(f"[DEBUG] Prompt preview: {prompt[:200]}...")
    
    # 🤖 LLM Generation
    llm_start = time.time()
    for token in chat_model.stream(prompt):
        yield token
    
    print(f"[TIME] LLM response: {time.time() - llm_start:.2f}s")
    print(f"[TIME] Total: {time.time() - total_start:.2f}s")


# ======================
# API Endpoint
# ======================

@app.post("/chat")
def chat(req: ChatRequest):
    return StreamingResponse(
        stream_answer(req.question),
        media_type="text/plain"
    )