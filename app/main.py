from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr
from slowapi import Limiter
from slowapi.util import get_remote_address
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

# FastAPI app
app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://scriptura-ui.vercel.app/", #  Frontend URL
        "http://localhost:5173" #localhost dev URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    )


limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter

# Schema
class QueryRequest(BaseModel):
    query: constr(min_length=1, max_length=500) # type: ignore

# Chat endpoint (no session)
@app.post("/search/")
@limiter.limit("10/minute")
async def get_response(request: Request, query_request: QueryRequest):
    query = query_request.query

    try:
        response = generate_openai_response(query, "")
        return {
            "query": query,
            "response": response,
            "source": "OpenAI"
        }

    except Exception as e:
        logger.error(f"Error during OpenAI call: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")

@app.get("/health/")
def health_check():
    return {"status": "✅ Scriptura AI backend live."}

@app.get("/")
def root():
    return {"message": "Welcome to Scriptura AI backend!"}

if __name__ != "__main__":
    app = app
