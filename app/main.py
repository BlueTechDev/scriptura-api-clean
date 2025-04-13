from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, constr
from slowapi import Limiter
from slowapi.util import get_remote_address;
from dotenv import load_dotenv
from app.openai_handler import generate_openai_response
import os
import logging

# Load .env vars
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App init
app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock this to frontend prod domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(SessionMiddleware, secret_key="super_secure_key")
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter

# Schema
class QueryRequest(BaseModel):
    query: constr(min_length=1, max_length=500) # type: ignore

# Context memory helpers
async def get_session_context(request: Request):
    return request.session.get("chat_history", [])

async def update_session_context(request: Request, user_message: str, bot_response: str):
    session_data = request.session.get("chat_history", [])
    if len(session_data) >= 20:
        session_data = session_data[2:]
    session_data.append(f"**User:** {user_message}")
    session_data.append(f"**Assistant:** {bot_response}")
    request.session["chat_history"] = session_data

# Chat endpoint
@app.post("/search/")
@limiter.limit("10/minute")
async def get_response(request: Request, query_request: QueryRequest):
    query = query_request.query
    context = "\n".join(await get_session_context(request))

    try:
        response = generate_openai_response(query, context)
        await update_session_context(request, query, response)

        return {
            "query": query,
            "response": response,
            "context": context,
            "source": "OpenAI"
        }

    except Exception as e:
        logger.error(f"Error during OpenAI call: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")

# Health check
@app.get("/health/")
def health_check():
    return {"status": "✅ Scriptura AI backend live."}

# Vercel / Render ASGI support
if __name__ != "__main__":
    app = app
