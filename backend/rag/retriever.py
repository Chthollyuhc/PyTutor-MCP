"""SQLite FTS5 local retrieval with a replaceable vector-store interface."""
from __future__ import annotations

import re
import math
import sqlite3
import os
from pathlib import Path
from typing import Any

from backend.database import PROJECT_ROOT


KB_ROOT = PROJECT_ROOT / "docs" / "knowledge_base"
INDEX_PATH = Path(os.getenv("PYTUTOR_KNOWLEDGE_DB_PATH", PROJECT_ROOT / "pytutor_knowledge.sqlite3")).expanduser().resolve()


def _tokens(value: str) -> list[str]:
    return re.findall(r"[\w+#.-]+", value.lower(), flags=re.UNICODE)


def ingest_knowledge_base(root: Path = KB_ROOT, index_path: Path = INDEX_PATH) -> int:
    """Index local Markdown/text knowledge documents; safe to rerun (full index refresh)."""
    docs: list[tuple[str, str, str, str]] = []
    for path in sorted(root.rglob("*")) if root.exists() else []:
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            if current and len(current) + len(paragraph) > 900:
                chunks.append(current)
                current = ""
            current = f"{current}\n\n{paragraph}".strip()
        if current:
            chunks.append(current)
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{path.relative_to(root).as_posix()}::{idx}"
            docs.append((chunk_id, chunk, path.name, str(path.relative_to(root))))

    index_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(index_path)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS knowledge_chunks (id TEXT PRIMARY KEY, content TEXT NOT NULL, source TEXT NOT NULL, path TEXT NOT NULL, terms TEXT NOT NULL)")
        conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(id UNINDEXED, content, source UNINDEXED, path UNINDEXED, tokenize='unicode61')")
        conn.execute("DELETE FROM knowledge_chunks")
        conn.execute("DELETE FROM knowledge_fts")
        conn.executemany(
            "INSERT INTO knowledge_chunks(id, content, source, path, terms) VALUES (?, ?, ?, ?, ?)",
            [(i, c, s, p, " ".join(_tokens(c))) for i, c, s, p in docs],
        )
        conn.executemany(
            "INSERT INTO knowledge_fts(id, content, source, path) VALUES (?, ?, ?, ?)",
            [(i, c, s, p) for i, c, s, p in docs],
        )
        conn.commit()
    finally:
        conn.close()
    return len(docs)


def retrieve_knowledge(query: str, *, top_k: int = 4, index_path: Path = INDEX_PATH) -> list[dict[str, Any]]:
    """Retrieve chunks with sparse TF-IDF cosine similarity from the local SQLite index."""
    if not query.strip() or not index_path.exists():
        return []
    conn = sqlite3.connect(index_path)
    try:
        query_terms = _tokens(query)
        if not query_terms:
            return []
        rows = conn.execute("SELECT id, content, source, path, terms FROM knowledge_chunks").fetchall()
        docs = [(row, _tokens(row[4])) for row in rows]
        n_docs = len(docs)
        if not n_docs:
            return []
        document_frequency: dict[str, int] = {}
        for _, terms in docs:
            for term in set(terms):
                document_frequency[term] = document_frequency.get(term, 0) + 1
        query_counts = {term: query_terms.count(term) for term in set(query_terms)}
        query_vector = {term: count * (math.log((n_docs + 1) / (document_frequency.get(term, 0) + 1)) + 1)
                        for term, count in query_counts.items()}
        query_norm = math.sqrt(sum(value * value for value in query_vector.values())) or 1
        ranked = []
        for row, terms in docs:
            counts = {term: terms.count(term) for term in set(terms)}
            vector = {term: count * (math.log((n_docs + 1) / (document_frequency.get(term, 0) + 1)) + 1)
                      for term, count in counts.items()}
            norm = math.sqrt(sum(value * value for value in vector.values())) or 1
            score = sum(query_vector.get(term, 0) * value for term, value in vector.items()) / (query_norm * norm)
            if score > 0:
                ranked.append((score, row))
        ranked.sort(key=lambda item: item[0], reverse=True)
    finally:
        conn.close()
    return [{"id": row[0], "content": row[1], "source": row[2], "path": row[3], "score": score}
            for score, row in ranked[:top_k]]
