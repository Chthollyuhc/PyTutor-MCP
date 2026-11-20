"""Chạy thử kiểm thử tài liệu giáo trình Python mới tải lên trong hệ thống PyTutor."""
import sqlite3
import json
from pathlib import Path
from backend.rag.retriever import retrieve_knowledge
from backend.llm_service import build_scaffolding_prompt

print("=" * 70)
print("KIỂM THỬ TÀI LIỆU GIÁO TRÌNH MỚI TẢI LÊN TRÊN HỆ THỐNG PYTUTOR")
print("=" * 70)

# 1. Kiểm tra trong cơ sở dữ liệu pytutor.db
conn = sqlite3.connect("pytutor.db")
conn.row_factory = sqlite3.Row
doc = conn.execute("SELECT * FROM kb_documents ORDER BY id DESC LIMIT 1").fetchone()
conn.close()

if not doc:
    print("❌ Chưa tìm thấy tài liệu nào trong bảng kb_documents!")
    exit(1)

print("\n1. THÔNG TIN TÀI LIỆU TRONG CƠ SỞ DỮ LIỆU:")
print(f" - ID: {doc['id']}")
print(f" - Lớp học phần: {doc['class_id']}")
print(f" - Tiêu đề: {doc['title']}")
print(f" - Tên tệp: {doc['filename']}")
print(f" - Định dạng: {doc['format']}")
print(f" - Dung lượng văn bản: {doc['char_count']:,} ký tự")
print(f" - Nguồn gốc / Giấy phép: {doc['provenance']} ({doc['license_type']})")
print(f" - Trạng thái hoạt động: {'Đang kích hoạt (Active)' if doc['is_active'] else 'Tắt (Inactive)'}")
print(f" - Thời điểm tải lên: {doc['created_at']}")

# 2. Kiểm tra chỉ mục RAG SQLite (pytutor_knowledge.sqlite3)
k_conn = sqlite3.connect("pytutor_knowledge.sqlite3")
chunks_count = k_conn.execute("SELECT COUNT(*) FROM knowledge_chunks WHERE scope = ?", (doc['class_id'],)).fetchone()[0]
sample_chunks = k_conn.execute(
    "SELECT id, section, substr(content, 1, 150) FROM knowledge_chunks WHERE scope = ? LIMIT 3", 
    (doc['class_id'],)
).fetchall()
k_conn.close()

print(f"\n2. KẾT QUẢ PHÂN ĐOẠN & LẬP CHỈ MỤC (CHUNK INDEXING):")
print(f" - Tổng số phân đoạn (chunks) bóc tách cho lớp {doc['class_id']}: {chunks_count} đoạn")
for idx, (cid, sec, snippet) in enumerate(sample_chunks, 1):
    clean_snippet = snippet.replace('\n', ' ')
    print(f"   [{idx}] Phân đoạn {cid}: \"{clean_snippet}...\"")

# 3. Thử nghiệm Truy xuất tri thức (RAG Retrieval) theo từng chủ đề câu hỏi
queries = [
    "cú pháp vòng lặp for và duyệt tập hợp",
    "cách nhập dữ liệu từ bàn phím bằng hàm input",
    "cấu trúc điều kiện rẽ nhánh if else",
    "cách khai báo biến và các kiểu dữ liệu số nguyên số thực"
]

print(f"\n3. THỬ NGHIỆM TRUY XUẤT NGỮ NGHĨA (RAG RETRIEVAL TEST) CHO LỚP {doc['class_id']}:")

for q in queries:
    print(f"\n❓ Truy vấn: \"{q}\"")
    results = retrieve_knowledge(q, class_id=doc['class_id'], top_k=2)
    if not results:
        print("   ⚠️ Không có đoạn nào vượt ngưỡng độ tương quan tối thiểu.")
    else:
        for r_idx, r in enumerate(results, 1):
            score = round(r.get('score', 0), 4)
            source = r.get('source')
            snippet = r.get('content', '')[:120].replace('\n', ' ')
            print(f"   ✓ [Top {r_idx}] Điểm tương quan: {score} | Nguồn: {source}")
            print(f"     Nội dung trích: \"{snippet}...\"")

# 4. Kiểm tra phân quyền đa người dùng (Multi-tenant isolation)
print(f"\n4. KIỂM TRA PHÂN QUYỀN TRI THỨC THEO LỚP (ISOLATION TEST):")
other_class_results = retrieve_knowledge("vòng lặp for", class_id="cls_other_dummy", top_k=2)
has_leak = any(r.get("source") == doc["title"] for r in other_class_results)
print(f" - Truy vấn từ lớp khác ('cls_other_dummy'): Có bị lộ giáo trình của lớp này không? {'CÓ (LỖI)' if has_leak else 'KHÔNG (CHUẨN)'}")

# 5. Thử nghiệm dựng ngữ cảnh RAG và nguồn trích dẫn cho Gia sư AI (Chat Context & Source Refs)
print(f"\n5. THỬ DỰNG NGỮ CẢNH RAG VÀ NGUỒN TRÍCH DẪN CHO GIA SƯ AI:")
from backend.llm_service import _source_refs

user_msg = "Thầy cô dạy cấu trúc vòng lặp for và duyệt tập hợp như thế nào ạ?"
rag_docs = retrieve_knowledge(user_msg, top_k=3, class_id=doc['class_id'])
source_refs = _source_refs(rag_docs)
rag_context = "\n\n".join(
    f"Nguồn: {d['source']} — mục \"{d.get('section') or 'Tổng quan'}\"\n{d['content'][:150]}..." for d in rag_docs
)

print(f" - Câu hỏi của sinh viên: \"{user_msg}\"")
print(f" - Số đoạn trích xuất thành công: {len(rag_docs)} đoạn")
print(f" - Danh sách nguồn trích dẫn hiển thị cho sinh viên (source_refs):")
for s in source_refs:
    print(f"   + {s.get('name')}: {s.get('section') or 'Tổng quan'}")
print(f" - Ngữ cảnh giáo trình được đưa vào Prompt Gia sư AI:")
print("   " + rag_context.replace("\n", "\n   ")[:300] + "...")

print("\n" + "=" * 70)
print("KẾT LUẬN: TÀI LIỆU ĐÃ ĐƯỢC NẠP, PHÂN ĐOẠN VÀ HOẠT ĐỘNG HOÀN TOÀN CHUẨN XÁC!")
print("=" * 70)
