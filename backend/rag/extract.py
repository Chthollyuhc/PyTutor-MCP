"""Trích văn bản từ tài liệu giảng viên tải lên cho Gia sư AI (v5.4, Lát cắt C).

Chỉ trả về văn bản đã trích; tệp gốc không được lưu. Mọi lỗi người dùng (sai định dạng, vượt giới hạn,
PDF không có lớp chữ...) được báo bằng `ExtractionError` với thông điệp tiếng Việt hiển thị thẳng cho giảng viên.
"""
from __future__ import annotations

import io
import re
from pathlib import PurePath

ALLOWED_EXTENSIONS = (".md", ".txt", ".pdf", ".docx")
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_TEXT_CHARS = 150_000
MAX_PDF_PAGES = 200
MIN_PDF_TEXT_CHARS = 40          # dưới ngưỡng này coi là bản scan (không có lớp chữ)
CODE_RATIO_WARN = 0.4            # cảnh báo khi > 40% ký tự nằm trong khối code


class ExtractionError(ValueError):
    """Tài liệu không đạt tiêu chuẩn; `str(exc)` là thông điệp cho giảng viên."""


def file_format(filename: str) -> str:
    ext = PurePath(filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ExtractionError("Định dạng không được hỗ trợ. Chỉ nhận .md, .txt, .pdf (có lớp chữ) và .docx.")
    return ext.lstrip(".")


def _normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _extract_text_file(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-16"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ExtractionError("Không đọc được tệp văn bản. Hãy lưu tệp ở dạng UTF-8.")


def _extract_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - phụ thuộc môi trường
        raise ExtractionError("Máy chủ chưa cài thư viện đọc PDF (pypdf).") from exc
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise ExtractionError("PDF bị khóa bằng mật khẩu. Hãy gỡ mật khẩu rồi tải lại.")
        if len(reader.pages) > MAX_PDF_PAGES:
            raise ExtractionError(f"PDF quá dài (> {MAX_PDF_PAGES} trang). Hãy tách thành nhiều tài liệu.")
        text = "\n\n".join((page.extract_text() or "") for page in reader.pages)
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError("Không đọc được tệp PDF (tệp hỏng hoặc không hợp lệ).") from exc
    if len(text.strip()) < MIN_PDF_TEXT_CHARS:
        raise ExtractionError("PDF không có lớp chữ (có thể là bản scan). Hãy dùng bản PDF xuất từ Word/LaTeX hoặc tải .docx/.md.")
    return text


def _extract_docx(data: bytes) -> str:
    try:
        from docx import Document
        document = Document(io.BytesIO(data))
    except Exception as exc:
        raise ExtractionError("Không đọc được tệp .docx (tệp hỏng hoặc không hợp lệ).") from exc
    lines: list[str] = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            lines.append("")
            continue
        style = (paragraph.style.name or "") if paragraph.style is not None else ""
        match = re.match(r"(?i)^(heading|tiêu đề)\s*(\d)", style)
        if match or style.lower() == "title":
            lines.append(f"## {text}")  # heading → `##` để _chunk_document tách mục
        else:
            lines.append(text)
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                lines.append(" | ".join(cells))
    return "\n".join(lines)


def code_ratio(text: str) -> float:
    in_code = False
    code = 0
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            code += len(line)
    return code / len(text) if text else 0.0


def extract_text(filename: str, data: bytes) -> tuple[str, str, list[str]]:
    """Trả về (định dạng, văn bản đã trích, danh sách cảnh báo). Raise ExtractionError nếu không đạt."""
    fmt = file_format(filename)
    if not data:
        raise ExtractionError("Tệp rỗng.")
    if len(data) > MAX_FILE_BYTES:
        raise ExtractionError(f"Tệp quá lớn (> {MAX_FILE_BYTES // (1024 * 1024)} MB).")
    if fmt in ("md", "txt"):
        raw = _extract_text_file(data)
    elif fmt == "pdf":
        raw = _extract_pdf(data)
    else:
        raw = _extract_docx(data)
    text = _normalize(raw)
    if not text:
        raise ExtractionError("Không trích được nội dung chữ từ tài liệu.")
    if len(text) > MAX_TEXT_CHARS:
        raise ExtractionError(f"Nội dung quá dài ({len(text):,} ký tự > {MAX_TEXT_CHARS:,}). Hãy tách thành nhiều tài liệu.")
    warnings: list[str] = []
    if code_ratio(text) > CODE_RATIO_WARN:
        warnings.append("Tài liệu chứa nhiều khối code dài. Gia sư AI sẽ bỏ khối code khi trích đoạn; "
                        "hãy bảo đảm không có lời giải của bài tập trong lớp.")
    if fmt in ("pdf", "docx") and "\n## " not in f"\n{text}" and not text.startswith("## ") and len(text) > 3000:
        warnings.append("Không nhận ra tiêu đề mục; tài liệu sẽ được chia theo đoạn nên truy xuất có thể kém chính xác.")
    return fmt, text, warnings
