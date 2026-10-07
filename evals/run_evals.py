"""Small honest eval suite for the agentic RAG assistant.

Metrics (simple heuristics, described as such — not LLM-judge scores):
  - retrieval_hit@k: fraction of answerable questions where the expected source
    document appears among the top-k retrieved chunks.
  - keyword_recall: for answerable questions, fraction of expected keywords that
    appear (case-insensitive) in the agent's answer. A rough proxy for whether
    the answer contains the key facts — not a faithfulness proof.
  - abstention_accuracy: fraction of unanswerable questions where the agent
    correctly abstained ("I don't know"), plus no false abstentions on
    answerable ones.

Runs with no API key: the agent uses its extractive fallback, so the eval
measures retrieval + fallback quality, not a paid LLM.

Usage:  python evals/run_evals.py [--k 5]
Writes: evals/results.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import agent  # noqa: E402

EVAL_DIR = Path(__file__).parent


def keyword_recall(answer: str, keywords) -> float:
    if not keywords:
        return 1.0
    low = answer.lower()
    return sum(1 for kw in keywords if kw.lower() in low) / len(keywords)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    eval_set = json.loads((EVAL_DIR / "eval_set.json").read_text())
    rows, hits, recalls, abstain_ok, abstain_total, false_abstains = [], 0, [], 0, 0, 0

    for item in eval_set:
        res = agent.ask(item["question"])
        row = {"id": item["id"], "question": item["question"],
               "abstained": res["abstained"], "mode": res["mode"]}
        if item["answerable"]:
            sources = [r["source"] for r in res["retrieved"][:args.k]]
            hit = item["expected_source"] in sources
            hits += hit
            rec = keyword_recall(res["answer"], item["expected_keywords"])
            recalls.append(rec)
            row.update(retrieval_hit=hit, keyword_recall=round(rec, 3),
                       top_source=sources[0] if sources else None)
            if res["abstained"]:
                false_abstains += 1
        else:
            abstain_total += 1
            ok = res["abstained"]
            abstain_ok += ok
            row.update(abstention_correct=ok)
        rows.append(row)
        print(f"{item['id']}: abstained={res['abstained']} mode={res['mode']} "
              f"{ {k: v for k, v in row.items() if k not in ('id','question','abstained','mode')} }")

    n_answerable = sum(1 for i in eval_set if i["answerable"])
    summary = {
        "n_questions": len(eval_set),
        "n_answerable": n_answerable,
        "n_unanswerable": abstain_total,
        "retrieval_hit@k": round(hits / n_answerable, 3),
        "mean_keyword_recall": round(sum(recalls) / len(recalls), 3) if recalls else 0.0,
        "abstention_accuracy": round(abstain_ok / abstain_total, 3) if abstain_total else 0.0,
        "false_abstentions": false_abstains,
        "generation_mode": rows[0]["mode"] if rows else "n/a",
        "note": ("Heuristic metrics on a 13-question set; keyword recall is a rough "
                 "proxy for answer completeness, not a faithfulness proof. "
                 "Thresholds tuned on this same tiny set — treat as sanity checks."),
    }
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    (EVAL_DIR / "results.json").write_text(json.dumps(
        {"summary": summary, "rows": rows}, indent=2))
    print(f"\nWrote {EVAL_DIR / 'results.json'}")


if __name__ == "__main__":
    main()
