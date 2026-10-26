"""
Pydantic Schemas định nghĩa cấu trúc dữ liệu cho PyTutor Backend.
Bao gồm các mô hình cho:
- Authentication & Users (Login, Role)
- Exercise & Test Cases (Student view & Instructor CRUD)
- Submission & Execution (Run Test only, Submit with AI Tutor)
- Adaptive Student Model & Learning Events
- Health & Monitoring
"""
from typing import Optional, Any
from pydantic import BaseModel, Field


# ==============================================================================
# AUTH SCHEMAS
# ==============================================================================

class LoginRequest(BaseModel):
    username: str = Field(..., description="Tên đăng nhập (student hoặc gv_tran)")
    password: str = Field(..., description="Mật khẩu")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    full_name: str


class UserResponse(BaseModel):
    username: str
    role: str
    full_name: str


# ==============================================================================
# TEST CASE & EXECUTION SCHEMAS
# ==============================================================================

class TestCase(BaseModel):
    input: str = Field(..., description="Dữ liệu truyền vào stdin")
    expected_output: str = Field(..., description="Dữ liệu kỳ vọng in ra stdout")
    description: Optional[str] = Field("", description="Mô tả mục đích test case")


class TestResultItem(BaseModel):
    test_idx: int
    description: str
    input: str
    expected_output: str
    actual_output: str
    status: str = Field(..., description="PASS | FAIL | TIMEOUT | SYNTAX_ERROR | RUNTIME_ERROR | SKIPPED")
    error_message: Optional[str] = None
    stderr: Optional[str] = ""
    execution_time_ms: float = 0.0


class TestResults(BaseModel):
    total_tests: int
    passed_tests: int
    failed_tests: int
    all_passed: bool
    summary: str
    results: list[TestResultItem]


class ASTAnalysis(BaseModel):
    valid: bool
    syntax_error: Optional[Any] = None
    line_count: int = 0
    has_loops: bool = False
    loop_details: Optional[dict[str, Any]] = None
    has_recursion: bool = False
    recursive_functions: list[str] = []
    has_accumulator: bool = False
    accumulator_patterns: list[str] = []
    has_return: bool = False
    defined_functions: list[dict[str, Any]] = []
    observations: list[str] = []
    structural_summary: str = ""


# ==============================================================================
# RUN TEST ONLY & SUBMIT SOLUTION SCHEMAS (WITH MCP PROTOCOL TRACE)
# ==============================================================================

class MCPTraceItem(BaseModel):
    step: int
    tool_name: str
    action: str
    protocol: str = "JSON-RPC 2.0 (stdio)"
    duration_ms: float
    status: str = "SUCCESS"
    summary: str


class RunTestOnlyRequest(BaseModel):
    exercise_id: str = Field(..., description="Mã định danh bài tập")
    code: str = Field(..., description="Mã nguồn Python sinh viên chạy thử")


class RunTestOnlyResponse(BaseModel):
    exercise_id: str
    test_results: TestResults
    ast_analysis: ASTAnalysis
    mcp_trace: list[MCPTraceItem] = Field(default_factory=list, description="Nhật ký lệnh MCP JSON-RPC 2.0")


class SubmitRequest(BaseModel):
    exercise_id: str = Field(..., description="Mã định danh bài tập (ví dụ: ex_01_sum_1_to_n)")
    code: str = Field(..., description="Mã nguồn Python sinh viên nộp bài")
    hint_level: int = Field(1, ge=1, le=3, description="Mức độ gợi ý sư phạm: 1 (Gợi mở), 2 (Chẩn đoán), 3 (Mã giả)")
    session_id: Optional[str] = Field("default_session", description="Mã định danh phiên học viên phục vụ mô hình thích ứng")
    exam_session_id: Optional[str] = Field(None, description="Mã kỳ thi / đợt thực hành nếu đang làm bài trong lớp")
    action_type: str = Field("submit", description="'ask_ai' (chỉ xin gợi ý AI) hoặc 'submit' (nộp bài chấm điểm chính thức)")


class SubmitResponse(BaseModel):
    exercise_id: str
    test_results: TestResults
    ast_analysis: ASTAnalysis
    tutor_hint: str
    hint_level: int
    discovered_mcp_tools: list[str] = Field(default_factory=list)
    llm_source: str = Field("gemini-3.5-flash-lite", description="Nguồn sinh gợi ý")
    attempt_history: list[dict] = Field(default_factory=list, description="Lịch sử nộp bài gần nhất")
    student_model: Optional[dict] = Field(default=None, description="Mô hình học sinh thích ứng")
    mcp_trace: list[MCPTraceItem] = Field(default_factory=list, description="Nhật ký các lệnh MCP JSON-RPC 2.0")
    stars_earned: int = Field(0, description="Số sao tự lực đạt được (0-3 ⭐)")
    new_badges: list[dict] = Field(default_factory=list, description="Danh sách huy hiệu mới mở khóa")



class StudentProfileResponse(BaseModel):
    session_id: str
    class_id: Optional[str] = None
    total_exercises_attempted: int
    total_submissions: int
    mastered_exercises: list[str]
    struggling_exercises: list[str]
    in_progress_exercises: list[str] = Field(default_factory=list)
    average_hint_level: float
    summary: str
    recent_attempts: list[dict] = Field(default_factory=list)
    analytics_metrics: Optional[dict] = None
    diagnostic_evaluation: Optional[dict] = None


# ==============================================================================
# EXERCISE SCHEMAS
# ==============================================================================

class ExerciseSummary(BaseModel):
    id: str
    title: str
    difficulty: str
    category: str
    test_cases_count: int
    is_active: Optional[bool] = True


class ExerciseDetail(BaseModel):
    id: str
    title: str
    difficulty: str
    category: str
    description: str
    starter_code: str
    test_cases: list[TestCase]
    is_active: Optional[bool] = True


class ExerciseUpsertRequest(BaseModel):
    id: str = Field(..., description="Mã bài tập (ví dụ: ex_06_fibonacci)")
    title: str = Field(..., description="Tiêu đề bài tập")
    difficulty: str = Field(..., description="Dễ | Trung bình | Khó")
    category: str = Field(..., description="Chủ đề thuật toán")
    description: str = Field(..., description="Đề bài định dạng Markdown")
    starter_code: str = Field(..., description="Mã nguồn mẫu khởi tạo")
    test_cases: list[TestCase] = Field(..., description="Danh sách các test case")


# ==============================================================================
# INSTRUCTOR DASHBOARD SCHEMAS
# ==============================================================================

class InstructorDashboardStats(BaseModel):
    total_exercises: int
    total_submissions: int
    active_students: int
    pass_rate_percentage: float


class SubmissionItem(BaseModel):
    id: int
    session_id: str
    exercise_id: str
    exercise_title: str
    code: Optional[str] = ""
    hint_level: int
    passed_tests: int
    total_tests: int
    all_passed: bool
    llm_source: str
    tutor_hint: Optional[str] = ""
    timestamp: str


class CompilerConfig(BaseModel):
    executable_path: str = Field(..., description="Đường dẫn file thực thi Python thực tế (sys.executable)")
    python_version: str = Field(..., description="Phiên bản trình thông dịch Python (sys.version)")
    platform: str = Field(..., description="Hệ điều hành nền tảng (sys.platform)")
    execution_flags: list[str] = Field(..., description="Cờ thực thi: -u unbuffered, -c in-memory")
    encoding: str = Field(..., description="Bảng mã I/O UTF-8")
    isolation_mechanism: str = Field(..., description="Cơ chế cô lập tiến trình qua MCP JSON-RPC 2.0 stdio")
    sandbox_timeout_seconds: float = Field(5.0, description="Giới hạn thời gian timeout Sandbox")
    tracer_limits: str = Field(..., description="Giới hạn số bước tracer sys.settrace")
    database_engine: str = Field(..., description="Cơ chế cơ sở dữ liệu SQLite3 WAL Mode")


class HealthResponse(BaseModel):
    status: str = "ok"
    mcp_server_connected: bool
    discovered_tools: list[str]
    version: str = "3.6"
    compiler_config: Optional[CompilerConfig] = None


# ==============================================================================
# PHASE 8: MULTI-TURN CHAT & CUSTOM RUN SCHEMAS
# ==============================================================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' hoặc 'assistant'")
    content: str = Field(..., description="Nội dung tin nhắn")
    timestamp: Optional[str] = None


class TutorChatRequest(BaseModel):
    exercise_id: str = Field(..., description="Mã bài tập hiện tại")
    code: str = Field(..., description="Mã nguồn sinh viên đang viết")
    session_id: str = Field("default_session", description="Mã định danh phiên học viên")
    user_message: str = Field(..., description="Câu hỏi của sinh viên")
    history: list[ChatMessage] = Field(default_factory=list, description="Lịch sử hội thoại trước đó")
    exam_session_id: Optional[str] = Field(None, description="Mã kỳ thi / đợt thực hành nếu đang làm bài trong lớp")


class TutorChatResponse(BaseModel):
    reply: str
    llm_source: str = "gemini-3.5-flash-lite"
    updated_history: list[ChatMessage]


class CustomRunRequest(BaseModel):
    exercise_id: Optional[str] = None
    code: str = Field(..., description="Mã nguồn cần chạy thử")
    custom_input: str = Field("", description="Dữ liệu đầu vào tùy ý")


class CustomRunResponse(BaseModel):
    stdout: str
    stderr: str = ""
    execution_time_ms: float = 0.0
    status: str = Field(..., description="SUCCESS | RUNTIME_ERROR | TIMEOUT | SYNTAX_ERROR")
    error_message: Optional[str] = None


# ==============================================================================
# PHASE 9: EXECUTION STEP VISUALIZER & SKILL ROADMAP SCHEMAS
# ==============================================================================

class TraceStepItem(BaseModel):
    step: int
    line: int
    event: str
    func_name: str
    locals: dict[str, Any] = Field(default_factory=dict)
    stdout: str = ""


class TraceExecutionRequest(BaseModel):
    code: str = Field(..., description="Mã nguồn Python cần trace từng bước")
    stdin_input: str = Field("", description="Dữ liệu đầu vào giả lập")
    max_steps: int = Field(150, description="Số bước thực thi tối đa")


class TraceExecutionResponse(BaseModel):
    success: bool
    total_steps: int
    code_lines: list[str] = Field(default_factory=list)
    steps: list[TraceStepItem] = Field(default_factory=list)
    truncated: bool = False
    error: Optional[str] = None


class SkillNode(BaseModel):
    id: str
    title: str
    category: str
    difficulty: str
    prerequisites: list[str] = Field(default_factory=list)
    status: str = Field("LOCKED", description="MASTERED | NEEDS_MORE_STARS | IN_PROGRESS | AVAILABLE | LOCKED")
    min_stars_required: int = 2
    stars_earned: int = 0
    module_name: Optional[str] = None
    order_idx: int = 1
    skill_tag: Optional[str] = None
    status_description: Optional[str] = None
    is_unlocked: bool = True


class SkillRoadmapResponse(BaseModel):
    class_id: Optional[str] = None
    class_name: Optional[str] = None
    class_code: Optional[str] = None
    nodes: list[SkillNode]
    total_mastered: int
    total_exercises: int


# ==============================================================================
# PHASE 10: GAMIFICATION, STARS, BADGES & PYTHONIC REVIEW SCHEMAS
# ==============================================================================

class LeaderboardBadge(BaseModel):
    icon: str
    title: str


class LeaderboardItem(BaseModel):
    rank: int
    username: str
    full_name: str
    total_stars: int
    completed_exercises: int
    highest_clean_score: int = 0
    badges: list[LeaderboardBadge] = Field(default_factory=list)


class LeaderboardResponse(BaseModel):
    leaderboard: list[LeaderboardItem]
    total_students: int


class AchievementBadgeItem(BaseModel):
    badge_code: str
    badge_title: str
    badge_icon: str
    description: str
    unlocked_at: str


class UserAchievementsResponse(BaseModel):
    username: str
    total_stars: int
    completed_count: int
    exercise_stars: dict[str, int] = Field(default_factory=dict)
    clean_scores: dict[str, int] = Field(default_factory=dict)
    badges: list[AchievementBadgeItem] = Field(default_factory=list)


class PythonicReviewRequest(BaseModel):
    exercise_id: str = Field(..., description="Mã bài tập")
    code: str = Field(..., description="Mã nguồn sinh viên đã giải đúng")
    username: Optional[str] = Field("student", description="Tên đăng nhập hoặc session_id")


class PythonicReviewResponse(BaseModel):
    clean_score: int = Field(..., description="Điểm Clean Code (0-100)")
    strengths: str = Field(..., description="Điểm mạnh trong code của sinh viên")
    improvements: str = Field(..., description="Các điểm cần tối ưu hóa")
    pythonic_code: str = Field(..., description="Đoạn mã mẫu viết chuẩn Pythonic")
    explanation: str = Field(..., description="Giải thích lý do tối ưu")
    stars_earned: int = 0
    new_badges: list[dict] = Field(default_factory=list)


# ==============================================================================
# PHASE 12 & 13-14: CREDIT CLASSES, NEU LMS & EXAM SESSIONS SCHEMAS
# ==============================================================================

class CreditClassSummary(BaseModel):
    id: str
    class_code: str
    class_name: str
    course_code: Optional[str] = "CNTT1116"
    credits: Optional[int] = 3
    faculty: Optional[str] = "Khoa Công nghệ thông tin - NEU"
    semester: str = "Học kỳ 1 (2026-2027)"
    enrollment_code: Optional[str] = "NEU01"
    instructor_username: str = "gv_tran"
    instructor_name: Optional[str] = "Nguyễn Văn A"
    description: Optional[str] = ""
    student_count: int = 0
    session_count: int = 0
    exercise_count: int = 0
    is_enrolled: bool = False
    completed_in_class: int = 0
    progress_percent: int = 0
    created_at: Optional[str] = None


class CreditClassCreateRequest(BaseModel):
    class_code: str = Field(..., description="Mã lớp tín chỉ, ví dụ: CNTT1116(126)_01")
    class_name: str = Field(..., description="Tên lớp học phần")
    course_code: Optional[str] = Field("CNTT1116", description="Mã học phần")
    credits: Optional[int] = Field(3, description="Số tín chỉ")
    faculty: Optional[str] = Field("Khoa Công nghệ thông tin - NEU", description="Khoa phụ trách")
    semester: str = Field("Học kỳ 1 (2026-2027)", description="Học kỳ áp dụng")
    enrollment_code: Optional[str] = Field(None, description="Mã tham gia lớp (nếu để trống tự sinh)")
    instructor_name: Optional[str] = Field(None, description="Họ và tên giảng viên")
    description: Optional[str] = Field("", description="Mô tả lớp học phần")


class ClassEnrollmentRequest(BaseModel):
    student_username: Optional[str] = Field("student", description="Tên đăng nhập của sinh viên")


class ClassEnrollByCodeRequest(BaseModel):
    enrollment_code: str = Field(..., description="Mã tham gia lớp, ví dụ: NEU-PY01")


class ClassExerciseItem(BaseModel):
    class_exercise_id: Optional[int] = None
    class_id: str
    exercise_id: str
    id: str
    title: str
    difficulty: str
    category: str
    description: Optional[str] = ""
    test_cases_count: int = 0
    module_name: str = "Chương 1: Cơ sở lập trình Python"
    order_idx: int = 1
    prerequisite_id: Optional[str] = None
    min_stars_required: int = 2
    skill_tag: str = "Tư duy thuật toán"
    weight_point: int = 10
    stars_earned: int = 0
    status: str = "AVAILABLE"  # MASTERED | NEEDS_MORE_STARS | IN_PROGRESS | AVAILABLE | LOCKED
    status_description: Optional[str] = ""
    is_unlocked: bool = True


class ClassExerciseAssignRequest(BaseModel):
    exercise_id: str = Field(..., description="Mã bài tập từ ngân hàng đề")
    module_name: str = Field("Chương 1: Cơ sở lập trình Python", description="Tên chương / Module học phần")
    order_idx: Optional[int] = Field(None, description="Thứ tự học trong lộ trình")
    prerequisite_id: Optional[str] = Field(None, description="Bài tập tiên quyết trong lớp")
    min_stars_required: int = Field(2, ge=1, le=3, description="Thang đo số sao tối thiểu (1-3 ⭐)")
    skill_tag: str = Field("Tư duy thuật toán", description="Kỹ năng chuẩn đầu ra")
    weight_point: int = Field(10, description="Điểm trọng số bài tập")


class ClassExerciseUpdateRequest(BaseModel):
    module_name: Optional[str] = None
    order_idx: Optional[int] = None
    prerequisite_id: Optional[str] = None
    min_stars_required: Optional[int] = Field(None, ge=1, le=3)
    skill_tag: Optional[str] = None
    weight_point: Optional[int] = None


class ClassStudentProgressItem(BaseModel):
    id: int
    class_id: str
    student_username: str
    full_name: str
    enrolled_at: Optional[str] = None
    total_exercises: int = 0
    completed_exercises: int = 0
    total_stars: int = 0
    progress_percent: int = 0


class ExamSessionItem(BaseModel):
    id: str
    title: str
    class_id: str
    class_name: Optional[str] = ""
    class_code: Optional[str] = ""
    session_type: str = Field("PRACTICE", description="PRACTICE | EXAM")
    exercise_ids: list[str] = Field(default_factory=list)
    exercises: list[ExerciseSummary] = Field(default_factory=list)
    duration_minutes: int = 45
    allow_ai_hints: int = 1
    is_active: bool = True
    created_by: str = "gv_tran"
    created_at: Optional[str] = None


class ExamSessionCreateRequest(BaseModel):
    title: str = Field(..., description="Tiêu đề kỳ thi hoặc đợt thực hành")
    class_id: str = Field(..., description="Mã lớp tín chỉ áp dụng")
    session_type: str = Field("PRACTICE", description="PRACTICE hoặc EXAM")
    exercise_ids: list[str] = Field(..., description="Danh sách mã bài tập được chọn từ ngân hàng đề")
    duration_minutes: int = Field(45, ge=5, le=360, description="Thời gian làm bài tính bằng phút")
    allow_ai_hints: int = Field(1, description="1: Cho phép AI Tutor, 0: Khóa AI Tutor trong giờ thi")



