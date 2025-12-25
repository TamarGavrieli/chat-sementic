from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import time

from .schemas import ChatRequest
from .services import SemanticSearchService

# 🔹 RAG + LLM
from .llm.rag import build_prompt
from .llm.ollama_model import OllamaChatModel


# ======================
# App & Model Init
# ======================

app = FastAPI(title="Semantic Verdict Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM (מודל חזק, מקומי)
chat_model = OllamaChatModel(model="llama3.1:8b-instruct-q4_K_M")

# Vector DB
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_DIR = PROJECT_ROOT / "data" / "index"
search_service = SemanticSearchService(index_dir=INDEX_DIR)


# ======================
# Warm-up (קריטי למהירות)
# ======================

@app.on_event("startup")
def warmup_llm():
    print("[INFO] Warming up LLM...")
    try:
        # שולחים prompt קצר מאוד ולוקחים טוקן אחד
        for _ in chat_model.stream("שלום"):
            break
        print("[INFO] LLM warm-up completed")
    except Exception as e:
        print("[WARN] LLM warm-up failed:", e)


# ======================
# Streaming Answer Logic
# ======================

def stream_answer(question: str):
    # 🔍 Retrieval (RAG)
    start = time.time()
    print(f"[TIME] Started at {start}")
    results = search_service.search(question, k=2)
    print(f"[TIME] Search done: {time.time() - start:.2f}s")
    if not results:
        msg = "לא נמצאו קטעים רלוונטיים במסמכים עבור השאלה הזו."
        for ch in msg:
            yield ch
            time.sleep(0.01)
        return

    # 🧠 Build prompt (RAG אחד, אחיד)
    prompt = build_prompt(question, results)
    print(f"[TIME] Prompt built: {time.time() - start:.2f}s")
    print(f"[DEBUG] Calling LLM now...")
    # 🧪 Debug (אפשר למחוק בהמשך)
    print("==== PROMPT SENT TO LLM ====")
    print(prompt)
    print("================================")

    # 🤖 Streaming מה-LLM
    start_time = time.time()
    for token in chat_model.stream(prompt):
        yield token
    print(f"[INFO] LLM response time: {time.time() - start_time:.2f}s")
    print(f"[TIME] Total: {time.time() - start:.2f}s")


# ======================
# API Endpoint
# ======================

@app.post("/chat")
def chat(req: ChatRequest):
    return StreamingResponse(
        stream_answer(req.question),
        media_type="text/plain"
    )
