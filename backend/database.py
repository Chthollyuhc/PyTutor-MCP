"""
Database module cho PyTutor sử dụng SQLite.
Quản lý:
1. exercises: Ngân hàng bài tập (được khởi tạo từ exercises_data.py nếu trống, cho phép Giảng viên CRUD)
2. submissions: Lịch sử nộp bài và learning events phục vụ Adaptive Tutoring & Student Model
3. users: Tài khoản người dùng (sinh viên & giảng viên)
"""
import sqlite3
import json
import logging
import os
from pathlib import Path
from typing import Optional, Any

from backend.passwords import hash_password
from pytutor_shared.learner_model import (  # noqa: F401  (re-export cho get_class_insights và test)
    PROCESS_GROUPS, PROCESS_GROUP_KEYS, PROCESS_HINT_ASSISTED_LEVEL, PROCESS_INDEPENDENT_MAX_SUBMITS,
    PROCESS_PROGRESS_WINDOW, PROCESS_RETRY_MIN_RUNS, PROCESS_STUCK_MIN_ATTEMPTS,
    classify_learning_process, derive_learner_model, build_journey_points, process_event_sort_key,
)

logger = logging.getLogger("pytutor.database")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("PYTUTOR_DB_PATH", PROJECT_ROOT / "pytutor.db")).expanduser().resolve()


def get_db_connection() -> sqlite3.Connection:
    """Tạo kết nối SQLite với Row factory, timeout chống nghẽn và bật WAL mode."""
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    """Khởi tạo cấu trúc các bảng và nạp dữ liệu mẫu ban đầu nếu trống."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Bảng bài tập (exercises)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            starter_code TEXT NOT NULL,
            test_cases TEXT NOT NULL,
            created_by TEXT DEFAULT 'system',
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            is_active INTEGER DEFAULT 1
        )
    """)

    # 2. Bảng lịch sử nộp bài (submissions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            exercise_id TEXT NOT NULL,
            code TEXT NOT NULL,
            hint_level INTEGER DEFAULT 1,
            passed_tests INTEGER DEFAULT 0,
            total_tests INTEGER DEFAULT 0,
            all_passed INTEGER DEFAULT 0,
            llm_source TEXT DEFAULT '',
            tutor_hint TEXT DEFAULT '',
            action_type TEXT NOT NULL DEFAULT 'submit',
            timestamp TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercise_shares (
            exercise_id TEXT NOT NULL,
            instructor_username TEXT NOT NULL,
            granted_by TEXT NOT NULL,
            granted_at TEXT DEFAULT (datetime('now', 'localtime')),
            PRIMARY KEY (exercise_id, instructor_username),
            FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
        )
    """)
    submission_columns = {row[1] for row in cursor.execute("PRAGMA table_info(submissions)").fetchall()}
    if "action_type" not in submission_columns:
        cursor.execute("ALTER TABLE submissions ADD COLUMN action_type TEXT NOT NULL DEFAULT 'submit'")

    # 3. Bảng người dùng (users)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # 4. Bảng đánh giá sao tự lực theo bài tập (user_exercise_stars)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_exercise_stars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            exercise_id TEXT NOT NULL,
            stars_earned INTEGER NOT NULL CHECK (stars_earned BETWEEN 1 AND 3),
            best_submission_id INTEGER,
            highest_clean_score INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime')),
            UNIQUE(username, exercise_id)
        )
    """)

    # 5. Bảng huy hiệu thành tích của học viên (user_achievements)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            badge_code TEXT NOT NULL,
            badge_title TEXT NOT NULL,
            badge_icon TEXT DEFAULT '🏆',
            description TEXT DEFAULT '',
            unlocked_at TEXT DEFAULT (datetime('now', 'localtime')),
            UNIQUE(username, badge_code)
        )
    """)

    # 6. Bảng lớp tín chỉ / lớp học phần chuẩn NEU (credit_classes)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credit_classes (
            id TEXT PRIMARY KEY,
            class_code TEXT NOT NULL UNIQUE,
            class_name TEXT NOT NULL,
            course_code TEXT DEFAULT 'CNTT1116',
            credits INTEGER DEFAULT 3,
            faculty TEXT DEFAULT 'Khoa Công nghệ thông tin - NEU',
            semester TEXT DEFAULT 'Học kỳ 1 (2026-2027)',
            enrollment_code TEXT DEFAULT 'NEU01',
            instructor_username TEXT NOT NULL DEFAULT 'gv_tran',
            instructor_name TEXT DEFAULT 'Nguyễn Văn A',
            description TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # Tương thích ngược: Bổ sung các cột mới nếu bảng credit_classes đã tồn tại từ Phase 12
    try:
        cursor.execute("PRAGMA table_info(credit_classes)")
        existing_cols = [row[1] for row in cursor.fetchall()]
        if "course_code" not in existing_cols:
            cursor.execute("ALTER TABLE credit_classes ADD COLUMN course_code TEXT DEFAULT 'CNTT1116'")
        if "credits" not in existing_cols:
            cursor.execute("ALTER TABLE credit_classes ADD COLUMN credits INTEGER DEFAULT 3")
        if "faculty" not in existing_cols:
            cursor.execute("ALTER TABLE credit_classes ADD COLUMN faculty TEXT DEFAULT 'Khoa Công nghệ thông tin - NEU'")
        if "enrollment_code" not in existing_cols:
            cursor.execute("ALTER TABLE credit_classes ADD COLUMN enrollment_code TEXT DEFAULT 'NEU01'")
        if "instructor_name" not in existing_cols:
            cursor.execute("ALTER TABLE credit_classes ADD COLUMN instructor_name TEXT DEFAULT 'Nguyễn Văn A'")
    except Exception as e:
        logger.warning(f"Lỗi kiểm tra/thêm cột mới cho credit_classes: {e}")

    # 7. Bảng sinh viên thuộc lớp tín chỉ (class_enrollments)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id TEXT NOT NULL,
            student_username TEXT NOT NULL,
            enrolled_at TEXT DEFAULT (datetime('now', 'localtime')),
            UNIQUE(class_id, student_username)
        )
    """)

    # 8. Bảng kỳ thi & đợt thực hành (exam_sessions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            class_id TEXT NOT NULL,
            session_type TEXT NOT NULL,
            exercise_ids TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 45,
            allow_ai_hints INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            created_by TEXT DEFAULT 'gv_tran',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # 9. Bảng liên kết Bài tập & Cây kỹ năng theo từng Lớp học phần (class_exercises)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id TEXT NOT NULL,
            exercise_id TEXT NOT NULL,
            module_name TEXT DEFAULT 'Chương 1: Cơ sở lập trình Python',
            order_idx INTEGER DEFAULT 1,
            prerequisite_id TEXT DEFAULT NULL,
            min_stars_required INTEGER DEFAULT 2,
            skill_tag TEXT DEFAULT 'Tư duy thuật toán',
            weight_point INTEGER DEFAULT 10,
            added_at TEXT DEFAULT (datetime('now', 'localtime')),
            UNIQUE(class_id, exercise_id)
        )
    """)

    # Phase 16: structured LLM telemetry, chat ownership, and learner feedback.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS llm_interactions (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            task_type TEXT NOT NULL,
            model_name TEXT NOT NULL DEFAULT '',
            latency_ms REAL NOT NULL DEFAULT 0,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            input_guard TEXT NOT NULL DEFAULT 'allowed',
            output_guard TEXT NOT NULL DEFAULT 'allowed',
            status TEXT NOT NULL DEFAULT 'success',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tutor_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating IN (-1, 1)),
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (interaction_id) REFERENCES llm_interactions(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS llm_interaction_sources (
            interaction_id TEXT NOT NULL,
            source TEXT NOT NULL,
            PRIMARY KEY (interaction_id, source),
            FOREIGN KEY (interaction_id) REFERENCES llm_interactions(id) ON DELETE CASCADE
        )
    """)
    # v5.4: lượt Chạy thử (không lưu mã nguồn) để giảng viên thấy quá trình thử–sửa; không tính vào chỉ số chính thức của sinh viên.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS practice_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            exercise_id TEXT NOT NULL,
            passed_tests INTEGER NOT NULL DEFAULT 0,
            total_tests INTEGER NOT NULL DEFAULT 0,
            all_passed INTEGER NOT NULL DEFAULT 0,
            timestamp TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_practice_runs_user_ex ON practice_runs(username, exercise_id)")
    # v5.6: đặc trưng nhỏ gọn của mỗi lượt (loại lỗi, cờ AST) phục vụ mô hình người học v3. Chỉ thêm, không backfill.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempt_features (
            submission_id INTEGER PRIMARY KEY,
            error_class TEXT NOT NULL,
            status_counts TEXT NOT NULL DEFAULT '{}',
            ast_flags TEXT NOT NULL DEFAULT '{}',
            feature_version TEXT NOT NULL DEFAULT '1',
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
        )
    """)
    # v5.7: bổ sung đặc trưng chẩn đoán (test sai, sai định dạng). Chỉ ADD COLUMN, không backfill.
    for _tbl, _cols in (
        ("attempt_features", (("failed_tests", "TEXT DEFAULT '[]'"), ("format_mismatch_tests", "TEXT DEFAULT '[]'"))),
        ("practice_runs", (("error_class", "TEXT DEFAULT NULL"), ("failed_tests", "TEXT DEFAULT '[]'"),
                           ("format_mismatch_tests", "TEXT DEFAULT '[]'"), ("feature_version", "TEXT DEFAULT NULL"))),
    ):
        _existing = {row[1] for row in cursor.execute(f"PRAGMA table_info({_tbl})").fetchall()}
        for _name, _decl in _cols:
            if _name not in _existing:
                cursor.execute(f"ALTER TABLE {_tbl} ADD COLUMN {_name} {_decl}")
    # v5.4 (C): tài liệu giảng viên tải lên cho Gia sư AI, gắn theo lớp. Chỉ lưu văn bản đã trích, không lưu tệp gốc.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kb_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id TEXT NOT NULL,
            title TEXT NOT NULL,
            filename TEXT NOT NULL,
            format TEXT NOT NULL,
            content_text TEXT NOT NULL,
            provenance TEXT NOT NULL,
            license_type TEXT NOT NULL,
            uploaded_by TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            char_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (class_id) REFERENCES credit_classes(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_kb_documents_class ON kb_documents(class_id, is_active)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_llm_interactions_user_time ON llm_interactions(username, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_llm_interactions_task_time ON llm_interactions(task_type, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_credit_classes_owner ON credit_classes(instructor_username)")

    # Bảng đơn vị kiến thức (knowledge_components) cho phép giảng viên mở rộng động
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_components (
            kc TEXT PRIMARY KEY,
            label_vi TEXT NOT NULL,
            keywords TEXT NOT NULL,
            created_by TEXT DEFAULT 'system',
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            is_active INTEGER DEFAULT 1
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM knowledge_components")
    if cursor.fetchone()[0] == 0:
        from pytutor_shared.learner_model import KC_DEFINITIONS
        for d in KC_DEFINITIONS:
            cursor.execute("""
                INSERT INTO knowledge_components (kc, label_vi, keywords, created_by, is_active)
                VALUES (?, ?, ?, 'system', 1)
            """, (d["kc"], d["label_vi"], json.dumps(d.get("keywords", []), ensure_ascii=False)))

    conn.commit()

    # Nạp/Cập nhật người dùng chuẩn Đại học Kinh tế Quốc dân (NEU)
    users_seed = [
        ("student", "student123", "student", "Trần Minh Khánh - SV K65 CNTT (MSV: 11236131)"),
        ("gv_tran", "gv123", "instructor", "Nguyễn Văn A (Giảng viên Khoa Công nghệ thông tin - NEU)"),
        ("gv_tuan", "gv123", "instructor", "Trần Văn B (Giảng viên Khoa Công nghệ thông tin - NEU)")
    ]
    for u_name, u_pass, u_role, u_fullname in users_seed:
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (u_name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                (u_name, hash_password(u_pass), u_role, u_fullname)
            )
        else:
            cursor.execute(
                "UPDATE users SET full_name = ?, role = ? WHERE username = ?",
                (u_fullname, u_role, u_name)
            )
    conn.commit()

    # Nạp 5 bài tập mẫu ban đầu từ seed/exercises_seed.json (file dữ liệu, không import mcp_server) nếu bảng exercises trống
    cursor.execute("SELECT COUNT(*) FROM exercises")
    if cursor.fetchone()[0] == 0:
        try:
            seed_path = Path(__file__).resolve().parent.parent / "seed" / "exercises_seed.json"
            seed_exercises = json.loads(seed_path.read_text(encoding="utf-8"))
            for ex in seed_exercises:
                cursor.execute("""
                    INSERT INTO exercises (
                        id, title, difficulty, category, description, starter_code, test_cases, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ex["id"],
                    ex["title"],
                    ex["difficulty"],
                    ex["category"],
                    ex["description"],
                    ex["starter_code"],
                    json.dumps(ex["test_cases"], ensure_ascii=False),
                    "system"
                ))
            conn.commit()
            logger.info("Đã seed thành công 5 bài tập mẫu vào SQLite.")
        except Exception as e:
            logger.error(f"Lỗi khi seed bài tập mẫu: {e}")

    # Xoá các môn học mẫu cũ để thay thế bằng danh mục môn học thực tế của NEU LMS
    old_class_ids = ['cls_it1110_01', 'cls_it1110_02', 'cls_neu_cntt1116_01', 'cls_neu_cntt1116_02', 'cls_neu_cntt1142_01']
    for old_id in old_class_ids:
        cursor.execute("DELETE FROM credit_classes WHERE id = ?", (old_id,))
        cursor.execute("DELETE FROM class_exercises WHERE class_id = ?", (old_id,))
        cursor.execute("DELETE FROM class_enrollments WHERE class_id = ?", (old_id,))
        cursor.execute("DELETE FROM exam_sessions WHERE class_id = ?", (old_id,))
    cursor.execute("DELETE FROM credit_classes WHERE id LIKE 'cls_it1110%'")
    cursor.execute("DELETE FROM class_exercises WHERE class_id LIKE 'cls_it1110%'")
    cursor.execute("DELETE FROM class_enrollments WHERE class_id LIKE 'cls_it1110%'")
    cursor.execute("DELETE FROM exam_sessions WHERE class_id LIKE 'cls_it1110%'")
    conn.commit()

    # Nạp/Cập nhật 24 Lớp học phần chuẩn Đại học Kinh tế Quốc dân (NEU) từ LMS
    neu_classes = [
        (
            "cls_neu_cntt1128_02",
            "CNTT1128(223)_02",
            "Cơ sở lập trình",
            "CNTT1128",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-23-24-BMCNTT",
            "NEU-CSLP",
            "gv_tran",
            "Nguyễn Văn A",
            "Học phần Cơ sở lập trình Python cơ bản - Khoa Công nghệ thông tin NEU"
        ),
        (
            "cls_neu_cntt1187_01",
            "CNTT1187(225)_01",
            "Lập trình phân tích dữ liệu",
            "CNTT1187",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK03-25-26-KCNTT",
            "NEU-PTDL",
            "gv_tuan",
            "Trần Văn B",
            "Học phần lập trình phân tích dữ liệu và tiền xử lý số liệu với Python"
        ),
        (
            "cls_neu_cntt1131_04",
            "CNTT1131(124)_04",
            "Lập trình hướng đối tượng",
            "CNTT1131",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK01-24-25-BMCNTT",
            "NEU-HDDT",
            "gv_tran",
            "Nguyễn Văn A",
            "Phương pháp lập trình hướng đối tượng nâng cao, cấu trúc lớp và kế thừa"
        ),
        (
            "cls_neu_cntt1152_01",
            "CNTT1152(125)_01",
            "Hệ quản trị cơ sở dữ liệu",
            "CNTT1152",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-25-26-KCNTT",
            "NEU-HQTCSDL",
            "gv_tran",
            "Nguyễn Văn A",
            "Thiết kế, tối ưu hóa truy vấn và quản trị cơ sở dữ liệu quan hệ"
        ),
        (
            "cls_neu_cntt1167_01",
            "CNTT1167(225)_01",
            "Điện toán đám mây",
            "CNTT1167",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-25-26-KCNTT",
            "NEU-CLOUD",
            "gv_tran",
            "Nguyễn Văn A",
            "Kiến trúc hạ tầng đám mây, dịch vụ phân tán và container hóa"
        ),
        (
            "cls_neu_cntt1117_02",
            "CNTT1117(125)_02",
            "Phân tích và thiết kế hệ thống",
            "CNTT1117",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-25-26-KCNTT",
            "NEU-PTTKHT",
            "gv_tuan",
            "Trần Văn B",
            "Quy trình phân tích nghiệp vụ, mô hình hóa UML và thiết kế hệ thống phần mềm"
        ),
        (
            "cls_neu_cntt1121_01",
            "CNTT1121(225)_01",
            "Quản trị mạng",
            "CNTT1121",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-25-26-KCNTT",
            "NEU-QTM",
            "gv_tuan",
            "Trần Văn B",
            "Cấu hình định tuyến, chuyển mạch và bảo mật hệ thống mạng doanh nghiệp"
        ),
        (
            "cls_neu_cntt1154_01",
            "CNTT1154(225)_01",
            "Mạng kết nối vạn vật",
            "CNTT1154",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-25-26-KCNTT",
            "NEU-IOT",
            "gv_tran",
            "Nguyễn Văn A",
            "Giao thức truyền thông IoT, cảm biến thông minh và xử lý dữ liệu biên"
        ),
        (
            "cls_neu_tikt1130_04",
            "TIKT1130(124)_04",
            "Cơ sở dữ liệu",
            "TIKT1130",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK01-24-25-BMTHKT",
            "NEU-CSDL",
            "gv_tran",
            "Nguyễn Văn A",
            "Mô hình dữ liệu quan hệ, đại số quan hệ và chuẩn hóa dữ liệu"
        ),
        (
            "cls_neu_cntt1114_01",
            "CNTT1114(224)_01",
            "Mạng máy tính và truyền số liệu",
            "CNTT1114",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-24-25-BMCNTT",
            "NEU-MMT",
            "gv_tuan",
            "Trần Văn B",
            "Mô hình OSI/TCP-IP, truyền số liệu và giao thức mạng cơ sở"
        ),
        (
            "cls_neu_tiht1101_02",
            "TIHT1101(124)_02",
            "Cấu trúc dữ liệu và giải thuật",
            "TIHT1101",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK01-24-25-BMHTTTQL",
            "NEU-CTDL",
            "gv_tran",
            "Nguyễn Văn A",
            "Cấu trúc dữ liệu tuyến tính, cây, đồ thị và thuật toán tìm kiếm sắp xếp"
        ),
        (
            "cls_neu_tiht1123_02",
            "TIHT1123(224)_02",
            "Ứng dụng trí tuệ nhân tạo trong kinh doanh và quản lý",
            "TIHT1123",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-24-25-BMHTTTQL",
            "NEU-AI",
            "gv_tuan",
            "Trần Văn B",
            "Mô hình học máy, phân loại dự báo và trợ lý thông minh trong doanh nghiệp"
        ),
        (
            "cls_neu_cntt1107_01",
            "CNTT1107(224)_01",
            "Hệ điều hành",
            "CNTT1107",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-24-25-BMCNTT",
            "NEU-HDH",
            "gv_tran",
            "Nguyễn Văn A",
            "Quản lý tiến trình, bộ nhớ, đồng bộ hóa và hệ thống tập tin"
        ),
        (
            "cls_neu_cntt1165_03",
            "CNTT1165(224)_03",
            "Thiết kế WEB",
            "CNTT1165",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-24-25-BMCNTT",
            "NEU-WEB",
            "gv_tuan",
            "Trần Văn B",
            "Phát triển ứng dụng Web Frontend hiện đại với HTML5, CSS3 và JavaScript"
        ),
        (
            "cls_neu_cntt1112_02",
            "CNTT1112(224)_02",
            "Kiến trúc máy tính",
            "CNTT1112",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-24-25-BMCNTT",
            "NEU-KTMT",
            "gv_tran",
            "Nguyễn Văn A",
            "Tập lệnh máy tính, pipeline xử lý CPU và phân cấp bộ nhớ cache"
        ),
        (
            "cls_neu_cntt1153_02",
            "CNTT1153(125)_02",
            "Lập trình Java",
            "CNTT1153",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK01-25-26-KCNTT",
            "NEU-JAVA",
            "gv_tuan",
            "Trần Văn B",
            "Ngôn ngữ Java, hướng đối tượng và lập trình ứng dụng doanh nghiệp"
        ),
        (
            "cls_neu_cntt1186_02",
            "CNTT1186(125)_02",
            "Các công nghệ hiện đại trong công nghệ thông tin",
            "CNTT1186",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK01-25-26-KCNTT",
            "NEU-CNHD",
            "gv_tuan",
            "Trần Văn B",
            "Công nghệ Microservices, DevOps, AI Agent và điện toán phân tán"
        ),
        (
            "cls_neu_cntt1172_01",
            "CNTT1172(325)_01",
            "Đề án - Công nghệ thông tin",
            "CNTT1172",
            4,
            "Khoa Công nghệ thông tin - NEU",
            "Năm học: 2025-2026",
            "NEU-DEAN",
            "gv_tran",
            "Nguyễn Văn A",
            "Nghiên cứu ứng dụng và triển khai hệ thống phần mềm chuyên ngành CNTT"
        ),
        (
            "cls_neu_cntt1116_02",
            "CNTT1116(123)_02",
            "Nhập môn Công nghệ thông tin",
            "CNTT1116",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK01-23-24-BMCNTT",
            "NEU-NMCNTT",
            "gv_tran",
            "Nguyễn Văn A",
            "Tổng quan ngành CNTT, tư duy giải quyết vấn đề và nền tảng số"
        ),
        (
            "cls_neu_tocb1107_02",
            "TOCB1107(123)_02",
            "Toán rời rạc",
            "TOCB1107",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK01-23-24-BMTCB",
            "NEU-TORR",
            "gv_tran",
            "Nguyễn Văn A",
            "Logic mệnh đề, tập hợp, quan hệ và lý thuyết đồ thị trong khoa học máy tính"
        ),
        (
            "cls_neu_tikt1129_01",
            "TIKT1129(125)_01",
            "Hệ thống thương mại điện tử",
            "TIKT1129",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK01-25-26-BMTHKT",
            "NEU-TMDT",
            "gv_tuan",
            "Trần Văn B",
            "Kiến trúc sàn thương mại điện tử, cổng thanh toán và trải nghiệm số"
        ),
        (
            "cls_neu_tiht1122_02",
            "TIHT1122(224)_02",
            "Quản trị tri thức",
            "TIHT1122",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-24-25-BMHTTTQL",
            "NEU-QTTT",
            "gv_tuan",
            "Trần Văn B",
            "Thu thập, biểu diễn tri thức và xây dựng hệ chuyên gia quản trị doanh nghiệp"
        ),
        (
            "cls_neu_cntt1182_01",
            "CNTT1182(223)_01",
            "Phương pháp tính",
            "CNTT1182",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK02-23-24-BMCNTT",
            "NEU-PPT",
            "gv_tran",
            "Nguyễn Văn A",
            "Giải tích số, giải gần đúng phương trình phi tuyến và nội suy dữ liệu"
        ),
        (
            "cls_neu_cntt1113_01",
            "CNTT1113(124)_01",
            "Kỹ thuật số",
            "CNTT1113",
            3,
            "Khoa Công nghệ thông tin - NEU",
            "HK01-24-25-BMCNTT",
            "NEU-KTS",
            "gv_tran",
            "Nguyễn Văn A",
            "Đại số Boole, mạch logic tổ hợp và mạch tuần tự"
        )
    ]
    for c_id, c_code, c_name, cr_code, crs, fac, sem, en_code, inst_user, inst_name, desc in neu_classes:
        cursor.execute("SELECT COUNT(*) FROM credit_classes WHERE id = ?", (c_id,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO credit_classes (
                    id, class_code, class_name, course_code, credits, faculty, semester,
                    enrollment_code, instructor_username, instructor_name, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (c_id, c_code, c_name, cr_code, crs, fac, sem, en_code, inst_user, inst_name, desc))
        else:
            cursor.execute("""
                UPDATE credit_classes SET
                    class_code = ?, class_name = ?, course_code = ?, credits = ?, faculty = ?,
                    semester = ?, enrollment_code = ?, instructor_username = ?, instructor_name = ?, description = ?
                WHERE id = ?
            """, (c_code, c_name, cr_code, crs, fac, sem, en_code, inst_user, inst_name, desc, c_id))
    conn.commit()

    # Nạp cấu hình Bài tập & Cây kỹ năng riêng cho các Lớp học phần lập trình trọng tâm
    # 1. Lớp cls_neu_cntt1128_02 (Cơ sở lập trình: 5 bài tập chuẩn phân tầng)
    curriculum_01 = [
        ("cls_neu_cntt1128_02", "ex_01_sum_1_to_n", "Chương 1: Biến, Nhập xuất & Vòng lặp cơ bản", 1, None, 2, "Vòng lặp For & Biến tích lũy", 10),
        ("cls_neu_cntt1128_02", "ex_03_factorial", "Chương 2: Phép nhân tích lũy & Đệ quy cơ sở", 2, "ex_01_sum_1_to_n", 2, "Tích lũy nhân & Trường hợp biên 0!", 10),
        ("cls_neu_cntt1128_02", "ex_02_prime_check", "Chương 3: Cấu trúc rẽ nhánh & Tối ưu thuật toán", 3, "ex_01_sum_1_to_n", 2, "Kiểm tra điều kiện biên & Cờ hiệu", 10),
        ("cls_neu_cntt1128_02", "ex_04_reverse_string", "Chương 4: Xử lý Chuỗi & Kỹ thuật Slicing", 4, "ex_03_factorial", 2, "String Indexing & Slicing", 10),
        ("cls_neu_cntt1128_02", "ex_05_count_vowels", "Chương 4: Duyệt Chuỗi & Tập hợp", 5, "ex_04_reverse_string", 3, "Chuẩn hóa chuỗi & Toán tử tập hợp", 10)
    ]
    for c_id, e_id, mod, ord_idx, prereq, min_stars, stag, weight in curriculum_01:
        cursor.execute("SELECT COUNT(*) FROM class_exercises WHERE class_id = ? AND exercise_id = ?", (c_id, e_id))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO class_exercises (
                    class_id, exercise_id, module_name, order_idx, prerequisite_id, min_stars_required, skill_tag, weight_point
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (c_id, e_id, mod, ord_idx, prereq, min_stars, stag, weight))

    # 2. Lớp cls_neu_cntt1187_01 (Lập trình phân tích dữ liệu: 3 bài tập số liệu & chuỗi)
    curriculum_02 = [
        ("cls_neu_cntt1187_01", "ex_01_sum_1_to_n", "Chương 1: Xử lý chuỗi số liệu", 1, None, 2, "Tính toán dữ liệu cơ bản", 10),
        ("cls_neu_cntt1187_01", "ex_04_reverse_string", "Chương 2: Tiền xử lý chuỗi văn bản", 2, "ex_01_sum_1_to_n", 2, "String Manipulation", 10),
        ("cls_neu_cntt1187_01", "ex_05_count_vowels", "Chương 3: Khai phá thuộc tính văn bản", 3, "ex_04_reverse_string", 2, "Text Analytics", 10)
    ]
    for c_id, e_id, mod, ord_idx, prereq, min_stars, stag, weight in curriculum_02:
        cursor.execute("SELECT COUNT(*) FROM class_exercises WHERE class_id = ? AND exercise_id = ?", (c_id, e_id))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO class_exercises (
                    class_id, exercise_id, module_name, order_idx, prerequisite_id, min_stars_required, skill_tag, weight_point
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (c_id, e_id, mod, ord_idx, prereq, min_stars, stag, weight))

    # 3. Lớp cls_neu_cntt1131_04 (Lập trình hướng đối tượng: 3 bài tập cấu trúc)
    curriculum_03 = [
        ("cls_neu_cntt1131_04", "ex_01_sum_1_to_n", "Chương 1: Cơ sở thuật toán & Tối ưu", 1, None, 2, "Vòng lặp & Tối ưu biến", 10),
        ("cls_neu_cntt1131_04", "ex_02_prime_check", "Chương 2: Cấu trúc điều kiện & Số học", 2, "ex_01_sum_1_to_n", 2, "Số học & Điều kiện biên", 10),
        ("cls_neu_cntt1131_04", "ex_03_factorial", "Chương 3: Phương thức & Đệ quy", 3, "ex_02_prime_check", 3, "Đệ quy & Hàm chuẩn", 10)
    ]
    for c_id, e_id, mod, ord_idx, prereq, min_stars, stag, weight in curriculum_03:
        cursor.execute("SELECT COUNT(*) FROM class_exercises WHERE class_id = ? AND exercise_id = ?", (c_id, e_id))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO class_exercises (
                    class_id, exercise_id, module_name, order_idx, prerequisite_id, min_stars_required, skill_tag, weight_point
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (c_id, e_id, mod, ord_idx, prereq, min_stars, stag, weight))
    conn.commit()

    # Ghi danh mặc định cho sinh viên:
    # student học 5 lớp tiêu biểu của K65 CNTT
    enrollments_seed = [
        ("cls_neu_cntt1128_02", "student"),
        ("cls_neu_cntt1187_01", "student"),
        ("cls_neu_cntt1131_04", "student"),
        ("cls_neu_cntt1152_01", "student"),
        ("cls_neu_cntt1167_01", "student")
    ]
    for c_id, s_name in enrollments_seed:
        cursor.execute("SELECT COUNT(*) FROM class_enrollments WHERE class_id = ? AND student_username = ?", (c_id, s_name))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT OR IGNORE INTO class_enrollments (class_id, student_username)
                VALUES (?, ?)
            """, (c_id, s_name))
    conn.commit()

    # Nạp Đợt thực hành và Kỳ thi mẫu cho lớp cls_neu_cntt1128_02
    cursor.execute("SELECT COUNT(*) FROM exam_sessions WHERE class_id = 'cls_neu_cntt1128_02'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT OR IGNORE INTO exam_sessions (
                id, title, class_id, session_type, exercise_ids, duration_minutes, allow_ai_hints, is_active, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "sess_neu_practice_01",
            "Đợt Thực hành Tuần 1: Làm quen Vòng lặp & Nhập xuất",
            "cls_neu_cntt1128_02",
            "PRACTICE",
            json.dumps(["ex_01_sum_1_to_n", "ex_02_prime_check", "ex_03_factorial"], ensure_ascii=False),
            90,
            1,
            1,
            "gv_tran"
        ))
        cursor.execute("""
            INSERT OR IGNORE INTO exam_sessions (
                id, title, class_id, session_type, exercise_ids, duration_minutes, allow_ai_hints, is_active, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "sess_neu_exam_midterm",
            "Kỳ thi Giữa kỳ Học phần Python (Chế độ Thi)",
            "cls_neu_cntt1128_02",
            "EXAM",
            json.dumps(["ex_02_prime_check", "ex_04_reverse_string"], ensure_ascii=False),
            45,
            0,
            1,
            "gv_tran"
        ))
        conn.commit()

    conn.close()


# ==============================================================================
# HÀM TRUY VẤN VÀ THAO TÁC BÀI TẬP (EXERCISES)
# ==============================================================================

def get_all_exercises(include_inactive: bool = False, instructor_username: Optional[str] = None) -> list[dict]:
    """Lấy danh sách tóm tắt tất cả bài tập."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """SELECT e.id, e.title, e.difficulty, e.category, e.test_cases, e.is_active, e.created_by,
                      owner.full_name AS created_by_name
               FROM exercises e LEFT JOIN users owner ON owner.username=e.created_by"""
    params: list[Any] = []
    if instructor_username:
        query += " LEFT JOIN exercise_shares sh ON sh.exercise_id=e.id AND sh.instructor_username=?"
        params.append(instructor_username)
        query += " WHERE (e.created_by IN ('system','seed','') OR e.created_by=? OR sh.instructor_username IS NOT NULL)"
        params.append(instructor_username)
        if not include_inactive:
            query += " AND e.is_active=1"
    elif not include_inactive:
        query += " WHERE e.is_active=1"
    query += " ORDER BY e.id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        try:
            tc_list = json.loads(r["test_cases"])
            tc_count = len(tc_list)
        except Exception:
            tc_count = 0

        item = {
            "id": r["id"],
            "title": r["title"],
            "difficulty": r["difficulty"],
            "category": r["category"],
            "test_cases_count": tc_count,
            "created_by": r["created_by"] or "system",
            "created_by_name": r["created_by_name"] or ("Hệ thống" if (r["created_by"] or "system") in {"system", "seed", ""} else r["created_by"]),
            "can_manage": bool(instructor_username and r["created_by"] == instructor_username),
        }
        if include_inactive:
            item["is_active"] = bool(r["is_active"])
        result.append(item)
    return result


def get_exercise_by_id(exercise_id: str) -> Optional[dict]:
    """Lấy thông tin chi tiết của bài tập bao gồm test cases parsed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, difficulty, category, description, starter_code, test_cases, is_active, created_by FROM exercises WHERE id = ?",
        (exercise_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    try:
        test_cases = json.loads(row["test_cases"])
    except Exception:
        test_cases = []

    return {
        "id": row["id"],
        "title": row["title"],
        "difficulty": row["difficulty"],
        "category": row["category"],
        "description": row["description"],
        "starter_code": row["starter_code"],
        "test_cases": test_cases,
        "is_active": bool(row["is_active"]),
        "created_by": row["created_by"] or "system",
    }


def get_exercise_owner(exercise_id: str) -> Optional[str]:
    conn = get_db_connection()
    row = conn.execute("SELECT created_by FROM exercises WHERE id=?", (exercise_id,)).fetchone()
    conn.close()
    return (row["created_by"] or "system") if row else None


def instructor_can_use_exercise(exercise_id: str, instructor_username: str) -> bool:
    conn = get_db_connection()
    row = conn.execute("""SELECT 1 FROM exercises e LEFT JOIN exercise_shares sh
        ON sh.exercise_id=e.id AND sh.instructor_username=? WHERE e.id=?
        AND (e.created_by IN ('system','seed','') OR e.created_by=? OR sh.instructor_username IS NOT NULL)""",
        (instructor_username, exercise_id, instructor_username)).fetchone()
    conn.close()
    return bool(row)


def grant_exercise_share(exercise_id: str, instructor_username: str, granted_by: str) -> bool:
    conn = get_db_connection()
    owner = conn.execute("SELECT created_by FROM exercises WHERE id=?", (exercise_id,)).fetchone()
    recipient = conn.execute("SELECT role FROM users WHERE username=?", (instructor_username,)).fetchone()
    if not owner or owner["created_by"] != granted_by or not recipient or recipient["role"] != "instructor":
        conn.close()
        return False
    conn.execute("INSERT OR IGNORE INTO exercise_shares(exercise_id,instructor_username,granted_by) VALUES(?,?,?)",
                 (exercise_id, instructor_username, granted_by))
    conn.commit(); conn.close()
    return True


def revoke_exercise_share(exercise_id: str, instructor_username: str, granted_by: str) -> bool:
    conn = get_db_connection()
    owner = conn.execute("SELECT created_by FROM exercises WHERE id=?", (exercise_id,)).fetchone()
    if not owner or owner["created_by"] != granted_by:
        conn.close(); return False
    conn.execute("DELETE FROM exercise_shares WHERE exercise_id=? AND instructor_username=?", (exercise_id, instructor_username))
    conn.commit(); conn.close(); return True


def save_exercise(
    exercise_id: str,
    title: str,
    difficulty: str,
    category: str,
    description: str,
    starter_code: str,
    test_cases: list[dict],
    created_by: str = "instructor"
) -> dict:
    """Tạo mới hoặc cập nhật bài tập (Upsert)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    tc_json = json.dumps(test_cases, ensure_ascii=False)

    cursor.execute("""
        INSERT INTO exercises (
            id, title, difficulty, category, description, starter_code, test_cases, created_by, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            difficulty = excluded.difficulty,
            category = excluded.category,
            description = excluded.description,
            starter_code = excluded.starter_code,
            test_cases = excluded.test_cases,
            is_active = 1
    """, (exercise_id, title, difficulty, category, description, starter_code, tc_json, created_by))
    conn.commit()
    conn.close()
    return get_exercise_by_id(exercise_id)


def delete_exercise(exercise_id: str) -> bool:
    """Xóa bài tập (hoặc đánh dấu ẩn)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exercises WHERE id = ?", (exercise_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ==============================================================================
# HÀM TRUY VẤN VÀ LƯU TRỮ LỊCH SỬ NỘP BÀI (SUBMISSIONS)
# ==============================================================================

def save_submission(
    session_id: str,
    exercise_id: str,
    code: str,
    hint_level: int,
    passed_tests: int,
    total_tests: int,
    all_passed: bool,
    llm_source: str,
    tutor_hint: str,
    attempt_features: Optional[dict] = None
) -> int:
    """Lưu sự kiện học tập và lịch sử nộp bài vào SQLite (kèm đặc trưng lượt nếu có)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO submissions (
            session_id, exercise_id, code, hint_level, passed_tests, total_tests, all_passed, llm_source, tutor_hint
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        exercise_id,
        code,
        hint_level,
        passed_tests,
        total_tests,
        1 if all_passed else 0,
        llm_source,
        tutor_hint
    ))
    submission_id = cursor.lastrowid
    if attempt_features:
        cursor.execute(
            "INSERT OR REPLACE INTO attempt_features(submission_id, error_class, status_counts, ast_flags, feature_version, failed_tests, format_mismatch_tests) VALUES (?,?,?,?,?,?,?)",
            (submission_id, str(attempt_features.get("error_class") or ""),
             json.dumps(attempt_features.get("status_counts") or {}, ensure_ascii=False),
             json.dumps(attempt_features.get("ast_flags") or {}, ensure_ascii=False),
             str(attempt_features.get("feature_version") or "1"),
             json.dumps(attempt_features.get("failed_tests") or []),
             json.dumps(attempt_features.get("format_mismatch_tests") or [])))
    conn.commit()
    conn.close()
    return submission_id


def get_attempts(session_id: str, exercise_id: str, limit: int = 5) -> list[dict]:
    """Lấy danh sách các lần nộp gần nhất của sinh viên cho bài tập cụ thể kèm mã nguồn đã nộp."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, code, hint_level, passed_tests, total_tests, all_passed, llm_source, tutor_hint, timestamp, action_type
        FROM submissions
        WHERE session_id = ? AND exercise_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (session_id, exercise_id, limit))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "exercise_id": exercise_id,
            "code": r["code"] or "",
            "hint_level": r["hint_level"],
            "passed": r["passed_tests"],
            "total": r["total_tests"],
            "all_passed": bool(r["all_passed"]),
            "llm_source": r["llm_source"],
            "tutor_hint": r["tutor_hint"] or "",
            "timestamp": r["timestamp"],
            "action_type": r["action_type"] or "submit"
        }
        for r in rows
    ]


def get_all_submissions(limit: int = 100, instructor_username: Optional[str] = None) -> list[dict]:
    """Lấy danh sách các lần nộp bài mới nhất phục vụ Dashboard Giảng viên (kèm code & tutor_hint)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    scope = """
        SELECT s.id, s.session_id, s.exercise_id, e.title as exercise_title,
               s.code, s.hint_level, s.passed_tests, s.total_tests, s.all_passed,
               s.llm_source, s.tutor_hint, s.timestamp
        FROM submissions s
        LEFT JOIN exercises e ON s.exercise_id = e.id
    """
    params: list[Any] = []
    if instructor_username:
        scope += """
        WHERE EXISTS (
            SELECT 1 FROM class_exercises ce
            JOIN credit_classes c ON c.id = ce.class_id
            JOIN class_enrollments en ON en.class_id = c.id AND en.student_username = s.session_id
            WHERE c.instructor_username = ? AND ce.exercise_id = s.exercise_id
        )
        """
        params.append(instructor_username)
    scope += " ORDER BY s.id DESC LIMIT ?"
    params.append(limit)
    cursor.execute(scope, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "session_id": r["session_id"],
            "exercise_id": r["exercise_id"],
            "exercise_title": r["exercise_title"] or r["exercise_id"],
            "code": r["code"] or "",
            "hint_level": r["hint_level"],
            "passed_tests": r["passed_tests"],
            "total_tests": r["total_tests"],
            "all_passed": bool(r["all_passed"]),
            "llm_source": r["llm_source"],
            "tutor_hint": r["tutor_hint"] or "",
            "timestamp": r["timestamp"]
        }
        for r in rows
    ]


def get_submission_by_id(submission_id: int, instructor_username: Optional[str] = None) -> Optional[dict]:
    """Lấy chi tiết đầy đủ của một bài nộp theo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT s.id, s.session_id, s.exercise_id, e.title as exercise_title,
               s.code, s.hint_level, s.passed_tests, s.total_tests, s.all_passed,
               s.llm_source, s.tutor_hint, s.timestamp
        FROM submissions s
        LEFT JOIN exercises e ON s.exercise_id = e.id
        WHERE s.id = ?
    """
    params: list[Any] = [submission_id]
    if instructor_username:
        query += """
          AND EXISTS (
              SELECT 1 FROM class_exercises ce
              JOIN credit_classes c ON c.id = ce.class_id
              JOIN class_enrollments en ON en.class_id = c.id AND en.student_username = s.session_id
              WHERE c.instructor_username = ? AND ce.exercise_id = s.exercise_id
          )
        """
        params.append(instructor_username)
    cursor.execute(query, params)
    r = cursor.fetchone()
    conn.close()

    if not r:
        return None

    return {
        "id": r["id"],
        "session_id": r["session_id"],
        "exercise_id": r["exercise_id"],
        "exercise_title": r["exercise_title"] or r["exercise_id"],
        "code": r["code"] or "",
        "hint_level": r["hint_level"],
        "passed_tests": r["passed_tests"],
        "total_tests": r["total_tests"],
        "all_passed": bool(r["all_passed"]),
        "llm_source": r["llm_source"],
        "tutor_hint": r["tutor_hint"] or "",
        "timestamp": r["timestamp"]
    }


def get_all_knowledge_components(include_inactive: bool = False) -> list[dict]:
    """Lấy danh sách các đơn vị kiến thức (KC) bao gồm cả KC mặc định và KC do giảng viên thêm."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        where_clause = "" if include_inactive else "WHERE is_active = 1"
        cursor.execute(f"SELECT kc, label_vi, keywords, created_by, created_at, is_active FROM knowledge_components {where_clause} ORDER BY rowid ASC")
        rows = cursor.fetchall()
        kcs = []
        for r in rows:
            try:
                kw = json.loads(r["keywords"]) if isinstance(r["keywords"], str) else (r["keywords"] or [])
            except Exception:
                kw = [k.strip() for k in str(r["keywords"]).split(",") if k.strip()]
            kcs.append({
                "kc": r["kc"],
                "label_vi": r["label_vi"],
                "keywords": kw,
                "created_by": r["created_by"] or "system",
                "created_at": r["created_at"],
                "is_active": bool(r["is_active"]),
            })
        if not kcs:
            from pytutor_shared.learner_model import KC_DEFINITIONS
            return list(KC_DEFINITIONS)
        return kcs
    except Exception as e:
        logger.warning(f"Lỗi đọc knowledge_components từ DB, dùng fallback: {e}")
        from pytutor_shared.learner_model import KC_DEFINITIONS
        return list(KC_DEFINITIONS)
    finally:
        conn.close()


def create_knowledge_component(kc: str, label_vi: str, keywords: list[str], created_by: str = "instructor") -> dict:
    """Tạo hoặc cập nhật một đơn vị kiến thức mới do giảng viên định nghĩa."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        kw_json = json.dumps(keywords, ensure_ascii=False)
        cursor.execute("""
            INSERT INTO knowledge_components (kc, label_vi, keywords, created_by, is_active)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(kc) DO UPDATE SET
                label_vi = excluded.label_vi,
                keywords = excluded.keywords,
                is_active = 1
        """, (kc, label_vi, kw_json, created_by))
        conn.commit()
        return {
            "kc": kc,
            "label_vi": label_vi,
            "keywords": keywords,
            "created_by": created_by,
            "is_active": True,
        }
    finally:
        conn.close()


def delete_knowledge_component(kc: str) -> bool:
    """Xóa (đánh dấu inactive) một đơn vị kiến thức do giảng viên thêm. Không cho xóa 6 KC hệ thống."""
    system_kcs = {"io_format", "conditional", "loop", "accumulator", "string", "recursion"}
    if kc in system_kcs:
        raise ValueError("Không thể xóa các đơn vị kiến thức hạt nhân của hệ thống.")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE knowledge_components SET is_active = 0 WHERE kc = ?", (kc,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def compute_student_model(session_id: str, class_id: Optional[str] = None) -> dict:
    """
    [Phase 13-14] Tính toán Mô hình Học sinh (Student Model) & Bộ Phân tích Học tập Định lượng 4 Chiều (4D Learning Analytics Engine)
    kèm Đánh giá Tự động từ Hệ thống Gia sư (Diagnostic Evaluation) chính xác 100% dựa trên số liệu thực nghiệm SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Lọc theo lớp học phần nếu có class_id
    class_filter_eids = None
    if class_id:
        try:
            cursor.execute("SELECT exercise_id FROM class_exercises WHERE class_id = ?", (class_id,))
            c_rows = cursor.fetchall()
            if c_rows:
                class_filter_eids = set(r["exercise_id"] for r in c_rows)
        except Exception:
            class_filter_eids = None

    # Lấy toàn bộ bài nộp của học viên này (order by id ASC để biết bài nộp đầu tiên)
    cursor.execute("""
        SELECT id, exercise_id, hint_level, passed_tests, total_tests, all_passed, timestamp
        FROM submissions
        WHERE session_id = ? AND action_type = 'submit'
        ORDER BY id ASC
    """, (session_id,))
    sub_rows = [dict(r) for r in cursor.fetchall()]

    # Lấy thông tin sao từ user_exercise_stars nếu có
    stars_map = {}
    try:
        cursor.execute("SELECT exercise_id, stars_earned, highest_clean_score FROM user_exercise_stars WHERE username = ?", (session_id,))
        stars_map = {r["exercise_id"]: dict(r) for r in cursor.fetchall()}
    except Exception:
        stars_map = {}

    # Lấy danh mục bài tập (để phân tích topic_mastery)
    ex_meta_rows = []
    try:
        if class_id:
            cursor.execute("""
                SELECT ce.exercise_id as id, ce.module_name as category, ce.module_name as module_name, ce.skill_tag as skill_tag, e.category as exercise_category, e.title, ce.min_stars_required
                FROM class_exercises ce
                JOIN exercises e ON ce.exercise_id = e.id
                WHERE ce.class_id = ?
                ORDER BY ce.order_idx ASC
            """, (class_id,))
            ex_meta_rows = [dict(r) for r in cursor.fetchall()]
        else:
            cursor.execute("SELECT id, title, category FROM exercises WHERE is_active = 1 ORDER BY id ASC")
            ex_meta_rows = [dict(r) for r in cursor.fetchall()]
    except Exception:
        ex_meta_rows = []

    # Mô hình người học v3: đọc thêm lượt hỏi AI (bỏ Exam-Mode-Guard), lượt chạy thử và đặc trưng lượt.
    ask_rows, run_rows, feature_rows = [], [], []
    kc_defs = None
    try:
        cursor.execute("""
            SELECT id, exercise_id, hint_level, passed_tests, timestamp
            FROM submissions
            WHERE session_id = ? AND action_type = 'ask_ai' AND COALESCE(llm_source, '') != 'Exam-Mode-Guard'
            ORDER BY id ASC
        """, (session_id,))
        ask_rows = [dict(r) for r in cursor.fetchall()]
        cursor.execute("""
            SELECT id, exercise_id, passed_tests, all_passed, timestamp
            FROM practice_runs
            WHERE username = ?
            ORDER BY id ASC
        """, (session_id,))
        run_rows = [dict(r) for r in cursor.fetchall()]
        cursor.execute("""
            SELECT f.submission_id, f.error_class
            FROM attempt_features f JOIN submissions s ON s.id = f.submission_id
            WHERE s.session_id = ?
        """, (session_id,))
        feature_rows = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT kc, label_vi, keywords FROM knowledge_components WHERE is_active = 1 ORDER BY rowid ASC")
        kc_raw_rows = [dict(r) for r in cursor.fetchall()]
        kc_defs = []
        for r in kc_raw_rows:
            try:
                kw = json.loads(r["keywords"]) if isinstance(r["keywords"], str) else (r["keywords"] or [])
            except Exception:
                kw = [k.strip() for k in str(r["keywords"]).split(",") if k.strip()]
            kc_defs.append({"kc": r["kc"], "label_vi": r["label_vi"], "keywords": kw})
        kc_defs = kc_defs or None  # rỗng -> dùng KC mặc định trong pytutor_shared
    except Exception:
        kc_defs = None

    conn.close()

    # Áp dụng bộ lọc bài tập nếu có class_filter_eids
    if class_filter_eids is not None:
        sub_rows = [s for s in sub_rows if s["exercise_id"] in class_filter_eids]
        ask_rows = [a for a in ask_rows if a["exercise_id"] in class_filter_eids]
        run_rows = [r for r in run_rows if r["exercise_id"] in class_filter_eids]

    total_submissions = len(sub_rows)

    # Nhóm theo bài tập
    grouped_by_exercise: dict[str, list[dict]] = {}
    for s in sub_rows:
        eid = s["exercise_id"]
        if eid not in grouped_by_exercise:
            grouped_by_exercise[eid] = []
        grouped_by_exercise[eid].append(s)

    mastered_exercises = []
    struggling_exercises = []
    in_progress_exercises = []

    first_try_pass_count = 0
    exercise_autonomy_scores = []
    autonomy_by_exercise: dict[str, int] = {}
    total_hint_sum = 0
    total_hint_count = 0

    for eid, s_list in grouped_by_exercise.items():
        first_sub = s_list[0]
        if first_sub["all_passed"] == 1:
            first_try_pass_count += 1

        has_passed = any(s["all_passed"] == 1 for s in s_list)
        max_hint = max(s["hint_level"] for s in s_list)
        total_hint_sum += max_hint
        total_hint_count += 1

        # Tính điểm tự lực cho bài này
        if has_passed:
            mastered_exercises.append(eid)
            passed_sub = next(s for s in s_list if s["all_passed"] == 1)
            star_info = stars_map.get(eid)
            stars = star_info["stars_earned"] if star_info else (3 if passed_sub["hint_level"] == 1 else (2 if passed_sub["hint_level"] == 2 else 1))
            if stars == 3:
                exercise_autonomy_scores.append(100)
            elif stars == 2:
                exercise_autonomy_scores.append(70)
            else:
                exercise_autonomy_scores.append(40)
            autonomy_by_exercise[eid] = exercise_autonomy_scores[-1]
        else:
            if len(s_list) >= 2 or max_hint >= 3:
                struggling_exercises.append(eid)
            else:
                in_progress_exercises.append(eid)
            best_ratio = max((s["passed_tests"] / max(1, s["total_tests"])) for s in s_list)
            exercise_autonomy_scores.append(round(best_ratio * 40))
            autonomy_by_exercise[eid] = exercise_autonomy_scores[-1]

    distinct_count = len(grouped_by_exercise)
    autonomy_score = round(sum(exercise_autonomy_scores) / max(1, len(exercise_autonomy_scores))) if exercise_autonomy_scores else 0
    first_try_pass_rate = round((first_try_pass_count / max(1, distinct_count)) * 100, 1) if distinct_count > 0 else 0.0
    avg_attempts_to_solve = round(total_submissions / max(1, distinct_count), 1) if distinct_count > 0 else 0.0
    avg_hint = round(total_hint_sum / max(1, total_hint_count), 1) if total_hint_count > 0 else 1.0

    # Phổ lỗi (Error Breakdown)
    passed_runs = sum(1 for s in sub_rows if s["all_passed"] == 1)
    logic_errors = sum(1 for s in sub_rows if s["all_passed"] == 0 and s["passed_tests"] > 0)
    syntax_or_runtime_errors = sum(1 for s in sub_rows if s["all_passed"] == 0 and s["passed_tests"] == 0)

    error_breakdown = {
        "total_runs": total_submissions,
        "passed_runs": passed_runs,
        "passed_percent": round((passed_runs / max(1, total_submissions)) * 100, 1) if total_submissions > 0 else 0.0,
        "logic_errors": logic_errors,
        "logic_error_percent": round((logic_errors / max(1, total_submissions)) * 100, 1) if total_submissions > 0 else 0.0,
        "syntax_or_runtime_errors": syntax_or_runtime_errors,
        "syntax_error_percent": round((syntax_or_runtime_errors / max(1, total_submissions)) * 100, 1) if total_submissions > 0 else 0.0
    }

    # Phân tích theo từng Chương / Chủ đề (Topic Mastery)
    topics_dict: dict[str, list[dict]] = {}
    for em in ex_meta_rows:
        cat = em.get("category", "Chương trình")
        if cat not in topics_dict:
            topics_dict[cat] = []
        topics_dict[cat].append(em)

    topic_mastery = []
    for cat_name, ex_list in topics_dict.items():
        t_total = len(ex_list)
        t_completed = sum(1 for e in ex_list if e["id"] in mastered_exercises)
        t_pct = round((t_completed / max(1, t_total)) * 100)
        t_stars = [stars_map[e["id"]]["stars_earned"] for e in ex_list if e["id"] in stars_map and e["id"] in mastered_exercises]
        avg_stars_topic = round(sum(t_stars) / max(1, len(t_stars)), 1) if t_stars else 0.0
        topic_mastery.append({
            "topic_name": cat_name,
            "completed": t_completed,
            "total": t_total,
            "percentage": t_pct,
            "avg_stars": avg_stars_topic
        })

    # Lỗi lặp lại: bài có từ 2 lượt nộp chính thức chưa đạt trở lên (quy ước vận hành).
    title_map = {em["id"]: em.get("title") or em["id"] for em in ex_meta_rows}
    recurring_difficulties = []
    for eid, s_list in grouped_by_exercise.items():
        failed_subs = [s for s in s_list if s["all_passed"] == 0]
        if len(failed_subs) < 2:
            continue
        zero_pass = sum(1 for s in failed_subs if s["passed_tests"] == 0)
        recurring_difficulties.append({
            "exercise_id": eid,
            "title": title_map.get(eid, eid),
            "unsuccessful_submissions": len(failed_subs),
            "total_submissions": len(s_list),
            "dominant_error": "syntax_or_runtime" if zero_pass * 2 > len(failed_subs) else "logic",
            "resolved": eid in mastered_exercises,
        })
    recurring_difficulties.sort(key=lambda item: (item["resolved"], -item["unsuccessful_submissions"], item["exercise_id"]))

    # Bước luyện tập tiếp theo: ưu tiên bài đang nghẽn → bài dở dang → bài chưa thử → bài chưa đạt 3 sao.
    next_practice = None
    unresolved = [item for item in recurring_difficulties if not item["resolved"]]
    attempted_ids = set(grouped_by_exercise.keys())
    if unresolved:
        target = unresolved[0]
        next_practice = {"exercise_id": target["exercise_id"], "title": target["title"], "reason_code": "unresolved_recurring",
                         "reason": f"Bài này đã có {target['unsuccessful_submissions']} lượt nộp chưa đạt và chưa hoàn thành."}
    elif struggling_exercises or in_progress_exercises:
        eid = (struggling_exercises or in_progress_exercises)[0]
        next_practice = {"exercise_id": eid, "title": title_map.get(eid, eid), "reason_code": "in_progress",
                         "reason": "Bài đã nộp nhưng chưa vượt qua toàn bộ kiểm thử."}
    else:
        untried = next((em for em in ex_meta_rows if em["id"] not in attempted_ids), None)
        if untried:
            next_practice = {"exercise_id": untried["id"], "title": untried.get("title") or untried["id"],
                             "reason_code": "next_unattempted", "reason": "Bài kế tiếp trong danh sách mà bạn chưa nộp."}
        else:
            below_three = next((eid for eid in mastered_exercises
                                if (stars_map.get(eid) or {}).get("stars_earned", 3) < 3), None)
            if below_three:
                next_practice = {"exercise_id": below_three, "title": title_map.get(below_three, below_three),
                                 "reason_code": "retry_for_autonomy",
                                 "reason": "Bài đã hoàn thành với gợi ý mức cao; có thể tự làm lại không cần gợi ý."}

    # Đánh giá Tự động từ Hệ thống Gia sư (Diagnostic Evaluation)
    if total_submissions == 0:
        level_classification = "Chưa có dữ liệu thực hành (Bắt đầu làm bài tập đầu tiên)"
        strengths_analysis = "Học viên vừa tham gia hệ thống. Hãy chọn bài tập cơ sở đầu tiên trên Lộ trình để bắt đầu tích lũy kinh nghiệm!"
        weaknesses_and_bottlenecks = "Chưa ghi nhận điểm nghẽn nào."
        recommended_next_action = "Mở bài tập Chương 1 để bắt đầu thực hành viết mã nguồn Python đầu tiên."
    elif len(mastered_exercises) >= 4 and autonomy_score >= 80:
        level_classification = "Hoàn thành nhiều bài với mức hỗ trợ thấp"
        strengths_analysis = (
            f"Đã hoàn thành {len(mastered_exercises)}/{distinct_count} bài tập đã thử với chỉ số tự lực {autonomy_score}/100. "
            f"Tỷ lệ hoàn thành ngay lần đầu đạt {first_try_pass_rate}%, trung bình chỉ mất {avg_attempts_to_solve} lần nộp/bài."
        )
        if struggling_exercises:
            weaknesses_and_bottlenecks = f"Cần lưu ý xử lý dứt điểm các bài tập đang vướng mắc: {', '.join(struggling_exercises)}."
        elif error_breakdown["logic_errors"] > 0:
            weaknesses_and_bottlenecks = f"Thỉnh thoảng vẫn gặp sai lệch ở các test case biên (lỗi logic kiểm thử chiếm {error_breakdown['logic_error_percent']}%)."
        else:
            weaknesses_and_bottlenecks = "Không có điểm nghẽn kỹ thuật nào đáng kể."
        recommended_next_action = "Thử các thử thách 'Tối ưu Code Pythonic' hoặc bài kế tiếp trên lộ trình."
    elif len(mastered_exercises) >= 2 and autonomy_score >= 60:
        level_classification = "Hoàn thành ổn định, còn dùng gợi ý ở một số bài"
        strengths_analysis = (
            f"Đã hoàn thành {len(mastered_exercises)}/{distinct_count} bài tập với chỉ số tự lực {autonomy_score}/100. "
            f"Vượt qua bài tập với mức trợ giúp trung bình Level {avg_hint} (chủ yếu dùng Gợi ý nhẹ hoặc Chỉ chỗ sai)."
        )
        if struggling_exercises:
            weaknesses_and_bottlenecks = (
                f"Đang gặp điểm nghẽn tại bài tập: {', '.join(struggling_exercises)}. "
                f"Phổ lỗi ghi nhận: {error_breakdown['logic_error_percent']}% lỗi logic test case và {error_breakdown['syntax_error_percent']}% lỗi cú pháp/runtime."
            )
        else:
            weaknesses_and_bottlenecks = "Chưa ghi nhận bài nào bị nghẽn; một số bài hoàn thành sau khi dùng gợi ý mức cao."
        recommended_next_action = "Tiếp tục bài tập kế tiếp và xem lại các bước giải để củng cố tính độc lập khi lập trình."
    else:
        level_classification = "Đang xây nền tảng, còn nhiều lượt nộp chưa đạt"
        strengths_analysis = (
            f"Đã tích cực nộp bài {total_submissions} lượt và hoàn thành {len(mastered_exercises)} bài tập. "
            f"Trung bình {avg_attempts_to_solve} lượt nộp cho mỗi bài đã thử."
        )
        weaknesses_and_bottlenecks = (
            f"Tỷ lệ lỗi logic chiếm {error_breakdown['logic_error_percent']}% và lỗi cú pháp chiếm {error_breakdown['syntax_error_percent']}%. "
            f"Bài đang nghẽn: {', '.join(struggling_exercises) if struggling_exercises else 'chưa xác định được bài cụ thể'}."
        )
        recommended_next_action = next_practice["reason"] if next_practice else ""

    evidence_status = "no_data" if total_submissions == 0 else ("limited" if distinct_count < 3 else "sufficient")
    if evidence_status == "limited":
        level_classification = "Chưa đủ dữ liệu để phân loại"
        strengths_analysis = "Đã ghi nhận hoạt động học tập; cần thêm bài làm để nhận diện điểm mạnh ổn định."
        weaknesses_and_bottlenecks = "Chưa đủ dữ liệu để kết luận về điểm nghẽn hoặc dạng lỗi thường gặp."
        recommended_next_action = "Tiếp tục luyện thêm bài tập trong học phần để hồ sơ có đủ dữ liệu phân tích."

    diagnostic_evaluation = {
        "level_classification": level_classification,
        "strengths_analysis": strengths_analysis,
        "weaknesses_and_bottlenecks": weaknesses_and_bottlenecks,
        "recommended_next_action": recommended_next_action
    }

    analytics_metrics = {
        "total_submissions": total_submissions,
        "distinct_exercises_attempted": distinct_count,
        "mastered_exercises": mastered_exercises,
        "struggling_exercises": struggling_exercises,
        "in_progress_exercises": in_progress_exercises,
        "autonomy_score": autonomy_score,
        "first_try_pass_rate": first_try_pass_rate,
        "avg_attempts_to_solve": avg_attempts_to_solve,
        "average_hint_level": avg_hint,
        "error_breakdown": error_breakdown,
        "topic_mastery": topic_mastery,
        "data_status": evidence_status,
        "sample_size": distinct_count,
        "recurring_difficulties": recurring_difficulties,
        "next_practice": next_practice,
        "metric_definition_version": "2"
    }

    learner_model = derive_learner_model(
        exercises=ex_meta_rows,
        submissions=sub_rows,
        asks=ask_rows,
        runs=run_rows,
        features={r["submission_id"]: r for r in feature_rows},
        autonomy_by_exercise=autonomy_by_exercise,
        analytics_data_status=evidence_status,
        kc_definitions=kc_defs,
    )

    summary = (
        f"🎯 Xếp loại: {level_classification} | Chỉ số tự lực: {autonomy_score}/100.\n"
        f"🌟 Điểm mạnh: {strengths_analysis}\n"
        f"⚠️ Cần lưu ý: {weaknesses_and_bottlenecks}\n"
        f"🧭 Khuyến nghị: {recommended_next_action}"
    )

    return {
        "session_id": session_id,
        "class_id": class_id,
        "total_exercises_attempted": distinct_count,
        "total_submissions": total_submissions,
        "mastered_exercises": mastered_exercises,
        "struggling_exercises": struggling_exercises,
        "in_progress_exercises": in_progress_exercises,
        "average_hint_level": avg_hint,
        "summary": summary,
        "analytics_metrics": analytics_metrics,
        "diagnostic_evaluation": diagnostic_evaluation,
        "learner_model": learner_model
    }


def get_instructor_stats(instructor_username: Optional[str] = None) -> dict:
    """Tổng hợp thống kê học tập cho Giảng viên."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if instructor_username:
        params = (instructor_username,)
        cursor.execute("""
            SELECT COUNT(DISTINCT e.id)
            FROM exercises e
            JOIN class_exercises ce ON ce.exercise_id = e.id
            JOIN credit_classes c ON c.id = ce.class_id
            WHERE c.instructor_username = ? AND e.is_active = 1
        """, params)
        total_exercises = cursor.fetchone()[0]
        scoped = """
            SELECT COUNT(DISTINCT s.id), COUNT(DISTINCT s.session_id),
                   SUM(CASE WHEN s.all_passed = 1 THEN 1 ELSE 0 END)
            FROM submissions s
            WHERE EXISTS (
                SELECT 1 FROM class_exercises ce
                JOIN credit_classes c ON c.id = ce.class_id
                JOIN class_enrollments en ON en.class_id = c.id AND en.student_username = s.session_id
                WHERE c.instructor_username = ? AND ce.exercise_id = s.exercise_id
            )
        """
        cursor.execute(scoped, params)
        total_submissions, active_students, passed_submissions = cursor.fetchone()
    else:
        cursor.execute("SELECT COUNT(*) FROM exercises WHERE is_active = 1")
        total_exercises = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM submissions")
        total_submissions = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM submissions")
        active_students = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM submissions WHERE all_passed = 1")
        passed_submissions = cursor.fetchone()[0]

    pass_rate = round((passed_submissions / total_submissions * 100), 1) if total_submissions > 0 else 0.0

    conn.close()

    return {
        "total_exercises": total_exercises,
        "total_submissions": total_submissions,
        "active_students": active_students,
        "pass_rate_percentage": pass_rate
    }


# ==============================================================================
# PHASE 10: AUTONOMY STARS & PYTHONIC REVIEW
# ==============================================================================

def calculate_autonomy_stars(attempt_count: int, max_hint_level_used: int, all_passed: bool) -> int:
    """
    Quy tắc tính sao tự lực:
    - Nếu chưa pass 100% test cases: 0 Sao
    - Nếu pass 100%:
        + Dùng gợi ý <= Mức 1 (hoặc không hỏi AI): 3 SAO (Tự lực Xuất sắc ⭐⭐⭐)
        + Dùng gợi ý Mức 2 (Chỉ chỗ sai): 2 SAO (Khá giỏi ⭐⭐)
        + Cần gợi ý Mức 3 (Hướng dẫn từng bước): 1 SAO (Đã hoàn thành ⭐)
    """
    if not all_passed:
        return 0
    if max_hint_level_used <= 1:
        return 3
    elif max_hint_level_used == 2:
        return 2
    else:
        return 1


def save_exercise_stars(
    username: str,
    exercise_id: str,
    stars: int,
    clean_score: int = 0,
    submission_id: Optional[int] = None
) -> dict:
    """Lưu hoặc cập nhật số sao cao nhất và điểm clean code cao nhất cho bài tập."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT stars_earned, highest_clean_score FROM user_exercise_stars
            WHERE username = ? AND exercise_id = ?
        """, (username, exercise_id))
        row = cursor.fetchone()

        if row:
            new_stars = max(row["stars_earned"], stars)
            new_clean = max(row["highest_clean_score"], clean_score)
            cursor.execute("""
                UPDATE user_exercise_stars
                SET stars_earned = ?, highest_clean_score = ?, best_submission_id = COALESCE(?, best_submission_id),
                    updated_at = datetime('now', 'localtime')
                WHERE username = ? AND exercise_id = ?
            """, (new_stars, new_clean, submission_id, username, exercise_id))
        elif 1 <= stars <= 3:
            new_stars = stars
            new_clean = clean_score
            cursor.execute("""
                INSERT INTO user_exercise_stars (
                    username, exercise_id, stars_earned, best_submission_id, highest_clean_score
                ) VALUES (?, ?, ?, ?, ?)
            """, (username, exercise_id, stars, submission_id, clean_score))
        else:
            # Chưa có dòng sao và lượt này không cấp sao (vd. Pythonic Review trước khi "Nộp bài"):
            # bảng có CHECK (stars_earned BETWEEN 1 AND 3) nên không tạo dòng 0 sao; sao chỉ sinh từ `submit`.
            new_stars = 0
            new_clean = clean_score
        conn.commit()
    finally:
        conn.close()

    return {
        "username": username,
        "exercise_id": exercise_id,
        "stars_earned": new_stars,
        "highest_clean_score": new_clean,
        # Keep the response field for older clients; achievements are no longer awarded.
        "new_badges": []
    }


def get_user_achievements(username: str) -> dict:
    """Lấy thống kê sao tự lực của học viên (tên hàm giữ lại để tương thích)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT exercise_id, stars_earned, highest_clean_score, updated_at
        FROM user_exercise_stars
        WHERE username = ?
    """, (username,))
    stars = [dict(r) for r in cursor.fetchall()]

    total_stars = sum(s["stars_earned"] for s in stars)

    conn.close()
    return {
        "username": username,
        "total_stars": total_stars,
        "completed_count": len(stars),
        "exercise_stars": {s["exercise_id"]: s["stars_earned"] for s in stars},
        "clean_scores": {s["exercise_id"]: s["highest_clean_score"] for s in stars},
        # Keep the API field for compatibility; historical badge rows remain stored but hidden.
        "badges": []
    }


def get_class_leaderboard(limit: int = 20) -> list[dict]:
    """Lấy bảng xếp hạng lớp học theo tổng số sao và số bài hoàn thành."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Nhóm theo username (bao gồm cả users và session_id từ user_exercise_stars)
    cursor.execute("""
        SELECT 
            COALESCE(u.username, s.username) as username,
            COALESCE(u.full_name, s.username) as full_name,
            COALESCE(u.role, 'student') as role,
            COALESCE(SUM(s.stars_earned), 0) as total_stars,
            COUNT(s.id) as completed_exercises,
            COALESCE(MAX(s.highest_clean_score), 0) as highest_clean_score
        FROM user_exercise_stars s
        LEFT JOIN users u ON s.username = u.username
        GROUP BY s.username
        ORDER BY total_stars DESC, completed_exercises DESC, highest_clean_score DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()

    leaderboard = []
    for rank, r in enumerate(rows, start=1):
        leaderboard.append({
            "rank": rank,
            "username": r["username"],
            "full_name": r["full_name"],
            "total_stars": r["total_stars"],
            "completed_exercises": r["completed_exercises"],
            "highest_clean_score": r["highest_clean_score"]
        })

    conn.close()
    return leaderboard


# ==============================================================================
# HÀM QUẢN LÝ LỚP TÍN CHỈ, GHI DANH & KỲ THI (PHASE 12: CREDIT CLASSES & EXAMS)
# ==============================================================================

def get_credit_classes(instructor_username: Optional[str] = None, current_username: Optional[str] = None) -> list[dict]:
    """Lấy danh sách các Lớp tín chỉ kèm sĩ số sinh viên, số bài tập theo lớp và số đợt thi."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT c.*,
               (SELECT COUNT(*) FROM class_enrollments e WHERE e.class_id = c.id) as student_count,
               (SELECT COUNT(*) FROM exam_sessions s WHERE s.class_id = c.id AND s.is_active = 1) as session_count,
               (SELECT COUNT(*) FROM class_exercises ce WHERE ce.class_id = c.id) as exercise_count
        FROM credit_classes c
        WHERE 1=1
    """
    params = []
    if instructor_username:
        query += " AND c.instructor_username = ?"
        params.append(instructor_username)
    query += " ORDER BY c.created_at DESC, c.id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    result = []
    for r in rows:
        item = dict(r)
        c_id = item["id"]
        is_enrolled = False
        completed_in_class = 0
        if current_username:
            cursor.execute("SELECT COUNT(*) FROM class_enrollments WHERE class_id = ? AND student_username = ?", (c_id, current_username))
            is_enrolled = cursor.fetchone()[0] > 0

            cursor.execute("""
                SELECT COUNT(DISTINCT ce.exercise_id)
                FROM class_exercises ce
                JOIN submissions s ON ce.exercise_id = s.exercise_id
                WHERE ce.class_id = ? AND s.session_id = ? AND s.all_passed = 1
            """, (c_id, current_username))
            completed_in_class = cursor.fetchone()[0]

        item["is_enrolled"] = is_enrolled
        item["completed_in_class"] = completed_in_class
        ex_cnt = item.get("exercise_count", 0)
        item["progress_percent"] = round((completed_in_class / max(1, ex_cnt)) * 100) if ex_cnt > 0 else 0
        result.append(item)

    conn.close()
    return result


def get_credit_class_by_id(class_id: str, current_username: Optional[str] = None) -> Optional[dict]:
    """Lấy chi tiết một Lớp tín chỉ theo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*,
               (SELECT COUNT(*) FROM class_enrollments e WHERE e.class_id = c.id) as student_count,
               (SELECT COUNT(*) FROM exam_sessions s WHERE s.class_id = c.id AND s.is_active = 1) as session_count,
               (SELECT COUNT(*) FROM class_exercises ce WHERE ce.class_id = c.id) as exercise_count
        FROM credit_classes c
        WHERE c.id = ?
    """, (class_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    item = dict(row)
    is_enrolled = False
    completed_in_class = 0
    if current_username:
        cursor.execute("SELECT COUNT(*) FROM class_enrollments WHERE class_id = ? AND student_username = ?", (class_id, current_username))
        is_enrolled = cursor.fetchone()[0] > 0
        cursor.execute("""
            SELECT COUNT(DISTINCT ce.exercise_id)
            FROM class_exercises ce
            JOIN submissions s ON ce.exercise_id = s.exercise_id
            WHERE ce.class_id = ? AND s.session_id = ? AND s.all_passed = 1
        """, (class_id, current_username))
        completed_in_class = cursor.fetchone()[0]

    item["is_enrolled"] = is_enrolled
    item["completed_in_class"] = completed_in_class
    ex_cnt = item.get("exercise_count", 0)
    item["progress_percent"] = round((completed_in_class / max(1, ex_cnt)) * 100) if ex_cnt > 0 else 0
    conn.close()
    return item


def instructor_owns_class(class_id: str, instructor_username: str) -> bool:
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM credit_classes WHERE id = ? AND instructor_username = ?",
            (class_id, instructor_username),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def get_class_by_enrollment_code(enrollment_code: str) -> Optional[dict]:
    """Tìm Lớp học phần theo mã tham gia (enrollment_code)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM credit_classes WHERE UPPER(enrollment_code) = UPPER(?)", (enrollment_code.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_credit_class(
    class_code: str,
    class_name: str,
    course_code: str = "CNTT1116",
    credits: int = 3,
    faculty: str = "Khoa Công nghệ thông tin - NEU",
    semester: str = "Học kỳ 1 (2026-2027)",
    enrollment_code: Optional[str] = None,
    instructor_username: str = "gv_tran",
    instructor_name: Optional[str] = None,
    description: str = "",
    class_id: Optional[str] = None
) -> dict:
    """Giảng viên tạo mới một Lớp tín chỉ / Lớp học phần chuẩn NEU."""
    import re
    if not class_id:
        clean_code = re.sub(r'[^a-zA-Z0-9]+', '_', class_code).strip('_').lower()
        class_id = f"cls_{clean_code}"

    if not enrollment_code:
        import uuid
        enrollment_code = f"NEU-{str(uuid.uuid4())[:4].upper()}"

    if not instructor_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT full_name FROM users WHERE username = ?", (instructor_username,))
        u_row = cursor.fetchone()
        instructor_name = u_row[0] if u_row else "Giảng viên NEU"
        conn.close()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO credit_classes (
            id, class_code, class_name, course_code, credits, faculty, semester,
            enrollment_code, instructor_username, instructor_name, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (class_id, class_code, class_name, course_code, credits, faculty, semester, enrollment_code, instructor_username, instructor_name, description))
    conn.commit()
    conn.close()
    return get_credit_class_by_id(class_id) or {
        "id": class_id,
        "class_code": class_code,
        "class_name": class_name,
        "course_code": course_code,
        "credits": credits,
        "faculty": faculty,
        "semester": semester,
        "enrollment_code": enrollment_code,
        "instructor_username": instructor_username,
        "instructor_name": instructor_name,
        "description": description,
        "student_count": 0,
        "session_count": 0,
        "exercise_count": 0,
        "is_enrolled": False,
        "completed_in_class": 0,
        "progress_percent": 0
    }


def enroll_student_in_class(class_id: str, student_username: str) -> bool:
    """Ghi danh sinh viên vào một Lớp học phần."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO class_enrollments (class_id, student_username)
            VALUES (?, ?)
        """, (class_id, student_username))
        conn.commit()
        success = cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Lỗi ghi danh sinh viên {student_username} vào lớp {class_id}: {e}")
        success = False
    finally:
        conn.close()
    return success


def unenroll_student_from_class(class_id: str, student_username: str) -> bool:
    """Sinh viên hủy ghi danh khỏi một Lớp học phần."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM class_enrollments WHERE class_id = ? AND student_username = ?", (class_id, student_username))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def get_student_classes(student_username: str) -> list[dict]:
    """Lấy danh sách các lớp học phần mà sinh viên đang tham gia kèm tiến độ hoàn thành."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*,
               (SELECT COUNT(*) FROM class_enrollments e WHERE e.class_id = c.id) as student_count,
               (SELECT COUNT(*) FROM exam_sessions s WHERE s.class_id = c.id AND s.is_active = 1) as session_count,
               (SELECT COUNT(*) FROM class_exercises ce WHERE ce.class_id = c.id) as exercise_count
        FROM credit_classes c
        JOIN class_enrollments e ON e.class_id = c.id
        WHERE e.student_username = ?
        ORDER BY c.created_at DESC
    """, (student_username,))
    rows = cursor.fetchall()

    result = []
    for r in rows:
        item = dict(r)
        c_id = item["id"]
        cursor.execute("""
            SELECT COUNT(DISTINCT ce.exercise_id)
            FROM class_exercises ce
            JOIN submissions s ON ce.exercise_id = s.exercise_id
            WHERE ce.class_id = ? AND s.session_id = ? AND s.all_passed = 1
        """, (c_id, student_username))
        completed_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(ues.stars_earned), 0)
            FROM class_exercises ce
            JOIN user_exercise_stars ues ON ce.exercise_id = ues.exercise_id
            WHERE ce.class_id = ? AND ues.username = ?
        """, (c_id, student_username))
        total_stars = cursor.fetchone()[0]

        ex_cnt = item.get("exercise_count", 0)
        item["completed_in_class"] = completed_count
        item["total_stars_in_class"] = total_stars
        item["progress_percent"] = round((completed_count / max(1, ex_cnt)) * 100) if ex_cnt > 0 else 0
        item["is_enrolled"] = True
        result.append(item)

    conn.close()
    return result


def get_class_students(class_id: str) -> list[dict]:
    """Lấy danh sách các sinh viên đã ghi danh trong một Lớp tín chỉ."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.class_id, e.student_username, e.enrolled_at,
               COALESCE(u.full_name, e.student_username) as full_name
        FROM class_enrollments e
        LEFT JOIN users u ON e.student_username = u.username
        WHERE e.class_id = ?
        ORDER BY e.enrolled_at ASC
    """, (class_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_class_students_with_progress(class_id: str) -> list[dict]:
    """Giảng viên xem danh sách sinh viên trong lớp học phần kèm tiến độ bài tập và sao tích lũy."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.class_id, e.student_username, e.enrolled_at,
               COALESCE(u.full_name, e.student_username) as full_name
        FROM class_enrollments e
        LEFT JOIN users u ON e.student_username = u.username
        WHERE e.class_id = ?
        ORDER BY e.enrolled_at ASC
    """, (class_id,))
    students = [dict(r) for r in cursor.fetchall()]

    # Tổng số bài tập trong lớp
    cursor.execute("SELECT COUNT(*) FROM class_exercises WHERE class_id = ?", (class_id,))
    total_class_ex = cursor.fetchone()[0]

    for st in students:
        s_user = st["student_username"]
        # Đếm số bài đã pass trong lớp
        cursor.execute("""
            SELECT COUNT(DISTINCT ce.exercise_id)
            FROM class_exercises ce
            JOIN submissions s ON ce.exercise_id = s.exercise_id
            WHERE ce.class_id = ? AND s.session_id = ? AND s.all_passed = 1
        """, (class_id, s_user))
        completed = cursor.fetchone()[0]

        # Đếm tổng sao trong lớp
        cursor.execute("""
            SELECT COALESCE(SUM(ues.stars_earned), 0)
            FROM class_exercises ce
            JOIN user_exercise_stars ues ON ce.exercise_id = ues.exercise_id
            WHERE ce.class_id = ? AND ues.username = ?
        """, (class_id, s_user))
        stars = cursor.fetchone()[0]

        st["total_exercises"] = total_class_ex
        st["completed_exercises"] = completed
        st["total_stars"] = stars
        st["progress_percent"] = round((completed / max(1, total_class_ex)) * 100) if total_class_ex > 0 else 0

    conn.close()
    return students


def save_llm_interaction(record: dict[str, Any]) -> None:
    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO llm_interactions (
                id, username, role, task_type, model_name, latency_ms,
                prompt_tokens, completion_tokens, input_guard, output_guard, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record["id"], record["username"], record["role"], record["task_type"],
            record.get("model_name", ""), record.get("latency_ms", 0),
            record.get("prompt_tokens"), record.get("completion_tokens"),
            record.get("input_guard", "allowed"), record.get("output_guard", "allowed"),
            record.get("status", "success"),
        ))
        conn.commit()
    finally:
        conn.close()


def save_llm_interaction_sources(interaction_id: str, sources: list[str]) -> None:
    conn = get_db_connection()
    try:
        conn.executemany("INSERT OR IGNORE INTO llm_interaction_sources(interaction_id, source) VALUES (?, ?)",
                         [(interaction_id, source) for source in set(sources)])
        conn.commit()
    finally:
        conn.close()


def save_tutor_feedback(interaction_id: str, username: str, rating: int) -> bool:
    conn = get_db_connection()
    try:
        owner = conn.execute("SELECT username FROM llm_interactions WHERE id = ?", (interaction_id,)).fetchone()
        if not owner or owner["username"] != username:
            return False
        before_changes = conn.total_changes
        conn.execute("""
            INSERT OR IGNORE INTO tutor_feedback(interaction_id, username, rating)
            VALUES (?, ?, ?)
        """, (interaction_id, username, rating))
        if conn.total_changes == before_changes:
            existing = conn.execute("SELECT username FROM tutor_feedback WHERE interaction_id = ?", (interaction_id,)).fetchone()
            if existing and existing["username"] == username:
                return True
            return False
        conn.commit()
        return True
    finally:
        conn.close()


def save_practice_run(username: str, exercise_id: str, passed_tests: int, total_tests: int, all_passed: bool,
                      features: Optional[dict] = None) -> bool:
    """Ghi một lượt Chạy thử (không lưu mã nguồn). Lỗi ghi chỉ log cảnh báo, không làm hỏng phản hồi."""
    try:
        conn = get_db_connection()
        try:
            feats = features or {}
            conn.execute(
                "INSERT INTO practice_runs(username, exercise_id, passed_tests, total_tests, all_passed, error_class, failed_tests, format_mismatch_tests, feature_version) VALUES (?,?,?,?,?,?,?,?,?)",
                (username, exercise_id, int(passed_tests or 0), int(total_tests or 0), 1 if all_passed else 0,
                 feats.get("error_class"), json.dumps(feats.get("failed_tests") or []),
                 json.dumps(feats.get("format_mismatch_tests") or []), feats.get("feature_version")),
            )
            conn.commit()
            return True
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001 - ghi chạy thử là phụ trợ
        logger.warning("Không ghi được lượt chạy thử: %s", exc)
        return False


MAX_KB_DOCUMENTS_PER_CLASS = 20
_KB_META_COLUMNS = "id, class_id, title, filename, format, provenance, license_type, uploaded_by, is_active, char_count, created_at"


def count_kb_documents(class_id: str) -> int:
    conn = get_db_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM kb_documents WHERE class_id = ?", (class_id,)).fetchone()[0]
    finally:
        conn.close()


def create_kb_document(class_id: str, title: str, filename: str, fmt: str, content_text: str,
                       provenance: str, license_type: str, uploaded_by: str) -> int:
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "INSERT INTO kb_documents(class_id, title, filename, format, content_text, provenance, license_type, "
            "uploaded_by, char_count) VALUES (?,?,?,?,?,?,?,?,?)",
            (class_id, title, filename, fmt, content_text, provenance, license_type, uploaded_by, len(content_text)))
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_kb_documents(class_id: str, include_text: bool = False) -> list[dict[str, Any]]:
    columns = _KB_META_COLUMNS + (", content_text" if include_text else "")
    conn = get_db_connection()
    try:
        rows = conn.execute(f"SELECT {columns} FROM kb_documents WHERE class_id = ? ORDER BY id DESC", (class_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def set_kb_document_active(class_id: str, doc_id: int, is_active: bool) -> bool:
    conn = get_db_connection()
    try:
        cur = conn.execute("UPDATE kb_documents SET is_active = ? WHERE id = ? AND class_id = ?",
                           (1 if is_active else 0, doc_id, class_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_kb_document(class_id: str, doc_id: int) -> bool:
    conn = get_db_connection()
    try:
        cur = conn.execute("DELETE FROM kb_documents WHERE id = ? AND class_id = ?", (doc_id, class_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_active_kb_documents_for_index() -> list[dict[str, Any]]:
    """Danh sách tài liệu lớp đang bật, truyền cho retriever (để retriever không phải import database)."""
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT id, class_id, title, content_text FROM kb_documents WHERE is_active = 1 ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _clamp_days(days: int) -> int:
    return max(1, min(int(days), 90))


def _class_insights_extras(class_id: str, days: int, exercise_titles: dict[str, str], active_students: list[str]) -> dict[str, Any]:
    """v5.7: số liệu bổ sung cho 'Tình hình lớp' (chỉ thêm khóa; mô tả, ngưỡng quy ước chưa hiệu chuẩn).

    Không đổi cách tính sao/mô hình người học; lượt cũ chưa có đặc trưng được tính vào tỉ lệ phủ.
    """
    from statistics import median
    window = f"-{days} days"
    conn = get_db_connection()
    try:
        sub_rows = conn.execute("""
            SELECT s.id, s.session_id AS username, s.exercise_id, s.action_type, s.all_passed, s.timestamp,
                   f.error_class, f.failed_tests, f.format_mismatch_tests, f.feature_version
            FROM submissions s
            JOIN class_exercises ce ON ce.exercise_id = s.exercise_id AND ce.class_id = ?
            JOIN class_enrollments en ON en.class_id = ce.class_id AND en.student_username = s.session_id
            LEFT JOIN attempt_features f ON f.submission_id = s.id
            WHERE s.timestamp >= datetime('now', 'localtime', ?)
            ORDER BY s.id ASC
        """, (class_id, window)).fetchall()
        run_rows = conn.execute("""
            SELECT r.username, r.exercise_id, r.all_passed, r.timestamp, r.error_class, r.failed_tests,
                   r.format_mismatch_tests, r.feature_version
            FROM practice_runs r
            JOIN class_exercises ce ON ce.exercise_id = r.exercise_id AND ce.class_id = ?
            JOIN class_enrollments en ON en.class_id = ce.class_id AND en.student_username = r.username
            WHERE r.timestamp >= datetime('now', 'localtime', ?)
            ORDER BY r.id ASC
        """, (class_id, window)).fetchall()
        tc_rows = conn.execute("""
            SELECT e.id, e.test_cases FROM exercises e
            JOIN class_exercises ce ON ce.exercise_id = e.id AND ce.class_id = ?
        """, (class_id,)).fetchall()
    finally:
        conn.close()

    def loads(text: Any) -> list:
        try:
            val = json.loads(text) if text else []
            return val if isinstance(val, list) else []
        except (TypeError, ValueError):
            return []

    test_meta: dict[str, list[dict]] = {}
    for tr_ in tc_rows:
        test_meta[tr_["id"]] = loads(tr_["test_cases"])

    # Loại lỗi theo bài (nộp và chạy thử tách riêng) + test hay sai
    errors: dict[str, dict[str, Any]] = {}
    failing: dict[str, dict[int, dict[str, Any]]] = {}
    total_rows = featured = 0

    def add_error(eid: str, source: str, row: Any, student: str) -> None:
        nonlocal total_rows, featured
        total_rows += 1
        if not row["error_class"] or not row["feature_version"]:
            return
        featured += 1
        item = errors.setdefault(eid, {"submit": {}, "run": {}, "format_only_submit": 0, "format_only_run": 0})
        item[source][row["error_class"]] = item[source].get(row["error_class"], 0) + 1
        failed = loads(row["failed_tests"])
        mism = set(loads(row["format_mismatch_tests"]))
        if failed and set(failed) == mism:
            item["format_only_" + source] += 1
        for idx in failed:
            t = failing.setdefault(eid, {}).setdefault(int(idx), {"count": 0, "students": set(), "format_count": 0})
            t["count"] += 1
            t["students"].add(student)
            if idx in mism:
                t["format_count"] += 1

    for r in sub_rows:
        if r["action_type"] == "submit":
            add_error(r["exercise_id"], "submit", r, r["username"])
    for r in run_rows:
        add_error(r["exercise_id"], "run", r, r["username"])

    error_breakdown = [
        {"exercise_id": eid, "title": exercise_titles.get(eid, eid), **item}
        for eid, item in sorted(errors.items())
    ]
    failing_tests = []
    for eid, tests in sorted(failing.items()):
        tcs = test_meta.get(eid, [])
        top = sorted(tests.items(), key=lambda kv: (-kv[1]["count"], kv[0]))[:3]
        failing_tests.append({"exercise_id": eid, "title": exercise_titles.get(eid, eid), "tests": [
            {"test_idx": idx, "attempts": v["count"], "students": len(v["students"]), "format_attempts": v["format_count"],
             "description": (tcs[idx - 1].get("description") if 0 < idx <= len(tcs) else None) or f"Test #{idx}",
             "input": (str(tcs[idx - 1].get("input", "")).strip()[:120] if 0 < idx <= len(tcs) else "")}
            for idx, v in top]})

    # Khoảng thời gian từ sự kiện đầu tới lần nộp đạt đầu (suy ra từ mốc đã có, không phải thời gian ngồi làm)
    from datetime import datetime
    def parse(ts: Any):
        try:
            return datetime.strptime(str(ts)[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
    first_event: dict[tuple[str, str], Any] = {}
    first_pass: dict[tuple[str, str], Any] = {}
    for r in list(sub_rows) + list(run_rows):
        t = parse(r["timestamp"])
        if t is None:
            continue
        key = (r["username"], r["exercise_id"])
        if key not in first_event or t < first_event[key]:
            first_event[key] = t
    for r in sub_rows:
        if r["action_type"] == "submit" and r["all_passed"] == 1:
            t = parse(r["timestamp"])
            key = (r["username"], r["exercise_id"])
            if t is not None and (key not in first_pass or t < first_pass[key]):
                first_pass[key] = t
    by_ex: dict[str, list[float]] = {}
    for key, tp in first_pass.items():
        if key in first_event:
            by_ex.setdefault(key[1], []).append(max(0.0, (tp - first_event[key]).total_seconds() / 60))
    time_to_pass = [{"exercise_id": eid, "title": exercise_titles.get(eid, eid), "median_minutes": round(median(v), 1), "n": len(v)}
                    for eid, v in sorted(by_ex.items())]

    # Xu hướng theo ngày
    day_active: dict[str, set] = {}
    day_pass: dict[str, int] = {}
    for key, tp in first_pass.items():
        day_pass[tp.strftime("%Y-%m-%d")] = day_pass.get(tp.strftime("%Y-%m-%d"), 0) + 1
    for r in list(sub_rows) + list(run_rows):
        if r["timestamp"]:
            day_active.setdefault(str(r["timestamp"])[:10], set()).add(r["username"])
    daily = [{"date": d, "active_students": len(day_active.get(d, ())), "first_passes": day_pass.get(d, 0)}
             for d in sorted(set(day_active) | set(day_pass))]

    # Tổng quan KC: tái dùng compute_student_model, không viết lại logic
    kc_counts: dict[str, dict[str, int]] = {}
    kc_labels: dict[str, str] = {}
    modeled = 0
    for username in active_students:
        try:
            model = compute_student_model(username, class_id=class_id)
        except Exception as exc:  # noqa: BLE001 - phụ trợ, không làm hỏng insights
            logger.warning("Không tính được mô hình cho %s: %s", username, exc)
            continue
        modeled += 1
        for c in (model.get("learner_model") or {}).get("concepts") or []:
            kc_labels[c["kc"]] = c.get("label_vi") or c["kc"]
            bucket = kc_counts.setdefault(c["kc"], {"no_evidence": 0, "developing": 0, "struggling": 0, "secure": 0})
            bucket[c.get("state") or "no_evidence"] = bucket.get(c.get("state") or "no_evidence", 0) + 1
    kc_overview = [{"kc": k, "label_vi": kc_labels.get(k, k), "students": v} for k, v in kc_counts.items()]

    return {
        "kc_overview": {"modeled_students": modeled, "items": kc_overview},
        "error_breakdown_by_exercise": error_breakdown,
        "feature_coverage_percent": round(featured / total_rows * 100, 1) if total_rows else 0.0,
        "failing_tests_by_exercise": failing_tests,
        "time_to_pass_by_exercise": time_to_pass,
        "daily_trend": daily,
    }


def get_class_insights(class_id: str, days: int = 7) -> dict[str, Any]:
    """Góc nhìn sư phạm theo lớp cho giảng viên sở hữu lớp (đã kiểm tra quyền ở endpoint).

    Chỉ tính lượt `action_type='submit'` của sinh viên ghi danh trên bài thuộc lớp, trong N ngày gần nhất.
    Các ngưỡng (limited < 3, "cần hỗ trợ" = có bài ≥ 2 lượt chưa đạt và chưa qua) là quy ước vận hành.
    """
    days = _clamp_days(days)
    conn = get_db_connection()
    try:
        class_row = conn.execute("SELECT id, class_code, class_name FROM credit_classes WHERE id = ?", (class_id,)).fetchone()
        if not class_row:
            return {}
        enrolled = conn.execute("""
            SELECT en.student_username AS username, COALESCE(u.full_name, en.student_username) AS full_name
            FROM class_enrollments en LEFT JOIN users u ON u.username = en.student_username
            WHERE en.class_id = ? ORDER BY en.student_username
        """, (class_id,)).fetchall()
        exercises = conn.execute("""
            SELECT ce.exercise_id AS id, COALESCE(e.title, ce.exercise_id) AS title, ce.module_name AS topic, ce.order_idx
            FROM class_exercises ce LEFT JOIN exercises e ON e.id = ce.exercise_id
            WHERE ce.class_id = ? ORDER BY ce.order_idx ASC, ce.exercise_id ASC
        """, (class_id,)).fetchall()
        rows = conn.execute("""
            SELECT s.id, s.session_id, s.exercise_id, s.passed_tests, s.total_tests, s.all_passed
            FROM submissions s
            JOIN class_exercises ce ON ce.exercise_id = s.exercise_id AND ce.class_id = ?
            JOIN class_enrollments en ON en.class_id = ce.class_id AND en.student_username = s.session_id
            WHERE s.action_type = 'submit' AND s.timestamp >= datetime('now', 'localtime', ?)
            ORDER BY s.id ASC
        """, (class_id, f"-{days} days")).fetchall()
        ask_rows = conn.execute("""
            SELECT s.id, s.session_id, s.exercise_id, s.hint_level, s.timestamp
            FROM submissions s
            JOIN class_exercises ce ON ce.exercise_id = s.exercise_id AND ce.class_id = ?
            JOIN class_enrollments en ON en.class_id = ce.class_id AND en.student_username = s.session_id
            WHERE s.action_type = 'ask_ai' AND s.timestamp >= datetime('now', 'localtime', ?)
        """, (class_id, f"-{days} days")).fetchall()
        run_rows = conn.execute("""
            SELECT r.id, r.username AS session_id, r.exercise_id, r.passed_tests, r.all_passed, r.timestamp
            FROM practice_runs r
            JOIN class_exercises ce ON ce.exercise_id = r.exercise_id AND ce.class_id = ?
            JOIN class_enrollments en ON en.class_id = ce.class_id AND en.student_username = r.username
            WHERE r.timestamp >= datetime('now', 'localtime', ?)
        """, (class_id, f"-{days} days")).fetchall()
        submit_ts = {r["id"]: r["timestamp"] for r in conn.execute("""
            SELECT s.id, s.timestamp FROM submissions s
            JOIN class_exercises ce ON ce.exercise_id = s.exercise_id AND ce.class_id = ?
            WHERE s.action_type = 'submit' AND s.timestamp >= datetime('now', 'localtime', ?)
        """, (class_id, f"-{days} days")).fetchall()}
    finally:
        conn.close()

    def pct(part: int, whole: int) -> float:
        return round(part / whole * 100, 1) if whole else 0.0

    total = len(rows)
    passed = sum(1 for r in rows if r["all_passed"] == 1)
    partial = sum(1 for r in rows if r["all_passed"] == 0 and r["passed_tests"] > 0)
    zero_pass = sum(1 for r in rows if r["all_passed"] == 0 and r["passed_tests"] == 0)
    active_students = sorted({r["session_id"] for r in rows})

    # Theo bài tập
    exercise_meta = {e["id"]: dict(e) for e in exercises}
    per_exercise: dict[str, dict[str, Any]] = {}
    per_pair: dict[tuple[str, str], list] = {}
    for r in rows:
        per_pair.setdefault((r["session_id"], r["exercise_id"]), []).append(r)
    for (student, eid), subs in per_pair.items():
        item = per_exercise.setdefault(eid, {"submissions": 0, "unsuccessful": 0, "zero_pass": 0, "partial": 0,
                                             "students_attempted": 0, "students_passed": 0, "first_try_pass": 0})
        item["submissions"] += len(subs)
        item["unsuccessful"] += sum(1 for s in subs if s["all_passed"] == 0)
        item["zero_pass"] += sum(1 for s in subs if s["all_passed"] == 0 and s["passed_tests"] == 0)
        item["partial"] += sum(1 for s in subs if s["all_passed"] == 0 and s["passed_tests"] > 0)
        item["students_attempted"] += 1
        item["students_passed"] += 1 if any(s["all_passed"] == 1 for s in subs) else 0
        item["first_try_pass"] += 1 if subs[0]["all_passed"] == 1 else 0
    bottlenecks = []
    for eid, item in per_exercise.items():
        meta = exercise_meta.get(eid, {"title": eid, "topic": ""})
        bottlenecks.append({
            "exercise_id": eid, "title": meta["title"], "topic": meta.get("topic") or "",
            **item,
            "unsuccessful_percent": pct(item["unsuccessful"], item["submissions"]),
            "completion_percent": pct(item["students_passed"], item["students_attempted"]),
            "avg_submissions_per_student": round(item["submissions"] / item["students_attempted"], 1),
            "dominant_error": ("none" if item["unsuccessful"] == 0 else
                               "syntax_or_runtime" if item["zero_pass"] > item["partial"] else "logic"),
        })
    bottlenecks.sort(key=lambda b: (-b["unsuccessful"], b["completion_percent"], b["exercise_id"]))

    # Phân nhóm quá trình theo từng cặp sinh viên–bài (v5.4): chạy thử + hỏi gợi ý + nộp, theo thứ tự thời gian.
    event_lists: dict[tuple[str, str], list[tuple]] = {}
    for rr in run_rows:
        event_lists.setdefault((rr["session_id"], rr["exercise_id"]), []).append(
            (rr["timestamp"] or "", 0, rr["id"], {"kind": "run", "passed_tests": rr["passed_tests"], "all_passed": bool(rr["all_passed"])}))
    for ar in ask_rows:
        event_lists.setdefault((ar["session_id"], ar["exercise_id"]), []).append(
            (ar["timestamp"] or "", 1, ar["id"], {"kind": "ask", "hint_level": ar["hint_level"]}))
    for r_ in rows:
        event_lists.setdefault((r_["session_id"], r_["exercise_id"]), []).append(
            (submit_ts.get(r_["id"], ""), 2, r_["id"], {"kind": "submit", "passed_tests": r_["passed_tests"],
                                                         "all_passed": r_["all_passed"] == 1}))
    process_by_pair: dict[tuple[str, str], str] = {}
    for pair, evs in event_lists.items():
        group = classify_learning_process([e[3] for e in sorted(evs, key=lambda e: e[:3])])
        if group:
            process_by_pair[pair] = group
    overall_groups = {k: 0 for k in PROCESS_GROUP_KEYS}
    groups_by_exercise: dict[str, dict[str, int]] = {}
    for (_, eid), group in process_by_pair.items():
        overall_groups[group] += 1
        groups_by_exercise.setdefault(eid, {k: 0 for k in PROCESS_GROUP_KEYS})[group] += 1
    process_groups = {
        "definitions": PROCESS_GROUPS,
        "overall": overall_groups,
        "by_exercise": [{"exercise_id": e["id"], "title": e["title"], "topic": e["topic"] or "",
                         "groups": groups_by_exercise[e["id"]]} for e in exercises if e["id"] in groups_by_exercise],
        "pairs": len(process_by_pair),
        "practice_runs": len(run_rows),
    }
    process_students = sorted({stu for stu, _ in process_by_pair})

    # Theo sinh viên (chỉ hiển thị cho giảng viên sở hữu lớp; không đưa vào LLM)
    name_map = {e["username"]: e["full_name"] for e in enrolled}
    students = []
    for student in sorted(set(active_students) | set(process_students)):
        pairs = {eid: subs for (stu, eid), subs in per_pair.items() if stu == student}
        process_by_exercise = {eid: grp for (stu, eid), grp in process_by_pair.items() if stu == student}
        stuck = [eid for eid, grp in process_by_exercise.items() if grp == "stuck"]
        distinct = len(pairs)
        submissions = sum(len(subs) for subs in pairs.values())
        unsuccessful = sum(1 for subs in pairs.values() for s in subs if s["all_passed"] == 0)
        students.append({
            "username": student, "full_name": name_map.get(student, student),
            "distinct_exercises": distinct, "submissions": submissions, "unsuccessful": unsuccessful,
            "exercises_passed": sum(1 for subs in pairs.values() if any(s["all_passed"] == 1 for s in subs)),
            "stuck_exercises": [{"exercise_id": eid, "title": exercise_meta.get(eid, {}).get("title", eid)} for eid in sorted(stuck)],
            "needs_support": bool(stuck),
            "process_by_exercise": process_by_exercise,
            "data_status": "limited" if distinct < 3 else "sufficient",
        })
    students.sort(key=lambda s: (not s["needs_support"], -len(s["stuck_exercises"]), -s["unsuccessful"], s["username"]))
    inactive = [e["username"] for e in enrolled if e["username"] not in set(active_students) | set(process_students)]

    data_status = "no_data" if total == 0 else ("limited" if len(active_students) < 3 else "sufficient")
    caveats = [
        "Số lượt nộp, phân bố kết quả và bài nghẽn chỉ tính lượt Nộp bài chính thức. Nhóm quá trình dùng thêm lượt Chạy thử và Hỏi Gia sư AI, và chỉ là bằng chứng mô tả, không phải điểm hay metric chính thức của sinh viên.",
        "Lượt Chạy thử chỉ được ghi từ phiên bản v5.4; dữ liệu trước đó không có nên nhóm quá trình của giai đoạn cũ có thể bị đánh giá thấp (ví dụ thiếu lượt thử).",
        "Tỷ lệ 'đạt ngay lần đầu' tính theo lượt nộp đầu tiên trong khoảng thời gian đang xem, có thể không phải lượt đầu tiên từ trước tới nay.",
        "Phân loại lỗi dựa trên số kiểm thử đạt: không đạt kiểm thử nào (thường là lỗi cú pháp/runtime) và đạt một phần (thường là lỗi logic/biên); đây là phân loại gần đúng.",
        f"Ngưỡng 'mẫu nhỏ' (< 3) và nhóm quá trình (Mắc kẹt = ≥ {PROCESS_STUCK_MIN_ATTEMPTS} lượt chạy thử + nộp mà số test đạt tốt nhất không tăng trong {PROCESS_PROGRESS_WINDOW} lượt gần nhất; Đạt độc lập = ≤ {PROCESS_INDEPENDENT_MAX_SUBMITS} lượt nộp, gợi ý ≤ 1) là quy ước vận hành, chưa hiệu chuẩn và chưa kiểm chứng giáo dục.",
    ]
    if data_status == "limited":
        caveats.insert(0, "Dưới 3 sinh viên có hoạt động trong khoảng này: số liệu chỉ mang tính mô tả, chưa đại diện cho lớp.")
    try:
        extras = _class_insights_extras(class_id, days, {e["id"]: e["title"] for e in exercises},
                                        sorted(set(active_students) | set(process_students)))
    except Exception as exc:  # noqa: BLE001 - phần bổ sung không được làm hỏng insights cũ
        logger.warning("Không tính được số liệu bổ sung của lớp %s: %s", class_id, exc)
        extras = {}
    result = {
        "class": dict(class_row), "days": days, "data_status": data_status,
        "sample": {"submissions": total, "active_students": len(active_students), "enrolled_students": len(enrolled),
                   "inactive_students": len(inactive), "exercises_attempted": len(per_exercise),
                   "exercises_in_class": len(exercises)},
        "pass_rate": pct(passed, total),
        "process_groups": process_groups,
        "error_mix": {"passed": passed, "partial": partial, "zero_pass": zero_pass,
                      "passed_percent": pct(passed, total), "partial_percent": pct(partial, total),
                      "zero_pass_percent": pct(zero_pass, total)},
        "bottlenecks": bottlenecks,
        "students": students,
        "students_needing_support": sum(1 for s in students if s["needs_support"]),
        "caveats": caveats,
    }
    result.update(extras)
    # v5.8: ma trận SV × bài, dựng từ chính process_by_pair (không tính lại nhóm); chỉ thêm khóa.
    pass_groups = {"independent_pass", "retry_pass", "hint_pass"}
    matrix_exercises = []
    for e in exercises:
        pairs_e = [g for (_, eid_), g in process_by_pair.items() if eid_ == e["id"]]
        matrix_exercises.append({
            "exercise_id": e["id"], "title": e["title"], "topic": e["topic"] or "", "order_idx": e["order_idx"],
            "students_passed": sum(1 for g in pairs_e if g in pass_groups),
            "students_attempted": len(pairs_e), "students_enrolled": len(enrolled)})
    matrix_rows = [
        {"username": en["username"], "full_name": en["full_name"],
         "cells": {e["id"]: process_by_pair.get((en["username"], e["id"])) for e in exercises}}
        for en in sorted(enrolled, key=lambda x: ((x["full_name"] or "").casefold(), x["username"]))]
    result["matrix"] = {"exercises": matrix_exercises, "rows": matrix_rows, "group_keys": list(PROCESS_GROUP_KEYS)}
    return result


def _load_json_list(text: Any) -> list:
    try:
        val = json.loads(text) if text else []
        return val if isinstance(val, list) else []
    except (TypeError, ValueError):
        return []


def _is_format_only(failed_text: Any, mismatch_text: Any) -> bool:
    failed, mism = _load_json_list(failed_text), set(_load_json_list(mismatch_text))
    return bool(failed) and set(failed) == mism


def get_exercise_journey(username: str, exercise_id: str, days: Optional[int] = None, limit: int = 60,
                         include_code: bool = False) -> dict[str, Any]:
    """v5.8: dấu chân (chạy thử + hỏi AI + nộp) của MỘT cặp sinh viên–bài, chỉ đọc.

    `days=None` là toàn bộ lịch sử (màn sinh viên); có `days` thì dùng đúng cửa sổ của ma trận lớp để nhóm khớp nhau.
    `include_code=True` chỉ dành cho chính sinh viên; phía giảng viên không nhận mã nguồn.
    """
    window_sql, window_args = "", ()
    if days is not None:
        window_sql, window_args = " AND {col} >= datetime('now', 'localtime', ?)", (f"-{_clamp_days(days)} days",)
    conn = get_db_connection()
    try:
        sub_rows = conn.execute(f"""
            SELECT s.id, s.action_type, s.hint_level, s.passed_tests, s.total_tests, s.all_passed, s.timestamp, s.code,
                   f.failed_tests, f.format_mismatch_tests
            FROM submissions s LEFT JOIN attempt_features f ON f.submission_id = s.id
            WHERE s.session_id = ? AND s.exercise_id = ?{window_sql.format(col='s.timestamp')}
            ORDER BY s.id ASC
        """, (username, exercise_id) + window_args).fetchall()
        run_rows = conn.execute(f"""
            SELECT r.id, r.passed_tests, r.total_tests, r.all_passed, r.timestamp, r.failed_tests, r.format_mismatch_tests
            FROM practice_runs r WHERE r.username = ? AND r.exercise_id = ?{window_sql.format(col='r.timestamp')}
            ORDER BY r.id ASC
        """, (username, exercise_id) + window_args).fetchall()
        first_run = conn.execute("SELECT MIN(timestamp) FROM practice_runs").fetchone()[0]
        title_row = conn.execute("SELECT title FROM exercises WHERE id = ?", (exercise_id,)).fetchone()
    finally:
        conn.close()

    events: list[dict[str, Any]] = []
    code_by_sub: dict[int, str] = {}
    for r in run_rows:
        events.append({"kind": "run", "id": r["id"], "timestamp": r["timestamp"], "passed_tests": r["passed_tests"],
                       "total_tests": r["total_tests"], "all_passed": bool(r["all_passed"]),
                       "format_only": _is_format_only(r["failed_tests"], r["format_mismatch_tests"])})
    for r in sub_rows:
        if r["action_type"] == "ask_ai":
            events.append({"kind": "ask", "id": r["id"], "timestamp": r["timestamp"], "hint_level": r["hint_level"],
                           "passed_tests": r["passed_tests"], "total_tests": r["total_tests"], "submission_id": r["id"]})
        elif r["action_type"] == "submit":
            events.append({"kind": "submit", "id": r["id"], "timestamp": r["timestamp"], "passed_tests": r["passed_tests"],
                           "total_tests": r["total_tests"], "all_passed": r["all_passed"] == 1, "submission_id": r["id"],
                           "format_only": _is_format_only(r["failed_tests"], r["format_mismatch_tests"])})
            code_by_sub[r["id"]] = r["code"]
    events.sort(key=process_event_sort_key)
    built = build_journey_points(events)
    points, summary = built["points"], built["summary"]
    total_points = len(points)
    cut = max(0, total_points - max(1, limit))
    if cut:
        points = points[cut:]
        fp = summary["first_pass_index"]
        summary["first_pass_index"] = fp - cut if fp is not None and fp >= cut else None
    if include_code:
        for p in points:
            if p["kind"] == "submit" and p.get("submission_id") in code_by_sub:
                p["code"] = code_by_sub[p["submission_id"]]
    first_event_ts = events[0]["timestamp"] if events else None
    return {
        "exercise_id": exercise_id, "title": (title_row["title"] if title_row else None) or exercise_id,
        "points": points, "summary": summary, "total_points": total_points, "truncated": bool(cut),
        "runs_recorded_from": first_run,
        "has_events_before_runs": bool(first_run and first_event_ts and first_event_ts < first_run),
    }


def get_student_journey_overview(username: str, class_id: Optional[str] = None, recent_limit: int = 5) -> dict[str, Any]:
    """v5.8: tối đa N bài hoạt động gần nhất (dấu chân rút gọn) và số bài nộp đạt lần đầu tuần này / tuần trước."""
    scope_sql, scope_args = "", ()
    if class_id:
        scope_sql, scope_args = " AND exercise_id IN (SELECT exercise_id FROM class_exercises WHERE class_id = ?)", (class_id,)
    conn = get_db_connection()
    try:
        recent = conn.execute(f"""
            SELECT exercise_id, MAX(ts) AS last_ts FROM (
                SELECT exercise_id, timestamp AS ts FROM submissions
                WHERE session_id = ? AND action_type IN ('submit', 'ask_ai'){scope_sql}
                UNION ALL
                SELECT exercise_id, timestamp AS ts FROM practice_runs WHERE username = ?{scope_sql}
            ) GROUP BY exercise_id ORDER BY last_ts DESC, exercise_id ASC LIMIT ?
        """, (username,) + scope_args + (username,) + scope_args + (recent_limit,)).fetchall()
        week = conn.execute(f"""
            SELECT COALESCE(SUM(first_ts >= datetime('now', 'localtime', '-7 days')), 0) AS this_week,
                   COALESCE(SUM(first_ts >= datetime('now', 'localtime', '-14 days')
                                AND first_ts < datetime('now', 'localtime', '-7 days')), 0) AS prev_week
            FROM (SELECT MIN(timestamp) AS first_ts FROM submissions
                  WHERE session_id = ? AND action_type = 'submit' AND all_passed = 1{scope_sql}
                  GROUP BY exercise_id)
        """, (username,) + scope_args).fetchone()
    finally:
        conn.close()
    exercises = []
    for r in recent:
        j = get_exercise_journey(username, r["exercise_id"], limit=12)
        exercises.append({"exercise_id": r["exercise_id"], "title": j["title"], "last_activity": r["last_ts"],
                          "group": j["summary"]["group"], "best": j["summary"]["best"],
                          "counts": j["summary"]["counts"], "points": j["points"],
                          "first_pass_at": j["summary"].get("first_pass_at"),
                          "attempts_to_first_pass": j["summary"].get("attempts_to_first_pass")})
    return {"week": {"this": int(week["this_week"] or 0), "prev": int(week["prev_week"] or 0)},
            "recent_exercises": exercises}


def get_class_learning_summary(class_id: str, days: int = 7) -> dict[str, Any]:
    """Read-only aggregate for instructor AI; never exposes raw student code or identities.

    Dẫn xuất từ get_class_insights nhưng loại bỏ toàn bộ thông tin theo từng sinh viên.
    """
    insights = get_class_insights(class_id, days)
    if not insights:
        return {}
    sample = insights["sample"]
    topics: dict[str, dict[str, Any]] = {}
    for item in insights["bottlenecks"]:
        topic = topics.setdefault(item["topic"] or "Chưa gán chủ đề", {"topic": item["topic"] or "Chưa gán chủ đề",
                                                                     "attempts": 0, "unsuccessful": 0})
        topic["attempts"] += item["submissions"]
        topic["unsuccessful"] += item["unsuccessful"]
    metrics = {
        "submissions": sample["submissions"],
        "passed": insights["error_mix"]["passed"],
        "active_students": sample["active_students"],
        "enrolled_students": sample["enrolled_students"],
        "exercises_attempted": sample["exercises_attempted"],
        "pass_rate": insights["pass_rate"],
        "data_status": insights["data_status"],
        "sample_size": sample["active_students"],
        "students_needing_support": insights["students_needing_support"],
    }
    aggregate_keys = ("exercise_id", "title", "topic", "submissions", "unsuccessful", "unsuccessful_percent",
                      "students_attempted", "students_passed", "completion_percent",
                      "avg_submissions_per_student", "dominant_error")
    return {
        "class": insights["class"], "days": insights["days"], "metrics": metrics,
        "topics": sorted(topics.values(), key=lambda t: (-t["unsuccessful"], -t["attempts"]))[:8],
        "error_mix": insights["error_mix"],
        "process_groups": {"definitions": insights["process_groups"]["definitions"],
                           "overall": insights["process_groups"]["overall"],
                           "pairs": insights["process_groups"]["pairs"]},
        "bottlenecks": [{key: item[key] for key in aggregate_keys} for item in insights["bottlenecks"][:5]],
        "caveats": insights["caveats"],
    }


def get_tutor_feedback_summary(instructor_username: str, days: int = 30) -> dict[str, Any]:
    """Tổng hợp đánh giá 👍/👎 theo loại tác vụ cho sinh viên thuộc các lớp của giảng viên.

    Chỉ trả về số đếm; không có nội dung phản hồi, mã nguồn hay danh tính người đánh giá.
    """
    days = _clamp_days(days)
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT li.task_type AS task_type,
                   COUNT(*) AS interactions,
                   SUM(CASE WHEN tf.rating = 1 THEN 1 ELSE 0 END) AS helpful,
                   SUM(CASE WHEN tf.rating = -1 THEN 1 ELSE 0 END) AS not_helpful,
                   SUM(CASE WHEN li.status IN ('fallback', 'blocked', 'blocked_fallback') THEN 1 ELSE 0 END) AS fallback_or_blocked
            FROM llm_interactions li
            LEFT JOIN tutor_feedback tf ON tf.interaction_id = li.id
            WHERE li.role = 'student'
              AND li.created_at >= datetime('now', 'localtime', ?)
              AND li.username IN (
                  SELECT en.student_username FROM class_enrollments en
                  JOIN credit_classes c ON c.id = en.class_id
                  WHERE c.instructor_username = ?)
            GROUP BY li.task_type ORDER BY li.task_type
        """, (f"-{days} days", instructor_username)).fetchall()
    finally:
        conn.close()
    by_task = []
    for row in rows:
        item = dict(row)
        item["helpful"] = item["helpful"] or 0
        item["not_helpful"] = item["not_helpful"] or 0
        item["rated"] = item["helpful"] + item["not_helpful"]
        item["helpful_percent"] = round(item["helpful"] / item["rated"] * 100, 1) if item["rated"] else None
        by_task.append(item)
    total_rated = sum(item["rated"] for item in by_task)
    return {
        "days": days,
        "by_task": by_task,
        "total_interactions": sum(item["interactions"] for item in by_task),
        "total_rated": total_rated,
        "data_status": "no_data" if total_rated == 0 else ("limited" if total_rated < 10 else "sufficient"),
        "note": "Đánh giá là tự nguyện nên chỉ phản ánh những phản hồi được chấm; ngưỡng 10 lượt là quy ước vận hành.",
    }


def get_autonomy_hint_context(username: str, exercise_id: str) -> dict[str, Any]:
    """Ngữ cảnh tính sao tự lực của một bài, đọc trên TOÀN BỘ lịch sử (không giới hạn N lượt gần nhất).

    - `max_hint_level_used`: mức gợi ý cao nhất ở các lượt `ask_ai` cho tới lần `submit` pass đầu tiên
      (chưa từng pass thì tính mọi lượt `ask_ai`). `hint_level` của lượt `submit` không được gộp;
      lượt `ask_ai` bị EXAM guard khóa không tính vì người học không nhận được gợi ý.
    - `has_passed_before`: đã có lượt `submit` pass → các lượt nộp lại chỉ là ôn tập, không đổi mức sao.
    Gọi hàm này TRƯỚC khi lưu lượt nộp hiện tại.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MIN(id) AS first_pass_id FROM submissions
            WHERE session_id = ? AND exercise_id = ? AND action_type = 'submit' AND all_passed = 1
        """, (username, exercise_id))
        first_pass_id = cursor.fetchone()["first_pass_id"]
        bound_sql, params = "", [username, exercise_id]
        if first_pass_id is not None:
            bound_sql = " AND id < ?"
            params.append(first_pass_id)
        cursor.execute(f"""
            SELECT COALESCE(MAX(hint_level), 1) AS max_hint, COUNT(*) AS ask_ai_count FROM submissions
            WHERE session_id = ? AND exercise_id = ? AND action_type = 'ask_ai'
              AND COALESCE(llm_source, '') != 'Exam-Mode-Guard'{bound_sql}
        """, params)
        hint_row = cursor.fetchone()
        cursor.execute("""
            SELECT COUNT(*) AS submit_count FROM submissions
            WHERE session_id = ? AND exercise_id = ? AND action_type = 'submit'
        """, (username, exercise_id))
        submit_count = cursor.fetchone()["submit_count"]
    finally:
        conn.close()
    return {
        "max_hint_level_used": max(1, min(int(hint_row["max_hint"] or 1), 3)),
        "ask_ai_count": int(hint_row["ask_ai_count"] or 0),
        "submit_count": int(submit_count or 0),
        "has_passed_before": first_pass_id is not None,
    }


def get_latest_passed_submission_code(username: str, exercise_id: str) -> Optional[str]:
    """Code của lượt `submit` pass gần nhất ở bài này; None nếu chưa từng nộp pass (dùng để khóa phạm vi chat)."""
    conn = get_db_connection()
    try:
        row = conn.execute("""
            SELECT code FROM submissions
            WHERE session_id = ? AND exercise_id = ? AND action_type = 'submit' AND all_passed = 1
            ORDER BY id DESC LIMIT 1
        """, (username, exercise_id)).fetchone()
    finally:
        conn.close()
    return row["code"] if row else None


def explain_autonomy_stars(stars: int, max_hint_level_used: int, attempt_count: int,
                           has_passed_before: bool = False) -> dict[str, Any]:
    """Giải thích tường minh vì sao bài nộp nhận số sao này (đi kèm calculate_autonomy_stars)."""
    hint_names = {1: "không dùng gợi ý hoặc chỉ Mức 1 (gợi mở)", 2: "Mức 2 (chẩn đoán lỗi)", 3: "Mức 3 (dàn ý và khung code)"}
    level = max(1, min(int(max_hint_level_used or 1), 3))
    if stars >= 3:
        improve = "Đây là mức cao nhất. Bạn có thể thử Thử thách tối ưu code Pythonic."
    elif stars == 2:
        improve = ("Để đạt 3 sao ở các bài tiếp theo: tự giải và chỉ dùng gợi ý Mức 1 hoặc không cần gợi ý. "
                   "Sao của bài này đã chốt theo mức gợi ý đã dùng trước lần nộp đạt đầu tiên; làm lại bài chỉ để ôn tập.")
    else:
        improve = ("Để đạt 2–3 sao ở các bài tiếp theo: thử dừng ở gợi ý Mức 2 hoặc Mức 1 trước khi nộp. "
                   "Sao của bài này đã chốt theo mức gợi ý đã dùng trước lần nộp đạt đầu tiên; làm lại bài chỉ để ôn tập.")
    explanation = (f"Bạn vượt qua toàn bộ kiểm thử; mức gợi ý cao nhất bạn đã dùng ở nút Hỏi Gia sư AI trước lần nộp đạt "
                   f"đầu tiên của bài này là {hint_names[level]}, nên nhận {stars} sao.")
    if has_passed_before:
        explanation += " Bạn đã nộp đạt bài này từ trước, nên lượt nộp lại này là ôn tập và không thay đổi mức sao."
    return {
        "stars": stars,
        "max_hint_level_used": level,
        "attempt_count": attempt_count,
        "is_review_resubmission": bool(has_passed_before),
        "explanation": explanation,
        "rule": [
            {"stars": 3, "condition": "Vượt qua 100% kiểm thử, mức gợi ý cao nhất là Mức 1 hoặc không dùng"},
            {"stars": 2, "condition": "Vượt qua 100% kiểm thử, có dùng gợi ý Mức 2"},
            {"stars": 1, "condition": "Vượt qua 100% kiểm thử, có dùng gợi ý Mức 3"},
        ],
        "how_to_improve": improve,
        "note": ("Số lần nộp không làm giảm sao. Mức gợi ý được tính trên toàn bộ các lượt Hỏi Gia sư AI cho tới lần nộp đạt đầu tiên; "
                 "nộp lại sau đó không làm tăng sao. "
                 "Sao tự lực là quy ước của PyTutor về mức hỗ trợ đã dùng, không phải điểm học phần hay thang đo năng lực đã kiểm chứng."),
    }


# ==============================================================================
# HÀM QUẢN LÝ BÀI TẬP VÀ CÂY KỸ NĂNG THEO LỚP (CLASS CURRICULUM & SKILL TREE)
# ==============================================================================

def get_class_exercises(class_id: str, student_username: Optional[str] = None) -> list[dict]:
    """
    Lấy danh sách các bài tập thuộc một Lớp học phần kèm cấu hình Lộ trình kỹ năng (Curriculum).
    Nếu có student_username, tính toán trạng thái theo kết quả hoàn thành bài:
    - MASTERED: Đã pass 100% test cases (số sao không phải điều kiện mở khóa)
    - IN_PROGRESS: Đã thử nộp nhưng chưa pass 100%
    - AVAILABLE: Chưa nộp, nhưng không có bài tiên quyết HOẶC bài tiên quyết đã MASTERED
    - LOCKED: Chưa nộp và bài tiên quyết chưa MASTERED
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ce.id as class_exercise_id, ce.class_id, ce.exercise_id, ce.module_name, ce.order_idx,
               ce.prerequisite_id, ce.min_stars_required, ce.skill_tag, ce.weight_point, ce.added_at,
               e.title, e.difficulty, e.category, e.description, e.test_cases
        FROM class_exercises ce
        JOIN exercises e ON ce.exercise_id = e.id
        WHERE ce.class_id = ?
        ORDER BY ce.order_idx ASC, ce.id ASC
    """, (class_id,))
    rows = cursor.fetchall()

    if not rows:
        conn.close()
        return []

    passed_exercises = {}
    student_stars = {}
    attempted_exercises = set()

    if student_username:
        cursor.execute("""
            SELECT exercise_id, MAX(all_passed) as has_passed, COUNT(*) as attempts
            FROM submissions
            WHERE session_id = ?
            GROUP BY exercise_id
        """, (student_username,))
        for r in cursor.fetchall():
            attempted_exercises.add(r["exercise_id"])
            if r["has_passed"] == 1:
                passed_exercises[r["exercise_id"]] = True

        cursor.execute("SELECT exercise_id, stars_earned FROM user_exercise_stars WHERE username = ?", (student_username,))
        for r in cursor.fetchall():
            student_stars[r["exercise_id"]] = r["stars_earned"]

    conn.close()

    mastered_set = set(passed_exercises)
    mastered_set.update(eid for eid, stars in student_stars.items() if stars > 0)

    items = []
    for r in rows:
        eid = r["exercise_id"]
        st_stars = student_stars.get(eid, 0)
        prereq = r["prerequisite_id"]

        try:
            tc_count = len(json.loads(r["test_cases"]))
        except Exception:
            tc_count = 0

        if eid in mastered_set:
            status_val = "MASTERED"
            status_desc = f"Đã hoàn thành bài ({st_stars} ⭐ tự lực)" if st_stars else "Đã vượt qua tất cả bộ kiểm thử"
        elif eid in attempted_exercises:
            status_val = "IN_PROGRESS"
            status_desc = "Đang thực hành (Chưa vượt qua tất cả test cases)"
        else:
            if not prereq or prereq in mastered_set:
                status_val = "AVAILABLE"
                status_desc = "Sẵn sàng làm bài"
            else:
                status_val = "LOCKED"
                status_desc = f"Khóa - Cần hoàn thành bài tiên quyết ({prereq})"

        items.append({
            "class_exercise_id": r["class_exercise_id"],
            "class_id": r["class_id"],
            "exercise_id": eid,
            "id": eid,
            "title": r["title"],
            "difficulty": r["difficulty"],
            "category": r["category"],
            "description": r["description"],
            "test_cases_count": tc_count,
            "module_name": r["module_name"],
            "order_idx": r["order_idx"],
            "prerequisite_id": prereq,
            "min_stars_required": 0,
            "skill_tag": r["skill_tag"],
            "weight_point": r["weight_point"],
            "stars_earned": st_stars,
            "status": status_val,
            "status_description": status_desc,
            "is_unlocked": status_val != "LOCKED"
        })

    return items


def add_exercise_to_class(
    class_id: str,
    exercise_id: str,
    module_name: str = "Chương 1: Cơ sở lập trình Python",
    order_idx: Optional[int] = None,
    prerequisite_id: Optional[str] = None,
    skill_tag: str = "Tư duy thuật toán",
    weight_point: int = 10
) -> dict:
    """Giảng viên gán một bài tập vào lớp; cột rubric cũ được giữ ở giá trị trung tính."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if order_idx is None:
        cursor.execute("SELECT COALESCE(MAX(order_idx), 0) + 1 FROM class_exercises WHERE class_id = ?", (class_id,))
        order_idx = cursor.fetchone()[0]

    cursor.execute("""
        INSERT OR REPLACE INTO class_exercises (
            class_id, exercise_id, module_name, order_idx, prerequisite_id, min_stars_required, skill_tag, weight_point
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (class_id, exercise_id, module_name, order_idx, prerequisite_id, 0, skill_tag, weight_point))
    conn.commit()
    conn.close()
    return {
        "class_id": class_id,
        "exercise_id": exercise_id,
        "module_name": module_name,
        "order_idx": order_idx,
        "prerequisite_id": prerequisite_id,
        "min_stars_required": 0,
        "skill_tag": skill_tag,
        "weight_point": weight_point
    }


def update_class_exercise(
    class_id: str,
    exercise_id: str,
    module_name: Optional[str] = None,
    order_idx: Optional[int] = None,
    prerequisite_id: Optional[str] = None,
    skill_tag: Optional[str] = None,
    weight_point: Optional[int] = None
) -> bool:
    """Giảng viên cập nhật thông tin bài tập trong lớp học phần."""
    conn = get_db_connection()
    cursor = conn.cursor()

    updates = []
    params = []
    if module_name is not None:
        updates.append("module_name = ?")
        params.append(module_name)
    if order_idx is not None:
        updates.append("order_idx = ?")
        params.append(order_idx)
    if prerequisite_id is not None:
        updates.append("prerequisite_id = ?")
        params.append(prerequisite_id if prerequisite_id != "" else None)
    if skill_tag is not None:
        updates.append("skill_tag = ?")
        params.append(skill_tag)
    if weight_point is not None:
        updates.append("weight_point = ?")
        params.append(weight_point)

    if not updates:
        conn.close()
        return True

    params.extend([class_id, exercise_id])
    query = f"UPDATE class_exercises SET {', '.join(updates)} WHERE class_id = ? AND exercise_id = ?"
    cursor.execute(query, params)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def remove_exercise_from_class(class_id: str, exercise_id: str) -> bool:
    """Giảng viên gỡ bài tập khỏi Lớp học phần."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM class_exercises WHERE class_id = ? AND exercise_id = ?", (class_id, exercise_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def get_exercise_class_info(
    exercise_id: str,
    student_username: Optional[str] = None,
    preferred_class_id: Optional[str] = None,
) -> Optional[dict]:
    """Tìm thông tin lớp học phần chứa exercise_id, ưu tiên preferred_class_id hoặc lớp sinh viên đang học."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if preferred_class_id:
            cursor.execute("""
                SELECT c.id, c.class_name, c.class_code, c.semester
                FROM class_exercises ce
                JOIN credit_classes c ON c.id = ce.class_id
                WHERE ce.exercise_id = ? AND ce.class_id = ?
                LIMIT 1
            """, (exercise_id, preferred_class_id))
            row = cursor.fetchone()
            if row:
                return dict(row)

        if student_username:
            cursor.execute("""
                SELECT c.id, c.class_name, c.class_code, c.semester
                FROM class_exercises ce
                JOIN credit_classes c ON c.id = ce.class_id
                JOIN class_enrollments en ON en.class_id = ce.class_id
                WHERE ce.exercise_id = ? AND en.student_username = ?
                ORDER BY c.created_at DESC
                LIMIT 1
            """, (exercise_id, student_username))
            row = cursor.fetchone()
            if row:
                return dict(row)

        cursor.execute("""
            SELECT c.id, c.class_name, c.class_code, c.semester
            FROM class_exercises ce
            JOIN credit_classes c ON c.id = ce.class_id
            WHERE ce.exercise_id = ?
            ORDER BY c.created_at DESC
            LIMIT 1
        """, (exercise_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_exam_sessions(
    class_id: Optional[str] = None,
    session_type: Optional[str] = None,
    active_only: bool = True
) -> list[dict]:
    """Lấy danh sách các Đợt thực hành & Kỳ thi (kèm thông tin lớp và chi tiết bài tập)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT s.*, c.class_name, c.class_code
        FROM exam_sessions s
        JOIN credit_classes c ON s.class_id = c.id
        WHERE 1=1
    """
    params = []
    if active_only:
        query += " AND s.is_active = 1"
    if class_id:
        query += " AND s.class_id = ?"
        params.append(class_id)
    if session_type:
        query += " AND s.session_type = ?"
        params.append(session_type.upper())
    query += " ORDER BY s.created_at DESC, s.id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Pre-cache exercises to attach details
    cursor.execute("SELECT id, title, difficulty, category, test_cases FROM exercises")
    all_ex_rows = cursor.fetchall()
    ex_dict = {}
    for er in all_ex_rows:
        try:
            tc_cnt = len(json.loads(er["test_cases"]))
        except Exception:
            tc_cnt = 0
        ex_dict[er["id"]] = {
            "id": er["id"],
            "title": er["title"],
            "difficulty": er["difficulty"],
            "category": er["category"],
            "test_cases_count": tc_cnt
        }

    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        raw_ids = item.get("exercise_ids", "[]")
        try:
            ex_ids = json.loads(raw_ids) if isinstance(raw_ids, str) else raw_ids
        except Exception:
            ex_ids = []
        item["exercise_ids"] = ex_ids
        item["exercises"] = [ex_dict[eid] for eid in ex_ids if eid in ex_dict]
        item["is_active"] = bool(item["is_active"])
        item["allow_ai_hints"] = int(item["allow_ai_hints"])
        result.append(item)
    return result


def get_exam_session_by_id(session_id: str) -> Optional[dict]:
    """Lấy chi tiết một Kỳ thi hoặc Đợt thực hành theo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, c.class_name, c.class_code
        FROM exam_sessions s
        JOIN credit_classes c ON s.class_id = c.id
        WHERE s.id = ?
    """, (session_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    item = dict(row)
    raw_ids = item.get("exercise_ids", "[]")
    try:
        ex_ids = json.loads(raw_ids) if isinstance(raw_ids, str) else raw_ids
    except Exception:
        ex_ids = []
    item["exercise_ids"] = ex_ids
    item["is_active"] = bool(item["is_active"])
    item["allow_ai_hints"] = int(item["allow_ai_hints"])

    cursor.execute("SELECT id, title, difficulty, category, test_cases FROM exercises")
    all_ex_rows = cursor.fetchall()
    conn.close()

    ex_dict = {}
    for er in all_ex_rows:
        try:
            tc_cnt = len(json.loads(er["test_cases"]))
        except Exception:
            tc_cnt = 0
        ex_dict[er["id"]] = {
            "id": er["id"],
            "title": er["title"],
            "difficulty": er["difficulty"],
            "category": er["category"],
            "test_cases_count": tc_cnt
        }
    item["exercises"] = [ex_dict[eid] for eid in ex_ids if eid in ex_dict]
    return item


def create_exam_session(
    title: str,
    class_id: str,
    session_type: str,
    exercise_ids: list[str],
    duration_minutes: int = 45,
    allow_ai_hints: int = 1,
    created_by: str = "gv_tran",
    session_id: Optional[str] = None
) -> dict:
    """Tạo mới một Kỳ thi hoặc Đợt thực hành."""
    import uuid
    s_type = session_type.upper()
    if not session_id:
        prefix = "exam" if s_type == "EXAM" else "sess"
        session_id = f"{prefix}_{str(uuid.uuid4())[:8]}"

    # Chế độ EXAM mặc định khóa gợi ý (0) nếu không chỉ định rõ
    if s_type == "EXAM" and (allow_ai_hints is None or allow_ai_hints == 1):
        # nếu người dùng không chọn allow_ai_hints=1 rõ ràng, trong EXAM mặc định = 0
        pass

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO exam_sessions (
            id, title, class_id, session_type, exercise_ids, duration_minutes, allow_ai_hints, is_active, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (
        session_id,
        title,
        class_id,
        s_type,
        json.dumps(exercise_ids, ensure_ascii=False),
        duration_minutes,
        allow_ai_hints,
        created_by
    ))
    conn.commit()
    conn.close()
    return get_exam_session_by_id(session_id) or {
        "id": session_id,
        "title": title,
        "class_id": class_id,
        "session_type": s_type,
        "exercise_ids": exercise_ids,
        "exercises": [],
        "duration_minutes": duration_minutes,
        "allow_ai_hints": allow_ai_hints,
        "is_active": True,
        "created_by": created_by
    }


def delete_exam_session(session_id: str) -> bool:
    """Giảng viên xóa một Kỳ thi / Đợt thực hành."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exam_sessions WHERE id = ?", (session_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

