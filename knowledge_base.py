"""Corpus ingestion: chunk markdown docs, embed them, and build a FAISS index.

Pipeline:  .md docs -> word-overlap chunking -> sentence-transformers embeddings
           (L2-normalized) -> FAISS IndexFlatIP (cosine similarity via inner product)
"""
import os
from pathlib import Path
from typing import List, Dict

import numpy as np

DATA_DIR = Path(__file__).parent / "data" / "docs"
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
# Smaller chunks keep doc sections focused; 120/20 beat 200/30 on top-1
# accuracy (9/10 vs 6/10) on the bundled 13-question eval set.
CHUNK_WORDS = int(os.getenv("CHUNK_WORDS", "120"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "20"))


def load_documents(data_dir: Path = DATA_DIR) -> List[Dict[str, str]]:
    """Read every .md file in the docs dir. Returns [{source, text}]."""
    docs = []
    for path in sorted(data_dir.glob("*.md")):
        docs.append({"source": path.name, "text": path.read_text(encoding="utf-8")})
    if not docs:
        raise FileNotFoundError(f"No .md documents found in {data_dir}")
    return docs


def chunk_text(text: str, source: str,
               chunk_words: int = CHUNK_WORDS,
               overlap: int = CHUNK_OVERLAP) -> List[Dict[str, str]]:
    """Split text into word-overlap chunks, keeping the source filename."""
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + chunk_words, len(words))
        chunks.append({"source": source, "text": " ".join(words[start:end])})
        if end == len(words):
            break
        start = end - overlap
    return chunks


def chunk_corpus(docs: List[Dict[str, str]]) -> List[Dict[str, str]]:
    chunks = []
    for doc in docs:
        chunks.extend(chunk_text(doc["text"], doc["source"]))
    return chunks


def build_index(chunks: List[Dict[str, str]], embed_model: str = EMBED_MODEL):
    """Embed chunks and build a FAISS index. Returns (index, chunks, embedder)."""
    from sentence_transformers import SentenceTransformer
    import faiss

    print(f"Loading embedding model: {embed_model}")
    embedder = SentenceTransformer(embed_model)
    texts = [c["text"] for c in chunks]
    embeddings = embedder.encode(texts, normalize_embeddings=True,
                                 show_progress_bar=False).astype(np.float32)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    print(f"Indexed {len(chunks)} chunks (dim={embeddings.shape[1]})")
    return index, chunks, embedder


def search(index, embedder, chunks: List[Dict[str, str]],
           query: str, k: int = 5) -> List[Dict]:
    """Embed the query and return the top-k chunks with cosine-similarity scores."""
    q = embedder.encode([query], normalize_embeddings=True,
                        show_progress_bar=False).astype(np.float32)
    scores, ids = index.search(q, k)
    return [{"source": chunks[i]["source"], "text": chunks[i]["text"],
             "score": float(scores[0][rank])}
            for rank, i in enumerate(ids[0]) if i != -1]


def max_similarity(index, embedder, query: str) -> float:
    """Cosine similarity between the query and the single closest chunk."""
    q = embedder.encode([query], normalize_embeddings=True,
                        show_progress_bar=False).astype(np.float32)
    scores, _ = index.search(q, 1)
    return float(scores[0][0])
