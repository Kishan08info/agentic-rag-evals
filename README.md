# Agentic RAG Assistant with Evals

A portfolio-grade **agentic RAG** system: a LangGraph agent that decides whether to
retrieve from a local knowledge base, answers with citations, and honestly says
"I don't know" when the documents don't cover the question — plus a small,
transparent eval suite measuring retrieval and answer quality.

Built with **LangGraph**, **sentence-transformers**, **FAISS**, and **FastAPI**.
Runs fully offline with no API key (extractive fallback); plug in any
OpenAI-compatible endpoint for generative answers.

## Architecture

```
                    ┌─────────────┐
                    │   router    │  max cosine sim(question, corpus)
                    │ (skip or    │  < ROUTE_THRESHOLD → abstain (no retrieval)
                    │  retrieve?) │  ≥ threshold      → retrieve
                    └──────┬──────┘
                           │ retrieve
                    ┌──────▼──────┐
                    │  retrieval  │  FAISS top-k over embedded chunks
                    │    tool     │  (all-MiniLM-L6-v2, IndexFlatIP ≈ cosine)
                    └──────┬──────┘
                           │ grade
                    ┌──────▼──────┐
              best < ANSWER_THRESHOLD ──▶ abstain: "I don't know based on
                    │                        the available documents."
              best ≥ threshold
                    ▼
              generate: LLM (if key set) or extractive fallback,
                        always with [source: filename] citations
```

- **Knowledge base:** 6 original markdown docs about a fictional company
  (*Nimbus Analytics*) in `data/docs/` — product, pricing, API, security, FAQ,
  changelog. Chunked with word overlap (120/20 — beat 200/30 on top-1 accuracy,
  9/10 vs 6/10, on the eval set), embedded with `all-MiniLM-L6-v2`, stored in
  FAISS.
- **Agent:** a LangGraph `StateGraph` (`agent.py`) with `router → retrieve →
  generate` nodes and conditional edges. The router's similarity gate and the
  post-retrieval confidence grade are the two "don't hallucinate" guardrails.
- **LLM layer** (`llm.py`): provider-agnostic — any OpenAI-compatible
  `/chat/completions` endpoint via `LLM_BASE_URL`/`LLM_API_KEY`. With no key,
  the agent degrades to clearly-labeled **extractive answers** (top passages
  quoted verbatim with sources). It never pretends a fallback is generated.

## Run it

```bash
pip install -r requirements.txt

# CLI
python cli.py "How much does the Growth plan cost?"

# API + demo UI
uvicorn app:app --reload
# open http://localhost:8000  (demo UI)
# curl -X POST localhost:8000/ask -H "Content-Type: application/json" \
#   -d '{"question": "Is Nimbus SOC 2 compliant?"}'
```

For generative answers, copy `.env.example` to `.env` and set `LLM_BASE_URL`
and `LLM_API_KEY` (any OpenAI-compatible endpoint). Without them everything
still works via the extractive fallback.

With Docker:

```bash
docker build -t agentic-rag-evals .
docker run -p 8000:8000 --env-file .env agentic-rag-evals
```

## Evals

`evals/run_evals.py` runs a 13-question set (10 answerable, 3 unanswerable)
against the agent and reports three simple heuristic metrics:

| Metric | What it measures | Result (extractive mode, no LLM key) |
|---|---|---|
| retrieval hit@5 | expected source doc in top-5 retrieved chunks | **0.9** (9/10) |
| mean keyword recall | expected key facts present in the answer (case-insensitive) | **0.875** |
| abstention accuracy | unanswerable questions correctly abstained | **1.0** (3/3) |
| false abstentions | answerable questions wrongly abstained | 1 (the "v2.4 changelog" question — retrieval confidence 0.222 fell below the 0.30 bar, so the agent abstained rather than answer from weak evidence) |

Run them yourself (no API key needed):

```bash
python evals/run_evals.py
```

These are deliberately simple heuristics — keyword recall is a rough proxy for
answer completeness, not a faithfulness proof, and the thresholds were tuned on
this same tiny set. Treat them as sanity checks, documented in
`evals/results.json`.

## What's genuinely implemented vs. stubbed

**Implemented:** markdown ingestion with overlap chunking; dense retrieval with
FAISS; a real LangGraph agent graph with routing + abstention guardrails;
cited answers; FastAPI service (`/ask`, `/health`, `/sources`) with a minimal
demo UI and CLI; a runnable eval suite with real numbers above; Docker build.

**Honestly limited / not claimed:** no LLM-as-judge evals; no reranker or
hybrid (BM25+dense) retrieval; no multi-hop reasoning; the "generative" path
needs your own key and is unverified here — evals ran in extractive mode;
thresholds picked on 13 questions will need retuning on a real corpus.

## What this demonstrates

- Agentic control flow with LangGraph: tool use, conditional routing, graceful abstention
- Production RAG concerns: chunking strategy, cosine retrieval, citation grounding
- Eval-driven development: small, honest metrics before scaling up
- API design + graceful degradation (works with zero external services)

## Interview talking points

- Why gate retrieval on similarity at all? (Saves compute on out-of-domain
  questions; the abstain path is cheaper than a doomed retrieval + generation.)
- Why two thresholds (route vs. answer)? (Route is a cheap pre-filter; the
  post-retrieval grade sees actual evidence before committing to an answer.)
- Why extractive fallback instead of failing without a key? (A portfolio
  project should be runnable by anyone; the fallback is labeled, not disguised.)
- What's the first thing you'd improve? (Hybrid retrieval + a cross-encoder
  reranker, then LLM-judge faithfulness evals on a larger set.)
