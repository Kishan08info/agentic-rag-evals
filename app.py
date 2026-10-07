"""FastAPI service for the agentic RAG assistant.

Endpoints:
  GET  /          -> minimal demo UI
  GET  /health    -> liveness + index stats
  GET  /sources   -> documents in the knowledge base
  POST /ask       -> {"question": "..."} -> agent answer with citations
"""
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

import agent
import knowledge_base as kb

app = FastAPI(title="Agentic RAG Assistant")

STATIC_DIR = Path(__file__).parent / "static"


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class RetrievedChunk(BaseModel):
    source: str
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    citations: List[str]
    abstained: bool
    mode: str
    retrieved: List[RetrievedChunk]


@app.get("/health")
def health():
    agent._ensure_index()
    return {"status": "ok",
            "chunks_indexed": len(agent._chunks),
            "llm_configured": __import__("llm").llm_available(),
            "thresholds": {"route": agent.ROUTE_THRESHOLD,
                           "answer": agent.ANSWER_THRESHOLD}}


@app.get("/sources")
def sources():
    return {"documents": [d["source"] for d in kb.load_documents()]}


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest):
    try:
        return agent.ask(req.question)
    except Exception as e:  # pragma: no cover - surfaced honestly
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
def demo_ui():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")
