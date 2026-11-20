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

# Ngưỡng cosine tối thiểu để một đoạn được coi là "có liên quan". Đây là tham số vận hành,
# được chọn bằng benchmark cố định (evaluate_rag_benchmark.py), không phải ngưỡng đã chuẩn hóa.
MIN_RELEVANCE = 0.16
MAX_CHUNK_CHARS = 900

# Từ chức năng tiếng Việt/Anh không mang nội dung; loại khỏi truy vấn và chỉ mục để câu hỏi
# ngoài phạm vi không "khớp" tài liệu chỉ vì trùng hư từ.
STOPWORDS = frozenset("""
là gì của và trong các một những được để khi với cho có không thì mà này đó nào như thế sao
hãy giải thích em mình bạn tôi anh chị thầy cô ạ nhé vậy rồi cũng đã sẽ đang về từ ra vào lên
tại vì nên hay hoặc nếu bao nhiêu ai đâu làm cách dùng viết xin hỏi giúp biết muốn cần
the a an of and or to in is are what how why do does can i you it for on with this that be
""".split())


def _connect(index_path: Path) -> sqlite3.Connection:
    """Kết nối SQLite theo luật dự án: timeout=20.0 + WAL."""
    conn = sqlite3.connect(index_path, timeout=20.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def _tokens(value: str) -> list[str]:
    raw = re.findall(r"[\w+#]+", value.lower(), flags=re.UNICODE)
    # Token một ký tự (n, x, s, d...) là tên biến trong ví dụ, không phải nội dung: nếu giữ lại, câu hỏi
    # chứa "n" sẽ khớp mọi mục có ví dụ dùng biến n (vd. `n % 10`) thay vì mục nói về khái niệm được hỏi.
    return [token for token in raw if len(token) > 1 and token not in STOPWORDS and not token.isdigit()]


def _split_sections(text: str) -> list[tuple[str, str]]:
    """Tách tài liệu Markdown thành (tiêu đề mục, nội dung) theo heading gần nhất."""
    sections: list[tuple[str, list[str]]] = [("", [])]
    in_code = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
        heading = None if in_code else re.match(r"^#{1,3}\s+(.*\S)\s*$", line)
        if heading:
            sections.append((heading.group(1), []))
        else:
            sections[-1][1].append(line)
    return [(title, "\n".join(body).strip()) for title, body in sections if "\n".join(body).strip()]


def _chunk_document(text: str) -> list[tuple[str, str]]:
    """Trả về danh sách (mục, đoạn) với mỗi đoạn không quá MAX_CHUNK_CHARS khi có thể."""
    chunks: list[tuple[str, str]] = []
    for title, body in _split_sections(text):
        current = ""
        for paragraph in [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]:
            # Dòng "Nguồn: ..." là siêu dữ liệu về xuất xứ tài liệu, không phải kiến thức để truy xuất.
            if paragraph.startswith("Nguồn:"):
                continue
            if current and len(current) + len(paragraph) > MAX_CHUNK_CHARS:
                chunks.append((title, current))
                current = ""
            current = f"{current}\n\n{paragraph}".strip()
        if current:
            chunks.append((title, current))
    return chunks


def _knowledge_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [path for path in sorted(root.rglob("*")) if path.is_file() and path.suffix.lower() in {".md", ".txt"}]


GLOBAL_SCOPE = "global"


def ingest_knowledge_base(root: Path = KB_ROOT, index_path: Path = INDEX_PATH,
                          class_documents: list[dict[str, Any]] | None = None) -> int:
    """Index local Markdown/text knowledge documents; safe to rerun (full index refresh).

    `docs/knowledge_base` được nạp với scope 'global'. `class_documents` (do backend truyền vào, mỗi phần tử có
    id, class_id, title, content_text) được nạp với scope = class_id để chỉ truy xuất được trong lớp đó.
    Module này không import `database` cho phần tài liệu lớp nên không có phụ thuộc vòng.
    """
    docs: list[tuple[str, str, str, str, str, str]] = []
    for path in _knowledge_files(root):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        rel = path.relative_to(root).as_posix()
        for idx, (section, chunk) in enumerate(_chunk_document(text)):
            docs.append((f"{rel}::{idx}", chunk, path.name, rel, section, GLOBAL_SCOPE))
    for document in class_documents or []:
        text = (document.get("content_text") or "").strip()
        if not text:
            continue
        key = f"class/{document['class_id']}/{document['id']}"
        for idx, (section, chunk) in enumerate(_chunk_document(text)):
            docs.append((f"{key}::{idx}", chunk, document.get("title") or key, key, section, str(document["class_id"])))

    index_path.parent.mkdir(parents=True, exist_ok=True)
    conn = _connect(index_path)
    try:
        # Chỉ mục là dữ liệu dẫn xuất từ docs/knowledge_base nên được dựng lại toàn bộ mỗi lần nạp.
        conn.execute("DROP TABLE IF EXISTS knowledge_chunks")
        conn.execute("DROP TABLE IF EXISTS knowledge_fts")
        conn.execute("CREATE TABLE knowledge_chunks (id TEXT PRIMARY KEY, content TEXT NOT NULL, source TEXT NOT NULL, path TEXT NOT NULL, section TEXT NOT NULL DEFAULT '', terms TEXT NOT NULL, scope TEXT NOT NULL DEFAULT 'global')")
        conn.execute("CREATE VIRTUAL TABLE knowledge_fts USING fts5(id UNINDEXED, content, source UNINDEXED, path UNINDEXED, tokenize='unicode61')")
        conn.executemany(
            "INSERT INTO knowledge_chunks(id, content, source, path, section, terms, scope) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [(i, c, s, p, sec, " ".join(_tokens(f"{sec}\n{c}")), scope) for i, c, s, p, sec, scope in docs],
        )
        conn.executemany(
            "INSERT INTO knowledge_fts(id, content, source, path) VALUES (?, ?, ?, ?)",
            [(i, c, s, p) for i, c, s, p, _, _ in docs],
        )
        conn.commit()
    finally:
        conn.close()
    return len(docs)


def retrieve_knowledge(query: str, *, top_k: int = 4, index_path: Path = INDEX_PATH,
                       min_score: float = MIN_RELEVANCE, class_id: str | None = None) -> list[dict[str, Any]]:
    """Retrieve chunks with sparse TF-IDF cosine similarity from the local SQLite index.

    Chỉ trả về đoạn có điểm >= min_score; danh sách rỗng nghĩa là "không có nguồn phù hợp"
    và nơi gọi phải nói rõ giới hạn thay vì trích nguồn không liên quan.

    `class_id=None` (mặc định) chỉ tìm trong tài liệu chung (scope 'global') nên kết quả và benchmark không đổi;
    với `class_id` thì tìm thêm trong tài liệu giảng viên của đúng lớp đó, không bao giờ của lớp khác.
    """
    if not query.strip() or not index_path.exists():
        return []
    conn = _connect(index_path)
    try:
        query_terms = _tokens(query)
        if not query_terms:
            return []
        try:
            rows = conn.execute(
                "SELECT id, content, source, path, section, terms, scope FROM knowledge_chunks WHERE scope IN (?, ?)",
                (GLOBAL_SCOPE, str(class_id) if class_id else GLOBAL_SCOPE)).fetchall()
        except sqlite3.OperationalError:
            return []
        docs = [(row, row[5].split()) for row in rows]
        n_docs = len(docs)
        if not n_docs:
            return []
        document_frequency: dict[str, int] = {}
        for _, terms in docs:
            for term in set(terms):
                document_frequency[term] = document_frequency.get(term, 0) + 1

        def idf(term: str) -> float:
            return math.log((n_docs + 1) / (document_frequency.get(term, 0) + 1)) + 1

        query_counts = {term: query_terms.count(term) for term in set(query_terms)}
        query_vector = {term: count * idf(term) for term, count in query_counts.items()}
        query_norm = math.sqrt(sum(value * value for value in query_vector.values())) or 1
        ranked = []
        for row, terms in docs:
            counts: dict[str, int] = {}
            for term in terms:
                counts[term] = counts.get(term, 0) + 1
            vector = {term: count * idf(term) for term, count in counts.items()}
            norm = math.sqrt(sum(value * value for value in vector.values())) or 1
            score = sum(query_vector.get(term, 0) * value for term, value in vector.items()) / (query_norm * norm)
            if score >= min_score:
                ranked.append((score, row))
        ranked.sort(key=lambda item: (-item[0], item[1][0]))
    finally:
        conn.close()
    return [{"id": row[0], "content": row[1], "source": row[2], "path": row[3], "section": row[4],
             "score": round(score, 4), "scope": row[6]} for score, row in ranked[:top_k]]


def list_knowledge_documents(root: Path = KB_ROOT) -> list[dict[str, Any]]:
    """Danh mục tài liệu đang được nạp cho RAG, để giảng viên kiểm tra nguồn kiến thức của AI.

    Đọc trực tiếp thư mục KB (không qua chỉ mục) nên phản ánh đúng những gì sẽ được nạp.
    """
    documents: list[dict[str, Any]] = []
    for path in _knowledge_files(root):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        chunks = _chunk_document(text)
        title_match = re.search(r"^#\s+(.*\S)\s*$", text, flags=re.MULTILINE)
        provenance_match = re.search(r"^Nguồn:\s*(.*\S)\s*$", text, flags=re.MULTILINE)
        sections: list[str] = []
        for section, _ in chunks:
            if section and section not in sections:
                sections.append(section)
        documents.append({
            "path": path.relative_to(root).as_posix(),
            "title": title_match.group(1) if title_match else path.name,
            "provenance": provenance_match.group(1) if provenance_match else "Chưa ghi nguồn gốc trong tài liệu.",
            "sections": sections,
            "chunk_count": len(chunks),
            "char_count": len(text),
        })
    return documents
