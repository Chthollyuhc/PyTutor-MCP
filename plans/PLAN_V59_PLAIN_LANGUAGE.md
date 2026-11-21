# Plan v5.9 — "Lời thường": màn sinh viên và giảng viên ai cũng hiểu, ai cũng muốn mở

> **Người thực hiện:** một agent lập trình (ví dụ Gemini 3.8 Flash). Plan viết để làm **tuần tự, từng bước**, mỗi bước có lệnh kiểm tra.
> **Người duyệt:** người dùng và giảng viên hướng dẫn. Bảng "Trước → sau" ở mục 2 là phần để duyệt câu chữ.
> **Ngày lập:** 21/11/2026. Dựa trên mã v5.8 đã có trong repo (chưa commit).

---

## 0. Đọc trước (bắt buộc với người thực hiện)

1. Làm **đúng thứ tự** từ Bước 0 tới Bước 7. Chỉ sang bước sau khi mục "Kiểm tra" của bước hiện tại đã đạt.
2. **Không tự viết câu nhận xét mới.** Mọi câu hiển thị cho người dùng đều có sẵn trong plan:
   - câu nhận xét do `backend/plain_language.py` sinh ra (Bước 1);
   - chữ tĩnh trên giao diện (tiêu đề, nút) có nguyên văn trong code mẫu ở Bước 3–5.
3. Code mẫu trong plan là **bản tham chiếu**. Chép nguyên văn trước, rồi chạy test. Test sai thì sửa code cho khớp test. **Không sửa test cho khớp code**, trừ khi mục "Lỗi thường gặp" (mục 8) nói vậy.
4. Gặp chỗ plan không khớp với mã thật (tên hàm khác, dòng không tìm thấy): **dừng lại**, ghi vào báo cáo cuối (mục 9) phần "Chỗ plan không khớp". Không đoán.
5. Môi trường: Windows 11, PowerShell. Dùng `py` (không dùng `python3`), `npm.cmd`, dùng `;` thay cho `&&`.

---

## 1. Bối cảnh và quyết định đã chốt

**Bối cảnh.** v5.8 đã bớt số liệu, nhưng thầy hướng dẫn vẫn thấy màn hình **quá học thuật**. Có năm nguyên nhân:
- Chữ là từ của người nghiên cứu: "khái niệm", "đang hình thành", "chưa có bằng chứng", "trung vị", "k/n", "quy ước vận hành chưa hiệu chuẩn".
- Biểu đồ phải học mới đọc được: trục "số test đạt", ký hiệu M1 và ×8, ma trận 7 màu kèm chú giải.
- Màn hình nói về "hệ thống nghĩ gì về bạn", trong khi người dùng chỉ hỏi "xong chưa, còn bao nhiêu, làm gì bây giờ".
- Lần nào mở ra cũng giống nhau, không có tin mới, không có gì để vui.
- Phải bấm nút mới thấy.

**Quyết định đã chốt với người dùng:**
1. **Làm lại cả chữ lẫn biểu đồ.**
2. **Người dùng là sinh viên nhập môn CNTT.**
   - Giữ từ của môn học: vòng lặp, câu lệnh if, hàm, lỗi cú pháp, chạy thử, nộp bài, gợi ý mức 1/2/3, sao.
   - Bỏ từ của người làm hệ thống: khái niệm, trạng thái, bằng chứng, nhóm quá trình, mức tự làm, trung vị, dữ liệu hạn chế, quy ước.
   - Màn giảng viên cũng bỏ nhóm từ thứ hai.
3. **Yếu tố "game" nhẹ, chỉ giữ thứ gắn với việc học thật.**
   - Có: chặng đường học phần có sao, tin vui về tiến bộ của chính mình, lời khen cụ thể, "còn N bài nữa".
   - Không: chuỗi ngày học, điểm kinh nghiệm/cấp độ ảo, huy hiệu sưu tầm, so sánh hay xếp hạng với bạn, hiệu ứng và thông báo dồn dập.
4. **Không làm** nút "sao chép tin nhắn" cho giảng viên.

**Phạm vi v5.9:** chỉ đổi **cách nói và cách vẽ**, không đổi cách tính.
- Không thu thập dữ liệu mới, không đổi schema.
- Không đổi luật sao, mô hình người học, chiến lược gợi ý hay chỉ số chính thức.
- Màn kỹ thuật v5.8 **không xóa**: chuyển vào mục thu gọn "Xem số liệu đầy đủ" cho người cần phân tích (và cho chương đánh giá của khóa luận).

---

## 2. Trước → sau (để người dùng và thầy duyệt câu chữ)

| Chỗ | Trước (v5.8) | Sau (v5.9) |
|---|---|---|
| Trang chủ sinh viên | 4 ô số: Lớp học phần, Bài hoàn thành, Điểm nỗ lực tích lũy, Chỉ số tự lập (mã còn hiện **85%** mặc định khi chưa có dữ liệu) | Thẻ **"Hôm nay của bạn"** (xem mục 6, Bước 3) |
| Câu chính | "Khái niệm “Vòng lặp” đáng luyện thêm" | "Tuần này bạn làm đúng 2 bài mới, nhiều hơn tuần trước 1 bài." |
| Tin vui | không có | "Bạn không bỏ cuộc: bài Số nguyên tố đúng hết sau 7 lần thử." |
| Chặng đường | không có ở trang chủ | 5 trạm theo lộ trình lớp: bài xong có ★★★, "Bạn ở đây", bài khóa có ổ khóa; "Còn 2 bài nữa là xong học phần." |
| Kỹ năng | 6 ô "Khá vững / Đang hình thành / Đang vướng / Chưa có bằng chứng" + "Vì sao hệ thống nghĩ vậy" (câu có ≥ và "tự làm trung bình") | Một dòng: "Bạn làm tốt: Vòng lặp · Đang luyện: Câu lệnh if · Nên luyện thêm: Đệ quy" |
| Dấu chân một bài | Biểu đồ có trục "số test đạt", ký hiệu M1, ×8, chú giải 4 mục | Các bước bằng lời: "Chạy thử: đúng 3 trên 5 · Đúng thêm", "Nộp bài: đúng hết" |
| Sau khi nộp đạt | "Hệ thống đã ghi nhận 3 điểm nỗ lực vào hồ sơ năng lực và cập nhật lộ trình kỹ năng của bạn." | "**Đúng hết rồi!** Bạn làm đúng hết bài này và có 3 sao. Bạn tự làm, không cần gợi ý lớn." + một tin vui nếu có |
| Đầu màn giảng viên | "7 ngày qua · 8/10 SV có hoạt động · 3 việc nên xem" + nhãn "Mẫu nhỏ · chỉ mô tả" | **Bản tin lớp** 3–5 câu: "Tuần này có 8 trong 10 bạn vào làm bài, làm đúng thêm 23 bài. Phần lớn các bạn đang ổn. 2 bạn nên được hỏi thăm: An, Hà. Bài khó nhất lúc này: Số nguyên tố. Nhiều bạn sai ở trường hợp “n = 1” (ví dụ đầu vào: 1)." |
| Nhóm sinh viên | Ma trận 7 màu + chú giải | Ba cột tên: **Nên hỏi thăm / Đang cố gắng / Đang ổn**, mỗi tên có một câu lý do; dòng "Chưa bắt đầu (2): …" |
| Theo bài | Thanh chồng 6 loại lỗi, "trung vị (n=6)" | "6 trong 10 bạn đã làm xong, 3 bạn đang làm." + lỗi hay gặp nói bằng ví dụ + "Các bạn làm xong thường mất khoảng 20 phút." |
| Thẻ lớp ở danh sách lớp | "2 SV cần chú ý · 1 vấn đề chung" | "2 bạn nên hỏi thăm · bài khó: Số nguyên tố" |
| Giới hạn | "quy ước vận hành chưa hiệu chuẩn" lặp ở nhiều chỗ | Một mục thu gọn "Hệ thống nhận xét thế nào?" + một dòng nhỏ "Nhận xét tự động…, có thể chưa chính xác." |

Trung thực khoa học vẫn giữ:
- Dùng từ rào đón ("có vẻ", "có thể chưa chính xác").
- Mục "Hệ thống nhận xét thế nào?" ghi đúng ngưỡng đang dùng.
- Số liệu đầy đủ vẫn còn trong "Xem số liệu đầy đủ".

---

## 3. Luật bất biến — KHÔNG được làm

1. **Không** `git commit`, `git reset`, `git checkout`, `git stash`, không đổi nhánh. Người dùng tự xem diff và quyết định.
2. **Không** ghi vào `pytutor.db` hay `pytutor_knowledge.sqlite3` thật. Mọi test và QA chạy trên DB tạm (mục 4).
3. **Không** sửa:
   - cách tính sao (`calculate_autonomy_stars`, `explain_autonomy_stars`);
   - `compute_student_model` (ở cả `backend/database.py` lẫn `mcp_server/storage.py`) và `derive_learner_model`;
   - `classify_learning_process`, các hằng `PROCESS_*`, `select_hint_strategy`;
   - guardrails, RAG, prompt LLM.
4. **Không** sửa câu `explanation` trong `pytutor_shared/learner_model.py`. Trong file này chỉ được thêm 2 khóa vào `build_journey_points` (Bước 1.1).
5. `backend/` **không** import từ `mcp_server/`.
6. API **chỉ thêm**: thêm khóa mới vào phản hồi, không đổi và không xóa khóa cũ. Test v5.7/v5.8 phải đạt nguyên.
7. **Không** thêm thư viện (npm hay pip). Không dùng LLM trong luồng mới.
8. **Không** đổi `SHOW_EXAM_SESSIONS`, `LeaderboardModal`, màn giám sát bài nộp, luồng `/api/submit`.
9. **Không** xóa file v5.8: `AttemptStrip.jsx`, `ConceptMap.jsx`, `JourneyHeadline.jsx`, `backend/student_journey.py`, `ClassViewParts.jsx`. Chỉ ngừng dùng ở màn chính. Không xóa test cũ.
10. **Không** đưa mã nguồn của sinh viên vào bất kỳ phản hồi nào dành cho giảng viên.
11. Màn sinh viên **không bao giờ** hiện chữ "mắc kẹt", "xếp hạng", không so sánh với bạn khác.
12. Trước khi sửa `backend/`, tắt backend dev đang chạy ở cổng 8000, nếu có (nó tự khởi động lại trên DB thật khi file đổi).

---

## 4. Môi trường và lệnh chuẩn

Chạy test Python, **mỗi module một DB tạm**, bằng script có sẵn:

```powershell
.\.claude\run_isolated.ps1 test_plain_language_v59
```

Chạy nhiều module một lúc (mỗi module vẫn có DB riêng):

```powershell
.\.claude\run_isolated.ps1 test_plain_language_v59 test_visual_views_v58 test_class_overview_v57 test_data_capture_v57 test_learner_model test_thesis_upgrade test_phase16_ai_upgrade test_phase17_adaptive_analytics test_qa_authorization test_pedagogy_v55
```

Script (không phải unittest) và replay, chạy trong DB tạm:

```powershell
$env:PYTHONIOENCODING = "utf-8"; $env:PYTUTOR_DISABLE_LLM = "1"
$tmpDb = Join-Path $env:TEMP ("pytutor_check_" + [guid]::NewGuid().ToString("N") + ".db")
$tmpKb = Join-Path $env:TEMP ("pytutor_kb_" + [guid]::NewGuid().ToString("N") + ".sqlite3")
$env:PYTUTOR_DB_PATH = $tmpDb; $env:PYTUTOR_KNOWLEDGE_DB_PATH = $tmpKb
try { py -m mcp_server.test_mcp_server; py -m backend.test_backend_e2e; py evaluate_learner_model_policy.py; py evaluate_phase17_adaptive.py }
finally {
  Remove-Item Env:PYTUTOR_DB_PATH, Env:PYTUTOR_KNOWLEDGE_DB_PATH -ErrorAction SilentlyContinue
  Remove-Item $tmpDb, "$tmpDb-wal", "$tmpDb-shm", $tmpKb -Force -ErrorAction SilentlyContinue
}
```

Biên dịch Python: `py -m compileall -q backend mcp_server pytutor_shared`

Frontend (chạy trong thư mục `frontend`):

```powershell
cd frontend; npm.cmd run test:theme; npm.cmd run test:ui-utils; npm.cmd run build; cd ..
```

Lưu ý: cảnh báo chunk > 500 kB khi build là bình thường.

---

## 5. Quy tắc chữ và hình (áp cho mọi câu trong v5.9)

**Chữ**
1. Viết như đang nói chuyện: câu ngắn, xưng "bạn" với sinh viên. Màn giảng viên gọi sinh viên là "bạn" (ví dụ "2 bạn nên hỏi thăm").
2. Không dùng ký hiệu: `≥`, `≤`, `%`, `#`, `n=`, `k/n`. Viết "4 trên 5 trường hợp", "8 trong 10 bạn".
3. Nói việc cụ thể, không đánh giá chung.
4. Nói điều tốt trước, rồi đúng **một** việc nên làm.
5. Dùng "lần", không dùng "lượt". Dùng "trường hợp" (hoặc "trường hợp kiểm tra"), không dùng "test".
6. Danh sách từ cấm nằm ở `BANNED_WORDS` trong `backend/plain_language.py`; frontend có test quét từ cấm (Bước 3.3).

**Hình** (chỉ dùng các dạng ai cũng hiểu, không cần chú giải)
- Chặng đường (giống màn theo dõi đơn hàng), ngôi sao ★, thanh tiến độ có ghi chữ ngay bên cạnh.
- Nhóm tên theo 3 màu: đỏ = nên hỏi thăm, vàng = đang cố gắng, xanh = đang ổn. Xám = chưa bắt đầu.
- Một con số lớn kèm một câu.
- **Không** dùng ở màn chính: biểu đồ có trục, thanh chồng nhiều màu, ma trận màu, biểu đồ đường, hay bất kỳ hình nào cần bảng chú giải.
- Mỗi hình đi kèm một câu nói đúng điều hình muốn nói. Che hình đi, câu vẫn phải đủ ý.

---

## 6. Các bước

### Bước 0 — Kiểm tra nền (chưa sửa gì)

1. Đọc lướt các file sẽ sửa:
   - `pytutor_shared/learner_model.py` (hàm `build_journey_points`);
   - `backend/database.py` (hàm `get_student_journey_overview`);
   - `backend/main.py`: các endpoint `/api/student/journey`, `/api/instructor/classes/{class_id}/insights`, `/api/instructor/classes-attention`, `/api/instructor/classes/{class_id}/students/{username}/exercises/{exercise_id}/journey`;
   - `frontend/src/components/StudentProfileModal.jsx`, `frontend/src/components/InstructorPedagogyPanels.jsx` (hàm `ClassInsightsPanel`, `ClassesAttentionList`), `frontend/src/components/classview/ClassViewParts.jsx`;
   - `frontend/src/pages/StudentPortalPage.jsx`, `frontend/src/pages/StudentIDE.jsx`.
2. Chạy bộ test nền (mục 4, lệnh nhiều module, bỏ `test_plain_language_v59` vì chưa có).

**Kiểm tra:** mọi module báo `OK` (một số module có thể báo `skipped` cho phần cần DB, như vậy là bình thường). Nếu đã có test fail **trước khi sửa**, ghi tên test vào báo cáo cuối rồi vẫn tiếp tục, nhưng không được làm tăng số test fail.

---

### Bước 1 — Hàm thuần `backend/plain_language.py` và test

#### 1.1. Thêm 2 khóa vào `build_journey_points` (`pytutor_shared/learner_model.py`)

Trong hàm `build_journey_points`, làm 3 thay đổi:
- Thêm 2 biến cạnh `first_pass_index: Optional[int] = None`:
  ```python
  first_pass_at: Optional[str] = None
  attempts_to_first_pass: Optional[int] = None
  ```
- Ngay trong khối `if kind == "submit" and all_passed and first_pass_index is None:`, sau dòng gán `first_pass_index`, thêm:
  ```python
  first_pass_at = ev.get("timestamp")
  attempts_to_first_pass = counts["run"] + counts["submit"]
  ```
- Trong dict `"summary"` trả về, thêm 2 khóa (giữ nguyên các khóa cũ):
  ```python
  "first_pass_at": first_pass_at,
  "attempts_to_first_pass": attempts_to_first_pass,
  ```

Không đổi gì khác trong file.

#### 1.2. Thêm 2 khóa vào `get_student_journey_overview` (`backend/database.py`)

Trong vòng `for r in recent:`, dict `exercises.append({...})` thêm 2 khóa (giữ nguyên khóa cũ):
```python
"first_pass_at": j["summary"].get("first_pass_at"),
"attempts_to_first_pass": j["summary"].get("attempts_to_first_pass"),
```

#### 1.3. Tạo file mới `backend/plain_language.py` (chép nguyên văn)

```python
"""Lời thường cho màn sinh viên và giảng viên (v5.9): hàm thuần, tất định, không DB, không LLM.

Chỉ đổi cách NÓI, không đổi cách TÍNH. Số liệu đầu vào lấy từ get_class_insights, get_exercise_journey,
get_student_journey_overview, mô hình người học và lộ trình lớp có sẵn. Đây là nơi DUY NHẤT sinh câu nhận xét;
giao diện chỉ hiển thị nguyên văn các trường *_vi.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Optional

from backend.class_overview import OVERVIEW_THRESHOLDS
from pytutor_shared.learner_model import PROCESS_PROGRESS_WINDOW, PROCESS_STUCK_MIN_ATTEMPTS

PLAIN_VERSION = "1"
PASS_GROUPS = ("independent_pass", "retry_pass", "hint_pass")
NEAR_PASS_MIN_SHARE = 0.5      # đúng từ một nửa số trường hợp trở lên thì nói "sắp xong" (quy tắc trình bày)
PERSISTENCE_MIN_ATTEMPTS = 5   # từ 5 lần thử trở lên mới khen "không bỏ cuộc"
MOMENT_WINDOW_DAYS = 7
STORY_VISIBLE_STEPS = 8
RUNS_CONDENSE_MIN = 3

KC_PLAIN = {
    "io_format": "In và nhập dữ liệu",
    "conditional": "Câu lệnh if",
    "loop": "Vòng lặp",
    "accumulator": "Cộng dồn trong vòng lặp",
    "string": "Xử lý chuỗi",
    "recursion": "Đệ quy",
}
GROUP_TITLES_VI = {"check_in": "Nên hỏi thăm", "trying": "Đang cố gắng", "doing_well": "Đang ổn",
                   "not_started": "Chưa bắt đầu"}
NOTE_STUDENT_VI = "Nhận xét tự động từ các lần bạn chạy thử và nộp bài, có thể chưa chính xác."
FEW_DATA_VI = "Lớp mới có ít hoạt động nên nhận xét có thể chưa chính xác."

# Từ cấm trong MỌI câu do module này sinh ra (test kiểm tra). Tên bài, tên sinh viên và mô tả test do giảng viên
# viết được chèn nguyên văn nên không thuộc phạm vi kiểm tra.
BANNED_WORDS = (
    "khái niệm", "trạng thái", "bằng chứng", "quy ước", "hiệu chuẩn", "trung vị", "tự làm", "nhóm quá trình",
    "mắc kẹt", "đạt độc lập", "thử–sửa", "thử-sửa", "dữ liệu hạn chế", "mẫu nhỏ", "heuristic", "lượt", "xếp hạng",
    "kém", "yếu", "thất bại", "expected", "≥", "≤", "%", "#", "n=", " sv ", "kc", "test",
)

REASON_BY_CODE = {
    "unresolved_recurring": "Bạn đã thử bài này vài lần mà chưa xong. Thử lại với cách nghĩ mới nhé.",
    "in_progress": "Bạn đã nộp bài này nhưng chưa đúng hết. Sửa thêm một chút nhé.",
    "next_unattempted": "Đây là bài tiếp theo bạn chưa làm.",
    "retry_for_autonomy": "Bạn đã xong bài này nhờ gợi ý. Thử tự làm lại để chắc tay hơn.",
}
BUTTON_BY_CODE = {"next_unattempted": "Bắt đầu", "retry_for_autonomy": "Làm lại"}


# ------------------------------------------------------------------ tiện ích
def kc_name(kc: Optional[str], label_vi: Optional[str] = None) -> str:
    """Tên kỹ năng bằng từ của môn học; kỹ năng do giảng viên tự thêm thì giữ tên giảng viên đặt."""
    return KC_PLAIN.get(kc or "") or label_vi or kc or ""


def first_name(full_name: Optional[str]) -> Optional[str]:
    """'Trần Minh Khánh - SV K65' -> 'Khánh'; 'SV An (giả lập)' -> 'An'."""
    if not full_name:
        return None
    base = re.sub(r"\(.*?\)", " ", str(full_name).split(" - ")[0])
    parts = base.split()
    return parts[-1] if parts else None


def _parse_ts(ts: Any) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.strptime(str(ts).replace("T", " ")[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def format_when(ts: Any) -> Optional[str]:
    """'2026-11-20 09:05:33' -> '20/11 09:05'."""
    d = _parse_ts(ts)
    return d.strftime("%d/%m %H:%M") if d else None


def _correct(passed: Any, total: Any) -> str:
    return f"đúng {int(passed or 0)} trên {int(total or 0)}"


# ------------------------------------------------------------------ sinh viên: chặng đường học phần
def build_course_path(class_exercises: Optional[list[dict]], class_id: Optional[str],
                      class_name: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Chặng đường từ get_class_exercises(class_id, username) (đã có status và stars_earned)."""
    indexed = sorted(enumerate(class_exercises or []), key=lambda x: (x[1].get("order_idx") or 0, x[0]))
    items = [it for _, it in indexed]
    if not items:
        return None
    statuses = [it.get("status") for it in items]
    current = next((i for i, s in enumerate(statuses) if s == "IN_PROGRESS"), None)
    if current is None:
        current = next((i for i, s in enumerate(statuses) if s == "AVAILABLE"), None)
    steps = []
    for i, it in enumerate(items):
        s = statuses[i]
        if s == "MASTERED":
            kind = "done"
        elif i == current:
            kind = "current"
        elif s == "LOCKED":
            kind = "locked"
        else:
            kind = "open"
        eid = it.get("exercise_id") or it.get("id")
        steps.append({"exercise_id": eid, "title": it.get("title") or eid, "number": i + 1, "kind": kind,
                      "stars": int(it.get("stars_earned") or 0) if kind == "done" else 0})
    total = len(steps)
    done = sum(1 for st in steps if st["kind"] == "done")
    remaining = total - done
    caption = (f"Bạn đã xong cả {total} bài của học phần." if remaining == 0
               else f"Còn {remaining} bài nữa là xong học phần.")
    return {"class_id": class_id, "class_name": class_name or "", "steps": steps, "total": total,
            "done": done, "remaining": remaining, "caption_vi": caption}


# ------------------------------------------------------------------ sinh viên: thẻ "Hôm nay của bạn"
def _near_pass(recent: list[dict]):
    for ex in recent:
        best = ex.get("best") or {}
        p, t = int(best.get("passed") or 0), int(best.get("total") or 0)
        if ex.get("group") in PASS_GROUPS or t <= 0 or p >= t:
            continue
        if p / t >= NEAR_PASS_MIN_SHARE:
            return ex, p, t
    return None


def _moments(concepts: list[dict], recent: list[dict], now: datetime) -> list[dict[str, str]]:
    """Tối đa 2 tin vui trong 7 ngày gần nhất. Thứ tự: không bỏ cuộc -> tự làm đúng -> làm tốt một phần."""
    since = now - timedelta(days=MOMENT_WINDOW_DAYS)
    fresh = []
    for ex in recent:
        d = _parse_ts(ex.get("first_pass_at"))
        if d and d >= since and ex.get("group") in PASS_GROUPS:
            fresh.append((d, ex))
    fresh.sort(key=lambda x: x[0], reverse=True)
    out: list[dict[str, str]] = []
    persist = next((ex for _, ex in fresh if ex.get("group") in ("retry_pass", "hint_pass")
                    and int(ex.get("attempts_to_first_pass") or 0) >= PERSISTENCE_MIN_ATTEMPTS), None)
    if persist:
        out.append({"kind": "persistence", "text_vi": (f"Bạn không bỏ cuộc: bài {persist['title']} đúng hết sau "
                                                       f"{int(persist['attempts_to_first_pass'])} lần thử.")})
    indep = next((ex for _, ex in fresh if ex.get("group") == "independent_pass"), None)
    if indep:
        out.append({"kind": "independent", "text_vi": f"Bạn tự làm đúng bài {indep['title']} chỉ sau vài lần thử."})
    fresh_ids = {ex.get("exercise_id") for _, ex in fresh}
    skill = next((c for c in concepts if c.get("state") == "secure"
                  and any(d.get("exercise_id") in fresh_ids for d in (c.get("exercise_details") or []))), None)
    if skill:
        out.append({"kind": "new_skill",
                    "text_vi": f"Bạn đã làm tốt phần {kc_name(skill.get('kc'), skill.get('label_vi'))} rồi."})
    return out[:2]


def _headline(has_activity: bool, week: dict, near) -> str:
    this, prev = int(week.get("this") or 0), int(week.get("prev") or 0)
    if not has_activity:
        return "Chào mừng bạn! Hãy bắt đầu với bài đầu tiên."
    if this > 0:
        if this > prev:
            return f"Tuần này bạn làm đúng {this} bài mới, nhiều hơn tuần trước {this - prev} bài."
        if this == prev:
            return f"Tuần này bạn làm đúng {this} bài mới, đều tay như tuần trước."
        return f"Tuần này bạn làm đúng {this} bài mới."
    if near:
        ex, p, t = near
        return f"Bạn sắp xong bài {ex['title']} rồi: đã đúng {p} trên {t} trường hợp."
    return "Sẵn sàng làm tiếp chưa? Bài tiếp theo đang chờ bạn."


def _next_step(concepts: list[dict], next_practice: Optional[dict], near) -> Optional[dict[str, str]]:
    if near:
        ex, p, t = near
        return {"exercise_id": ex["exercise_id"], "title": ex["title"], "button_vi": "Làm tiếp",
                "reason_vi": f"Lần trước bạn đã đúng {p} trên {t} trường hợp. Sửa thêm một chút là xong."}
    for c in concepts:
        if c.get("state") != "struggling":
            continue
        target = next((d for d in (c.get("exercise_details") or []) if d.get("status") != "passed"), None)
        if target:
            return {"exercise_id": target["exercise_id"], "title": target.get("title") or target["exercise_id"],
                    "button_vi": "Luyện bài này",
                    "reason_vi": f"Bài này giúp bạn luyện thêm phần {kc_name(c.get('kc'), c.get('label_vi'))}."}
    if next_practice and next_practice.get("exercise_id"):
        code = next_practice.get("reason_code")
        return {"exercise_id": next_practice["exercise_id"],
                "title": next_practice.get("title") or next_practice["exercise_id"],
                "button_vi": BUTTON_BY_CODE.get(code, "Làm tiếp"),
                "reason_vi": REASON_BY_CODE.get(code, "Đây là bài nên làm tiếp.")}
    return None


def _skills(concepts: list[dict]):
    buckets: dict[str, list[str]] = {"good": [], "practicing": [], "needs_practice": []}
    key = {"secure": "good", "developing": "practicing", "struggling": "needs_practice"}
    for c in concepts:
        b = key.get(c.get("state"))
        if b:
            buckets[b].append(kc_name(c.get("kc"), c.get("label_vi")))
    parts = []
    if buckets["good"]:
        parts.append("Bạn làm tốt: " + ", ".join(buckets["good"]))
    if buckets["practicing"]:
        parts.append("Đang luyện: " + ", ".join(buckets["practicing"]))
    if buckets["needs_practice"]:
        parts.append("Nên luyện thêm: " + ", ".join(buckets["needs_practice"]))
    return buckets, (" · ".join(parts) or None)


def build_today_card(*, full_name: Optional[str], concepts: Optional[list[dict]], next_practice: Optional[dict],
                     week: Optional[dict], recent: Optional[list[dict]], path: Optional[dict],
                     now: datetime) -> dict[str, Any]:
    concepts, recent, week = list(concepts or []), list(recent or []), dict(week or {})
    name = first_name(full_name)
    near = _near_pass(recent)
    has_activity = bool(recent) or int(week.get("this") or 0) > 0 or any(c.get("exercise_details") for c in concepts)
    skills, skills_vi = _skills(concepts)
    return {
        "greeting_vi": f"Chào {name}" if name else "Chào bạn",
        "headline_vi": _headline(has_activity, week, near),
        "moments": _moments(concepts, recent, now) if has_activity else [],
        "next_step": _next_step(concepts, next_practice, near),
        "skills": skills,
        "skills_vi": skills_vi,
        "path": path,
        "note_vi": NOTE_STUDENT_VI,
        "version": PLAIN_VERSION,
    }


# ------------------------------------------------------------------ câu chuyện một bài (sinh viên và giảng viên)
def _condense_runs(points: list[dict]) -> list[dict]:
    """Gộp từ 3 lần chạy thử liên tiếp trở lên thành một bước."""
    out, i = [], 0
    while i < len(points):
        p = points[i]
        if p.get("kind") != "run":
            out.append(dict(p))
            i += 1
            continue
        j = i
        while j < len(points) and points[j].get("kind") == "run":
            j += 1
        group = points[i:j]
        if len(group) >= RUNS_CONDENSE_MIN:
            out.append({"kind": "runs", "count": len(group), "passed": max(int(x.get("passed") or 0) for x in group),
                        "total": group[-1].get("total"), "all_passed": False,
                        "is_new_best": any(x.get("is_new_best") for x in group), "format_only": False,
                        "timestamp": group[0].get("timestamp")})
        else:
            out.extend(dict(x) for x in group)
        i = j
    return out


def _step(p: dict, seen_attempt: bool) -> dict[str, Any]:
    kind = p.get("kind")
    passed, total = p.get("passed"), p.get("total")
    tag, tag_tone, tone = None, None, "neutral"
    if kind == "ask":
        text, icon = f"Hỏi Gia sư AI, gợi ý mức {int(p.get('hint_level') or 0)}", "message"
    elif kind == "runs":
        text, icon = f"Chạy thử {p['count']} lần: tốt nhất {_correct(passed, total)}", "play"
    elif kind == "run":
        text, icon = f"Chạy thử: {_correct(passed, total)}", "play"
    elif p.get("all_passed"):
        text, icon, tone = "Nộp bài: đúng hết", "check", "done"
    else:
        text, icon = f"Nộp bài: {_correct(passed, total)}", "send"
    if kind != "ask" and not p.get("all_passed"):
        if p.get("format_only"):
            tag, tag_tone = "Chỉ sai cách in kết quả", "info"
        elif p.get("is_new_best") and seen_attempt and int(passed or 0) > 0:
            tag, tag_tone = "Đúng thêm", "good"
    step = {"kind": kind, "icon": icon, "tone": tone, "text_vi": text, "tag_vi": tag, "tag_tone": tag_tone,
            "when_vi": format_when(p.get("timestamp"))}
    if p.get("code"):
        step["code"] = p["code"]
    return step


def build_story(points: Optional[list[dict]], summary: Optional[dict], *, audience: str = "student",
                student_name: Optional[str] = None) -> dict[str, Any]:
    """Một câu tóm tắt + các bước. audience='teacher' nói ở ngôi thứ ba và không bao giờ có mã nguồn
    (endpoint giảng viên vốn không trả mã nguồn trong points)."""
    points, summary = list(points or []), dict(summary or {})
    counts = summary.get("counts") or {}
    runs, asks, submits = int(counts.get("run") or 0), int(counts.get("ask") or 0), int(counts.get("submit") or 0)
    attempts = runs + submits
    best = summary.get("best") or {}
    p, t = int(best.get("passed") or 0), int(best.get("total") or 0)
    teacher = audience == "teacher"
    who = (student_name or "Bạn này") if teacher else "Bạn"
    if not points:
        text = (f"{who} chưa làm bài này trong khoảng thời gian đang xem." if teacher
                else "Bạn chưa làm bài này. Bấm “Chạy thử” để bắt đầu.")
    elif summary.get("first_pass_at") or summary.get("first_pass_index") is not None:
        n = int(summary.get("attempts_to_first_pass") or attempts or 1)
        text = f"{who} làm đúng ngay lần đầu." if n <= 1 else f"{who} thử {n} lần rồi làm đúng hết."
    elif attempts == 0:
        text = (f"{who} mới hỏi Gia sư AI, chưa chạy thử lần nào." if teacher
                else "Bạn đã xem gợi ý nhưng chưa chạy thử. Bấm “Chạy thử” để xem kết quả.")
    elif submits == 0:
        text = (f"{who} đã chạy thử {runs} lần, tốt nhất {_correct(p, t)} trường hợp, chưa nộp bài." if teacher
                else f"Bạn đã chạy thử {runs} lần, tốt nhất {_correct(p, t)} trường hợp. Khi thấy ổn, bấm “Nộp bài” nhé.")
    elif summary.get("group") == "stuck":
        text = (f"{who} đã thử {attempts} lần, tốt nhất {_correct(p, t)} trường hợp. Mấy lần gần đây chưa đúng thêm, "
                "bạn ấy có thể cần được hỏi thăm." if teacher else
                f"Bạn đã thử {attempts} lần, tốt nhất {_correct(p, t)} trường hợp. Mấy lần gần đây chưa đúng thêm. "
                "Thử bấm “Chạy từng bước” để xem code chạy thế nào, hoặc hỏi Gia sư AI.")
    else:
        text = (f"{who} đã thử {attempts} lần, tốt nhất {_correct(p, t)} trường hợp." if teacher
                else f"Bạn đã thử {attempts} lần, tốt nhất {_correct(p, t)} trường hợp. Sửa từng chỗ một nhé.")
    if teacher and asks and points:
        text += f" Đã hỏi Gia sư AI {asks} lần."
    steps, seen = [], False
    for q in _condense_runs(points):
        steps.append(_step(q, seen))
        if q.get("kind") in ("run", "runs", "submit"):
            seen = True
    return {"summary_vi": text, "steps": steps, "visible_from": max(0, len(steps) - STORY_VISIBLE_STEPS)}


def story_one_liner(item: dict) -> str:
    """Một câu cho mỗi bài trong danh sách "Các bài gần đây" của sinh viên."""
    counts, best = item.get("counts") or {}, item.get("best") or {}
    if item.get("group") in PASS_GROUPS:
        return "Đã làm đúng hết."
    if int(counts.get("submit") or 0) == 0 and int(counts.get("run") or 0) > 0:
        return f"Đã chạy thử {int(counts['run'])} lần, chưa nộp bài."
    if int(best.get("total") or 0) > 0:
        return f"Đang làm: tốt nhất {_correct(best.get('passed'), best.get('total'))} trường hợp."
    return "Đang làm."


# ------------------------------------------------------------------ giảng viên: bản tin lớp
def _period(days: int):
    days = int(days or 7)
    return ("Tuần này", "tuần này") if days == 7 else (f"Trong {days} ngày qua", f"{days} ngày qua")


def _names(items: list[dict], limit: int = 3) -> str:
    names = [x["full_name"] for x in items[:limit]]
    extra = len(items) - limit
    return ", ".join(names) + (f" và {extra} bạn khác" if extra > 0 else "")


def _sorted_people(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda x: ((x.get("full_name") or "").casefold(), x.get("username") or ""))


def _groups(rows: list[dict], ex_ids: list[str], titles: dict[str, str], attention: Optional[list[dict]]):
    """Chia MỌI sinh viên ghi danh vào đúng một trong 4 nhóm, xếp A→Z. Dùng lại nhóm quá trình có sẵn ở matrix."""
    codes: dict[str, set] = {}
    for a in attention or []:
        codes.setdefault(a.get("student"), set()).add(a.get("code"))
    g: dict[str, list[dict]] = {"check_in": [], "trying": [], "doing_well": [], "not_started": []}
    for r in _sorted_people(rows):
        cells = r.get("cells") or {}
        ordered = [(eid, cells.get(eid)) for eid in ex_ids if cells.get(eid)]
        person = {"username": r["username"], "full_name": r.get("full_name") or r["username"]}
        if not ordered:
            g["not_started"].append(person)
            continue
        stuck = [e for e, grp in ordered if grp == "stuck"]
        passes = [e for e, grp in ordered if grp in PASS_GROUPS]
        hints = [e for e, grp in ordered if grp == "hint_pass"]
        practice = [e for e, grp in ordered if grp == "practice_only"]
        c = codes.get(r["username"], set())
        if stuck:
            reason = (f"Đang gặp khó ở bài {titles[stuck[0]]}: thử nhiều lần mà mấy lần gần đây chưa đúng thêm."
                      if len(stuck) == 1 else f"Đang gặp khó ở {len(stuck)} bài, ví dụ bài {titles[stuck[0]]}.")
            g["check_in"].append({**person, "reason_vi": reason, "exercise_id": stuck[0]})
        elif not passes:
            reason = (f"Đã chạy thử {len(practice)} bài nhưng chưa nộp bài nào." if len(practice) == len(ordered)
                      else f"Đang làm {len(ordered)} bài, chưa có bài nào đúng hết.")
            g["trying"].append({**person, "reason_vi": reason, "exercise_id": ordered[0][0]})
        elif "hint_dependence" in c:
            g["trying"].append({**person, "reason_vi": f"Có {len(hints)} bài làm đúng nhờ gợi ý mức 2 hoặc 3.",
                                "exercise_id": (hints or passes)[0]})
        elif "practice_only" in c:
            g["trying"].append({**person, "reason_vi": f"Chạy thử {len(practice)} bài nhưng chưa nộp.",
                                "exercise_id": (practice or [ordered[0][0]])[0]})
        else:
            g["doing_well"].append({**person, "done": len(passes)})
    return g


def _mistake(eid: str, failing_map: dict, error_map: dict) -> Optional[str]:
    tests = sorted(failing_map.get(eid) or [], key=lambda x: (-int(x.get("students") or 0),
                                                              -int(x.get("attempts") or 0), int(x.get("test_idx") or 0)))
    top = next((x for x in tests if int(x.get("students") or 0) >= 2), None)
    if top:
        desc = str(top.get("description") or "").strip().rstrip(".")
        inp = " / ".join(str(top.get("input") or "").split("\n")).strip()
        text = (f"Nhiều bạn sai ở trường hợp “{desc}”" if desc
                else f"Nhiều bạn sai ở trường hợp kiểm tra số {int(top.get('test_idx') or 0)}")
        if inp:
            text += f" (ví dụ đầu vào: {inp})"
        return text + "."
    e = error_map.get(eid)
    if e:
        fail_n = sum(int(n or 0) for src in ("submit", "run") for k, n in (e.get(src) or {}).items() if k != "passed")
        fmt_n = int(e.get("format_only_submit") or 0) + int(e.get("format_only_run") or 0)
        if (fail_n >= OVERVIEW_THRESHOLDS["format_only_min_attempts"]
                and fmt_n / fail_n >= OVERVIEW_THRESHOLDS["format_only_share"]):
            return "Nhiều bạn làm đúng ý nhưng in sai cách trình bày (thừa dấu cách hoặc sai chữ hoa, chữ thường)."
    return None


def _time(eid: str, ttp_map: dict) -> Optional[str]:
    t = ttp_map.get(eid)
    if not t or int(t.get("n") or 0) < 2:
        return None
    m = float(t.get("median_minutes") or 0)
    if m < 1:
        return "Các bạn làm xong thường chưa tới 1 phút."
    if m < 90:
        return f"Các bạn làm xong thường mất khoảng {round(m)} phút."
    return f"Các bạn làm xong thường mất khoảng {round(m / 60)} giờ."


def _exercises(ex_list: list[dict], rows: list[dict], insights: dict, overview: Optional[dict]) -> list[dict]:
    failing_map = {f["exercise_id"]: f.get("tests") or [] for f in insights.get("failing_tests_by_exercise") or []}
    error_map = {e["exercise_id"]: e for e in insights.get("error_breakdown_by_exercise") or []}
    ttp_map = {t["exercise_id"]: t for t in insights.get("time_to_pass_by_exercise") or []}
    unsucc = {b["exercise_id"]: int(b.get("unsuccessful") or 0) for b in insights.get("bottlenecks") or []}
    issue_ex = {i.get("exercise_id") for i in (overview or {}).get("class_issues") or []
                if i.get("code") in ("bottleneck", "failing_test", "format_mismatch")}
    items = []
    for idx, e in enumerate(ex_list):
        eid = e["exercise_id"]
        done, attempted = int(e.get("students_passed") or 0), int(e.get("students_attempted") or 0)
        enrolled = int(e.get("students_enrolled") or len(rows))
        working = max(0, attempted - done)
        stuck = sum(1 for r in rows if (r.get("cells") or {}).get(eid) == "stuck")
        done_vi = f"{done} trong {enrolled} bạn đã làm xong" + (f", {working} bạn đang làm" if working else "") + "."
        items.append({"exercise_id": eid, "title": e.get("title") or eid, "number": idx + 1, "done": done,
                      "working": working, "not_started": max(0, enrolled - attempted), "enrolled": enrolled,
                      "stuck": stuck, "done_vi": done_vi, "mistake_vi": _mistake(eid, failing_map, error_map),
                      "time_vi": _time(eid, ttp_map), "hardest": False})
    cands = [x for x in items if x["stuck"] >= 1 or x["exercise_id"] in issue_ex]
    if cands:
        hardest = max(cands, key=lambda x: (x["stuck"], unsucc.get(x["exercise_id"], 0), -x["number"]))
        hardest["hardest"] = True
    return items


def _class_skills(kc_overview: Optional[dict]) -> list[str]:
    good, needs = [], []
    for it in (kc_overview or {}).get("items") or []:
        c = it.get("students") or {}
        secure, struggling = int(c.get("secure") or 0), int(c.get("struggling") or 0)
        with_ev = sum(int(v or 0) for k, v in c.items() if k != "no_evidence")
        name = kc_name(it.get("kc"), it.get("label_vi"))
        if with_ev and secure >= 2 and secure * 2 >= with_ev:
            good.append(name)
        if struggling >= 2:
            needs.append(f"{name} ({struggling} bạn cần luyện thêm)")
    out = []
    if good:
        out.append("Phần lớn các bạn làm tốt: " + ", ".join(good) + ".")
    if needs:
        out.append("Nên ôn lại trên lớp: " + ", ".join(needs) + ".")
    return out


def how_it_works_vi() -> list[str]:
    """Luật chia nhóm nói bằng lời, lấy đúng hằng số đang dùng (không chép tay con số)."""
    t = OVERVIEW_THRESHOLDS
    return [
        (f"Nên hỏi thăm: bạn đã thử một bài từ {PROCESS_STUCK_MIN_ATTEMPTS} lần trở lên (chạy thử và nộp bài) mà "
         f"{PROCESS_PROGRESS_WINDOW} lần gần nhất không đúng thêm trường hợp nào."),
        (f"Đang cố gắng: bạn chưa làm đúng hết bài nào, hoặc có từ {t['hint_pass_min_exercises']} bài làm đúng nhờ "
         f"gợi ý mức 2 hoặc 3, hoặc chạy thử từ {t['practice_only_min_exercises']} bài trở lên mà chưa nộp."),
        "Đang ổn: các bạn còn lại có vào làm bài.",
        "Chưa bắt đầu: chưa chạy thử hay nộp bài nào trong khoảng thời gian đang xem.",
        "Thời gian làm bài tính từ lần thử đầu tới lần nộp đúng, không phải thời gian ngồi làm liên tục.",
        "Đây là nhận xét tự động theo quy tắc đơn giản, chưa được kiểm chứng. Thầy cô nên xem thêm trước khi kết luận.",
    ]


def _brief(days: int, rows: list[dict], groups: dict, exercises: list[dict], daily_trend: Optional[list[dict]]):
    period, period_lower = _period(days)
    enrolled = len(rows)
    active = enrolled - len(groups["not_started"])
    passes = sum(int(d.get("first_passes") or 0) for d in daily_trend or [])
    s: list[str] = []
    if active == 0:
        s.append(f"{period} chưa có bạn nào vào làm bài.")
        return s, active
    s.append(f"{period} có {active} trong {enrolled} bạn vào làm bài, làm đúng thêm {passes} bài." if passes
             else f"{period} có {active} trong {enrolled} bạn vào làm bài, chưa có bài nào được làm đúng hết.")
    well = len(groups["doing_well"])
    if well * 2 > active:
        s.append("Phần lớn các bạn đang ổn.")
    elif well * 2 == active:
        s.append("Một nửa số bạn đang ổn.")
    else:
        s.append("Nhiều bạn vẫn đang cố gắng.")
    k = len(groups["check_in"])
    s.append(f"{k} bạn nên được hỏi thăm: {_names(groups['check_in'])}." if k else "Chưa có bạn nào cần hỏi thăm ngay.")
    hardest = next((x for x in exercises if x["hardest"]), None)
    if hardest:
        s.append(f"Bài khó nhất lúc này: {hardest['title']}." + (f" {hardest['mistake_vi']}" if hardest["mistake_vi"] else ""))
    ns = len(groups["not_started"])
    if ns:
        s.append(f"{ns} bạn chưa bắt đầu trong {period_lower}.")
    return s, active


def build_class_plain_view(insights: Optional[dict], overview: Optional[dict] = None, days: int = 7) -> dict[str, Any]:
    """Bản tin lớp từ kết quả get_class_insights (+ overview của class_overview). Không tính lại nhóm nào."""
    insights = insights or {}
    matrix = insights.get("matrix") or {}
    ex_list = matrix.get("exercises") or []
    rows = matrix.get("rows") or []
    ex_ids = [e["exercise_id"] for e in ex_list]
    titles = {e["exercise_id"]: e.get("title") or e["exercise_id"] for e in ex_list}
    groups = _groups(rows, ex_ids, titles, (overview or {}).get("attention"))
    exercises = _exercises(ex_list, rows, insights, overview)
    brief, active = _brief(days, rows, groups, exercises, insights.get("daily_trend"))
    status = insights.get("data_status") or "no_data"
    return {
        "brief_vi": brief,
        "few_data_vi": FEW_DATA_VI if active and status in ("no_data", "limited") else None,
        "groups": groups,
        "group_titles_vi": dict(GROUP_TITLES_VI),
        "exercises": exercises,
        "skills_vi": _class_skills(insights.get("kc_overview")),
        "how_it_works_vi": how_it_works_vi(),
        "active": active,
        "enrolled": len(rows),
        "days": int(days or 7),
        "version": PLAIN_VERSION,
    }


def class_brief_line(plain: Optional[dict]) -> str:
    """Một dòng cho thẻ lớp ở danh sách lớp của giảng viên."""
    if not plain or not plain.get("active"):
        return f"Chưa có hoạt động trong {int((plain or {}).get('days') or 7)} ngày qua."
    k = len(plain["groups"]["check_in"])
    parts = [f"{k} bạn nên hỏi thăm" if k else "Chưa có bạn nào cần hỏi thăm"]
    hardest = next((x for x in plain.get("exercises") or [] if x.get("hardest")), None)
    if hardest:
        parts.append(f"bài khó: {hardest['title']}")
    return " · ".join(parts)
```

#### 1.4. Tạo file test mới `test_plain_language_v59.py` ở gốc repo (chép nguyên văn)

```python
"""v5.9 — Lời thường: câu chữ (thuần, không cần DB) và nối API (DB tạm).

Chạy: .\\.claude\\run_isolated.ps1 test_plain_language_v59
"""
import os
import unittest
from datetime import datetime

from backend.plain_language import (
    BANNED_WORDS, FEW_DATA_VI, NOTE_STUDENT_VI, build_class_plain_view, build_course_path, build_story,
    build_today_card, class_brief_line, first_name, format_when, how_it_works_vi, kc_name, story_one_liner,
)
from pytutor_shared.learner_model import build_journey_points

NOW = datetime(2026, 11, 21, 10, 0, 0)


def ev(kind, passed=0, total=5, all_passed=False, hint=0, ts="2026-11-20 09:00:00", i=1, fmt=False):
    return {"kind": kind, "passed_tests": passed, "total_tests": total, "all_passed": all_passed, "hint_level": hint,
            "timestamp": ts, "id": i, "submission_id": i if kind != "run" else None, "format_only": fmt}


def built(events):
    out = build_journey_points(events)
    return out["points"], out["summary"]


def rec(eid, title, group, passed, total, run=0, ask=0, submit=0, first_pass_at=None, attempts=None):
    return {"exercise_id": eid, "title": title, "group": group, "best": {"passed": passed, "total": total},
            "counts": {"run": run, "ask": ask, "submit": submit}, "first_pass_at": first_pass_at,
            "attempts_to_first_pass": attempts, "points": []}


def today(**kw):
    base = {"full_name": None, "concepts": [], "next_practice": None, "week": {"this": 0, "prev": 0},
            "recent": [], "path": None, "now": NOW}
    base.update(kw)
    return build_today_card(**base)


def collect_vi(obj, out):
    """Gom mọi chuỗi nằm dưới khóa kết thúc bằng _vi (chuỗi, danh sách chuỗi, hoặc dict chuỗi)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.endswith("_vi"):
                if isinstance(v, str):
                    out.append(v)
                elif isinstance(v, list):
                    out.extend(x for x in v if isinstance(x, str))
                elif isinstance(v, dict):
                    out.extend(x for x in v.values() if isinstance(x, str))
            collect_vi(v, out)
    elif isinstance(obj, list):
        for x in obj:
            collect_vi(x, out)
    return out


EX = [{"exercise_id": "e1", "title": "In tam giác", "order_idx": 1, "students_passed": 3, "students_attempted": 5,
       "students_enrolled": 6},
      {"exercise_id": "e2", "title": "Số nguyên tố", "order_idx": 2, "students_passed": 2, "students_attempted": 4,
       "students_enrolled": 6}]
ROWS = [  # cố ý không theo A→Z để kiểm tra hàm tự sắp xếp
    {"username": "u_khoa", "full_name": "Khoa", "cells": {"e1": None, "e2": None}},
    {"username": "u_an", "full_name": "An", "cells": {"e1": "independent_pass", "e2": "stuck"}},
    {"username": "u_binh", "full_name": "Bình", "cells": {"e1": "practice_only", "e2": "practice_only"}},
    {"username": "u_chi", "full_name": "Chi", "cells": {"e1": "in_progress", "e2": None}},
    {"username": "u_dung", "full_name": "Dũng", "cells": {"e1": "hint_pass", "e2": "hint_pass"}},
    {"username": "u_ha", "full_name": "Hà", "cells": {"e1": "independent_pass", "e2": "retry_pass"}},
]
OVERVIEW = {"attention": [{"code": "stuck", "student": "u_an"}, {"code": "hint_dependence", "student": "u_dung"},
                          {"code": "practice_only", "student": "u_binh"}], "class_issues": []}


def make_insights(status="sufficient", rows=ROWS):
    return {
        "data_status": status,
        "matrix": {"exercises": EX, "rows": rows},
        "daily_trend": [{"date": "2026-11-20", "active_students": 4, "first_passes": 3},
                        {"date": "2026-11-21", "active_students": 3, "first_passes": 2}],
        "failing_tests_by_exercise": [{"exercise_id": "e2", "title": "Số nguyên tố", "tests": [
            {"test_idx": 3, "description": "n = 1", "input": "1", "attempts": 6, "students": 3, "format_attempts": 0}]}],
        "error_breakdown_by_exercise": [{"exercise_id": "e1", "title": "In tam giác",
                                         "submit": {"logic_partial": 2, "passed": 3}, "run": {"logic_partial": 2},
                                         "format_only_submit": 1, "format_only_run": 1}],
        "time_to_pass_by_exercise": [{"exercise_id": "e1", "median_minutes": 12.4, "n": 3},
                                     {"exercise_id": "e2", "median_minutes": 0.5, "n": 1}],
        "bottlenecks": [{"exercise_id": "e2", "unsuccessful": 5}, {"exercise_id": "e1", "unsuccessful": 2}],
        "kc_overview": {"items": [
            {"kc": "loop", "label_vi": "Vòng lặp",
             "students": {"secure": 3, "developing": 1, "struggling": 0, "no_evidence": 2}},
            {"kc": "recursion", "label_vi": "Đệ quy",
             "students": {"secure": 0, "developing": 1, "struggling": 2, "no_evidence": 3}}]},
    }


class JourneyPointsKeysTests(unittest.TestCase):
    def test_first_pass_keys(self):
        _, s = built([ev("run", 1, i=1, ts="2026-11-20 09:00:00"), ev("run", 2, i=2, ts="2026-11-20 09:01:00"),
                      ev("submit", 5, all_passed=True, i=3, ts="2026-11-20 09:02:00")])
        self.assertEqual((s["first_pass_at"], s["attempts_to_first_pass"]), ("2026-11-20 09:02:00", 3))
        _, s2 = built([ev("run", 1)])
        self.assertEqual((s2["first_pass_at"], s2["attempts_to_first_pass"]), (None, None))


class TodayCardTests(unittest.TestCase):
    def test_names_and_time(self):
        self.assertEqual(first_name("Trần Minh Khánh - SV K65 CNTT (MSV: 11236131)"), "Khánh")
        self.assertEqual(first_name("SV An (giả lập)"), "An")
        self.assertIsNone(first_name(""))
        self.assertEqual(today(full_name="Trần Minh Khánh")["greeting_vi"], "Chào Khánh")
        self.assertEqual(today()["greeting_vi"], "Chào bạn")
        self.assertEqual(format_when("2026-11-20 09:05:33"), "20/11 09:05")
        self.assertEqual(format_when("2026-11-20T09:05:33"), "20/11 09:05")
        self.assertIsNone(format_when("không phải ngày"))
        self.assertEqual(kc_name("custom_kc", "Tên riêng"), "Tên riêng")

    def test_no_activity(self):
        t = today()
        self.assertEqual(t["headline_vi"], "Chào mừng bạn! Hãy bắt đầu với bài đầu tiên.")
        self.assertEqual(t["moments"], [])
        self.assertIsNone(t["next_step"])
        self.assertIsNone(t["skills_vi"])
        self.assertEqual(t["note_vi"], NOTE_STUDENT_VI)

    def test_headline_week_and_near(self):
        near = [rec("e1", "Tổng số chẵn", "in_progress", 4, 5, run=3, submit=1)]
        t = today(week={"this": 2, "prev": 1}, recent=near)
        self.assertEqual(t["headline_vi"], "Tuần này bạn làm đúng 2 bài mới, nhiều hơn tuần trước 1 bài.")
        self.assertEqual(t["next_step"], {"exercise_id": "e1", "title": "Tổng số chẵn", "button_vi": "Làm tiếp",
                                          "reason_vi": "Lần trước bạn đã đúng 4 trên 5 trường hợp. Sửa thêm một chút là xong."})
        self.assertEqual(today(week={"this": 1, "prev": 1}, recent=near)["headline_vi"],
                         "Tuần này bạn làm đúng 1 bài mới, đều tay như tuần trước.")
        self.assertEqual(today(week={"this": 1, "prev": 3}, recent=near)["headline_vi"], "Tuần này bạn làm đúng 1 bài mới.")
        stuck_near = [rec("e1", "Tổng số chẵn", "stuck", 3, 5, run=8, submit=2)]
        self.assertEqual(today(recent=stuck_near)["headline_vi"],
                         "Bạn sắp xong bài Tổng số chẵn rồi: đã đúng 3 trên 5 trường hợp.")
        far = [rec("e2", "Đệ quy", "in_progress", 1, 5, run=2)]
        self.assertEqual(today(recent=far)["headline_vi"], "Sẵn sàng làm tiếp chưa? Bài tiếp theo đang chờ bạn.")

    def test_moments(self):
        r = [rec("e3", "Số nguyên tố", "retry_pass", 5, 5, run=5, submit=2, first_pass_at="2026-11-20 09:00:00", attempts=7),
             rec("e4", "In tam giác", "independent_pass", 4, 4, run=1, submit=1, first_pass_at="2026-11-19 09:00:00",
                 attempts=2)]
        self.assertEqual([m["text_vi"] for m in today(recent=r)["moments"]],
                         ["Bạn không bỏ cuộc: bài Số nguyên tố đúng hết sau 7 lần thử.",
                          "Bạn tự làm đúng bài In tam giác chỉ sau vài lần thử."])
        old = [rec("e3", "Số nguyên tố", "retry_pass", 5, 5, run=5, submit=2, first_pass_at="2026-11-10 09:00:00",
                   attempts=7)]
        self.assertEqual(today(recent=old)["moments"], [])
        loop = [{"kc": "loop", "label_vi": "Vòng lặp", "state": "secure",
                 "exercise_details": [{"exercise_id": "e4", "status": "passed"}]}]
        moments = today(recent=r[1:], concepts=loop)["moments"]
        self.assertEqual([m["kind"] for m in moments], ["independent", "new_skill"])
        self.assertEqual(moments[1]["text_vi"], "Bạn đã làm tốt phần Vòng lặp rồi.")

    def test_next_step_branches(self):
        acc = [{"kc": "accumulator", "label_vi": "Biến tích lũy", "state": "struggling",
                "exercise_details": [{"exercise_id": "e5", "title": "Tổng các số", "status": "struggling"}]}]
        far = [rec("e5", "Tổng các số", "in_progress", 1, 5, run=2, submit=2)]
        self.assertEqual(today(concepts=acc, recent=far)["next_step"],
                         {"exercise_id": "e5", "title": "Tổng các số", "button_vi": "Luyện bài này",
                          "reason_vi": "Bài này giúp bạn luyện thêm phần Cộng dồn trong vòng lặp."})
        for code, button, reason in (
            ("next_unattempted", "Bắt đầu", "Đây là bài tiếp theo bạn chưa làm."),
            ("retry_for_autonomy", "Làm lại", "Bạn đã xong bài này nhờ gợi ý. Thử tự làm lại để chắc tay hơn."),
            ("in_progress", "Làm tiếp", "Bạn đã nộp bài này nhưng chưa đúng hết. Sửa thêm một chút nhé."),
            ("unresolved_recurring", "Làm tiếp", "Bạn đã thử bài này vài lần mà chưa xong. Thử lại với cách nghĩ mới nhé."),
            ("khac", "Làm tiếp", "Đây là bài nên làm tiếp."),
        ):
            step = today(recent=far, next_practice={"exercise_id": "e6", "title": "Bài mới", "reason_code": code})["next_step"]
            self.assertEqual((step["button_vi"], step["reason_vi"]), (button, reason))

    def test_skills_line(self):
        cs = [{"kc": "io_format", "state": "secure"}, {"kc": "loop", "state": "secure"},
              {"kc": "conditional", "state": "developing"}, {"kc": "recursion", "state": "struggling"},
              {"kc": "string", "state": "no_evidence"}]
        self.assertEqual(today(concepts=cs, recent=[rec("e1", "A", "in_progress", 0, 5, run=1)])["skills_vi"],
                         "Bạn làm tốt: In và nhập dữ liệu, Vòng lặp · Đang luyện: Câu lệnh if · Nên luyện thêm: Đệ quy")

    def test_course_path(self):
        rows = [{"exercise_id": "a", "title": "A", "order_idx": 1, "status": "MASTERED", "stars_earned": 3},
                {"exercise_id": "b", "title": "B", "order_idx": 2, "status": "MASTERED", "stars_earned": 2},
                {"exercise_id": "c", "title": "C", "order_idx": 3, "status": "IN_PROGRESS"},
                {"exercise_id": "d", "title": "D", "order_idx": 4, "status": "AVAILABLE"},
                {"exercise_id": "e", "title": "E", "order_idx": 5, "status": "LOCKED"}]
        p = build_course_path(rows, "cls", "Python K65")
        self.assertEqual([s["kind"] for s in p["steps"]], ["done", "done", "current", "open", "locked"])
        self.assertEqual([s["stars"] for s in p["steps"]], [3, 2, 0, 0, 0])
        self.assertEqual((p["remaining"], p["caption_vi"]), (3, "Còn 3 bài nữa là xong học phần."))
        rows[2]["status"] = "AVAILABLE"
        self.assertEqual([s["kind"] for s in build_course_path(rows, "cls", "Python K65")["steps"]],
                         ["done", "done", "current", "open", "locked"])
        self.assertEqual(build_course_path(rows[:2], "cls", "Python K65")["caption_vi"], "Bạn đã xong cả 2 bài của học phần.")
        self.assertIsNone(build_course_path([], "cls", "x"))


class StoryTests(unittest.TestCase):
    def test_passed_after_tries_and_steps(self):
        pts, summ = built([ev("run", 1, ts="2026-11-20 09:00:00", i=1), ev("run", 3, ts="2026-11-20 09:05:00", i=2),
                           ev("ask", hint=1, ts="2026-11-20 09:06:00", i=3),
                           ev("submit", 5, all_passed=True, ts="2026-11-20 09:10:00", i=4)])
        pts[-1]["code"] = "print(1)"
        s = build_story(pts, summ)
        self.assertEqual(s["summary_vi"], "Bạn thử 3 lần rồi làm đúng hết.")
        self.assertEqual([x["text_vi"] for x in s["steps"]],
                         ["Chạy thử: đúng 1 trên 5", "Chạy thử: đúng 3 trên 5", "Hỏi Gia sư AI, gợi ý mức 1",
                          "Nộp bài: đúng hết"])
        self.assertEqual([x["tag_vi"] for x in s["steps"]], [None, "Đúng thêm", None, None])
        self.assertEqual(s["steps"][3]["tone"], "done")
        self.assertEqual(s["steps"][0]["when_vi"], "20/11 09:00")
        self.assertEqual(s["steps"][3]["code"], "print(1)")
        self.assertNotIn("code", s["steps"][0])
        self.assertEqual(s["visible_from"], 0)
        t = build_story(pts, summ, audience="teacher", student_name="An")
        self.assertEqual(t["summary_vi"], "An thử 3 lần rồi làm đúng hết. Đã hỏi Gia sư AI 1 lần.")

    def test_other_branches(self):
        cases = [
            ([ev("submit", 4, total=4, all_passed=True)], "Bạn làm đúng ngay lần đầu."),
            ([ev("ask", hint=2)], "Bạn đã xem gợi ý nhưng chưa chạy thử. Bấm “Chạy thử” để xem kết quả."),
            ([ev("run", 1, i=1), ev("run", 2, i=2)],
             "Bạn đã chạy thử 2 lần, tốt nhất đúng 2 trên 5 trường hợp. Khi thấy ổn, bấm “Nộp bài” nhé."),
            ([ev("run", 1, i=1), ev("submit", 2, i=2)],
             "Bạn đã thử 2 lần, tốt nhất đúng 2 trên 5 trường hợp. Sửa từng chỗ một nhé."),
        ]
        for events, expected in cases:
            self.assertEqual(build_story(*built(events))["summary_vi"], expected)
        self.assertEqual(build_story([], {})["summary_vi"], "Bạn chưa làm bài này. Bấm “Chạy thử” để bắt đầu.")
        self.assertEqual(build_story([], {}, audience="teacher", student_name="An")["summary_vi"],
                         "An chưa làm bài này trong khoảng thời gian đang xem.")

    def test_stuck_and_condense(self):
        events = [ev("run", 2, i=k, ts=f"2026-11-20 09:0{k}:00") for k in range(8)] + \
                 [ev("submit", 2, i=20, ts="2026-11-20 09:30:00")]
        pts, summ = built(events)
        self.assertEqual(summ["group"], "stuck")
        s = build_story(pts, summ)
        self.assertEqual(s["summary_vi"], "Bạn đã thử 9 lần, tốt nhất đúng 2 trên 5 trường hợp. Mấy lần gần đây chưa đúng "
                                          "thêm. Thử bấm “Chạy từng bước” để xem code chạy thế nào, hoặc hỏi Gia sư AI.")
        self.assertEqual([x["text_vi"] for x in s["steps"]], ["Chạy thử 8 lần: tốt nhất đúng 2 trên 5", "Nộp bài: đúng 2 trên 5"])
        self.assertEqual([x["tag_vi"] for x in s["steps"]], [None, None])
        t = build_story(pts, summ, audience="teacher", student_name="An")
        self.assertEqual(t["summary_vi"], "An đã thử 9 lần, tốt nhất đúng 2 trên 5 trường hợp. Mấy lần gần đây chưa đúng "
                                          "thêm, bạn ấy có thể cần được hỏi thăm.")

    def test_format_tag_visible_from_and_one_liner(self):
        s = build_story(*built([ev("submit", 3, total=4, fmt=True)]))
        self.assertEqual(s["steps"][0]["tag_vi"], "Chỉ sai cách in kết quả")
        many = []
        for k in range(5):
            many += [ev("run", 1, i=2 * k, ts=f"2026-11-20 10:{k}0:00"),
                     ev("submit", 1, i=2 * k + 1, ts=f"2026-11-20 10:{k}5:00")]
        self.assertEqual(build_story(*built(many))["visible_from"], 2)
        self.assertEqual(story_one_liner(rec("e", "A", "retry_pass", 5, 5)), "Đã làm đúng hết.")
        self.assertEqual(story_one_liner(rec("e", "A", "practice_only", 2, 5, run=3)), "Đã chạy thử 3 lần, chưa nộp bài.")
        self.assertEqual(story_one_liner(rec("e", "A", "in_progress", 2, 5, run=1, submit=1)),
                         "Đang làm: tốt nhất đúng 2 trên 5 trường hợp.")


class ClassPlainTests(unittest.TestCase):
    def test_groups(self):
        g = build_class_plain_view(make_insights(), OVERVIEW, 7)["groups"]
        self.assertEqual([p["username"] for p in g["check_in"]], ["u_an"])
        self.assertEqual(g["check_in"][0]["reason_vi"],
                         "Đang gặp khó ở bài Số nguyên tố: thử nhiều lần mà mấy lần gần đây chưa đúng thêm.")
        self.assertEqual(g["check_in"][0]["exercise_id"], "e2")
        self.assertEqual([(p["username"], p["reason_vi"]) for p in g["trying"]], [
            ("u_binh", "Đã chạy thử 2 bài nhưng chưa nộp bài nào."),
            ("u_chi", "Đang làm 1 bài, chưa có bài nào đúng hết."),
            ("u_dung", "Có 2 bài làm đúng nhờ gợi ý mức 2 hoặc 3."),
        ])
        self.assertEqual([p["username"] for p in g["doing_well"]], ["u_ha"])
        self.assertEqual([p["username"] for p in g["not_started"]], ["u_khoa"])

    def test_exercises_and_hardest(self):
        ex = build_class_plain_view(make_insights(), OVERVIEW, 7)["exercises"]
        self.assertEqual(ex[0]["done_vi"], "3 trong 6 bạn đã làm xong, 2 bạn đang làm.")
        self.assertEqual(ex[0]["mistake_vi"],
                         "Nhiều bạn làm đúng ý nhưng in sai cách trình bày (thừa dấu cách hoặc sai chữ hoa, chữ thường).")
        self.assertEqual(ex[0]["time_vi"], "Các bạn làm xong thường mất khoảng 12 phút.")
        self.assertEqual(ex[1]["mistake_vi"], "Nhiều bạn sai ở trường hợp “n = 1” (ví dụ đầu vào: 1).")
        self.assertIsNone(ex[1]["time_vi"])
        self.assertEqual([e["hardest"] for e in ex], [False, True])

    def test_brief_and_skills(self):
        v = build_class_plain_view(make_insights(), OVERVIEW, 7)
        self.assertEqual(v["brief_vi"], [
            "Tuần này có 5 trong 6 bạn vào làm bài, làm đúng thêm 5 bài.",
            "Nhiều bạn vẫn đang cố gắng.",
            "1 bạn nên được hỏi thăm: An.",
            "Bài khó nhất lúc này: Số nguyên tố. Nhiều bạn sai ở trường hợp “n = 1” (ví dụ đầu vào: 1).",
            "1 bạn chưa bắt đầu trong tuần này.",
        ])
        self.assertEqual(v["skills_vi"], ["Phần lớn các bạn làm tốt: Vòng lặp.",
                                          "Nên ôn lại trên lớp: Đệ quy (2 bạn cần luyện thêm)."])
        self.assertIsNone(v["few_data_vi"])
        self.assertEqual(build_class_plain_view(make_insights("limited"), OVERVIEW, 7)["few_data_vi"], FEW_DATA_VI)
        self.assertEqual(class_brief_line(v), "1 bạn nên hỏi thăm · bài khó: Số nguyên tố")
        v14 = build_class_plain_view(make_insights(), OVERVIEW, 14)
        self.assertTrue(v14["brief_vi"][0].startswith("Trong 14 ngày qua có 5 trong 6 bạn"))
        self.assertEqual(v14["brief_vi"][-1], "1 bạn chưa bắt đầu trong 14 ngày qua.")

    def test_no_activity(self):
        empty_rows = [{"username": "u1", "full_name": "An", "cells": {"e1": None, "e2": None}}]
        v = build_class_plain_view(make_insights(rows=empty_rows), {"attention": []}, 7)
        self.assertEqual(v["brief_vi"], ["Tuần này chưa có bạn nào vào làm bài."])
        self.assertEqual(v["active"], 0)
        self.assertIsNone(v["few_data_vi"])
        self.assertEqual(class_brief_line(v), "Chưa có hoạt động trong 7 ngày qua.")

    def test_how_it_works_uses_constants(self):
        rules = how_it_works_vi()
        self.assertIn("từ 8 lần trở lên", rules[0])
        self.assertIn("5 lần gần nhất", rules[0])


class BannedWordsTests(unittest.TestCase):
    def test_all_generated_text_is_plain(self):
        texts: list = []
        r = [rec("e1", "Tổng số chẵn", "in_progress", 4, 5, run=3, submit=1),
             rec("e3", "Số nguyên tố", "retry_pass", 5, 5, run=5, submit=2, first_pass_at="2026-11-20 09:00:00", attempts=7),
             rec("e4", "In tam giác", "independent_pass", 4, 4, run=1, submit=1, first_pass_at="2026-11-19 09:00:00",
                 attempts=2)]
        cs = [{"kc": k, "state": s, "exercise_details": [{"exercise_id": "e4", "title": "In tam giác", "status": "struggling"}]}
              for k, s in (("io_format", "secure"), ("loop", "developing"), ("recursion", "struggling"))]
        path = build_course_path([{"exercise_id": "a", "title": "A", "order_idx": 1, "status": "MASTERED", "stars_earned": 3},
                                  {"exercise_id": "b", "title": "B", "order_idx": 2, "status": "AVAILABLE"}], "cls", "Python")
        variants = [{}, {"week": {"this": 2, "prev": 1}, "recent": r, "concepts": cs, "path": path},
                    {"week": {"this": 1, "prev": 1}, "recent": r[:1]}, {"recent": r[:1]}]
        for code in ("next_unattempted", "retry_for_autonomy", "in_progress", "unresolved_recurring", None):
            variants.append({"recent": [rec("e9", "Bài khác", "in_progress", 0, 5, run=1)],
                             "next_practice": {"exercise_id": "e6", "title": "Bài mới", "reason_code": code}})
        for kw in variants:
            collect_vi(today(**kw), texts)
        story_events = [
            [ev("run", 1, i=1), ev("run", 3, i=2), ev("ask", hint=1, i=3), ev("submit", 5, all_passed=True, i=4)],
            [ev("ask", hint=2)], [ev("run", 1, i=1), ev("run", 2, i=2)], [ev("submit", 3, total=4, fmt=True)],
            [ev("run", 2, i=k) for k in range(8)] + [ev("submit", 2, i=20)],
        ]
        for events in story_events:
            for audience in ("student", "teacher"):
                collect_vi(build_story(*built(events), audience=audience, student_name="An"), texts)
        texts.extend(story_one_liner(item) for item in r)
        for days in (7, 14):
            collect_vi(build_class_plain_view(make_insights(), OVERVIEW, days), texts)
        collect_vi(build_class_plain_view(make_insights("limited"), OVERVIEW, 7), texts)
        texts.append(class_brief_line(build_class_plain_view(make_insights(), OVERVIEW, 7)))
        texts.extend(how_it_works_vi())
        self.assertGreater(len(texts), 40)
        for t in texts:
            low = f" {t.lower()} "
            for w in BANNED_WORDS:
                self.assertNotIn(w, low, f"“{t}” chứa từ cấm “{w}”")


@unittest.skipUnless(os.environ.get("PYTUTOR_DB_PATH"), "cần PYTUTOR_DB_PATH (DB tạm)")
class PlainIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from backend import database as db
        from seed.seed_demo_class_v58 import CLASS_ID, build_demo_class
        cls.db, cls.class_id = db, CLASS_ID
        cls.info = build_demo_class(db)
        cls.ex = cls.info["exercise_ids"]

    def h(self, user, role, name=None):
        from backend.auth import create_token
        return {"Authorization": f"Bearer {create_token(user, role, name or user)}"}

    def client(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    def test_student_today_story_and_path(self):
        with self.client() as c:
            r = c.get(f"/api/student/journey?class_id={self.class_id}&exercise_id={self.ex[0]}",
                      headers=self.h("v58_binh", "student", "SV Bình (giả lập)"))
            self.assertEqual(r.status_code, 200, r.text)
            body = r.json()
            card = body["today"]
            self.assertEqual(card["greeting_vi"], "Chào Bình")
            self.assertEqual(card["path"]["class_id"], self.class_id)
            self.assertEqual(len(card["path"]["steps"]), len(self.ex))
            self.assertEqual(card["note_vi"], NOTE_STUDENT_VI)
            self.assertTrue(body["current"]["story"]["steps"])
            self.assertTrue(any(s.get("code") for s in body["current"]["story"]["steps"] if s["kind"] == "submit"))
            self.assertTrue(all(isinstance(e.get("story_vi"), str) for e in body["recent_exercises"]))
            self.assertIn("headline", body)  # khóa cũ v5.8 vẫn còn
            portal = c.get("/api/student/journey", headers=self.h("v58_binh", "student")).json()
            self.assertEqual(portal["today"]["path"]["class_id"], self.class_id)

    def test_instructor_plain_view_consistent(self):
        with self.client() as c:
            body = c.get(f"/api/instructor/classes/{self.class_id}/insights?days=30",
                         headers=self.h("gv_tran", "instructor")).json()
        plain = body["plain"]
        need = {s["username"] for s in body["students"] if s["needs_support"]}
        self.assertEqual({p["username"] for p in plain["groups"]["check_in"]}, need)
        everyone = [p["username"] for k in ("check_in", "trying", "doing_well", "not_started") for p in plain["groups"][k]]
        self.assertEqual(sorted(everyone), sorted(r["username"] for r in body["matrix"]["rows"]))
        self.assertEqual(len(everyone), len(set(everyone)))
        self.assertEqual(len(plain["exercises"]), len(self.ex))
        self.assertTrue(plain["brief_vi"])
        self.assertIn("action_cards", body)  # khóa cũ v5.8 vẫn còn

    def test_instructor_story_has_no_code(self):
        with self.client() as c:
            body = c.get(f"/api/instructor/classes/{self.class_id}/insights?days=30",
                         headers=self.h("gv_tran", "instructor")).json()
            target = (body["plain"]["groups"]["check_in"] or body["plain"]["groups"]["trying"])[0]
            r = c.get(f"/api/instructor/classes/{self.class_id}/students/{target['username']}"
                      f"/exercises/{target['exercise_id']}/journey?days=30", headers=self.h("gv_tran", "instructor"))
            self.assertEqual(r.status_code, 200, r.text)
            story = r.json()["story"]
            self.assertTrue(story["summary_vi"])
            self.assertFalse(any("code" in s for s in story["steps"]))

    def test_classes_attention_brief(self):
        with self.client() as c:
            rows = c.get("/api/instructor/classes-attention", headers=self.h("gv_tran", "instructor")).json()["classes"]
        demo = next(r for r in rows if r["id"] == self.class_id)
        self.assertIsInstance(demo["brief_vi"], str)
        self.assertIn("check_in", demo)


if __name__ == "__main__":
    unittest.main()
```

**Kiểm tra Bước 1:**
- `py -m compileall -q backend mcp_server pytutor_shared` không báo lỗi.
- `.\.claude\run_isolated.ps1 test_plain_language_v59`: các lớp thuần đạt. Lớp `PlainIntegrationTests` lúc này **fail** là đúng, vì Bước 2 chưa làm; ghi nhận và sang Bước 2.
- `.\.claude\run_isolated.ps1 test_visual_views_v58 test_learner_model` vẫn `OK`.

---

### Bước 2 — Nối vào API (`backend/main.py`)

#### 2.1. Import

- Ở nhóm import thư viện chuẩn đầu file (cạnh `import json`), thêm:
  ```python
  from datetime import datetime
  ```
- Ngay sau dòng `from backend.student_journey import build_student_headline, describe_exercise_journey, DISCLAIMER_VI`, thêm:
  ```python
  from backend.plain_language import (build_class_plain_view, build_course_path, build_story, build_today_card,
                                      class_brief_line, story_one_liner)
  ```

#### 2.2. Endpoint `/api/instructor/classes/{class_id}/insights`

Trong khối `if insights:`, sau dòng gán `insights["action_cards"] = ...`, thêm:
```python
        insights["plain"] = build_class_plain_view(insights, insights["overview"], days)
```

#### 2.3. Endpoint `/api/instructor/classes-attention`

Trong vòng `for cls in get_credit_classes(...)`, sửa như sau (giữ nguyên khóa cũ, cache và cách sắp xếp):
- Trong `try:`, sau dòng `issues = len(overview.get("class_issues", []))`, thêm:
  ```python
              plain = build_class_plain_view(insights, overview, 7) if insights else None
              check_in = len(plain["groups"]["check_in"]) if plain else 0
              brief = class_brief_line(plain)
  ```
- Trong `except`, đổi dòng gán thành:
  ```python
              attention, issues, status, check_in, brief = 0, 0, "error", 0, "Chưa tải được tình hình lớp này."
  ```
- Trong `rows.append({...})`, thêm 2 khóa: `"check_in": check_in, "brief_vi": brief`.

#### 2.4. Endpoint dấu chân của giảng viên (`.../students/{username}/exercises/{exercise_id}/journey`)

- Đổi dòng `enrolled = {s.get("username") or s.get("student_username") for s in get_class_students(class_id)}` thành 2 dòng:
  ```python
      students = get_class_students(class_id)
      enrolled = {s.get("username") or s.get("student_username") for s in students}
  ```
- Ngay trước `return journey`, thêm:
  ```python
      name = next((s.get("full_name") for s in students
                   if (s.get("username") or s.get("student_username")) == username), None) or username
      journey["story"] = build_story(journey["points"], journey["summary"], audience="teacher", student_name=name)
  ```

#### 2.5. Endpoint `/api/student/journey`

- Ngay **trên** dòng `@app.get("/api/student/journey")`, thêm hàm trợ giúp:
  ```python
  def _pick_path_class(username: str, class_id: Optional[str], recent: list[dict]) -> Optional[dict]:
      """Lớp để vẽ chặng đường: lớp đang xem; nếu không có thì lớp chứa bài vừa làm gần nhất; nếu không thì lớp đầu tiên."""
      if class_id:
          cls = get_credit_class_by_id(class_id) or {}
          return {"id": class_id, "class_name": cls.get("class_name"), "exercises": get_class_exercises(class_id, username)}
      classes = get_student_classes(username)
      if not classes:
          return None
      loaded = [{"id": c["id"], "class_name": c.get("class_name"), "exercises": get_class_exercises(c["id"], username)}
                for c in classes]
      for item in recent or []:
          for c in loaded:
              if any(e.get("exercise_id") == item.get("exercise_id") for e in c["exercises"]):
                  return c
      return loaded[0]
  ```
- Trong thân endpoint, giữ nguyên mọi dòng cũ. Thêm như sau:
  - Ngay sau dòng `overview = get_student_journey_overview(username, class_id=class_id)`:
    ```python
        for item in overview["recent_exercises"]:
            item["story_vi"] = story_one_liner(item)
    ```
  - Trong khối `if exercise_id:`, sau dòng gán `current["description_vi"]`:
    ```python
            current["story"] = build_story(current["points"], current["summary"], audience="student")
    ```
  - Ngay trước `return {`:
    ```python
        path_class = _pick_path_class(username, class_id, overview["recent_exercises"])
        path = (build_course_path(path_class["exercises"], path_class["id"], path_class["class_name"])
                if path_class else None)
        today = build_today_card(full_name=token_data.get("name"), concepts=lm.get("concepts", []),
                                 next_practice=next_practice, week=overview["week"],
                                 recent=overview["recent_exercises"], path=path, now=datetime.now())
    ```
  - Trong dict trả về, thêm khóa `"today": today,` (giữ nguyên các khóa cũ).

**Kiểm tra Bước 2:**
- `py -m compileall -q backend mcp_server pytutor_shared` không lỗi.
- `.\.claude\run_isolated.ps1 test_plain_language_v59 test_visual_views_v58 test_class_overview_v57 test_qa_authorization` đều `OK`, kể cả `PlainIntegrationTests`.

---

### Bước 3 — Thành phần giao diện dùng chung

Tạo thư mục mới `frontend/src/components/plain/` và các file dưới đây, chép nguyên văn. **Trong các file này, kể cả comment, không được có từ cấm** (danh sách ở Bước 3.3).

#### 3.1. `frontend/src/utils/path.js`

```js
/** Cửa sổ trạm cho chặng đường học phần: tối đa `max` trạm quanh bài đang làm. Hàm thuần. */
export function windowSteps(steps, max = 8) {
  const list = Array.isArray(steps) ? steps : [];
  if (list.length <= max) return { visible: list, hiddenBefore: 0, hiddenAfter: 0 };
  let c = list.findIndex((s) => s.kind === 'current');
  if (c < 0) c = list.findIndex((s) => s.kind !== 'done');
  if (c < 0) c = list.length - 1;
  let start = Math.max(0, c - 3);
  const end = Math.min(list.length, start + max);
  start = Math.max(0, end - max);
  return { visible: list.slice(start, end), hiddenBefore: start, hiddenAfter: list.length - end };
}
```

#### 3.2. `frontend/src/utils/path.test.js`

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { windowSteps } from './path.js';

const mk = (kinds) => kinds.map((kind, i) => ({ exercise_id: `e${i + 1}`, kind }));

test('ít trạm thì hiện hết', () => {
  const r = windowSteps(mk(['done', 'current', 'open']), 8);
  assert.equal(r.visible.length, 3);
  assert.equal(r.hiddenBefore, 0);
  assert.equal(r.hiddenAfter, 0);
});

test('nhiều trạm thì giữ bài đang làm trong cửa sổ', () => {
  const kinds = Array.from({ length: 12 }, (_, i) => (i < 6 ? 'done' : i === 6 ? 'current' : 'locked'));
  const r = windowSteps(mk(kinds), 8);
  assert.equal(r.visible.length, 8);
  assert.equal(r.hiddenBefore, 3);
  assert.equal(r.hiddenAfter, 1);
  assert.ok(r.visible.some((s) => s.kind === 'current'));
});

test('bài đang làm ở cuối danh sách', () => {
  const kinds = Array.from({ length: 12 }, (_, i) => (i < 11 ? 'done' : 'current'));
  const r = windowSteps(mk(kinds), 8);
  assert.equal(r.hiddenBefore, 4);
  assert.equal(r.hiddenAfter, 0);
});

test('không có bài đang làm thì lấy bài đầu tiên chưa xong', () => {
  const kinds = Array.from({ length: 12 }, (_, i) => (i < 10 ? 'done' : 'locked'));
  const r = windowSteps(mk(kinds), 8);
  assert.ok(r.visible.some((s) => s.exercise_id === 'e11'));
});

test('xong hết thì hiện các trạm cuối', () => {
  const r = windowSteps(mk(Array(12).fill('done')), 8);
  assert.equal(r.hiddenBefore, 4);
  assert.equal(r.hiddenAfter, 0);
});
```

#### 3.3. `frontend/src/utils/plainCopy.test.js` (kiểm tra từ cấm tự động)

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const components = join(here, '..', 'components');
const FILES = [
  ...readdirSync(join(components, 'plain')).filter((f) => f.endsWith('.jsx')).map((f) => join(components, 'plain', f)),
  join(components, 'StudentProfileModal.jsx'),
];
const BANNED = ['khái niệm', 'trạng thái', 'bằng chứng', 'quy ước', 'hiệu chuẩn', 'trung vị', 'tự làm',
  'nhóm quá trình', 'mắc kẹt', 'đạt độc lập', 'thử–sửa', 'lượt', 'heuristic', 'xếp hạng'];

test('các màn lời thường không chứa từ chuyên môn', () => {
  for (const file of FILES) {
    const text = readFileSync(file, 'utf8').toLowerCase();
    for (const word of BANNED) assert.ok(!text.includes(word), `${file} chứa "${word}"`);
  }
});
```

Sửa `frontend/package.json`, dòng script `test:ui-utils` thành:
```json
"test:ui-utils": "node --test src/utils/share.test.js src/utils/path.test.js src/utils/plainCopy.test.js",
```

#### 3.4. `frontend/src/components/plain/CoursePath.jsx`

```jsx
import React from 'react';
import { CheckCircle2, Lock, MapPin } from 'lucide-react';
import { windowSteps } from '../../utils/path';

const KIND_TEXT = { done: 'đã xong', current: 'bạn đang ở đây', open: 'chưa làm', locked: 'chưa mở, cần xong bài trước' };

function StationIcon({ step }) {
  const base = 'flex size-9 shrink-0 items-center justify-center rounded-full';
  if (step.kind === 'done') return <span className={`${base} bg-success-soft text-success-strong`}><CheckCircle2 aria-hidden="true" className="size-5" /></span>;
  if (step.kind === 'current') return <span className={`${base} bg-primary text-primary-foreground`}><MapPin aria-hidden="true" className="size-5" /></span>;
  if (step.kind === 'locked') return <span className={`${base} border border-border bg-surface-raised text-muted`}><Lock aria-hidden="true" className="size-4" /></span>;
  return <span className={`${base} border border-border bg-surface text-sm font-bold text-foreground`}>{step.number}</span>;
}

function Stars({ count }) {
  if (!count) return null;
  return (
    <span aria-label={`${count} trên 3 sao`} className="block text-xs tracking-wide text-amber-500">
      {'★'.repeat(count)}{'☆'.repeat(Math.max(0, 3 - count))}
    </span>
  );
}

/** Chặng đường học phần: mỗi bài là một trạm. Dưới 640px thành danh sách dọc. */
export default function CoursePath({ path, onOpenExercise }) {
  const { visible, hiddenBefore, hiddenAfter } = windowSteps(path?.steps, 8);
  if (!visible.length) return null;
  const cls = 'flex w-full items-center gap-3 rounded-2xl p-2 text-left sm:flex-col sm:gap-1.5 sm:text-center';
  return (
    <div className="space-y-2">
      {path.class_name && <p className="text-xs font-semibold text-muted">{path.class_name}</p>}
      <ol aria-label={`Chặng đường học phần ${path.class_name || ''}`.trim()} className="grid gap-2 sm:grid-flow-col sm:auto-cols-fr">
        {visible.map((step) => {
          const label = `${step.title}: ${KIND_TEXT[step.kind]}`;
          const body = (
            <>
              <StationIcon step={step} />
              <span className="min-w-0">
                <span className={`line-clamp-2 block break-words text-xs font-semibold ${step.kind === 'locked' ? 'text-muted' : 'text-foreground'}`}>{step.title}</span>
                {step.kind === 'current' && <span className="block text-[11px] font-semibold text-primary">Bạn ở đây</span>}
                {step.kind === 'done' && <Stars count={step.stars} />}
              </span>
            </>
          );
          return (
            <li key={step.exercise_id}>
              {step.kind !== 'locked' && onOpenExercise ? (
                <button type="button" aria-label={label} onClick={() => onOpenExercise(step.exercise_id, path.class_id)} className={`${cls} cursor-pointer hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400`}>
                  {body}
                </button>
              ) : (
                <div role="group" aria-label={label} className={cls}>{body}</div>
              )}
            </li>
          );
        })}
      </ol>
      <p className="text-center text-sm text-muted">
        {hiddenBefore > 0 && <span>+{hiddenBefore} bài trước · </span>}
        {path.caption_vi}
        {hiddenAfter > 0 && <span> · +{hiddenAfter} bài sau</span>}
      </p>
    </div>
  );
}
```

#### 3.5. `frontend/src/components/plain/TodayCard.jsx`

```jsx
import React from 'react';
import { ArrowRight, CheckCircle2, Trophy } from 'lucide-react';
import CoursePath from './CoursePath';

/** Thẻ "Hôm nay của bạn": lời chào, một câu chính, tin vui, chặng đường, một việc tiếp theo. Câu chữ lấy nguyên văn từ backend. */
export default function TodayCard({ today, onOpenExercise, showGreeting = true }) {
  if (!today) return null;
  const next = today.next_step;
  const nextInPath = Boolean(next && today.path?.steps?.some((s) => s.exercise_id === next.exercise_id));
  return (
    <section aria-labelledby="today-title" className="space-y-4 rounded-3xl border border-border bg-surface p-5 shadow-bento sm:p-6">
      <div>
        {showGreeting && <p className="text-sm text-muted">{today.greeting_vi}</p>}
        <h2 id="today-title" className="mt-1 text-xl font-bold leading-snug tracking-tight text-foreground sm:text-2xl">{today.headline_vi}</h2>
      </div>
      {(today.moments || []).length > 0 && (
        <ul className="space-y-2">
          {today.moments.map((m) => (
            <li key={m.kind} className="flex items-start gap-2 rounded-2xl border border-success-line bg-success-soft px-3 py-2 text-sm text-success-strong">
              <Trophy aria-hidden="true" className="mt-0.5 size-4 shrink-0" />
              <span>{m.text_vi}</span>
            </li>
          ))}
        </ul>
      )}
      {today.path && <CoursePath path={today.path} onOpenExercise={onOpenExercise} />}
      {next && (
        <div className="flex flex-col gap-3 border-t border-border pt-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <p className="break-words text-base font-bold text-foreground">{next.title}</p>
            <p className="mt-0.5 text-sm text-muted">{next.reason_vi}</p>
          </div>
          {onOpenExercise && (
            <button
              type="button"
              onClick={() => onOpenExercise(next.exercise_id, nextInPath ? today.path.class_id : undefined)}
              className="inline-flex min-h-11 shrink-0 cursor-pointer items-center justify-center gap-2 rounded-full bg-primary px-5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2"
            >
              {next.button_vi} <ArrowRight aria-hidden="true" className="size-4" />
            </button>
          )}
        </div>
      )}
      {today.skills_vi && (
        <p className="flex items-start gap-2 text-sm text-foreground">
          <CheckCircle2 aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-success" />
          <span>{today.skills_vi}</span>
        </p>
      )}
      <p className="text-[11px] text-muted">{today.note_vi}</p>
    </section>
  );
}
```

#### 3.6. `frontend/src/components/plain/StorySteps.jsx`

```jsx
import React, { useState } from 'react';
import { CheckCircle2, MessageCircle, Play, RotateCcw, Send } from 'lucide-react';

const ICONS = { play: Play, message: MessageCircle, send: Send, check: CheckCircle2 };
const DOT = {
  neutral: 'border-border bg-surface text-muted',
  done: 'border-success-line bg-success-soft text-success-strong',
};
const TAG = {
  good: 'bg-success-soft text-success-strong',
  info: 'bg-info-soft text-info-strong',
};

/** Câu chuyện của một bài: một câu tóm tắt và các bước theo thời gian. Câu chữ lấy nguyên văn từ backend (khóa `story`). */
export default function StorySteps({ story, onLoadCode }) {
  const [showAll, setShowAll] = useState(false);
  if (!story) return null;
  const steps = story.steps || [];
  const from = showAll ? 0 : Math.max(0, story.visible_from || 0);
  return (
    <div className="space-y-3">
      <p className="text-sm leading-relaxed text-foreground">{story.summary_vi}</p>
      {from > 0 && (
        <button type="button" onClick={() => setShowAll(true)} className="cursor-pointer text-xs font-semibold text-primary hover:underline">
          Xem cả {steps.length} bước
        </button>
      )}
      {steps.length > 0 && (
        <ol className="space-y-3 border-l-2 border-border pl-5">
          {steps.slice(from).map((s, i) => {
            const Icon = ICONS[s.icon] || Play;
            return (
              <li key={`${from + i}-${s.kind}`} className="relative">
                <span aria-hidden="true" className={`absolute -left-[2.06rem] top-0 flex size-6 items-center justify-center rounded-full border ${DOT[s.tone] || DOT.neutral}`}>
                  <Icon className="size-3.5" />
                </span>
                <p className="text-sm text-foreground">
                  {s.text_vi}
                  {s.tag_vi && <span className={`ml-2 inline-block rounded-full px-2 py-0.5 text-[11px] font-semibold ${TAG[s.tag_tone] || TAG.info}`}>{s.tag_vi}</span>}
                </p>
                {s.when_vi && <p className="text-[11px] text-muted">{s.when_vi}</p>}
                {s.code && onLoadCode && (
                  <button type="button" onClick={() => onLoadCode(s.code)} className="mt-1 inline-flex min-h-8 cursor-pointer items-center gap-1.5 rounded-full border border-border bg-surface px-3 text-xs font-semibold text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400">
                    <RotateCcw aria-hidden="true" className="size-3.5" /> Nạp lại code lần này
                  </button>
                )}
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
```

#### 3.7. `frontend/src/components/plain/ClassBrief.jsx`

```jsx
import React from 'react';

/** Bản tin lớp: vài câu nói như trợ giảng báo cáo. Câu chữ lấy nguyên văn từ backend (khóa `plain`). */
export default function ClassBrief({ plain }) {
  if (!plain) return null;
  return (
    <section aria-labelledby="class-brief" className="space-y-2 rounded-2xl border border-border bg-surface-raised p-4">
      <h5 id="class-brief" className="text-sm font-bold text-foreground">Bản tin lớp</h5>
      <p className="text-sm leading-relaxed text-foreground">{(plain.brief_vi || []).join(' ')}</p>
      {(plain.skills_vi || []).map((s) => <p key={s} className="text-sm text-foreground">{s}</p>)}
      {plain.few_data_vi && <p className="text-[11px] text-muted">{plain.few_data_vi}</p>}
    </section>
  );
}
```

#### 3.8. `frontend/src/components/plain/StudentGroups.jsx`

```jsx
import React from 'react';

const TONES = {
  check_in: { box: 'border-destructive-line bg-destructive-soft/40', title: 'text-destructive-strong', empty: 'Không có bạn nào.' },
  trying: { box: 'border-warning-line bg-warning-soft/40', title: 'text-warning-strong', empty: 'Không có bạn nào.' },
  doing_well: { box: 'border-success-line bg-success-soft/40', title: 'text-success-strong', empty: 'Chưa có bạn nào.' },
};

function Pile({ kind, title, items, onOpenStudent }) {
  const tone = TONES[kind];
  const withReason = kind !== 'doing_well';
  return (
    <div className={`rounded-2xl border p-3 ${tone.box}`}>
      <h6 className={`text-sm font-bold ${tone.title}`}>{title} · {items.length} bạn</h6>
      {items.length === 0 ? (
        <p className="mt-1.5 text-xs text-muted">{tone.empty}</p>
      ) : withReason ? (
        <ul className="mt-2 space-y-1">
          {items.map((p) => (
            <li key={p.username}>
              <button
                type="button"
                onClick={() => onOpenStudent && p.exercise_id && onOpenStudent(p)}
                className="w-full cursor-pointer rounded-xl px-2 py-1.5 text-left hover:bg-surface focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
              >
                <span className="block text-sm font-semibold text-foreground">{p.full_name}</span>
                <span className="block text-xs text-muted">{p.reason_vi}</span>
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <ul className="mt-2 flex flex-wrap gap-1.5">
          {items.map((p) => <li key={p.username} className="rounded-full bg-surface px-2.5 py-0.5 text-xs text-foreground">{p.full_name}</li>)}
        </ul>
      )}
    </div>
  );
}

/** Các bạn trong lớp chia 3 cột theo đèn giao thông, xếp A→Z. Bấm vào tên để xem câu chuyện của bạn đó ở bài liên quan. */
export default function StudentGroups({ plain, onOpenStudent }) {
  const g = plain?.groups;
  if (!g) return null;
  const t = plain.group_titles_vi || {};
  return (
    <section aria-labelledby="class-groups" className="space-y-3">
      <h5 id="class-groups" className="text-sm font-bold text-foreground">Các bạn trong lớp</h5>
      <div className="grid gap-3 md:grid-cols-3">
        <Pile kind="check_in" title={t.check_in} items={g.check_in || []} onOpenStudent={onOpenStudent} />
        <Pile kind="trying" title={t.trying} items={g.trying || []} onOpenStudent={onOpenStudent} />
        <Pile kind="doing_well" title={t.doing_well} items={g.doing_well || []} />
      </div>
      {(g.not_started || []).length > 0 && (
        <p className="text-xs text-muted">
          <strong className="text-foreground">{t.not_started} ({g.not_started.length}):</strong> {g.not_started.map((p) => p.full_name).join(', ')}
        </p>
      )}
    </section>
  );
}
```

#### 3.9. `frontend/src/components/plain/ExerciseProgressList.jsx`

```jsx
import React from 'react';

/** Bài tập của lớp: thanh tiến độ có ghi chữ ngay bên dưới, lỗi hay gặp nói bằng ví dụ. */
export default function ExerciseProgressList({ exercises, onOpenExercise }) {
  const items = exercises || [];
  if (!items.length) return null;
  return (
    <section aria-labelledby="class-exercises" className="space-y-3">
      <h5 id="class-exercises" className="text-sm font-bold text-foreground">Bài tập của lớp</h5>
      <ul className="space-y-2">
        {items.map((e) => {
          const pct = e.enrolled ? Math.round((e.done / e.enrolled) * 100) : 0;
          return (
            <li key={e.exercise_id} className="space-y-1.5 rounded-2xl border border-border bg-surface-raised p-3">
              <div className="flex items-start justify-between gap-3">
                <p className="min-w-0 break-words text-sm font-semibold text-foreground">
                  <span className="text-muted">Bài {e.number}.</span> {e.title}
                  {e.hardest && <span className="ml-2 inline-block rounded-full bg-warning-soft px-2 py-0.5 text-[11px] font-semibold text-warning-strong">Khó nhất</span>}
                </p>
                {onOpenExercise && (
                  <button type="button" onClick={() => onOpenExercise(e.exercise_id)} className="shrink-0 cursor-pointer text-xs font-semibold text-primary hover:underline">
                    Xem bài
                  </button>
                )}
              </div>
              <div role="progressbar" aria-label={e.done_vi} aria-valuemin={0} aria-valuemax={e.enrolled} aria-valuenow={e.done} className="h-2 overflow-hidden rounded-full bg-border">
                <div className="h-full rounded-full bg-success" style={{ width: `${pct}%` }} />
              </div>
              <p className="text-xs text-foreground">{e.done_vi}</p>
              {e.mistake_vi && <p className="text-xs text-muted">{e.mistake_vi}</p>}
              {e.time_vi && <p className="text-xs text-muted">{e.time_vi}</p>}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
```

#### 3.10. `frontend/src/components/plain/HowItWorks.jsx`

```jsx
import React from 'react';

/** Cách hệ thống chia nhóm, nói bằng lời (thu gọn mặc định). */
export default function HowItWorks({ items }) {
  if (!items?.length) return null;
  return (
    <details className="rounded-2xl border border-border px-4 py-3 text-xs text-muted">
      <summary className="cursor-pointer font-semibold text-foreground">Hệ thống nhận xét thế nào?</summary>
      <ul className="mt-2 list-disc space-y-1 pl-4 leading-relaxed">
        {items.map((s) => <li key={s}>{s}</li>)}
      </ul>
    </details>
  );
}
```

**Kiểm tra Bước 3:** `cd frontend; npm.cmd run test:ui-utils; npm.cmd run build; cd ..`. Test sẽ báo lỗi ở `StudentProfileModal.jsx` vì file cũ còn từ cấm; điều này **đúng như dự kiến** và sẽ hết sau Bước 4.1. Các test `share` và `path` phải đạt, và build phải thành công.

---

### Bước 4 — Màn sinh viên

#### 4.1. Viết lại `frontend/src/components/StudentProfileModal.jsx` (thay toàn bộ nội dung file)

```jsx
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, ChevronDown, RotateCcw, X } from 'lucide-react';
import { fetchStudentJourney } from '../services/api';
import { useAuth } from '../context/AuthContext';
import TodayCard from './plain/TodayCard';
import StorySteps from './plain/StorySteps';

/** Hành trình học (v5.9, lời thường): thẻ hôm nay, bài đang mở, các bài gần đây. Mọi câu nhận xét lấy từ backend. */

function RecentExercise({ item, classId, onOpenExercise }) {
  const [open, setOpen] = useState(false);
  const [state, setState] = useState({ loading: false, error: false, story: null });
  const toggle = () => {
    const next = !open;
    setOpen(next);
    if (next && !state.story && !state.loading) {
      setState({ loading: true, error: false, story: null });
      fetchStudentJourney(classId, item.exercise_id)
        .then((res) => setState({ loading: false, error: false, story: res.current?.story || null }))
        .catch(() => setState({ loading: false, error: true, story: null }));
    }
  };
  return (
    <li className="rounded-2xl border border-border bg-surface">
      <button
        type="button"
        aria-expanded={open}
        onClick={toggle}
        className="flex w-full cursor-pointer items-center justify-between gap-3 rounded-2xl p-3 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
      >
        <span className="min-w-0">
          <span className="block break-words text-sm font-semibold text-foreground">{item.title}</span>
          <span className="block text-xs text-muted">{item.story_vi}</span>
        </span>
        <ChevronDown aria-hidden="true" className={`size-4 shrink-0 text-muted transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="space-y-3 border-t border-border p-3">
          {state.loading && <p className="text-xs text-muted">Đang tải…</p>}
          {state.error && <p role="alert" className="text-xs text-destructive-strong">Chưa tải được bài này. Thử lại sau.</p>}
          {state.story && <StorySteps story={state.story} />}
          {onOpenExercise && (
            <button
              type="button"
              onClick={() => onOpenExercise(item.exercise_id)}
              className="inline-flex min-h-8 cursor-pointer items-center rounded-full border border-border px-3 text-xs font-semibold text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
            >
              Mở bài này
            </button>
          )}
        </div>
      )}
    </li>
  );
}

export default function StudentProfileModal({ isOpen, onClose, classId, currentExerciseId, onLoadCode }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [journey, setJourney] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const closeRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return undefined;
    let cancelled = false;
    setIsLoading(true);
    setLoadError(false);
    fetchStudentJourney(classId, currentExerciseId || '')
      .then((data) => { if (!cancelled) setJourney(data); })
      .catch((err) => {
        console.error('Lỗi khi tải Hành trình học:', err);
        if (!cancelled) { setJourney(null); setLoadError(true); }
      })
      .finally(() => { if (!cancelled) setIsLoading(false); });
    return () => { cancelled = true; };
  }, [isOpen, classId, currentExerciseId, reloadKey]);

  useEffect(() => {
    if (!isOpen) return undefined;
    closeRef.current?.focus();
    const onKey = (event) => { if (event.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  const openExercise = useCallback((exerciseId, pathClassId) => {
    const cid = classId || pathClassId;
    onClose();
    navigate(`/student/ide/${encodeURIComponent(exerciseId)}${cid ? `?classId=${encodeURIComponent(cid)}` : ''}`);
  }, [classId, navigate, onClose]);

  const loadCode = useCallback((code) => {
    if (onLoadCode) onLoadCode(code);
    onClose();
  }, [onLoadCode, onClose]);

  if (!isOpen) return null;

  const current = journey?.current;
  const others = (journey?.recent_exercises || []).filter((e) => e.exercise_id !== current?.exercise_id);
  const noActivity = journey && !current?.points?.length && others.length === 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-3 backdrop-blur-sm animate-fade-in sm:p-6" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div role="dialog" aria-modal="true" aria-labelledby="journey-title" className="flex max-h-[92vh] w-full max-w-3xl select-text flex-col overflow-hidden rounded-3xl border border-border bg-surface shadow-bento">
        <div className="flex shrink-0 items-center justify-between border-b border-border bg-surface-raised px-5 py-3.5 sm:px-6">
          <div className="min-w-0">
            <h2 id="journey-title" className="text-sm font-bold tracking-wide text-foreground sm:text-base">Hành trình học</h2>
            <p className="truncate text-[11px] text-muted">{user?.full_name || 'Sinh viên'}</p>
          </div>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            aria-label="Đóng Hành trình học"
            className="cursor-pointer rounded-xl bg-surface p-2 text-muted transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
          >
            <X aria-hidden="true" className="size-4" />
          </button>
        </div>

        <div className="flex-1 space-y-6 overflow-y-auto p-5 sm:p-6" aria-busy={isLoading}>
          {isLoading ? (
            <div role="status" className="space-y-2 py-16 text-center text-sm text-muted">
              <div className="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-emerald-500" />
              <p>Đang tải hành trình học…</p>
            </div>
          ) : journey ? (
            <>
              <TodayCard today={journey.today} onOpenExercise={openExercise} />

              {current?.points?.length > 0 && (
                <section aria-labelledby="journey-current" className="space-y-3 rounded-2xl border border-border bg-surface p-4">
                  <h3 id="journey-current" className="break-words text-sm font-bold text-foreground">Bài bạn đang mở: {current.title}</h3>
                  <StorySteps story={current.story} onLoadCode={loadCode} />
                </section>
              )}

              {noActivity ? (
                <p className="rounded-2xl border border-dashed border-border p-4 text-center text-sm text-muted">
                  Bạn chưa làm bài nào. Mở một bài và bấm “Chạy thử” để bắt đầu.
                </p>
              ) : others.length > 0 && (
                <section aria-labelledby="journey-recent" className="space-y-3">
                  <h3 id="journey-recent" className="text-sm font-bold text-foreground">Các bài gần đây</h3>
                  <ul className="space-y-2">
                    {others.map((item) => (
                      <RecentExercise key={item.exercise_id} item={item} classId={classId} onOpenExercise={openExercise} />
                    ))}
                  </ul>
                </section>
              )}
            </>
          ) : loadError ? (
            <div role="alert" className="space-y-3 rounded-2xl border border-destructive-line bg-destructive-soft px-4 py-8 text-center">
              <AlertCircle aria-hidden="true" className="mx-auto size-6 text-destructive-strong" />
              <p className="font-medium text-foreground">Không tải được Hành trình học.</p>
              <p className="text-sm text-muted">Có thể do mất kết nối tới máy chủ. Dữ liệu học tập của bạn không bị ảnh hưởng.</p>
              <button
                type="button"
                onClick={() => setReloadKey((k) => k + 1)}
                className="inline-flex min-h-9 cursor-pointer items-center gap-1.5 rounded-full border border-border bg-surface px-4 font-medium text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
              >
                <RotateCcw aria-hidden="true" className="size-3.5" /> Thử lại
              </button>
            </div>
          ) : null}
        </div>

        <div className="flex shrink-0 items-center justify-between border-t border-border bg-surface-raised px-5 py-3 text-xs text-muted sm:px-6">
          <span className="hidden sm:inline">Khoa Công nghệ thông tin - Đại học Kinh tế Quốc dân (NEU)</span>
          <button
            type="button"
            onClick={onClose}
            className="cursor-pointer rounded-full bg-surface px-4 py-1.5 font-medium text-foreground hover:bg-canvas focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
}
```

#### 4.2. Trang chủ sinh viên `frontend/src/pages/StudentPortalPage.jsx`

1. Dòng 1: đổi `import React, { useState, useEffect } from 'react';` thành `import React, { useCallback, useState, useEffect } from 'react';`
2. Trong danh sách import từ `'../services/api'`, thêm `fetchStudentJourney`.
3. Thêm import: `import TodayCard from '../components/plain/TodayCard';`
4. Trong thân component, ngay sau dòng `const navigate = useNavigate();`, thêm:
   ```jsx
   const [today, setToday] = useState({ loading: true, error: false, data: null });
   const loadToday = useCallback(() => {
     setToday((s) => ({ ...s, loading: true, error: false }));
     fetchStudentJourney()
       .then((res) => setToday({ loading: false, error: false, data: res.today || null }))
       .catch(() => setToday({ loading: false, error: true, data: null }));
   }, []);
   useEffect(() => { loadToday(); }, [loadToday]);
   const openExerciseFromToday = (exerciseId, classId) =>
     navigate(`/student/ide/${encodeURIComponent(exerciseId)}${classId ? `?classId=${encodeURIComponent(classId)}` : ''}`);
   ```
5. Thay **toàn bộ** khối `{/* Bento KPIs Grid */}` (thẻ `<div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-6">` chứa 4 `<Stat>`) bằng:
   ```jsx
   <div className="mt-6">
     {today.loading ? (
       <div aria-hidden="true" className="h-40 animate-pulse rounded-3xl bg-surface-raised" />
     ) : today.error ? (
       <p className="flex items-center gap-2 text-sm text-muted">
         Chưa tải được phần này.
         <button type="button" onClick={loadToday} className="cursor-pointer font-semibold text-primary hover:underline">Thử lại</button>
       </p>
     ) : (
       <TodayCard today={today.data} onOpenExercise={openExerciseFromToday} showGreeting={false} />
     )}
   </div>
   ```
   (Trang chủ đã có lời chào "Xin chào, …" nên tắt lời chào trong thẻ.)
6. Xóa dòng `const autonomyScore = profile?.analytics_metrics?.autonomy_score ?? 85;`.
7. Trong khối "Tiến độ học tập", đổi câu:
   ```jsx
   Bạn đã hoàn thành <strong className="text-foreground">{totalSolved} bài tập</strong> với độ tự làm thuật toán đạt <strong className="text-foreground">{autonomyScore}%</strong>.
   ```
   thành:
   ```jsx
   Bạn đã làm xong <strong className="text-foreground">{totalSolved} bài</strong> và có <strong className="text-foreground">{totalStars} sao</strong>.
   ```
8. Tìm trong file: không còn chỗ nào dùng `autonomyScore`. Nếu `Stat` và `totalClasses` không còn được dùng, xóa `Stat` khỏi import `../components/ui` và xóa dòng `const totalClasses = ...`.

#### 4.3. Màn chúc mừng sau khi nộp đạt `frontend/src/pages/StudentIDE.jsx`

1. Thêm `fetchStudentJourney` vào danh sách import từ `'../services/api'`.
2. Ngay dưới các dòng import, thêm hằng:
   ```jsx
   const STAR_MEANING = {
     3: 'Bạn tự làm, không cần gợi ý lớn.',
     2: 'Bạn có dùng gợi ý mức 2.',
     1: 'Bạn có dùng gợi ý mức 3.',
   };
   ```
3. Cạnh dòng `const [submissionSuccess, setSubmissionSuccess] = useState(null);`, thêm:
   ```jsx
   const [successMoment, setSuccessMoment] = useState(null);
   ```
4. Trong `handleSubmit`, ngay sau lời gọi `setSubmissionSuccess({ ... })` (trong nhánh `if (res.test_results?.all_passed)`), thêm:
   ```jsx
   setSuccessMoment(null);
   fetchStudentJourney(currentClass?.id || null, selectedExerciseId)
     .then((d) => setSuccessMoment(d?.today?.moments?.[0]?.text_vi || null))
     .catch(() => {});
   ```
5. Trong modal "Thông báo nộp bài thành công":
   - Đổi tiêu đề `Nộp bài thành công` thành `Đúng hết rồi!`.
   - Thay đoạn `<p id="submit-success-desc" ...>Hệ thống đã ghi nhận … lộ trình kỹ năng của bạn.</p>` bằng:
     ```jsx
     <p id="submit-success-desc" className="mt-2 text-sm leading-relaxed text-muted">
       Bạn làm đúng hết bài này và có <strong className="font-semibold text-foreground">{submissionSuccess.starsEarned} sao</strong>. {STAR_MEANING[submissionSuccess.starsEarned] || ''}
     </p>
     ```
   - Ngay sau khối `<div>` chứa tiêu đề và câu trên, thêm:
     ```jsx
     {successMoment && (
       <p className="rounded-2xl border border-success-line bg-success-soft px-3 py-2 text-sm text-success-strong">{successMoment}</p>
     )}
     ```
   - Giữ nguyên hàng sao và hai nút.

#### 4.4. Chữ nhỏ ở trang lớp và Header (chỉ đổi chữ, không đổi logic)

- `frontend/src/pages/StudentClassDetailPage.jsx`:
  - `{totalClassStars} điểm nỗ lực đã tích lũy` → `{totalClassStars} sao đã nhận`
  - trong Badge vàng: `{earnedStars} điểm nỗ lực` → `{earnedStars} sao`
- `frontend/src/components/Header.jsx`: đổi thuộc tính `title="Xem hành trình học: bạn đang ở đâu, tiến bộ thế nào, và nạp lại code đã nộp"` thành `title="Xem hành trình học của bạn"`.

**Kiểm tra Bước 4:** `cd frontend; npm.cmd run test:ui-utils; npm.cmd run build; cd ..`. Cả ba test đều đạt, kể cả test từ cấm, và build thành công.

---

### Bước 5 — Màn giảng viên

#### 5.1. `frontend/src/components/InstructorPedagogyPanels.jsx` — hàm `ClassInsightsPanel`

1. **Import:** thêm 4 dòng:
   ```jsx
   import ClassBrief from './plain/ClassBrief';
   import StudentGroups from './plain/StudentGroups';
   import ExerciseProgressList from './plain/ExerciseProgressList';
   import HowItWorks from './plain/HowItWorks';
   ```
   Nếu sau các bước dưới đây `formatCount` không còn được dùng trong file, xóa dòng `import { formatCount } from '../utils/share';`.
2. **Dòng mô tả dưới tiêu đề "Tình hình lớp":** thay biểu thức đang hiện `${data.days} ngày qua · … SV có hoạt động · … nên xem` bằng:
   ```jsx
   {data ? `${data.days} ngày gần nhất · bản tin tự động, cập nhật mỗi lần mở` : 'Đang tải…'}
   ```
   Xóa `{data && <DataStatusChip status={data.data_status} />}` ở **phần đầu panel**. Không xóa định nghĩa `DataStatusChip`, vì các chỗ khác vẫn dùng. Xóa dòng `const cardCount = ...`.
3. **Thay nhánh "chưa có dữ liệu":** thay
   ```jsx
   {data.data_status === 'no_data' ? (
     <div className="rounded-xl border border-dashed border-border p-6 text-center text-xs text-muted">
       <p className="font-semibold text-foreground">Chưa có lượt Nộp bài chính thức nào trong {data.days} ngày gần nhất.</p>
       <p className="mt-1 text-muted">Thử chọn khoảng thời gian dài hơn.</p>
     </div>
   ) : (
   ```
   bằng
   ```jsx
   {!data.plain || data.plain.active === 0 ? (
     <div className="rounded-xl border border-dashed border-border p-6 text-center text-sm text-muted">
       <p className="font-semibold text-foreground">Chưa có bạn nào chạy thử hay nộp bài trong {data.days} ngày qua.</p>
       <p className="mt-1">Thử chọn khoảng thời gian dài hơn.</p>
     </div>
   ) : (
   ```
4. **Chuyển khối cũ vào phần thu gọn:** ngay sau dấu `<>` của nhánh có dữ liệu, có 4 khối cũ theo thứ tự:
   - (a) đoạn `{data.data_status === 'limited' && (<p …>Dưới 3 sinh viên có hoạt động…</p>)}`;
   - (b) `{/* Tầng 1 — việc nên xem */}` cùng `<ActionCards … />`;
   - (c) `{/* Tầng 2 — ma trận lớp */}` cùng `<section aria-labelledby="class-matrix">…</section>`;
   - (d) `<section aria-labelledby="class-concepts">…</section>`.

   **Cắt** cả 4 khối (a)–(d), dán vào **đầu** thẻ `<div className="space-y-6 border-t border-border p-4">` nằm trong `<details>` (trước `<ClassOverviewSummary …/>`). Giữ nguyên nội dung từng khối.
5. **Chèn khối mới:** ở đúng chỗ vừa cắt (ngay sau `<>`), dán:
   ```jsx
   <ClassBrief plain={data.plain} />
   <StudentGroups
     plain={data.plain}
     onOpenStudent={(p) => openJourney({ username: p.username, full_name: p.full_name, exercise_id: p.exercise_id })}
   />
   <ExerciseProgressList exercises={data.plain.exercises} onOpenExercise={(exerciseId) => setExerciseTarget(exerciseId)} />
   <HowItWorks items={data.plain.how_it_works_vi} />
   ```
6. **Tên phần thu gọn:** đổi chữ trong `<summary>` từ `Dữ liệu chi tiết` thành `Xem số liệu đầy đủ`.
7. **Lời gọi `JourneyDrawer`** ở cuối panel: xóa dòng `LearnerModelDetail={StudentLearnerModelDetail}`. Hàm `StudentLearnerModelDetail` vẫn giữ, vì bảng sinh viên trong phần thu gọn còn dùng.

#### 5.2. `frontend/src/components/classview/ClassViewParts.jsx`

1. Thêm import: `import StorySteps from '../plain/StorySteps';`. Xóa `import AttemptStrip from '../journey/AttemptStrip';` nếu file không còn dùng.
2. **Thay toàn bộ hàm `JourneyDrawer`** bằng:
   ```jsx
   /** Ngăn câu chuyện của MỘT sinh viên ở MỘT bài (lời thường, không có mã nguồn). */
   export function JourneyDrawer({ classId, target, days, exerciseTitle, studentName, onClose }) {
     const [state, setState] = useState({ loading: true, error: '', data: null });
     const [attempt, setAttempt] = useState(0);
     useEffect(() => {
       let cancelled = false;
       setState({ loading: true, error: '', data: null });
       fetchStudentExerciseJourney(classId, target.username, target.exercise_id, days)
         .then((data) => { if (!cancelled) setState({ loading: false, error: '', data }); })
         .catch(() => { if (!cancelled) setState({ loading: false, error: 'Chưa tải được. Thử lại sau.', data: null }); });
       return () => { cancelled = true; };
     }, [classId, target.username, target.exercise_id, days, attempt]);
     const d = state.data;
     return (
       <Drawer title={`${studentName}: ${exerciseTitle}`} subtitle={`${days ? `${days} ngày gần nhất · ` : ''}không hiện code của sinh viên`} onClose={onClose}>
         {state.loading && <p role="status" className="text-muted">Đang tải…</p>}
         {state.error && (
           <div role="alert" className="space-y-2 rounded-xl border border-destructive-line bg-destructive-soft p-3 text-destructive-strong">
             <p>{state.error}</p>
             <button type="button" onClick={() => setAttempt((a) => a + 1)} className="cursor-pointer rounded-full border border-border bg-surface px-3 py-1 font-semibold text-foreground">Thử lại</button>
           </div>
         )}
         {d && (
           <>
             <StorySteps story={d.story} />
             {d.truncated && <p className="text-[11px] text-muted">Chỉ hiện {d.points.length} lần gần nhất trong tổng {d.total_points} lần.</p>}
           </>
         )}
       </Drawer>
     );
   }
   ```
3. **Hàm `ExerciseDrawer`:** giữ nguyên phần tính `mx`, `failing`, `err`, `ttp`, `groups`, `defs`, `values`. Ngay sau dòng tính `mx`, thêm:
   ```jsx
   const plainItem = (data.plain?.exercises || []).find((e) => e.exercise_id === exerciseId);
   ```
   Sau đó thay **toàn bộ khối `return (...)`** bằng:
   ```jsx
   return (
     <Drawer title={plainItem?.title || mx.title || exerciseId} subtitle={plainItem ? `Bài ${plainItem.number} trong lộ trình` : ''} onClose={onClose}>
       {plainItem && (
         <section className="space-y-1.5">
           <p className="text-sm text-foreground">{plainItem.done_vi}</p>
           {plainItem.mistake_vi && <p className="text-sm text-foreground">{plainItem.mistake_vi}</p>}
           {plainItem.time_vi && <p className="text-xs text-muted">{plainItem.time_vi}</p>}
         </section>
       )}
       <Link className="inline-flex min-h-9 items-center rounded-full border border-border bg-surface px-4 text-xs font-semibold text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer" to={`/instructor/exercises/${encodeURIComponent(exerciseId)}/edit`}>Mở đề bài để xem hoặc sửa</Link>
       <details className="rounded-xl border border-border">
         <summary className="cursor-pointer px-3 py-2 font-semibold text-foreground">Số liệu chi tiết của bài</summary>
         <div className="space-y-4 border-t border-border p-3">
           <section className="space-y-1.5">
             <h5 className="font-bold text-foreground">Test hay sai</h5>
             {!failing?.tests?.length ? <ChartEmpty>Chưa ghi nhận test sai nào có đặc trưng.</ChartEmpty> : (
               <ul className="space-y-1">
                 {failing.tests.map((t) => (
                   <li key={t.test_idx} className="rounded-lg border border-border p-2">
                     <span className="font-semibold text-foreground">Test #{t.test_idx}</span> “{t.description}”
                     <span className="text-muted"> — {t.attempts} lượt, {t.students} SV{t.format_attempts ? `, ${t.format_attempts} lượt chỉ sai định dạng` : ''}</span>
                   </li>
                 ))}
               </ul>
             )}
           </section>
           <section className="space-y-1.5">
             <h5 className="font-bold text-foreground">Loại lỗi (nộp + chạy thử)</h5>
             <StackedBarRows rows={err ? [{ key: exerciseId, label: 'Bài này', values }] : []} series={ERROR_SERIES} ariaLabel="Loại lỗi của bài" />
           </section>
           <section className="space-y-1.5">
             <h5 className="font-bold text-foreground">Thời gian tới khi đạt (trung vị)</h5>
             {ttp ? <p className="text-foreground"><span className="font-mono tabular-nums">{ttp.median_minutes}</span> phút (n={ttp.n}). Là khoảng giữa sự kiện đầu và lần nộp đạt đầu, không phải thời gian ngồi làm.</p> : <ChartEmpty>Chưa có SV nào đạt trong khoảng này.</ChartEmpty>}
           </section>
           <section className="space-y-1.5">
             <h5 className="font-bold text-foreground">Nhóm quá trình ở bài này</h5>
             <HBar
               ariaLabel="Số sinh viên theo nhóm quá trình ở bài này"
               rows={defs.map((d) => ({ key: d.key, label: d.label, value: groups[d.key] || 0, max: Math.max(1, mx.students_attempted || 1), text: formatShare(groups[d.key] || 0, mx.students_attempted || 0) }))}
             />
           </section>
         </div>
       </details>
     </Drawer>
   );
   ```
   Phần chữ kỹ thuật bên trong `<details>` được **giữ nguyên có chủ ý**: đó là số liệu đầy đủ dành cho người cần phân tích.

#### 5.3. `ClassesAttentionList` (cùng file `InstructorPedagogyPanels.jsx`) — chỉ đổi chữ

| Tìm | Thay bằng |
|---|---|
| `aria-label="Lớp cần chú ý"` | `aria-label="Các lớp cần xem tuần này"` |
| `Lớp cần chú ý (7 ngày gần nhất)` | `Các lớp cần xem tuần này` |
| `` {state.data ? `${state.data.needing_attention}/${state.data.total_classes} lớp có việc cần xem. ` : ''} `` và câu `Số việc theo quy ước vận hành chưa hiệu chuẩn, không phải điểm hay xếp hạng lớp.` | `` {state.data ? `${state.data.needing_attention} trong ${state.data.total_classes} lớp có việc nên xem. ` : ''}Nhận xét tự động, có thể chưa chính xác. `` |
| `{c.attention} SV cần chú ý · {c.issues} vấn đề chung` | `` {c.brief_vi || `${c.attention} bạn cần chú ý`} `` |
| `'Không có lớp nào cần xử lý ngay theo quy ước hiện tại.'` | `'Tuần này chưa có lớp nào cần xem ngay.'` |
| `{quiet.length} lớp khác chưa có việc cần xem hoặc chưa đủ dữ liệu (tìm theo mã để mở).` | `{quiet.length} lớp khác đang ổn hoặc chưa có hoạt động.` |

**Kiểm tra Bước 5:** `cd frontend; npm.cmd run test:theme; npm.cmd run test:ui-utils; npm.cmd run build; cd ..` đều đạt.

---

### Bước 6 — Kiểm chứng toàn bộ

1. `py -m compileall -q backend mcp_server pytutor_shared`
2. Test Python (mục 4, lệnh nhiều module, có `test_plain_language_v59`): tất cả `OK`.
3. Script và replay (mục 4): `test_mcp_server` 8/8, `test_backend_e2e` đạt. Hai replay phải ra **y nguyên** số liệu cũ: `evaluate_learner_model_policy.py` giữ 120/120 mức gợi ý, `evaluate_phase17_adaptive.py` 6/6. Lệch thì nghĩa là đã lỡ đụng vào logic mô hình; quay lại tìm và hoàn tác chỗ đó.
4. Frontend: `test:theme`, `test:ui-utils`, `build` đều đạt.
5. **Kiểm tra trên trình duyệt** (nếu người thực hiện không có trình duyệt tự động, ghi "chưa kiểm tra trình duyệt" vào báo cáo để người dùng tự làm):
   1. Xóa DB QA cũ, rồi tạo dữ liệu mẫu:
      ```powershell
      Remove-Item "$env:TEMP\pytutor_qa.db*", "$env:TEMP\pytutor_qa_kb.sqlite3" -Force -ErrorAction SilentlyContinue
      $env:PYTHONIOENCODING = "utf-8"; $env:PYTUTOR_DB_PATH = (Join-Path $env:TEMP "pytutor_qa.db"); py seed/seed_demo_class_v58.py
      Remove-Item Env:PYTUTOR_DB_PATH
      ```
   2. Mở hai server QA theo cấu hình `qa-backend` (cổng 8001) và `qa-frontend` (cổng 5174) trong `.claude/launch.json`. Mở `http://localhost:5174`.
   3. **Sinh viên** `v58_an` / mật khẩu `demo123`:
      - Trang chủ có thẻ "Hôm nay", chặng đường, nút "Làm tiếp"; không còn ô "Chỉ số tự lập".
      - Mở "Hành trình học" từ trang chủ và từ IDE; bấm mở một bài gần đây; bấm "Nạp lại code lần này".
      - Nộp đạt một bài: thấy "Đúng hết rồi!" và câu giải thích sao.
   4. **Giảng viên** `gv_tran` / `gv123`:
      - Danh sách lớp hiện dòng "… bạn nên hỏi thăm · bài khó: …".
      - Vào lớp `v58_demo`, tab "Góc nhìn sư phạm": thấy Bản tin lớp, Các bạn trong lớp, Bài tập của lớp.
      - Bấm tên một bạn ở "Nên hỏi thăm" thì ngăn bên phải hiện câu chuyện, không có code.
      - Bấm "Xem bài" thì ngăn bài hiện lời thường ở trên, số liệu ở trong phần thu gọn.
      - Mở "Xem số liệu đầy đủ" thì vẫn thấy ma trận và thẻ cũ.
   5. Ở cả hai vai trò: chế độ sáng và tối, màn rộng 375px (không cuộn ngang trang), dùng được bằng bàn phím (Tab, Enter, Esc), console không có lỗi đỏ.
   6. Đóng cả hai server sau khi xong.
6. **Tự rà chữ:** mở từng màn, đọc to các câu. Câu nào nghe như báo cáo khoa học thì ghi vào báo cáo cuối. **Không tự sửa câu ngoài plan.**

---

### Bước 7 — Tài liệu

1. `docs/VISUAL_DESIGN_RATIONALE.md`: thêm mục cuối "v5.9 — Lời thường", gồm:
   - vì sao v5.8 vẫn học thuật (5 ý ở mục 1);
   - quy tắc chữ và hình (mục 5);
   - bảng "Trước → sau" (mục 2);
   - bảng yếu tố game có/không (mục 1, quyết định 3);
   - nguyên tắc "chỉ đổi cách nói, không đổi cách tính";
   - chỗ giữ trung thực: mục "Hệ thống nhận xét thế nào?" và "Xem số liệu đầy đủ".

   Không thêm trích dẫn học thuật; chỉ nêu tên phương pháp.
2. `docs/PILOT_KIT.md`: thêm mục **"Thử 5 giây"**:
   - Chọn 3 người ngoài ngành và 2 sinh viên nhập môn.
   - Cho xem từng màn trong 5 giây rồi che lại.
   - Câu hỏi cho màn sinh viên: "Màn này nói gì? Bạn sẽ bấm gì tiếp?". Cho màn giảng viên: "Ai cần được hỏi thăm? Bài nào khó nhất?".
   - Ghi nguyên văn câu trả lời; "đạt" khi trả lời đúng ý chính.
   - Làm trên ảnh màn cũ (`docs/ui_audit/v58_before/` nếu có) và màn mới.
   - Chỉ ghi quan sát mô tả, không tuyên bố hiệu quả học tập.
3. `AI_HANDOFF_CONTEXT.md`: thêm mục `## 21. v5.9 — Lời thường (chưa commit)` gồm 5–7 dòng: module mới, khóa API mới (`today`, `story`, `story_vi`, `plain`, `brief_vi`, `check_in`), file giao diện mới, test mới, các phần v5.8 chuyển vào "Xem số liệu đầy đủ".
4. `PLAN.md`: thêm một dòng trạng thái v5.9 cạnh dòng v5.7/v5.8.
5. `CLAUDE.md`: thêm mục
   ```markdown
   ## 10. v5.9 (chưa commit) — Lời thường
   - Câu nhận xét cho SV/GV chỉ sinh ở `backend/plain_language.py` (hàm thuần, có `BANNED_WORDS`); giao diện hiển thị nguyên văn các trường `*_vi`. Màn chính: SV `TodayCard` (trang chủ + Hành trình học); GV "Bản tin lớp" + 3 nhóm bạn + bài tập của lớp; số liệu v5.8 nằm trong "Xem số liệu đầy đủ".
   - Test: `.\.claude\run_isolated.ps1 test_plain_language_v59`; frontend `npm.cmd run test:ui-utils` (gồm quét từ cấm ở `components/plain/` và `StudentProfileModal.jsx`).
   ```

---

## 7. Checklist cuối (đánh dấu từng dòng trong báo cáo)

- [ ] `py -m compileall` sạch.
- [ ] Mọi module Python ở mục 4 `OK`, gồm `test_plain_language_v59` (cả phần tích hợp).
- [ ] `test_mcp_server` 8/8, `test_backend_e2e` đạt; replay giữ nguyên (120/120, 6/6).
- [ ] `test:theme`, `test:ui-utils` (5 test `path` + test từ cấm + test `share`), `build` đều đạt.
- [ ] Không có thay đổi nào ở: logic sao, `compute_student_model`, `derive_learner_model`, `classify_learning_process`, guardrails, RAG, `/api/submit`.
- [ ] Không có khóa API cũ nào bị đổi hay xóa.
- [ ] Phản hồi cho giảng viên không chứa `code`.
- [ ] Màn sinh viên không có chữ "mắc kẹt", "xếp hạng", "tự làm".
- [ ] Không `git commit`, không đụng `pytutor.db`.
- [ ] Tài liệu ở Bước 7 đã cập nhật.
- [ ] Đã kiểm tra trình duyệt, hoặc đã ghi rõ là chưa.

---

## 8. Lỗi thường gặp

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| `test_thesis_upgrade` fail ở phần so khớp mã nguồn `compute_student_model` | Lỡ sửa `compute_student_model` trong `backend/database.py` hoặc `mcp_server/storage.py` | Hoàn tác phần đó. v5.9 chỉ thêm 2 khóa vào `get_student_journey_overview`. |
| `test_visual_views_v58` fail | Đã đổi khóa cũ hoặc câu của `backend/student_journey.py` | Không sửa file v5.8. Câu mới chỉ nằm trong `plain_language.py`. |
| `test_qa_authorization` fail 2 test khi chạy chung với module khác | Chạy nhiều module trên cùng một DB | Chạy bằng `run_isolated.ps1` (mỗi module một DB). |
| `PlainIntegrationTests` báo "skipped" | Chưa đặt `PYTUTOR_DB_PATH` | Chạy qua `run_isolated.ps1`. |
| Lỗi `KeyError: 'name'` hoặc lời chào luôn là "Chào bạn" | Token không có khóa `name` | Dùng `token_data.get("name")` (đã đúng trong plan); "Chào bạn" là kết quả dự phòng hợp lệ. |
| Test từ cấm của frontend báo `StudentProfileModal.jsx` | File cũ chưa được thay toàn bộ, hoặc comment mới chứa từ cấm | Thay toàn bộ file theo Bước 4.1; viết comment không dùng từ cấm. |
| Build báo không tìm thấy `./plain/...` | Sai đường dẫn import (`components/plain` so với `pages`) | Từ `pages/` dùng `../components/plain/...`; từ `components/` dùng `./plain/...`; từ `components/classview/` dùng `../plain/...`. |
| Màu `bg-success-soft` không hiện | Gõ sai tên token | Chỉ dùng token có trong `frontend/tailwind.config.js`: `success`, `warning`, `destructive`, `info` cùng các biến thể `-soft`, `-line`, `-strong`. |
| Câu mong đợi trong test lệch một dấu cách hay dấu chấm so với code | Chép sai | Sửa **code** cho khớp test. Test là đặc tả câu chữ đã được duyệt. |

---

## 9. Mẫu báo cáo cuối (người thực hiện điền và gửi lại)

```markdown
# Báo cáo v5.9 — Lời thường
## Đã làm
- Bước 0–7: (đánh dấu bước nào xong, bước nào chưa)
## Kết quả kiểm tra
- compileall: …
- Python (từng module): …
- Script/replay: test_mcp_server …, test_backend_e2e …, learner_model_policy …, phase17 …
- Frontend: test:theme …, test:ui-utils …, build …
- Trình duyệt: đã kiểm tra / chưa kiểm tra (lý do)
## Chỗ plan không khớp với mã thật
- (ghi nguyên văn chỗ không tìm thấy hoặc khác tên; đã xử lý thế nào)
## Câu nghe vẫn học thuật khi đọc to
- (màn hình, câu nguyên văn) — KHÔNG tự sửa, để người dùng quyết
## File đã thay đổi
- (liệt kê)
```
