from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import time
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ChatRequest
from .services import SemanticSearchService
from backend.app.utils.text import make_snippet






app = FastAPI(title="Semantic Verdict Chat")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_DIR = PROJECT_ROOT / "data" / "index"
search_service = SemanticSearchService(index_dir=INDEX_DIR)

def stream_answer(question: str):
    results = search_service.search(question)
    if not results:
        msg = "לא נמצאו קטעים רלוונטיים במסמכים עבור השאלה הזו.\n"
        for ch in msg:
            yield ch
            time.sleep(0.01)
        return

    source_snippets: dict[str, str] = {}
    for r in results:
        src = r["source"]
        if src in source_snippets:
            continue  

        raw_text = r.get("content") or ""
        text = make_snippet(raw_text, max_chars=220)
        source_snippets[src] = text



    lines: list[str] = [] 
    lines.append(" תשובה (מבוססת על הקטעים הרלוונטיים שנמצאו במסמכים):")
    lines.append("")  
    lines.append(" מקורות רלוונטיים:")
    lines.append("")
    for i, (src, snippet) in enumerate(source_snippets.items(), start=1):
        filename = Path(src).name
        lines.append(f"[{i}] {filename}")
        lines.append(f"    {snippet}")
        lines.append("")

    answer = "\n".join(lines)
    for ch in answer:
        yield ch
        time.sleep(0.01)




@app.post("/chat")
def chat(req: ChatRequest):
    return StreamingResponse(
        stream_answer(req.question),
        media_type="text/plain"
    )
