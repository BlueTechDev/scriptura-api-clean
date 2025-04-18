from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import faiss
import json
import numpy as np
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import re

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)
index_path = Path("app/data/embedded_data/faiss_index.idx")
data_path = Path("app/data/embedded_data/embedded_data.jsonl")

if not index_path.exists():
    raise FileNotFoundError("FAISS index not found. Run the pipeline first.")

faiss_index = faiss.read_index(str(index_path))

with open(data_path, "r", encoding="utf-8") as f:
    embedded_data = [json.loads(line) for line in f]

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

def sanitize_input(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r"[?!.]{2,}", ".", text)
    return text

@router.post("/qa")
def ask_scriptura(query: SearchRequest):
    cleaned_query = sanitize_input(query.query)
    if not cleaned_query or len(cleaned_query) < 3:
        raise HTTPException(status_code=400, detail="Please enter a meaningful question.")

    query_embedding = model.encode(cleaned_query).astype(np.float32)
    distances, indices = faiss_index.search(np.array([query_embedding]), query.top_k)

    if len(indices[0]) > 0 and indices[0][0] != -1:
        top_contexts = [embedded_data[i]["content"] for i in indices[0] if i != -1]
        context = "\n\n".join(top_contexts)

        if len(context.split()) > 1500:
            context = "\n\n".join(top_contexts[:2])

        response = generate_openai_response(cleaned_query, context=context)
        return {"response": response}

    fallback = generate_openai_response(cleaned_query)
    return {"response": fallback}

SYSTEM_PROMPT = """
You are a Scriptura AI assistant trained to provide biblically accurate, warm, and conversational guidance.

### CORE GUIDELINES
- You only speak from Scripture and doctrinally sound, conservative Christian teachings.
- You **never speculate** on doctrine.
- For complex theological matters (e.g. Trinity, Holy Communion), kindly advise the user to consult their pastor.
- When unsure or if something surpasses human understanding, you must **not guess**.

### RESPONSE STYLE
- Use a warm, approachable tone, as if you're gently guiding a curious believer.
- Keep formatting clean—speak plainly without markdown, special characters, or emojis.
- Do **not** cite titles or URLs. Respond conversationally, like a helpful pastor might.
- Always clarify when something is directly biblical versus a derived teaching.

### EXAMPLES
- "Scripture teaches..."
- "According to God's Word in..."
- "This is a teaching where it's best to speak with your pastor for personal guidance."

Stay rooted in grace, firm in truth.
"""

def generate_openai_response(query: str, context: str = "") -> str:
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context:
            messages.append({"role": "user", "content": f"Use the following doctrinal material as context when answering:\n\n{context}"})

        messages.append({"role": "user", "content": query})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"\U0001F525 OpenAI Chat Completions Error: {e}")
        raise
