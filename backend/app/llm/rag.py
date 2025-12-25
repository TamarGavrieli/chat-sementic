from typing import List, Dict
from pathlib import Path

MAX_CONTEXT_CHARS = 1000  

def build_prompt(question: str, chunks: List[Dict]) -> str:
    context_blocks = []
    current_length = 0

    for i, chunk in enumerate(chunks, start=1):
        source_name = Path(chunk["source"]).name
        content = chunk.get("content", "").strip()
        block = f"[Source {i}: {source_name}]\n{content}"
        if current_length + len(block) > MAX_CONTEXT_CHARS:
            break
        context_blocks.append(block)
        current_length += len(block)

    context_text = "\n\n".join(context_blocks)

    prompt = f"""
You are an experienced Israeli real-estate legal assistant.
Your job is to explain legal matters to non-lawyers in clear, fluent Hebrew.

Answer the question in clear, natural Hebrew.
Base your answer on the provided document excerpts.
You may paraphrase and explain the content in your own words.
Do NOT introduce facts that do not appear in the excerpts.
Do NOT copy sentences verbatim from the excerpts.

Question:
{question}

Relevant excerpts:
{context_text}

Structure your answer as:
1. A short direct answer (1-2 sentences)
2. A brief explanation (2-4 sentences) 
3. Sources used (e.g., Source 1, Source 3)

IMPORTANT: Write your entire answer in fluent, natural Hebrew. Be clear and professional.
Limit the answer to at most 120 words.


"""
    print(f"[DEBUG] Prompt length: {len(prompt)} chars")
    print(f"[DEBUG] Number of chunks used: {len(context_blocks)}")

    return prompt.strip()
