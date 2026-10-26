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
from pathlib import Path
from typing import Optional, Any

logger = logging.getLogger("pytutor.database")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "pytutor.db"


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
            timestamp TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

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
                (u_name, u_pass, u_role, u_fullname)
            )
        else:
            cursor.execute(
                "UPDATE users SET full_name = ?, role = ? WHERE username = ?",
                (u_fullname, u_role, u_name)
            )
    conn.commit()

    # Nạp 5 bài tập mẫu ban đầu từ mcp_server.exercises_data nếu bảng exercises trống
    cursor.execute("SELECT COUNT(*) FROM exercises")
    if cursor.fetchone()[0] == 0:
        try:
            from mcp_server.exercises_data import EXERCISES
            for ex in EXERCISES:
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

def get_all_exercises(include_inactive: bool = False) -> list[dict]:
    """Lấy danh sách tóm tắt tất cả bài tập."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if include_inactive:
        cursor.execute("SELECT id, title, difficulty, category, test_cases, is_active FROM exercises ORDER BY id ASC")
    else:
        cursor.execute("SELECT id, title, difficulty, category, test_cases FROM exercises WHERE is_active = 1 ORDER BY id ASC")
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
        "SELECT id, title, difficulty, category, description, starter_code, test_cases, is_active FROM exercises WHERE id = ?",
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
        "is_active": bool(row["is_active"])
    }


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
    tutor_hint: str
) -> int:
    """Lưu sự kiện học tập và lịch sử nộp bài vào SQLite."""
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
    conn.commit()
    conn.close()
    return submission_id


def get_attempts(session_id: str, exercise_id: str, limit: int = 5) -> list[dict]:
    """Lấy danh sách các lần nộp gần nhất của sinh viên cho bài tập cụ thể kèm mã nguồn đã nộp."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, code, hint_level, passed_tests, total_tests, all_passed, llm_source, tutor_hint, timestamp
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
            "timestamp": r["timestamp"]
        }
        for r in rows
    ]


def get_all_submissions(limit: int = 100) -> list[dict]:
    """Lấy danh sách các lần nộp bài mới nhất phục vụ Dashboard Giảng viên (kèm code & tutor_hint)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.session_id, s.exercise_id, e.title as exercise_title,
               s.code, s.hint_level, s.passed_tests, s.total_tests, s.all_passed,
               s.llm_source, s.tutor_hint, s.timestamp
        FROM submissions s
        LEFT JOIN exercises e ON s.exercise_id = e.id
        ORDER BY s.id DESC
        LIMIT ?
    """, (limit,))
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


def get_submission_by_id(submission_id: int) -> Optional[dict]:
    """Lấy chi tiết đầy đủ của một bài nộp theo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.session_id, s.exercise_id, e.title as exercise_title,
               s.code, s.hint_level, s.passed_tests, s.total_tests, s.all_passed,
               s.llm_source, s.tutor_hint, s.timestamp
        FROM submissions s
        LEFT JOIN exercises e ON s.exercise_id = e.id
        WHERE s.id = ?
    """, (submission_id,))
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
        WHERE session_id = ?
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
                SELECT ce.exercise_id as id, ce.module_name as category, e.title, ce.min_stars_required
                FROM class_exercises ce
                JOIN exercises e ON ce.exercise_id = e.id
                WHERE ce.class_id = ?
                ORDER BY ce.order_idx ASC
            """, (class_id,))
            ex_meta_rows = [dict(r) for r in cursor.fetchall()]
        else:
            cursor.execute("SELECT id, title, category FROM exercises WHERE is_active = 1")
            ex_meta_rows = [dict(r) for r in cursor.fetchall()]
    except Exception:
        ex_meta_rows = []

    conn.close()

    # Áp dụng bộ lọc bài tập nếu có class_filter_eids
    if class_filter_eids is not None:
        sub_rows = [s for s in sub_rows if s["exercise_id"] in class_filter_eids]

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
        else:
            if len(s_list) >= 2 or max_hint >= 3:
                struggling_exercises.append(eid)
            else:
                in_progress_exercises.append(eid)
            best_ratio = max((s["passed_tests"] / max(1, s["total_tests"])) for s in s_list)
            exercise_autonomy_scores.append(round(best_ratio * 40))

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

    # Đánh giá Tự động từ Hệ thống Gia sư (Diagnostic Evaluation)
    if total_submissions == 0:
        level_classification = "Chưa có dữ liệu thực hành (Bắt đầu làm bài tập đầu tiên)"
        strengths_analysis = "Học viên vừa tham gia hệ thống. Hãy chọn bài tập cơ sở đầu tiên trên Lộ trình để bắt đầu tích lũy kinh nghiệm!"
        weaknesses_and_bottlenecks = "Chưa ghi nhận điểm nghẽn nào."
        recommended_next_action = "Mở bài tập Chương 1 để bắt đầu thực hành viết mã nguồn Python đầu tiên."
    elif len(mastered_exercises) >= 4 and autonomy_score >= 80:
        level_classification = "Xuất sắc - Tư duy lập trình độc lập cao (Chuẩn A+ NEU)"
        strengths_analysis = (
            f"Đã hoàn thành xuất sắc {len(mastered_exercises)}/{distinct_count} bài tập đã thử sức với chỉ số tự lực {autonomy_score}/100. "
            f"Tỷ lệ hoàn thành ngay lần đầu đạt {first_try_pass_rate}%, trung bình chỉ mất {avg_attempts_to_solve} lần nộp/bài."
        )
        if struggling_exercises:
            weaknesses_and_bottlenecks = f"Cần lưu ý xử lý dứt điểm các bài tập đang vướng mắc: {', '.join(struggling_exercises)}."
        elif error_breakdown["logic_errors"] > 0:
            weaknesses_and_bottlenecks = f"Thỉnh thoảng vẫn gặp sai lệch ở các test case biên (lỗi logic kiểm thử chiếm {error_breakdown['logic_error_percent']}%)."
        else:
            weaknesses_and_bottlenecks = "Không có điểm nghẽn kỹ thuật nào đáng kể."
        recommended_next_action = "Tiếp tục tham gia các thử thách 'Tối ưu Code Pythonic' để nâng cao tư duy Clean Code chuẩn Senior."
    elif len(mastered_exercises) >= 2 and autonomy_score >= 60:
        level_classification = "Khá Giỏi - Nắm vững cú pháp cơ bản, cần nâng cao tối ưu code"
        strengths_analysis = (
            f"Đã làm chủ vững chắc {len(mastered_exercises)}/{distinct_count} bài tập với chỉ số tự lực {autonomy_score}/100. "
            f"Vượt qua bài tập với mức trợ giúp trung bình Level {avg_hint} (chủ yếu dùng Gợi ý nhẹ hoặc Chỉ chỗ sai)."
        )
        if struggling_exercises:
            weaknesses_and_bottlenecks = (
                f"Đang gặp điểm nghẽn tại bài tập: {', '.join(struggling_exercises)}. "
                f"Phổ lỗi ghi nhận: {error_breakdown['logic_error_percent']}% lỗi logic test case và {error_breakdown['syntax_error_percent']}% lỗi cú pháp/runtime."
            )
        else:
            weaknesses_and_bottlenecks = "Cần rèn luyện tính độc lập, tránh leo thang lên gợi ý Mức 3 ở các bài khó để giữ vững điểm tự lực."
        recommended_next_action = "Tập trung giải quyết bài tập tiếp theo trên Cây kỹ năng hoặc tự giải lại các bài đạt 1-2 sao để nâng lên 3 sao trọn vẹn."
    else:
        level_classification = "Đang rèn luyện nền tảng - Cần chú ý kiểm tra điều kiện biên"
        strengths_analysis = (
            f"Đã tích cực nộp bài {total_submissions} lượt và hoàn thành {len(mastered_exercises)} bài tập. "
            f"Có tinh thần kiên trì thử nghiệm sửa sai qua nhiều lần chạy thử."
        )
        weaknesses_and_bottlenecks = (
            f"Tỷ lệ lỗi logic chiếm {error_breakdown['logic_error_percent']}% và lỗi cú pháp chiếm {error_breakdown['syntax_error_percent']}%. "
            f"Đang gặp khó khăn ở các bài: {', '.join(struggling_exercises) if struggling_exercises else 'các bài xử lý mảng và chuỗi'}."
        )
        recommended_next_action = "Nên sử dụng tính năng 'Chạy từng bước (Visualizer)' để soi biến số và luồng rẽ nhánh, đọc kỹ bảng test case mẫu trước khi nộp."

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
        "topic_mastery": topic_mastery
    }

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
        "diagnostic_evaluation": diagnostic_evaluation
    }


def get_instructor_stats() -> dict:
    """Tổng hợp thống kê học tập cho Giảng viên."""
    conn = get_db_connection()
    cursor = conn.cursor()

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
# PHASE 10: GAMIFICATION, AUTONOMY STARS & ACHIEVEMENTS
# ==============================================================================

BADGE_DEFINITIONS = {
    "FIRST_SOLVE": {
        "title": "Bước Chân Đầu Tiên",
        "icon": "🌟",
        "description": "Hoàn thành xuất sắc bài tập lập trình đầu tiên."
    },
    "INDEPENDENT_HERO": {
        "title": "Bậc Thầy Tự Lực",
        "icon": "🏆",
        "description": "Đạt 3 Sao tự lực ở ít nhất 3 bài tập khác nhau."
    },
    "BUG_HUNTER": {
        "title": "Thợ Săn Lỗi Tự Thân",
        "icon": "⚡",
        "description": "Sửa đúng bài sau ít nhất một lần nộp trước đó bị lỗi."
    },
    "PYTHONIC_EXPLORER": {
        "title": "Nhà Khai Phá Pythonic",
        "icon": "🐍",
        "description": "Đạt điểm Clean Code trên 90 điểm trong phần review chuyên sâu."
    },
    "MARATHON_CODER": {
        "title": "Kiên Trì Bền Bỉ",
        "icon": "🧗",
        "description": "Hoàn thành một bài tập sau hơn 5 lần kiên trì thử sức."
    }
}


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


def check_and_unlock_badges(username: str) -> list[dict]:
    """Kiểm tra điều kiện và tự động mở khóa các huy hiệu mới cho học viên."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Lấy danh sách badge đã có
    cursor.execute("SELECT badge_code FROM user_achievements WHERE username = ?", (username,))
    existing_badges = {r["badge_code"] for r in cursor.fetchall()}

    # 2. Thống kê bài tập đã làm chủ & số sao
    cursor.execute("""
        SELECT COUNT(*) as solved_count,
               SUM(CASE WHEN stars_earned = 3 THEN 1 ELSE 0 END) as three_star_count,
               MAX(highest_clean_score) as max_clean
        FROM user_exercise_stars
        WHERE username = ?
    """, (username,))
    star_stats = cursor.fetchone()
    solved_count = star_stats["solved_count"] or 0
    three_star_count = star_stats["three_star_count"] or 0
    max_clean = star_stats["max_clean"] or 0

    # 3. Thống kê số lần nộp cho bài tập
    cursor.execute("""
        SELECT exercise_id, COUNT(*) as attempts, MAX(all_passed) as passed, MIN(all_passed) as had_fail
        FROM submissions
        WHERE session_id = ?
        GROUP BY exercise_id
    """, (username,))
    sub_stats = cursor.fetchall()

    has_recovered_from_fail = any(s["passed"] == 1 and s["had_fail"] == 0 for s in sub_stats)
    max_attempts_on_any = max([s["attempts"] for s in sub_stats], default=0)

    unlocked_now = []

    def award(code):
        if code not in existing_badges and code in BADGE_DEFINITIONS:
            info = BADGE_DEFINITIONS[code]
            cursor.execute("""
                INSERT OR IGNORE INTO user_achievements (username, badge_code, badge_title, badge_icon, description)
                VALUES (?, ?, ?, ?, ?)
            """, (username, code, info["title"], info["icon"], info["description"]))
            unlocked_now.append({"code": code, **info})

    # Điều kiện FIRST_SOLVE
    if solved_count >= 1:
        award("FIRST_SOLVE")

    # Điều kiện INDEPENDENT_HERO
    if three_star_count >= 3:
        award("INDEPENDENT_HERO")

    # Điều kiện BUG_HUNTER
    if has_recovered_from_fail:
        award("BUG_HUNTER")

    # Điều kiện PYTHONIC_EXPLORER
    if max_clean >= 90:
        award("PYTHONIC_EXPLORER")

    # Điều kiện MARATHON_CODER
    if max_attempts_on_any >= 5 and solved_count >= 1:
        award("MARATHON_CODER")

    conn.commit()
    conn.close()
    return unlocked_now


def save_exercise_stars(
    username: str,
    exercise_id: str,
    stars: int,
    clean_score: int = 0,
    submission_id: Optional[int] = None
) -> dict:
    """Lưu hoặc cập nhật số sao cao nhất và điểm clean code cao nhất cho bài tập."""
    conn = get_db_connection()
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
    else:
        new_stars = stars
        new_clean = clean_score
        cursor.execute("""
            INSERT INTO user_exercise_stars (
                username, exercise_id, stars_earned, best_submission_id, highest_clean_score
            ) VALUES (?, ?, ?, ?, ?)
        """, (username, exercise_id, stars, submission_id, clean_score))

    conn.commit()
    conn.close()

    newly_unlocked = check_and_unlock_badges(username)

    return {
        "username": username,
        "exercise_id": exercise_id,
        "stars_earned": new_stars,
        "highest_clean_score": new_clean,
        "new_badges": newly_unlocked
    }


def get_user_achievements(username: str) -> dict:
    """Lấy danh sách huy hiệu và sao bài tập của học viên."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT badge_code, badge_title, badge_icon, description, unlocked_at
        FROM user_achievements
        WHERE username = ?
        ORDER BY id ASC
    """, (username,))
    badges = [dict(r) for r in cursor.fetchall()]

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
        "badges": badges
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
        cursor.execute("SELECT badge_icon, badge_title FROM user_achievements WHERE username = ?", (r["username"],))
        b_rows = cursor.fetchall()
        badges = [{"icon": b["badge_icon"], "title": b["badge_title"]} for b in b_rows]

        leaderboard.append({
            "rank": rank,
            "username": r["username"],
            "full_name": r["full_name"],
            "total_stars": r["total_stars"],
            "completed_exercises": r["completed_exercises"],
            "highest_clean_score": r["highest_clean_score"],
            "badges": badges
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


# ==============================================================================
# HÀM QUẢN LÝ BÀI TẬP VÀ CÂY KỸ NĂNG THEO LỚP (CLASS CURRICULUM & SKILL TREE)
# ==============================================================================

def get_class_exercises(class_id: str, student_username: Optional[str] = None) -> list[dict]:
    """
    Lấy danh sách các bài tập thuộc một Lớp học phần kèm cấu hình Lộ trình kỹ năng (Curriculum).
    Nếu có student_username, tính toán trạng thái thích ứng của sinh viên theo Thang đo Rubric:
    - MASTERED: Đã pass 100% test cases VÀ đạt stars_earned >= min_stars_required
    - NEEDS_MORE_STARS: Đã pass 100% nhưng chưa đạt đủ min_stars_required
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

    mastered_set = set()
    for r in rows:
        eid = r["exercise_id"]
        min_stars = r["min_stars_required"] or 2
        st_stars = student_stars.get(eid, 0)
        has_passed = (eid in passed_exercises) or (st_stars > 0)
        if has_passed and st_stars >= min_stars:
            mastered_set.add(eid)

    items = []
    for r in rows:
        eid = r["exercise_id"]
        min_stars = r["min_stars_required"] or 2
        st_stars = student_stars.get(eid, 0)
        prereq = r["prerequisite_id"]

        try:
            tc_count = len(json.loads(r["test_cases"]))
        except Exception:
            tc_count = 0

        has_passed = (eid in passed_exercises) or (st_stars > 0)

        if eid in mastered_set:
            status_val = "MASTERED"
            status_desc = f"Đạt chuẩn xuất sắc ({st_stars}/{min_stars} ⭐)"
        elif has_passed and st_stars < min_stars:
            status_val = "NEEDS_MORE_STARS"
            status_desc = f"Đã giải đúng nhưng mới đạt {st_stars}/{min_stars} ⭐. Hãy tự giải lại với ít gợi ý hơn để đạt chuẩn!"
        elif eid in attempted_exercises:
            status_val = "IN_PROGRESS"
            status_desc = "Đang thực hành (Chưa vượt qua tất cả test cases)"
        else:
            if not prereq or prereq in mastered_set:
                status_val = "AVAILABLE"
                status_desc = f"Sẵn sàng thử thách (Yêu cầu {min_stars} ⭐)"
            else:
                status_val = "LOCKED"
                status_desc = f"Khóa - Cần hoàn thành đạt chuẩn bài tiên quyết ({prereq})"

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
            "min_stars_required": min_stars,
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
    min_stars_required: int = 2,
    skill_tag: str = "Tư duy thuật toán",
    weight_point: int = 10
) -> dict:
    """Giảng viên gán một bài tập vào Lớp học phần."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if order_idx is None:
        cursor.execute("SELECT COALESCE(MAX(order_idx), 0) + 1 FROM class_exercises WHERE class_id = ?", (class_id,))
        order_idx = cursor.fetchone()[0]

    cursor.execute("""
        INSERT OR REPLACE INTO class_exercises (
            class_id, exercise_id, module_name, order_idx, prerequisite_id, min_stars_required, skill_tag, weight_point
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (class_id, exercise_id, module_name, order_idx, prerequisite_id, min_stars_required, skill_tag, weight_point))
    conn.commit()
    conn.close()
    return {
        "class_id": class_id,
        "exercise_id": exercise_id,
        "module_name": module_name,
        "order_idx": order_idx,
        "prerequisite_id": prerequisite_id,
        "min_stars_required": min_stars_required,
        "skill_tag": skill_tag,
        "weight_point": weight_point
    }


def update_class_exercise(
    class_id: str,
    exercise_id: str,
    module_name: Optional[str] = None,
    order_idx: Optional[int] = None,
    prerequisite_id: Optional[str] = None,
    min_stars_required: Optional[int] = None,
    skill_tag: Optional[str] = None,
    weight_point: Optional[int] = None
) -> bool:
    """Giảng viên cập nhật cấu hình Cây kỹ năng / Lộ trình học phần của một bài tập trong lớp."""
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
    if min_stars_required is not None:
        updates.append("min_stars_required = ?")
        params.append(min_stars_required)
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

