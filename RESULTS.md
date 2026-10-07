# Verification results — agentic-rag-evals

Date: 2026-10-07. All runs in extractive mode (no `LLM_API_KEY` set), so the
numbers below measure retrieval + fallback quality, not a paid LLM.

## Eval suite (`python evals/run_evals.py`)

13 questions (10 answerable, 3 unanswerable), all-MiniLM-L6-v2 embeddings,
FAISS IndexFlatIP, chunk 120/20, thresholds route=0.30 / answer=0.30.

| Metric | Result |
|---|---|
| retrieval hit@5 | 0.9 (9/10) |
| mean keyword recall | 0.875 |
| abstention accuracy | 1.0 (3/3) |
| false abstentions | 1 |

The single false abstention is q07 ("What was added in version 2.4?"):
top-1 similarity 0.222 fell below the 0.30 bar, so the agent abstained rather
than answering from weak evidence. The single retrieval@5 miss is the same
question (router skipped retrieval). Full per-question rows: `evals/results.json`.

## Tuning notes (kept, not hidden)

- Chunk 200/30 → top-1 accuracy 6/10; chunk 120/20 → 9/10. Shipped 120/20.
- ANSWER_THRESHOLD 0.45 → 6 false abstentions; 0.30 → 1 false abstention
  with abstention accuracy still 1.0. Shipped 0.30.
- Thresholds were picked on this same 13-question set — documented in the
  README as sanity checks, not production values.

## E2E checks

- `python cli.py "How much does the Growth plan cost?"` → extractive answer
  quoting pricing.md with `[source: pricing.md]` citations. Pass.
- `POST /ask` via FastAPI TestClient (answerable + unanswerable) → 200,
  correct `abstained` flags, citations list populated. Pass.
- `GET /health` → `{"status": "ok", "chunks_indexed": 12, ...}`. Pass.
- `GET /` serves the demo UI. Pass.

## Environment quirk (sandbox only)

The sandbox sets a `no_proxy` value containing bracketed IPv6 literals
(`[::1]`), which httpx ≥ 0.28 fails to parse when huggingface_hub downloads
the embedding model. Workaround used here: export a sanitized
`no_proxy`/`NO_PROXY` without brackets before running. Not needed on a normal
machine; the model itself is cached from the standard HF hub path.
