"""CLI demo for the agentic RAG assistant.

Usage:
    python cli.py "How much does the Growth plan cost?"
    python cli.py          # interactive mode
"""
import json
import sys

import agent


def show(result: dict):
    print(f"\nQ: {result['question']}")
    print(f"A ({result['mode']}): {result['answer']}")
    if result["citations"]:
        print("Citations:", ", ".join(result["citations"]))
    if result["retrieved"]:
        top = ", ".join(f"{r['source']} ({r['score']})"
                        for r in result["retrieved"][:3])
        print(f"Top retrieved: {top}")


def main():
    if len(sys.argv) > 1:
        show(agent.ask(" ".join(sys.argv[1:])))
        return
    print("Agentic RAG CLI — ask about Nimbus Analytics (empty line quits).")
    while True:
        try:
            q = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            break
        show(agent.ask(q))


if __name__ == "__main__":
    main()
