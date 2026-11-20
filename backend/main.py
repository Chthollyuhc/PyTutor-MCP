"""
FastAPI Backend Application cho PyTutor.
Đóng vai trò MCP Host, Điều phối Sư phạm (Orchestrator) & Phân quyền (Auth & Roles).
"""
import sys
import logging
import uuid
import re
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, HTTPException, Depends, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

# Cấu hình UTF-8 cho logging trên Windows
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("pytutor.api")

from backend.database import (
    init_db,
    save_practice_run,
    MAX_KB_DOCUMENTS_PER_CLASS,
    count_kb_documents,
    create_kb_document,
    list_kb_documents,
    set_kb_document_active,
    delete_kb_document,
    get_active_kb_documents_for_index,
    get_db_connection,
    get_all_exercises as db_get_all_exercises,
    get_exercise_by_id as db_get_exercise_by_id,
    save_exercise as db_save_exercise,
    delete_exercise as db_delete_exercise,
    get_exercise_owner,
    instructor_can_use_exercise,
    grant_exercise_share,
    revoke_exercise_share,
    get_instructor_stats,
    get_all_submissions,
    get_submission_by_id,
    get_attempts,
    compute_student_model,
    calculate_autonomy_stars,
    save_exercise_stars,
    get_user_achievements,
    get_class_leaderboard,
    get_credit_classes,
    get_credit_class_by_id,
    get_class_by_enrollment_code,
    create_credit_class,
    enroll_student_in_class,
    unenroll_student_from_class,
    get_student_classes,
    get_class_students,
    get_class_students_with_progress,
    get_class_learning_summary,
    get_class_insights,
    get_exercise_journey,
    get_student_journey_overview,
    get_tutor_feedback_summary,
    explain_autonomy_stars,
    get_autonomy_hint_context,
    get_latest_passed_submission_code,
    instructor_owns_class,
    save_llm_interaction,
    save_llm_interaction_sources,
    save_tutor_feedback,
    get_class_exercises,
    add_exercise_to_class,
    update_class_exercise,
    remove_exercise_from_class,
    get_exam_sessions,
    get_exam_session_by_id,
    create_exam_session,
    delete_exam_session,
    get_all_knowledge_components,
    create_knowledge_component,
    delete_knowledge_component,
    get_exercise_class_info
)
from backend.auth import (
    authenticate_user,
    create_token,
    verify_token,
    require_instructor
)
from backend.schemas import (
    KnowledgeToggleRequest,
    HealthResponse,
    CompilerConfig,
    ExerciseSummary,
    ExerciseDetail,
    ExerciseUpsertRequest,
    ExerciseShareRequest,
    RunTestOnlyRequest,
    RunTestOnlyResponse,
    SubmitRequest,
    SubmitResponse,
    TestResults,
    ASTAnalysis,
    MCPTraceItem,
    StudentProfileResponse,
    LoginRequest,
    LoginResponse,
    UserResponse,
    InstructorDashboardStats,
    SubmissionItem,
    ChatMessage,
    TutorChatRequest,
    TutorChatResponse,
    TutorFeedbackRequest,
    InstructorAIChatRequest,
    InstructorAIChatResponse,
    CustomRunRequest,
    CustomRunResponse,
    TraceExecutionRequest,
    TraceExecutionResponse,
    SkillNode,
    SkillRoadmapResponse,
    LeaderboardResponse,
    UserAchievementsResponse,
    PythonicReviewRequest,
    PythonicReviewResponse,
    CreditClassSummary,
    CreditClassCreateRequest,
    ClassEnrollmentRequest,
    ClassEnrollByCodeRequest,
    ClassExerciseItem,
    ClassExerciseAssignRequest,
    ClassExerciseUpdateRequest,
    ClassStudentProgressItem,
    ExamSessionItem,
    ExamSessionCreateRequest,
    KnowledgeComponentItem,
    KnowledgeComponentCreateRequest
)
from backend.mcp_client import (
    discover_tools,
    get_exercise_list,
    get_exercise_details,
    run_test_only_pipeline,
    execute_submission_pipeline,
    save_learning_event_via_mcp,
    get_student_profile_via_mcp,
    run_custom_test_pipeline,
    get_code_structure_summary,
    execute_trace_pipeline
)
from backend.llm_service import (generate_tutor_hint, generate_chat_followup, generate_pythonic_review,
                                 generate_instructor_answer, build_pass_feedback)
from backend.guardrails import check_student_input
from backend.adaptive_policy import is_blank_attempt, select_hint_strategy
from backend.class_overview import build_class_overview, build_action_cards
from backend.student_journey import build_student_headline, describe_exercise_journey, pick_path_class, DISCLAIMER_VI
from backend.plain_language import (build_class_plain_view, build_course_path, build_story, build_today_card,
                                    class_brief_line, story_one_liner)
from pytutor_shared.learner_model import summarize_attempt_features




def rebuild_knowledge_index() -> int:
    """Dựng lại toàn bộ chỉ mục RAG: tài liệu chung + tài liệu lớp đang bật (truyền từ DB vào retriever)."""
    from backend.rag.retriever import ingest_knowledge_base
    return ingest_knowledge_base(class_documents=get_active_kb_documents_for_index())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Khởi tạo cơ sở dữ liệu SQLite khi khởi động ứng dụng."""
    try:
        init_db()
        logger.info("Cơ sở dữ liệu SQLite PyTutor đã sẵn sàng.")
        chunks = rebuild_knowledge_index()
        logger.info("RAG knowledge base ready: %s local chunks indexed.", chunks)
    except Exception as e:
        logger.error(f"Lỗi khởi tạo DB: {e}")
    yield


app = FastAPI(
    title="PyTutor API",
    description="Hệ thống hỗ trợ học lập trình Python với phản hồi thích ứng dựa trên mô hình người học. MCP được dùng làm giao thức tích hợp công cụ.",
    version="3.6",
    lifespan=lifespan
)

# Bật CORS cho phép kết nối từ Frontend (Vite / React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_student(token_data: dict = Depends(verify_token)) -> dict:
    """Role dependency for student-owned learning data and code execution."""
    if token_data.get("role") != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chức năng này dành cho sinh viên.")
    return token_data


def ensure_class_access(class_id: str, token_data: dict, *, hide_forbidden: bool = True) -> dict:
    """Load a class only when the current account is enrolled or owns it."""
    username = token_data.get("sub", "")
    cls = get_credit_class_by_id(
        class_id,
        current_username=username if token_data.get("role") == "student" else None,
    )
    allowed = bool(cls) and (
        (token_data.get("role") == "instructor" and instructor_owns_class(class_id, username))
        or (token_data.get("role") == "student" and cls.get("is_enrolled", False))
    )
    if not allowed:
        code = status.HTTP_404_NOT_FOUND if hide_forbidden else status.HTTP_403_FORBIDDEN
        raise HTTPException(status_code=code, detail="Không tìm thấy lớp hoặc bạn không có quyền truy cập.")
    return cls


# ==============================================================================
# 1. HỆ THỐNG XÁC THỰC & TÀI KHOẢN (AUTH & ROLES)
# ==============================================================================

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Đăng nhập hệ thống (student / student123, gv_tran / gv123)."""
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác."
        )

    token = create_token(
        username=user["username"],
        role=user["role"],
        full_name=user["full_name"]
    )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        username=user["username"],
        role=user["role"],
        full_name=user["full_name"]
    )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(token_data: dict = Depends(verify_token)):
    """Lấy thông tin người dùng hiện tại từ SQLite Database."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT username, role, full_name FROM users WHERE username = ?", (token_data["sub"],))
    row = c.fetchone()
    conn.close()
    if row:
        return UserResponse(
            username=row["username"],
            role=row["role"],
            full_name=row["full_name"]
        )
    return UserResponse(
        username=token_data["sub"],
        role=token_data["role"],
        full_name=token_data.get("name", token_data["sub"])
    )


# ==============================================================================
# 2. GIÁM SÁT HỆ THỐNG & TRUE MCP DISCOVERY
# ==============================================================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Kiểm tra sức khỏe Backend, xác nhận kết nối MCP Server và trích xuất cấu hình trình biên dịch thực tế."""
    compiler_info = CompilerConfig(
        executable_path=sys.executable,
        python_version=sys.version.split()[0],
        platform=sys.platform,
        execution_flags=["-u (Unbuffered I/O)", "-c (In-memory bytecode compile)"],
        encoding="utf-8 (PYTHONIOENCODING=utf-8)",
        isolation_mechanism="OS Subprocess Popen via MCP JSON-RPC 2.0 stdio",
        sandbox_timeout_seconds=5.0,
        tracer_limits="Max 150 steps / 3.0s timeout (sys.settrace)",
        database_engine="SQLite3 WAL Mode (timeout=20.0s)"
    )
    try:
        tools = await discover_tools()
        return HealthResponse(
            status="ok",
            mcp_server_connected=True,
            discovered_tools=tools,
            version="3.6",
            compiler_config=compiler_info
        )
    except Exception as e:
        logger.error(f"Lỗi kiểm tra sức khỏe MCP Server: {e}")
        return HealthResponse(
            status="degraded",
            mcp_server_connected=False,
            discovered_tools=[],
            version="3.6",
            compiler_config=compiler_info
        )


# ==============================================================================
# 3. NGÂN HÀNG BÀI TẬP (HỌC VIÊN & GIẢNG VIÊN ĐỌC)
# ==============================================================================

@app.get("/api/exercises", response_model=list[ExerciseSummary])
async def list_exercises(token_data: dict = Depends(verify_token)):
    """Lấy danh sách các bài tập lập trình Python có sẵn qua MCP Server."""
    try:
        exercises = await get_exercise_list()
        return exercises
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách bài tập từ MCP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể lấy danh sách bài tập từ MCP Server: {e}"
        )


@app.get("/api/exercises/{exercise_id}", response_model=ExerciseDetail)
async def get_exercise(
    exercise_id: str,
    class_id: Optional[str] = None,
    token_data: dict = Depends(verify_token)
):
    """Lấy chi tiết một bài tập: đề bài, starter code, test cases chuẩn."""
    try:
        data = await get_exercise_details(exercise_id)
        if "error" in data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data["error"])
        # Sinh viên đã từng `submit` pass bài này → giao diện mở sẵn phạm vi chat "code đã nộp" (khớp /api/tutor/chat).
        # Chỉ là gợi ý hiển thị (quyền thật do /api/tutor/chat quyết định) → lỗi DB không được làm hỏng việc xem đề.
        data["has_passed"] = False
        username = token_data.get("sub")
        if token_data.get("role") == "student":
            try:
                data["has_passed"] = get_latest_passed_submission_code(username, exercise_id) is not None
            except Exception as exc:
                logger.warning(f"Không đọc được trạng thái nộp đạt của bài {exercise_id}: {exc}")

        cls_info = get_exercise_class_info(exercise_id, student_username=username, preferred_class_id=class_id)
        if cls_info:
            data["class_id"] = cls_info["id"]
            data["class_name"] = cls_info["class_name"]
            data["class_code"] = cls_info["class_code"]
            data["semester"] = cls_info["semester"]

        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi lấy chi tiết bài tập {exercise_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi kết nối MCP Server: {e}"
        )


# ==============================================================================
# 4. CHẠY THỬ RIÊNG BIỆT (RUN TEST ONLY - KHÔNG TỐN AI QUOTA)
# ==============================================================================

@app.post("/api/run-test", response_model=RunTestOnlyResponse)
async def run_test_only(request: RunTestOnlyRequest, token_data: dict = Depends(verify_token)):
    """
    Chạy thử nhanh: Thực thi Sandbox và phân tích AST qua MCP
    mà KHÔNG gọi LLM (tiết kiệm quota AI, phản hồi dưới 1 giây, kèm MCP Trace).
    """
    try:
        res = await run_test_only_pipeline(exercise_id=request.exercise_id, code=request.code)
        if token_data.get("role") == "student":
            # v5.4: chỉ ghi số test đạt (không lưu mã nguồn); lỗi ghi chỉ log cảnh báo bên trong save_practice_run.
            tr = res.get("test_results") or {}
            try:
                run_features = summarize_attempt_features(tr, res.get("ast_analysis"))
            except Exception:  # noqa: BLE001 - đặc trưng chỉ là phụ trợ
                run_features = None
            save_practice_run(token_data["sub"], request.exercise_id, tr.get("passed_tests", 0),
                              tr.get("total_tests", 0), bool(tr.get("all_passed")), features=run_features)
        return RunTestOnlyResponse(
            exercise_id=request.exercise_id,
            test_results=TestResults(**res["test_results"]),
            ast_analysis=ASTAnalysis(**res["ast_analysis"]),
            mcp_trace=[MCPTraceItem(**t) for t in res.get("mcp_trace", [])]
        )
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logger.error(f"Lỗi khi chạy thử test cases: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi chạy thử: {e}"
        )


# ==============================================================================
# 5. NỘP BÀI & GIA SƯ AI THÍCH ỨNG (SUBMISSION & ADAPTIVE SCAFFOLDING)
# ==============================================================================

@app.post("/api/submit", response_model=SubmitResponse)
async def submit_solution(request: SubmitRequest, token_data: dict = Depends(require_student)):
    """
    Điểm chạm chính (Main E2E Route):
    1. Tiếp nhận mã nguồn, mức độ gợi ý và session_id
    2. Gọi MCP Server chạy Sandbox, phân tích AST, lấy lịch sử và student model (kèm MCP Trace)
    3. Đóng gói Context Bundle đa chiều và gọi AI Tutor sinh gợi ý sư phạm
    4. Lưu sự kiện học tập vào SQLite qua MCP Tool save_learning_event
    5. Trả về kết quả tổng hợp đầy đủ cho Frontend
    """
    try:
        student_username = token_data["sub"]
        is_exam_mode = False
        if request.exam_session_id:
            sess_info = get_exam_session_by_id(request.exam_session_id)
            if not sess_info or not sess_info.get("is_active", False):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đợt học đang hoạt động.")
            ensure_class_access(sess_info["class_id"], token_data)
            if request.exercise_id not in sess_info.get("exercise_ids", []):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bài tập không thuộc đợt học đã chọn.")
            is_exam_mode = sess_info.get("allow_ai_hints") == 0 or sess_info.get("session_type") == "EXAM"

        # Lớp dùng để tính mô hình người học: từ đợt học (đã kiểm tra), hoặc class_id nếu sinh viên đã ghi danh.
        # Không ghi danh thì bỏ qua lớp (không 403) vì giao diện có thể gửi lớp đầu tiên làm mặc định.
        model_class_id = None
        if request.exam_session_id:
            model_class_id = sess_info["class_id"]
        elif request.class_id:
            candidate = get_credit_class_by_id(request.class_id, current_username=student_username)
            if candidate and candidate.get("is_enrolled", False):
                model_class_id = request.class_id

        # 1. Thực thi pipeline qua MCP stdio
        pipeline_res = await execute_submission_pipeline(
            exercise_id=request.exercise_id,
            code=request.code,
            session_id=student_username,
            class_id=model_class_id,
            # Vết chạy chỉ phục vụ gợi ý (ask_ai) và chỉ khi AI không bị khóa; lỗi vết chạy không làm hỏng chấm bài.
            with_trace=request.action_type == "ask_ai" and not is_exam_mode,
        )

        exercise = pipeline_res["exercise"]
        test_results_raw = pipeline_res["test_results"]
        ast_analysis_raw = pipeline_res["ast_analysis"]
        attempt_history = pipeline_res.get("attempt_history", [])
        student_model = pipeline_res.get("student_model", None)
        discovered_tools = pipeline_res["discovered_tools"]
        mcp_trace = [MCPTraceItem(**t) for t in pipeline_res.get("mcp_trace", [])]

        # 2. Sinh gợi ý sư phạm: Nếu ở chế độ thi thì khóa AI tutor, ngược lại xử lý theo action_type
        hint_telemetry = None
        # Chưa có code chỉ được phép ở `ask_ai` (xin gợi ý); `submit` rỗng vẫn chấm như cũ.
        no_code = request.action_type == "ask_ai" and is_blank_attempt(request.code, exercise.get("starter_code"))
        adaptive_strategy = select_hint_strategy(request.hint_level, test_results_raw, attempt_history, student_model,
                                                 exercise_id=request.exercise_id, no_code=no_code)
        if is_exam_mode:
            tutor_hint = "🔒 **[Chế độ Kỳ thi / Kiểm tra nghiêm ngặt]** Hệ thống đã ghi nhận kết quả chấm điểm Test Cases của bạn. Trong chế độ Thi, tính năng gợi ý từ Gia sư AI được khóa để đảm bảo tính công bằng học thuật."
            llm_source = "Exam-Mode-Guard"
        elif request.action_type == "submit" and test_results_raw.get("all_passed", False):
            # Rút giàn giáo khi đã pass: phản hồi tất định (ghi nhận → tự kiểm → mở rộng tùy chọn), không gọi LLM.
            tutor_hint = build_pass_feedback(exercise, test_results_raw, ast_analysis_raw, adaptive_strategy=adaptive_strategy)
            llm_source = "System-Celebration"
        else:
            tutor_hint, llm_source, hint_telemetry = await generate_tutor_hint(
                exercise=exercise,
                code=request.code,
                test_results=test_results_raw,
                ast_analysis=ast_analysis_raw,
                hint_level=request.hint_level,
                attempt_history=attempt_history,
                student_model=student_model,
                adaptive_strategy=adaptive_strategy,
                trace=pipeline_res.get("failure_trace"),
            )

        hint_interaction_id = None
        if hint_telemetry:
            hint_interaction_id = str(uuid.uuid4())
            save_llm_interaction({"id": hint_interaction_id, "username": student_username,
                                  "role": "student", "task_type": "adaptive_hint", **hint_telemetry})

        # 2.1. Ngữ cảnh sao tự làm phải đọc TRƯỚC khi lưu lượt hiện tại (để biết đã từng nộp pass hay chưa).
        star_context = None
        if request.action_type == "submit" and test_results_raw.get("all_passed", False):
            star_context = get_autonomy_hint_context(student_username, request.exercise_id)

        # 3. Ghi nhận sự kiện học tập vào cơ sở dữ liệu qua MCP Tool
        try:
            await save_learning_event_via_mcp(
                session_id=student_username,
                exercise_id=request.exercise_id,
                code=request.code,
                hint_level=request.hint_level,
                passed_tests=test_results_raw.get("passed_tests", 0),
                total_tests=test_results_raw.get("total_tests", 0),
                all_passed=test_results_raw.get("all_passed", False),
                llm_source=llm_source,
                tutor_hint=tutor_hint,
                action_type=request.action_type,
                attempt_features=None if no_code else summarize_attempt_features(test_results_raw, ast_analysis_raw)
            )
        except Exception as e:
            logger.warning(f"Không thể lưu learning event qua MCP: {e}")

        # 3.1. Tính và lưu sao tự làm
        stars_earned = 0
        star_rationale = None
        new_badges = []
        # CHỈ tính và lưu sao khi là nộp bài chính thức (action_type == 'submit') và vượt qua toàn bộ test cases
        if star_context is not None:
            effective_user = student_username
            # Chống "cày sao" (S2.4): mức gợi ý cao nhất lấy từ TOÀN BỘ lượt `ask_ai` cho tới lần nộp pass đầu tiên
            # (không dùng attempt_history vì bị LIMIT 5 và lẫn hint_level của lượt `submit`). Nộp lại sau khi
            # đã pass cho ra đúng mức sao cũ, nên không thể đẩy trôi vết Mức 2/3 để tăng sao.
            max_hint_used = star_context["max_hint_level_used"]
            official_attempts = star_context["submit_count"] + 1

            stars_earned = calculate_autonomy_stars(
                attempt_count=official_attempts,
                max_hint_level_used=max_hint_used,
                all_passed=True
            )
            star_rationale = explain_autonomy_stars(
                stars_earned, max_hint_used, official_attempts,
                has_passed_before=star_context["has_passed_before"],
            )
            try:
                star_res = save_exercise_stars(
                    username=effective_user,
                    exercise_id=request.exercise_id,
                    stars=stars_earned,
                    clean_score=0
                )
                # Response compatibility only; no achievement badges are awarded.
            except Exception as e:
                logger.warning(f"Không thể cập nhật số sao bài tập: {e}")

        # 4. Đóng gói phản hồi
        return SubmitResponse(
            exercise_id=request.exercise_id,
            test_results=TestResults(**test_results_raw),
            ast_analysis=ASTAnalysis(**ast_analysis_raw),
            tutor_hint=tutor_hint,
            hint_level=request.hint_level,
            discovered_mcp_tools=discovered_tools,
            llm_source=llm_source,
            attempt_history=attempt_history,
            student_model=student_model,
            mcp_trace=mcp_trace,
            stars_earned=stars_earned,
            star_rationale=star_rationale,
            new_badges=new_badges,
            interaction_id=hint_interaction_id,
            adaptive_strategy=adaptive_strategy
        )

    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi chấm bài: {e}"
        )


# ==============================================================================
# PHASE 8: TRÒ CHUYỆN ĐA LƯỢT VỚI GIA SƯ AI & CHẠY THỬ CUSTOM INPUT
# ==============================================================================

@app.post("/api/tutor/chat", response_model=TutorChatResponse)
async def tutor_chat_endpoint(request: TutorChatRequest, token_data: dict = Depends(verify_token)):
    """
    Trò chuyện làm rõ với Gia sư AI (Multi-turn Follow-up Chat):
    - Tiếp nhận câu hỏi làm rõ từ học viên kèm ngữ cảnh bài làm và lịch sử hội thoại
    - Gọi LLM sinh phản hồi thân thiện, Socratic, không lộ code giải
    - Trả về câu trả lời và lịch sử hội thoại đã cập nhật
    """
    try:
        if token_data.get("role") != "student":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chat này dành cho sinh viên.")
        if request.class_id:
            class_info = get_credit_class_by_id(request.class_id, current_username=token_data["sub"])
            if not class_info or not class_info.get("is_enrolled", False):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn chưa ghi danh lớp học phần này.")
        # EXAM policy takes precedence; do not process or expose the message to AI.
        if request.exam_session_id:
            sess_info = get_exam_session_by_id(request.exam_session_id)
            if not sess_info or not sess_info.get("is_active", False):
                raise HTTPException(status_code=404, detail="Không tìm thấy đợt học đang hoạt động.")
            ensure_class_access(sess_info["class_id"], token_data)
            if request.class_id and request.class_id != sess_info["class_id"]:
                raise HTTPException(status_code=403, detail="Đợt học không thuộc lớp đã chọn.")
            if request.exercise_id and request.exercise_id not in sess_info.get("exercise_ids", []):
                raise HTTPException(status_code=403, detail="Bài tập không thuộc đợt học đã chọn.")
            if sess_info.get("allow_ai_hints") == 0 or sess_info.get("session_type") == "EXAM":
                exam_reply = "🔒 **[Chế độ Kỳ thi / Kiểm tra nghiêm ngặt]** Bạn đang trong thời gian làm bài thi. Tính năng trò chuyện và gợi ý từ Gia sư AI bị khóa để đảm bảo tính công bằng học thuật. Vui lòng tự hoàn thành bài làm và sử dụng nút Chạy thử code / Nộp bài."
                updated_history = list(request.history)
                updated_history.extend([ChatMessage(role="user", content=request.user_message), ChatMessage(role="assistant", content=exam_reply)])
                return TutorChatResponse(reply=exam_reply, llm_source="Exam-Mode-Guard", updated_history=updated_history)
        allowed, guard_reason = check_student_input(request.user_message)
        if not allowed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Câu hỏi chưa thuộc phạm vi hỗ trợ học Python.")
        ex_details = {}
        if request.exercise_id:
            try:
                ex_details = db_get_exercise_by_id(request.exercise_id) or {}
            except Exception:
                pass

        # S1.4: khóa phạm vi chat theo trạng thái nộp bài. Chưa có lượt `submit` pass ở bài này → chỉ giải thích
        # khái niệm, KHÔNG đưa code bài làm vào prompt. Đã pass → mở ngữ cảnh là code đã nộp (đọc từ DB,
        # không tin code do client gửi lên).
        passed_code = get_latest_passed_submission_code(token_data["sub"], request.exercise_id) if request.exercise_id else None
        chat_scope = "code_review" if passed_code is not None else "concept_only"
        # S8a: tóm tắt cấu trúc code ĐÃ NỘP (qua MCP) để cả LLM lẫn nhánh offline đều nói được về bài đã nộp.
        ast_summary = await get_code_structure_summary(passed_code) if passed_code else ""

        sm_data = compute_student_model(token_data["sub"], class_id=request.class_id)
        reply, llm_source, telemetry = await generate_chat_followup(
            exercise=ex_details,
            code=passed_code or "",
            user_message=request.user_message,
            history=request.history,
            ast_summary=ast_summary,
            student_model=sm_data,
            chat_scope=chat_scope,
            class_id=request.class_id,  # đã kiểm tra ghi danh ở trên; chỉ truy xuất tài liệu chung + của lớp này
        )
        interaction_id = str(uuid.uuid4())
        save_llm_interaction({"id": interaction_id, "username": token_data["sub"], "role": "student",
                              "task_type": "student_chat", **telemetry})
        save_llm_interaction_sources(interaction_id, telemetry.get("rag_sources", []))

        updated_history = list(request.history)
        updated_history.append(ChatMessage(role="user", content=request.user_message))
        updated_history.append(ChatMessage(role="assistant", content=reply))

        return TutorChatResponse(
            reply=reply,
            llm_source=llm_source,
            updated_history=updated_history,
            interaction_id=interaction_id,
            sources=telemetry.get("source_refs", []),
            knowledge_status=telemetry.get("knowledge_status") or ("grounded" if telemetry.get("source_refs") else "no_source"),
            chat_scope=chat_scope,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi xử lý tutor chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Không thể xử lý cuộc trò chuyện lúc này.")


@app.post("/api/tutor/feedback", status_code=status.HTTP_201_CREATED)
async def tutor_feedback_endpoint(request: TutorFeedbackRequest, token_data: dict = Depends(verify_token)):
    if token_data.get("role") != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ sinh viên mới gửi feedback gia sư.")
    if request.rating not in (-1, 1):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rating phải là 1 hoặc -1.")
    try:
        saved = save_tutor_feedback(request.interaction_id, token_data["sub"], request.rating)
    except Exception as exc:
        if "UNIQUE constraint" in str(exc):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bạn đã đánh giá phản hồi này rồi.")
        raise
    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phản hồi thuộc tài khoản này.")
    return {"status": "saved"}


@app.post("/api/instructor/ai/class-chat", response_model=InstructorAIChatResponse)
async def instructor_class_ai_chat(request: InstructorAIChatRequest, token_data: dict = Depends(require_instructor)):
    cls = get_credit_class_by_id(request.class_id)
    if not cls or not instructor_owns_class(request.class_id, token_data.get("sub", "")):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lớp hoặc bạn không có quyền truy cập.")
    if len(request.user_message.strip()) > 2000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Câu hỏi quá dài.")
    allowed, _ = check_student_input(request.user_message)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Câu hỏi chưa thuộc phạm vi phân tích học tập.")
    summary = get_class_learning_summary(request.class_id, request.days)
    reply, source, telemetry = await generate_instructor_answer(summary, request.user_message)
    interaction_id = str(uuid.uuid4())
    save_llm_interaction({"id": interaction_id, "username": token_data["sub"], "role": "instructor",
                          "task_type": "instructor_class_analytics", **telemetry})
    metrics = summary.get("metrics") or {}
    return InstructorAIChatResponse(
        reply=reply, interaction_id=interaction_id, class_id=request.class_id, llm_source=source,
        days=summary.get("days", request.days), data_status=metrics.get("data_status", "unknown"),
        sample={"submissions": metrics.get("submissions", 0), "active_students": metrics.get("active_students", 0),
                "enrolled_students": metrics.get("enrolled_students", 0)},
    )


_ATTENTION_CACHE: dict[str, tuple[float, dict]] = {}
_ATTENTION_TTL_SECONDS = 60.0


@app.get("/api/instructor/classes-attention")
async def instructor_classes_attention(token_data: dict = Depends(require_instructor)):
    """Tổng hợp số việc cần xem của MỌI lớp giảng viên sở hữu trong một lần gọi (cửa sổ 7 ngày cố định, đệm 60 giây).

    Chỉ trả lớp của chính giảng viên; xếp lớp theo số việc cần xem, không xếp sinh viên.
    """
    import time
    username = token_data.get("sub", "")
    cached = _ATTENTION_CACHE.get(username)
    if cached and time.monotonic() - cached[0] < _ATTENTION_TTL_SECONDS:
        return cached[1]
    rows = []
    for cls in get_credit_classes(instructor_username=username):
        try:
            insights = get_class_insights(cls["id"], 7)
            overview = build_class_overview(insights) if insights else {}
            status = (insights or {}).get("data_status", "no_data")
            attention = len(overview.get("attention", []))
            issues = len(overview.get("class_issues", []))
            plain = build_class_plain_view(insights, overview, 7) if insights else None
            check_in = len(plain["groups"]["check_in"]) if plain else 0
            brief = class_brief_line(plain)
        except Exception as exc:  # noqa: BLE001 - một lớp lỗi không làm hỏng cả danh sách
            logger.warning("Không tổng hợp được lớp %s: %s", cls.get("id"), exc)
            attention, issues, status, check_in, brief = 0, 0, "error", 0, "Chưa tải được tình hình lớp này."
        rows.append({"id": cls["id"], "class_code": cls.get("class_code"), "class_name": cls.get("class_name"),
                     "semester": cls.get("semester"), "attention": attention, "issues": issues,
                     "data_status": status, "total": attention + issues,
                     "check_in": check_in, "brief_vi": brief})
    rows.sort(key=lambda r: (-r["total"], (r["class_code"] or ""), r["id"]))
    result = {"days": 7, "classes": rows, "total_classes": len(rows),
              "needing_attention": sum(1 for r in rows if r["total"] > 0),
              "note": "Số việc cần xem theo quy ước vận hành chưa hiệu chuẩn; không phải điểm hay xếp hạng lớp."}
    _ATTENTION_CACHE[username] = (time.monotonic(), result)
    return result


@app.get("/api/instructor/classes/{class_id}/insights")
async def instructor_class_insights(class_id: str, days: int = 7, token_data: dict = Depends(require_instructor)):
    """Góc nhìn sư phạm theo lớp: bài gây nghẽn, cơ cấu lỗi, sinh viên cần hỗ trợ kèm cỡ mẫu và giới hạn."""
    if not get_credit_class_by_id(class_id) or not instructor_owns_class(class_id, token_data.get("sub", "")):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lớp hoặc bạn không có quyền truy cập.")
    if days < 1 or days > 90:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Khoảng thời gian phải từ 1 đến 90 ngày.")
    insights = get_class_insights(class_id, days)
    if insights:
        insights["overview"] = build_class_overview(insights)
        insights["action_cards"] = build_action_cards(insights["overview"], insights)
        insights["plain"] = build_class_plain_view(insights, insights["overview"], days)
    return insights


@app.get("/api/instructor/classes/{class_id}/students/{username}/exercises/{exercise_id}/journey")
async def instructor_student_exercise_journey(class_id: str, username: str, exercise_id: str, days: Optional[int] = None,
                                              token_data: dict = Depends(require_instructor)):
    """Dấu chân của MỘT sinh viên ở MỘT bài (v5.8). Giảng viên sở hữu lớp; không trả mã nguồn."""
    ensure_class_access(class_id, token_data)
    students = get_class_students(class_id)
    enrolled = {s.get("username") or s.get("student_username") for s in students}
    if username not in enrolled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sinh viên trong lớp này.")
    if exercise_id not in {e["exercise_id"] for e in get_class_exercises(class_id)}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài tập trong lớp này.")
    if days is not None and (days < 1 or days > 90):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Khoảng thời gian phải từ 1 đến 90 ngày.")
    journey = get_exercise_journey(username, exercise_id, days=days, include_code=False)
    journey.update({"class_id": class_id, "username": username, "days": days})
    name = next((s.get("full_name") for s in students
                 if (s.get("username") or s.get("student_username")) == username), None) or username
    journey["story"] = build_story(journey["points"], journey["summary"], audience="teacher", student_name=name)
    return journey


@app.get("/api/instructor/classes/{class_id}/students/{username}/learner-model")
async def instructor_student_learner_model(class_id: str, username: str, token_data: dict = Depends(require_instructor)):
    """Mô hình người học v3 của MỘT sinh viên trong lớp của giảng viên (heuristic mô tả, chưa hiệu chuẩn).

    Chỉ giảng viên sở hữu lớp và chỉ với sinh viên đã ghi danh. Không đưa vào /api/instructor/ai/class-chat.
    """
    ensure_class_access(class_id, token_data)
    enrolled = {s.get("username") or s.get("student_username") for s in get_class_students(class_id)}
    if username not in enrolled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sinh viên trong lớp này.")
    sm = compute_student_model(username, class_id=class_id)
    return {
        "class_id": class_id, "username": username,
        "data_status": (sm.get("analytics_metrics") or {}).get("data_status", "no_data"),
        "analytics_metrics": sm.get("analytics_metrics"),
        "learner_model": sm.get("learner_model"),
    }


@app.get("/api/instructor/ai/feedback-summary")
async def instructor_ai_feedback_summary(days: int = 30, token_data: dict = Depends(require_instructor)):
    """Tổng hợp 👍/👎 theo loại tác vụ AI cho sinh viên thuộc lớp của giảng viên (chỉ số đếm)."""
    if days < 1 or days > 90:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Khoảng thời gian phải từ 1 đến 90 ngày.")
    return get_tutor_feedback_summary(token_data.get("sub", ""), days)


@app.get("/api/instructor/knowledge-base")
async def instructor_knowledge_base(token_data: dict = Depends(require_instructor)):
    """Danh mục tài liệu nội bộ mà RAG đang nạp, để giảng viên kiểm tra nguồn kiến thức của AI."""
    from backend.rag.retriever import list_knowledge_documents, MIN_RELEVANCE
    documents = list_knowledge_documents()
    return {
        "documents": documents,
        "total_documents": len(documents),
        "total_chunks": sum(doc["chunk_count"] for doc in documents),
        "retrieval": {"method": "TF-IDF thưa + cosine trên SQLite cục bộ", "min_relevance": MIN_RELEVANCE, "top_k": 3},
        "scope": "global",
        "notice": ("Đây là tài liệu chung do dự án biên soạn nội bộ, áp dụng cho mọi lớp, chưa phải giáo trình chính thức của NEU. "
                   "Tài liệu riêng của từng lớp nằm ở tab \"Tài liệu cho Gia sư AI\" trong trang chi tiết lớp. "
                   "Khi không có đoạn nào đủ liên quan, gia sư trả lời không kèm nguồn."),
    }


# ------------------------------------------------------------------------------
# v5.4 (C): tài liệu giảng viên tải lên cho Gia sư AI, gắn theo lớp học phần
# ------------------------------------------------------------------------------
KB_LICENSE_TYPES = {"own": "Tự biên soạn", "licensed": "Được tác giả/đơn vị cấp phép", "open": "Tài liệu mở có giấy phép"}


def _kb_doc_view(doc: dict) -> dict:
    from backend.rag.retriever import _chunk_document
    text = doc.get("content_text")
    view = {k: v for k, v in doc.items() if k != "content_text"}
    view["is_active"] = bool(doc["is_active"])
    if text is not None:
        chunks = _chunk_document(text)
        view["chunk_count"] = len(chunks)
        view["sections"] = list(dict.fromkeys(section for section, _ in chunks if section))
    return view


@app.post("/api/instructor/classes/{class_id}/knowledge", status_code=status.HTTP_201_CREATED)
async def upload_class_knowledge(
    class_id: str,
    file: UploadFile = File(...),
    title: str = Form(""),
    license_type: str = Form(""),
    license_detail: str = Form(""),
    provenance: str = Form(""),
    no_personal_data: str = Form(""),
    token_data: dict = Depends(require_instructor),
):
    """Tải tài liệu cho Gia sư AI của đúng lớp này. Từ chối khi sai định dạng/quá giới hạn/thiếu khai báo."""
    from backend.rag.extract import ExtractionError, MAX_FILE_BYTES, extract_text, file_format
    ensure_class_access(class_id, token_data)
    filename = (file.filename or "").strip()
    try:
        file_format(filename)  # kiểm tra định dạng trước khi đọc nội dung
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if license_type not in KB_LICENSE_TYPES:
        raise HTTPException(status_code=422, detail="Hãy chọn quyền sử dụng tài liệu (tự biên soạn / được cấp phép / tài liệu mở).")
    if license_type == "open" and not license_detail.strip():
        raise HTTPException(status_code=422, detail="Tài liệu mở phải ghi rõ giấy phép (ví dụ CC BY 4.0).")
    if not provenance.strip():
        raise HTTPException(status_code=422, detail="Hãy khai báo nguồn gốc tài liệu (tác giả, năm, đường dẫn nếu có).")
    if no_personal_data.strip().lower() not in {"true", "1", "on", "yes"}:
        raise HTTPException(status_code=422, detail="Bạn cần cam kết tài liệu không chứa dữ liệu cá nhân sinh viên, đề thi hay đáp án bài tập của lớp.")
    if count_kb_documents(class_id) >= MAX_KB_DOCUMENTS_PER_CLASS:
        raise HTTPException(status_code=422, detail=f"Mỗi lớp tối đa {MAX_KB_DOCUMENTS_PER_CLASS} tài liệu. Hãy xóa bớt tài liệu cũ.")
    data = await file.read(MAX_FILE_BYTES + 1)
    try:
        fmt, text, warnings = extract_text(filename, data)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    clean_title = (title.strip() or filename.rsplit(".", 1)[0])[:200]
    detail = license_detail.strip()
    full_provenance = provenance.strip()[:500] + (f" · Giấy phép: {detail[:200]}" if detail else "")
    doc_id = create_kb_document(class_id, clean_title, filename[:255], fmt, text, full_provenance, license_type,
                                token_data["sub"])
    chunks = rebuild_knowledge_index()
    doc = next(d for d in list_kb_documents(class_id, include_text=True) if d["id"] == doc_id)
    return {"document": _kb_doc_view(doc), "warnings": warnings, "total_chunks_indexed": chunks}


@app.get("/api/instructor/classes/{class_id}/knowledge")
async def list_class_knowledge(class_id: str, token_data: dict = Depends(require_instructor)):
    ensure_class_access(class_id, token_data)
    from backend.rag import extract as kb_limits
    documents = [_kb_doc_view(d) for d in list_kb_documents(class_id, include_text=True)]
    return {
        "documents": documents,
        "total_documents": len(documents),
        "limits": {"max_documents": MAX_KB_DOCUMENTS_PER_CLASS, "max_file_mb": kb_limits.MAX_FILE_BYTES // (1024 * 1024),
                   "max_chars": kb_limits.MAX_TEXT_CHARS, "formats": list(kb_limits.ALLOWED_EXTENSIONS)},
        "license_types": KB_LICENSE_TYPES,
    }


@app.patch("/api/instructor/classes/{class_id}/knowledge/{doc_id}")
async def toggle_class_knowledge(class_id: str, doc_id: int, request: KnowledgeToggleRequest,
                                 token_data: dict = Depends(require_instructor)):
    ensure_class_access(class_id, token_data)
    if not set_kb_document_active(class_id, doc_id, request.is_active):
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu trong lớp này.")
    rebuild_knowledge_index()
    return {"id": doc_id, "is_active": request.is_active}


@app.delete("/api/instructor/classes/{class_id}/knowledge/{doc_id}")
async def delete_class_knowledge(class_id: str, doc_id: int, token_data: dict = Depends(require_instructor)):
    ensure_class_access(class_id, token_data)
    if not delete_kb_document(class_id, doc_id):
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu trong lớp này.")
    rebuild_knowledge_index()
    return {"id": doc_id, "deleted": True}


@app.post("/api/custom-run", response_model=CustomRunResponse)
async def custom_run_endpoint(request: CustomRunRequest, token_data: dict = Depends(verify_token)):
    """
    Chạy thử chương trình với dữ liệu đầu vào tự chọn (Custom Stdin):
    - Thực thi qua MCP Sandbox cô lập với timeout 5.0s
    - Trả về stdout, stderr, execution_time_ms và trạng thái
    """
    try:
        res = await run_custom_test_pipeline(code=request.code, custom_input=request.custom_input)
        return CustomRunResponse(
            stdout=res.get("stdout", ""),
            stderr=res.get("stderr", ""),
            execution_time_ms=res.get("execution_time_ms", 0.0),
            status=res.get("status", "SUCCESS"),
            error_message=res.get("error_message", None)
        )
    except Exception as e:
        logger.error(f"Lỗi khi chạy thử custom input: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi chạy thử: {e}"
        )


@app.post("/api/trace-execution", response_model=TraceExecutionResponse)
async def trace_execution_endpoint(request: TraceExecutionRequest, token_data: dict = Depends(verify_token)):
    """
    [MCP Tool 8] Tracing từng bước thực thi (Execution Step Visualizer):
    - Ghi lại từng frame execution qua sys.settrace trong MCP Server
    - Trả về danh sách code_lines, steps (line, event, locals, stdout), error
    """
    try:
        res = await execute_trace_pipeline(
            code=request.code,
            stdin_input=request.stdin_input,
            max_steps=request.max_steps
        )
        return TraceExecutionResponse(**res)
    except Exception as e:
        logger.error(f"Lỗi khi trace execution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tracing mã nguồn: {e}"
        )


@app.get("/api/student-model/{session_id}")
@app.get("/api/student/model")
async def get_student_model_endpoint(session_id: str = "default_session", token_data: dict = Depends(require_student)):
    """Lấy mô hình học sinh thích ứng theo session_id."""
    return compute_student_model(token_data["sub"])



@app.get("/api/student/profile", response_model=StudentProfileResponse)
async def get_student_profile_endpoint(
    session_id: str,
    exercise_id: str = "",
    class_id: Optional[str] = None,
    token_data: dict = Depends(require_student),
):
    """
    [Hồ sơ Thích ứng của Học viên - Phase 13/14 Quantitative Analytics]
    Gọi MCP Tool get_student_model và get_attempt_history qua giao thức MCP,
    trả về năng lực tổng hợp, 4D metrics, diagnostic evaluation và các lần nộp bài gần nhất.
    """
    try:
        session_id = token_data["sub"]
        if class_id:
            ensure_class_access(class_id, token_data)
        data = await get_student_profile_via_mcp(session_id=session_id, exercise_id=exercise_id, class_id=class_id)
        sm = data.get("student_model", {})
        attempts = data.get("recent_attempts", [])
        return StudentProfileResponse(
            session_id=session_id,
            class_id=class_id,
            total_exercises_attempted=sm.get("total_exercises_attempted", 0),
            total_submissions=sm.get("total_submissions", 0),
            mastered_exercises=sm.get("mastered_exercises", []),
            struggling_exercises=sm.get("struggling_exercises", []),
            in_progress_exercises=sm.get("in_progress_exercises", []),
            average_hint_level=sm.get("average_hint_level", 1.0),
            summary=sm.get("summary", "Đã nạp hồ sơ năng lực học sinh."),
            analytics_metrics=sm.get("analytics_metrics"),
            diagnostic_evaluation=sm.get("diagnostic_evaluation"),
            data_status=(sm.get("analytics_metrics") or {}).get("data_status", "available" if sm.get("total_submissions", 0) else "no_data"),
            learner_model=sm.get("learner_model"),
            recent_attempts=attempts
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Lỗi truy xuất student profile qua MCP, dùng fallback: {e}")
        sm = compute_student_model(session_id, class_id=class_id)
        attempts = get_attempts(session_id, exercise_id, limit=5) if exercise_id else []
        return StudentProfileResponse(
            session_id=session_id,
            class_id=class_id,
            total_exercises_attempted=sm.get("total_exercises_attempted", 0),
            total_submissions=sm.get("total_submissions", 0),
            mastered_exercises=sm.get("mastered_exercises", []),
            struggling_exercises=sm.get("struggling_exercises", []),
            in_progress_exercises=sm.get("in_progress_exercises", []),
            average_hint_level=sm.get("average_hint_level", 1.0),
            summary=sm.get("summary", "Đã nạp hồ sơ năng lực."),
            analytics_metrics=sm.get("analytics_metrics"),
            diagnostic_evaluation=sm.get("diagnostic_evaluation"),
            data_status=(sm.get("analytics_metrics") or {}).get("data_status", "available" if sm.get("total_submissions", 0) else "no_data"),
            learner_model=sm.get("learner_model"),
            recent_attempts=attempts
        )


def _pick_path_class(username: str, class_id: Optional[str], recent: list[dict],
                     focus_class_id: Optional[str] = None) -> Optional[dict]:
    """Lớp để vẽ chặng đường: lớp đang xem; nếu không thì lớp sinh viên vừa mở, lớp chứa nhiều bài làm gần đây nhất, lớp đầu tiên."""
    if class_id:
        cls = get_credit_class_by_id(class_id) or {}
        return {"id": class_id, "class_name": cls.get("class_name"), "exercises": get_class_exercises(class_id, username)}
    classes = get_student_classes(username)
    if not classes:
        return None
    loaded = [{"id": c["id"], "class_name": c.get("class_name"), "exercises": get_class_exercises(c["id"], username)}
              for c in classes]
    return pick_path_class(loaded, recent, focus_class_id)


@app.get("/api/student/journey")
async def get_student_journey_endpoint(
    class_id: Optional[str] = None,
    exercise_id: Optional[str] = None,
    focus_class_id: Optional[str] = None,
    token_data: dict = Depends(require_student),
):
    """Hành trình học (v5.8): câu tóm tắt, bản đồ khái niệm, dấu chân. Chỉ dữ liệu của chính người dùng trong token."""
    username = token_data["sub"]
    if class_id:
        ensure_class_access(class_id, token_data)
        if exercise_id and exercise_id not in {e["exercise_id"] for e in get_class_exercises(class_id)}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài tập trong lớp này.")
    elif exercise_id and not db_get_exercise_by_id(exercise_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài tập.")
    try:
        data = await get_student_profile_via_mcp(session_id=username, class_id=class_id)
        sm = data.get("student_model", {})
    except Exception as e:  # noqa: BLE001 - fallback như /api/student/profile
        logger.warning(f"Lỗi truy xuất hành trình qua MCP, dùng fallback: {e}")
        sm = compute_student_model(username, class_id=class_id)
    lm = sm.get("learner_model") or {}
    next_practice = (sm.get("analytics_metrics") or {}).get("next_practice")
    overview = get_student_journey_overview(username, class_id=class_id)
    for item in overview["recent_exercises"]:
        item["story_vi"] = story_one_liner(item)
    current = None
    if exercise_id:
        current = get_exercise_journey(username, exercise_id, include_code=True)
        current["description_vi"] = describe_exercise_journey(current["points"], current["summary"])
        current["story"] = build_story(current["points"], current["summary"], audience="student")
    path_class = _pick_path_class(username, class_id, overview["recent_exercises"], focus_class_id)
    path = (build_course_path(path_class["exercises"], path_class["id"], path_class["class_name"])
            if path_class else None)
    today = build_today_card(full_name=token_data.get("name"), concepts=lm.get("concepts", []),
                             next_practice=next_practice, week=overview["week"],
                             recent=overview["recent_exercises"], path=path, now=datetime.now())
    if today and today.get("next_step"):
        next_eid = today["next_step"].get("exercise_id")
        next_cls = get_exercise_class_info(next_eid, student_username=username, preferred_class_id=class_id)
        if next_cls:
            today["next_step"]["class_id"] = next_cls["id"]
            today["next_step"]["class_name"] = next_cls.get("class_name")
            today["next_step"]["class_code"] = next_cls.get("class_code")
    return {
        "today": today,
        "headline": build_student_headline(lm, next_practice, overview["week"], overview["recent_exercises"]),
        "week": overview["week"],
        "concepts": lm.get("concepts", []),
        "support_profile": lm.get("support_profile"),
        "next_practice": next_practice,
        "recent_exercises": overview["recent_exercises"],
        "current": current,
        "data_status": (sm.get("analytics_metrics") or {}).get("data_status", "no_data"),
        "disclaimer": DISCLAIMER_VI,
    }


@app.get("/api/skill-roadmap", response_model=SkillRoadmapResponse)
async def get_skill_roadmap_endpoint(
    session_id: str = "default_session",
    class_id: Optional[str] = None,
    token_data: dict = Depends(require_student),
):
    """
    [Legacy compatibility endpoint; progression is based on completion, not star thresholds.]
    """
    try:
        session_id = token_data["sub"]
        if class_id:
            ensure_class_access(class_id, token_data)
        achievements = get_user_achievements(session_id)
        stars_by_ex = achievements.get("exercise_stars", achievements.get("stars_by_exercise", {}))

        if class_id:
            cls_info = get_credit_class_by_id(class_id)
            class_name = cls_info.get("class_name") if cls_info else None
            class_code = cls_info.get("class_code") if cls_info else None
            class_exercises = get_class_exercises(class_id)

            if class_exercises:
                student_model = compute_student_model(session_id, class_id=class_id)
                mastered_set = set(student_model.get("mastered_exercises", []))
                struggling_set = set(student_model.get("struggling_exercises", []))
                in_prog_set = set(student_model.get("in_progress_exercises", []))

                completed_set = set(mastered_set)
                completed_set.update(ex_id for ex_id, stars in stars_by_ex.items() if stars > 0)

                nodes = []
                for item in class_exercises:
                    ex_id = item["exercise_id"]
                    stars_earned = stars_by_ex.get(ex_id, 0)
                    prereq = item.get("prerequisite_id")
                    prereqs = [prereq] if prereq else []
                    if ex_id in completed_set:
                        st = "MASTERED"
                        desc = f"Đã hoàn thành ({stars_earned} ⭐ tự làm)"
                        unlocked = True
                    elif ex_id in in_prog_set or ex_id in struggling_set:
                        st = "IN_PROGRESS"
                        desc = "Đang thực hành (Chưa vượt qua tất cả test cases)"
                        unlocked = True
                    else:
                        prereq_met = (not prereq) or (prereq in completed_set)
                        if prereq_met:
                            st = "AVAILABLE"
                            desc = "Sẵn sàng làm bài"
                            unlocked = True
                        else:
                            st = "LOCKED"
                            desc = f"Khóa - Cần hoàn thành bài tiên quyết ({prereq})"
                            unlocked = False

                    nodes.append(SkillNode(
                        id=ex_id,
                        title=item.get("title", ex_id),
                        category=item.get("category", "General"),
                        difficulty=item.get("difficulty", "EASY"),
                        prerequisites=prereqs,
                        status=st,
                        min_stars_required=1,
                        stars_earned=stars_earned,
                        module_name=item.get("module_name", "Chung"),
                        order_idx=item.get("order_idx", 1),
                        skill_tag=item.get("skill_tag", "Python Core"),
                        status_description=desc,
                        is_unlocked=unlocked
                    ))

                return SkillRoadmapResponse(
                    class_id=class_id,
                    class_name=class_name,
                    class_code=class_code,
                    nodes=nodes,
                    total_mastered=len([n for n in nodes if n.status == "MASTERED"]),
                    total_exercises=len(nodes)
                )

        # Fallback toàn cục (nếu không truyền class_id)
        exercises = db_get_all_exercises(include_inactive=False)
        student_model = compute_student_model(session_id)
        mastered_set = set(student_model.get("mastered_exercises", []))

        attempts_summary = {}
        for ex in exercises:
            ex_id = ex["id"]
            att = get_attempts(session_id, ex_id, limit=1)
            if att:
                attempts_summary[ex_id] = True

        prereq_map = {
            "ex_01_sum_1_to_n": [],
            "ex_02_prime_check": ["ex_01_sum_1_to_n"],
            "ex_03_factorial": ["ex_01_sum_1_to_n"],
            "ex_04_reverse_string": ["ex_01_sum_1_to_n"],
            "ex_05_count_vowels": ["ex_04_reverse_string"]
        }

        nodes = []
        for ex in exercises:
            ex_id = ex["id"]
            prereqs = prereq_map.get(ex_id, ["ex_01_sum_1_to_n"] if ex_id != "ex_01_sum_1_to_n" else [])
            stars_earned = stars_by_ex.get(ex_id, 0)

            if ex_id in mastered_set or stars_earned >= 1:
                st = "MASTERED"
                desc = f"Đạt chuẩn ({stars_earned} ⭐)"
                unlocked = True
            elif ex_id in attempts_summary:
                st = "IN_PROGRESS"
                desc = "Đang thực hành"
                unlocked = True
            else:
                all_prereqs_met = all((p in mastered_set or stars_by_ex.get(p, 0) >= 1) for p in prereqs)
                if all_prereqs_met:
                    st = "AVAILABLE"
                    desc = "Sẵn sàng làm bài"
                    unlocked = True
                else:
                    st = "LOCKED"
                    desc = "Khóa do chưa hoàn thành bài tiên quyết"
                    unlocked = False

            nodes.append(SkillNode(
                id=ex_id,
                title=ex["title"],
                category=ex["category"],
                difficulty=ex["difficulty"],
                prerequisites=prereqs,
                status=st,
                min_stars_required=1,
                stars_earned=stars_earned,
                status_description=desc,
                is_unlocked=unlocked
            ))

        return SkillRoadmapResponse(
            nodes=nodes,
            total_mastered=len([n for n in nodes if n.status == "MASTERED"]),
            total_exercises=len(nodes)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi xây dựng skill roadmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tải lộ trình kỹ năng: {e}"
        )


# ==============================================================================
# PHASE 10: SELF-RELIANCE STARS, PYTHONIC REVIEW & LEADERBOARD
# ==============================================================================

@app.post("/api/tutor/pythonic-review", response_model=PythonicReviewResponse)
async def pythonic_review_endpoint(request: PythonicReviewRequest, token_data: dict = Depends(require_student)):
    """
    [Phase 10: Thử thách Tối ưu Code Chuẩn Pythonic]
    Gia sư AI đóng vai trò Senior Python Tech Lead đánh giá mã nguồn đã pass 100%:
    - Chấm điểm Clean Code (0-100, sàn 70 khích lệ)
    - Chỉ ra điểm mạnh & cơ hội tối ưu (idiomatic Python)
    - Cung cấp đoạn code chuẩn mực mẫu và giải thích chuyên sâu
    """
    try:
        ex_detail = await get_exercise_details(request.exercise_id)
        if not ex_detail or ex_detail.get("error"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Không tìm thấy bài tập '{request.exercise_id}'")
        check = await run_test_only_pipeline(request.exercise_id, request.code)
        if not check.get("test_results", {}).get("all_passed", False):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ có thể yêu cầu review sau khi vượt qua toàn bộ test.")
        review_dict, llm_source, telemetry = await generate_pythonic_review(
            exercise=ex_detail,
            student_code=request.code
        )

        clean_score = review_dict.get("clean_score", 85)
        username = token_data["sub"]
        review_interaction_id = str(uuid.uuid4())
        save_llm_interaction({"id": review_interaction_id, "username": username, "role": "student",
                              "task_type": "pythonic_review", **telemetry})

        # Cập nhật điểm clean score nếu bài đã có dòng sao (từ `submit`); review không tự cấp sao
        # và không tạo dòng 0 sao. Huy hiệu không còn được cấp.
        save_res = save_exercise_stars(
            username=username,
            exercise_id=request.exercise_id,
            stars=0,
            clean_score=clean_score
        )

        return PythonicReviewResponse(
            clean_score=clean_score,
            strengths=review_dict.get("strengths", ""),
            improvements=review_dict.get("improvements", ""),
            pythonic_code=review_dict.get("pythonic_code", request.code),
            explanation=review_dict.get("explanation", ""),
            interaction_id=review_interaction_id,
            llm_source=llm_source,
            stars_earned=save_res.get("stars_earned", 0),
            new_badges=save_res.get("new_badges", [])
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi review Pythonic: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi review mã nguồn: {e}"
        )


@app.get("/api/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard_endpoint(limit: int = 20, token_data: dict = Depends(verify_token)):
    """
    [Phase 10: Bảng Xếp Hạng Lớp Học (Classroom Leaderboard)]
    Xếp hạng học viên theo tổng số sao tự làm, số bài đã làm chủ và điểm Clean Code.
    """
    try:
        leaderboard = get_class_leaderboard(limit=limit)
        return LeaderboardResponse(
            leaderboard=leaderboard,
            total_students=len(leaderboard)
        )
    except Exception as e:
        logger.error(f"Lỗi khi tải bảng xếp hạng: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tải bảng xếp hạng: {e}"
        )


@app.get("/api/student/achievements", response_model=UserAchievementsResponse)
async def get_student_achievements_endpoint(username: str = "student", token_data: dict = Depends(require_student)):
    """
    Lấy tổng số sao tự làm và số sao theo từng bài tập.
    """
    try:
        username = token_data["sub"]
        data = get_user_achievements(username)
        return UserAchievementsResponse(**data)
    except Exception as e:
        logger.error(f"Lỗi khi tải thành tích học viên: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tải thành tích: {e}"
        )


# ==============================================================================
# 6. QUẢN TRỊ BÀI TẬP & THỐNG KÊ CHO GIẢNG VIÊN (INSTRUCTOR CRUD)
# ==============================================================================

@app.get("/api/instructor/dashboard", response_model=InstructorDashboardStats)
async def instructor_dashboard(token_data: dict = Depends(require_instructor)):
    """Thống kê tổng quan học tập dành cho Giảng viên."""
    stats = get_instructor_stats(instructor_username=token_data.get("sub", ""))
    return InstructorDashboardStats(**stats)


@app.get("/api/instructor/submissions", response_model=list[SubmissionItem])
async def list_recent_submissions(token_data: dict = Depends(require_instructor)):
    """Xem toàn bộ lịch sử các lần nộp bài của sinh viên (kèm code & tutor hint)."""
    submissions = get_all_submissions(limit=100, instructor_username=token_data.get("sub", ""))
    return [SubmissionItem(**s) for s in submissions]


@app.get("/api/instructor/submissions/{submission_id}", response_model=SubmissionItem)
async def get_single_submission(
    submission_id: int,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên xem chi tiết một bài nộp cụ thể (mã nguồn + kết quả + phản hồi AI)."""
    sub = get_submission_by_id(submission_id, instructor_username=token_data.get("sub", ""))
    if not sub:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài nộp.")
    return SubmissionItem(**sub)


@app.get("/api/instructor/exercises", response_model=list[ExerciseSummary])
async def instructor_list_all_exercises(token_data: dict = Depends(require_instructor)):
    """Chỉ trả bài hệ thống, bài sở hữu hoặc bài được chia sẻ với giảng viên."""
    username = token_data.get("sub", "")
    rows = db_get_all_exercises(include_inactive=True, instructor_username=username)
    for row in rows:
        row["can_manage"] = row.get("created_by") == username
    return rows


@app.post("/api/instructor/exercises", response_model=ExerciseDetail)
async def create_new_exercise(
    exercise_data: ExerciseUpsertRequest,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên tạo mới một bài tập lập trình vào ngân hàng đề."""
    owner = get_exercise_owner(exercise_data.id)
    if owner:
        raise HTTPException(status_code=409, detail="Mã bài tập đã tồn tại. Mỗi bài tập phải có một chủ sở hữu rõ ràng.")
    tc_dicts = [tc.model_dump() for tc in exercise_data.test_cases]
    saved = db_save_exercise(
        exercise_id=exercise_data.id,
        title=exercise_data.title,
        difficulty=exercise_data.difficulty,
        category=exercise_data.category,
        description=exercise_data.description,
        starter_code=exercise_data.starter_code,
        test_cases=tc_dicts,
        created_by=token_data.get("sub", "instructor")
    )
    if not saved:
        raise HTTPException(status_code=400, detail="Không thể tạo bài tập.")
    return saved


@app.put("/api/instructor/exercises/{exercise_id}", response_model=ExerciseDetail)
async def update_exercise(
    exercise_id: str,
    exercise_data: ExerciseUpsertRequest,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên chỉnh sửa bài tập đã có."""
    if get_exercise_owner(exercise_id) != token_data.get("sub"):
        raise HTTPException(status_code=403, detail="Chỉ người tạo bài tập mới được chỉnh sửa.")
    tc_dicts = [tc.model_dump() for tc in exercise_data.test_cases]
    saved = db_save_exercise(
        exercise_id=exercise_id,
        title=exercise_data.title,
        difficulty=exercise_data.difficulty,
        category=exercise_data.category,
        description=exercise_data.description,
        starter_code=exercise_data.starter_code,
        test_cases=tc_dicts,
        created_by=token_data.get("sub", "instructor")
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập cần cập nhật.")
    return saved


@app.delete("/api/instructor/exercises/{exercise_id}")
async def remove_exercise(
    exercise_id: str,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên xóa một bài tập khỏi ngân hàng đề."""
    if get_exercise_owner(exercise_id) != token_data.get("sub"):
        raise HTTPException(status_code=403, detail="Chỉ người tạo bài tập mới được xóa.")
    deleted = db_delete_exercise(exercise_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập để xóa.")
    return {"status": "success", "message": f"Đã xóa bài tập {exercise_id}"}


@app.post("/api/instructor/exercises/{exercise_id}/shares", status_code=201)
async def share_exercise_with_instructor(exercise_id: str, request: ExerciseShareRequest,
                                         token_data: dict = Depends(require_instructor)):
    recipient = request.instructor_username.strip()
    if not grant_exercise_share(exercise_id, recipient, token_data.get("sub", "")):
        raise HTTPException(status_code=404, detail="Bài không thuộc quyền sở hữu của bạn hoặc giảng viên nhận không hợp lệ.")
    return {"status": "shared", "exercise_id": exercise_id, "instructor_username": recipient}


@app.delete("/api/instructor/exercises/{exercise_id}/shares/{instructor_username}")
async def unshare_exercise_from_instructor(exercise_id: str, instructor_username: str,
                                          token_data: dict = Depends(require_instructor)):
    if not revoke_exercise_share(exercise_id, instructor_username, token_data.get("sub", "")):
        raise HTTPException(status_code=404, detail="Bài không thuộc quyền sở hữu của bạn.")
    return {"status": "revoked", "exercise_id": exercise_id, "instructor_username": instructor_username}


# ==============================================================================
# QUẢN LÝ ĐƠN VỊ KIẾN THỨC (KNOWLEDGE COMPONENTS - KC) DÀNH CHO GIẢNG VIÊN
# ==============================================================================

@app.get("/api/knowledge-components", response_model=list[KnowledgeComponentItem])
def get_public_knowledge_components():
    """Lấy danh sách các đơn vị kiến thức (KC) đang hoạt động trong hệ thống."""
    return get_all_knowledge_components(include_inactive=False)


@app.get("/api/instructor/knowledge-components", response_model=list[KnowledgeComponentItem])
def get_instructor_knowledge_components(token_data: dict = Depends(require_instructor)):
    """[Giảng viên] Lấy toàn bộ danh sách các đơn vị kiến thức (bao gồm nguồn gốc người tạo)."""
    return get_all_knowledge_components(include_inactive=False)


@app.post("/api/instructor/knowledge-components", response_model=KnowledgeComponentItem)
def create_instructor_knowledge_component(
    body: KnowledgeComponentCreateRequest,
    token_data: dict = Depends(require_instructor)
):
    """[Giảng viên] Thêm hoặc cập nhật đơn vị kiến thức (KC) mới và từ khóa nhận diện."""
    username = token_data.get("sub", "instructor")
    raw_kc = body.kc
    if not raw_kc or not raw_kc.strip():
        from pytutor_shared.learner_model import _fold
        clean_text = _fold(body.label_vi)
        raw_kc = re.sub(r"[^a-z0-9]+", "_", clean_text).strip("_")
    raw_kc = raw_kc.strip().lower()
    if not re.match(r"^[a-z0-9_]{2,40}$", raw_kc):
        raise HTTPException(
            status_code=400,
            detail="Mã định danh KC (slug) chỉ được chứa chữ cái thường, số và dấu gạch dưới, độ dài từ 2 đến 40 ký tự."
        )
    clean_kws = [k.strip() for k in body.keywords if k and k.strip()]
    if not clean_kws:
        raise HTTPException(status_code=400, detail="Cần ít nhất một từ khóa nhận diện cho đơn vị kiến thức này.")

    res = create_knowledge_component(
        kc=raw_kc,
        label_vi=body.label_vi.strip(),
        keywords=clean_kws,
        created_by=username
    )
    return res


@app.delete("/api/instructor/knowledge-components/{kc}")
def delete_instructor_knowledge_component(
    kc: str,
    token_data: dict = Depends(require_instructor)
):
    """[Giảng viên] Xóa đơn vị kiến thức tùy chỉnh (không thể xóa 6 KC mặc định của hệ thống)."""
    try:
        success = delete_knowledge_component(kc)
        if not success:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn vị kiến thức cần xóa.")
        return {"status": "success", "message": f"Đã xóa đơn vị kiến thức '{kc}' thành công."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


# ==============================================================================
# PHASE 12: QUẢN LÝ LỚP TÍN CHỈ & KỲ THI / ĐỢT THỰC HÀNH (CREDIT CLASSES & EXAMS)
# ==============================================================================

@app.get("/api/classes", response_model=list[CreditClassSummary])
async def list_credit_classes(
    instructor_username: Optional[str] = None,
    student_username: Optional[str] = None,
    token_data: dict = Depends(verify_token),
):
    """Lấy danh sách các Lớp tín chỉ (kèm thông tin Học phần NEU, giảng viên, sĩ số, số bài tập và trạng thái ghi danh)."""
    try:
        username = token_data["sub"]
        if token_data.get("role") == "instructor":
            if student_username and student_username != username:
                raise HTTPException(status_code=403, detail="Không được truy vấn dữ liệu học viên theo tài khoản khác.")
            classes = get_credit_classes(instructor_username=username)
        elif token_data.get("role") == "student":
            if instructor_username and instructor_username != username:
                raise HTTPException(status_code=403, detail="Không được truy vấn lớp theo tài khoản giảng viên khác.")
            classes = get_credit_classes(current_username=username)
        else:
            raise HTTPException(status_code=403, detail="Vai trò không được phép truy cập danh sách lớp.")
        return [CreditClassSummary(**c) for c in classes]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách lớp tín chỉ: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tải danh sách lớp tín chỉ: {e}"
        )


@app.get("/api/student/my-classes", response_model=list[CreditClassSummary])
async def get_my_classes_endpoint(token_data: dict = Depends(require_student)):
    """
    [Cổng Lớp học phần của Tôi - My NEU Classes]
    Lấy danh sách các lớp học phần mà sinh viên hiện tại đã ghi danh, kèm tiến độ hoàn thành (%).
    """
    try:
        student_username = token_data.get("sub", "student")
        classes = get_student_classes(student_username)
        return [CreditClassSummary(**c) for c in classes]
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách lớp của sinh viên: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tải lớp học phần của bạn: {e}"
        )


@app.post("/api/instructor/classes", response_model=CreditClassSummary)
async def create_new_class(
    class_data: CreditClassCreateRequest,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên tạo mới một Lớp tín chỉ / Lớp học phần chuẩn NEU."""
    try:
        created = create_credit_class(
            class_code=class_data.class_code,
            class_name=class_data.class_name,
            course_code=class_data.course_code or "CNTT1116",
            credits=class_data.credits or 3,
            faculty=class_data.faculty or "Khoa Công nghệ thông tin - NEU",
            semester=class_data.semester,
            enrollment_code=class_data.enrollment_code or "",
            instructor_username=token_data.get("sub", "gv_tran"),
            description=class_data.description or ""
        )
        return CreditClassSummary(**created)
    except Exception as e:
        logger.error(f"Lỗi khi tạo lớp tín chỉ: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể tạo lớp tín chỉ: {e}"
        )


@app.post("/api/classes/{class_id}/enroll")
async def enroll_class_endpoint(
    class_id: str,
    body: Optional[ClassEnrollmentRequest] = None,
    token_data: dict = Depends(verify_token)
):
    """Sinh viên hoặc Giảng viên ghi danh người học vào lớp tín chỉ."""
    try:
        target_student = token_data.get("sub", "")
        if token_data.get("role") == "instructor":
            ensure_class_access(class_id, token_data)
            if not body or not body.student_username:
                raise HTTPException(status_code=422, detail="Giảng viên cần chỉ định sinh viên cần ghi danh.")
            target_student = body.student_username
        elif token_data.get("role") != "student":
            raise HTTPException(status_code=403, detail="Vai trò không được phép ghi danh.")

        success = enroll_student_in_class(class_id=class_id, student_username=target_student)
        return {
            "status": "success",
            "enrolled": success,
            "class_id": class_id,
            "student_username": target_student,
            "message": f"Đã ghi danh {target_student} vào lớp {class_id} thành công."
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Lỗi khi ghi danh lớp tín chỉ: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi ghi danh: {e}"
        )


@app.post("/api/classes/enroll-by-code")
async def enroll_class_by_code_endpoint(
    request: ClassEnrollByCodeRequest,
    token_data: dict = Depends(verify_token)
):
    """Sinh viên ghi danh vào Lớp học phần bằng Mã tham gia lớp (Enrollment Code)."""
    try:
        if token_data.get("role") != "student":
            raise HTTPException(status_code=403, detail="Chỉ sinh viên mới được ghi danh bằng mã lớp.")
        target_student = token_data["sub"]
        cls = get_class_by_enrollment_code(request.enrollment_code)
        if not cls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy lớp học phần với mã '{request.enrollment_code}'. Vui lòng kiểm tra lại."
            )

        success = enroll_student_in_class(class_id=cls["id"], student_username=target_student)
        return {
            "status": "success",
            "enrolled": success,
            "class_id": cls["id"],
            "class_code": cls["class_code"],
            "class_name": cls["class_name"],
            "student_username": target_student,
            "message": f"Đã ghi danh thành công vào lớp '{cls['class_name']}' ({cls['class_code']})!"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi ghi danh bằng mã: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi ghi danh: {e}"
        )


@app.delete("/api/classes/{class_id}/leave")
@app.post("/api/classes/{class_id}/leave")
async def leave_class_endpoint(
    class_id: str,
    token_data: dict = Depends(verify_token)
):
    """Sinh viên rời khỏi (hủy ghi danh) một Lớp học phần."""
    try:
        if token_data.get("role") != "student":
            raise HTTPException(status_code=403, detail="Chỉ sinh viên mới được rời lớp bằng chức năng này.")
        target_student = token_data["sub"]
        success = unenroll_student_from_class(class_id=class_id, student_username=target_student)
        return {
            "status": "success",
            "unenrolled": success,
            "class_id": class_id,
            "student_username": target_student,
            "message": f"Đã hủy ghi danh khỏi lớp {class_id} thành công."
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Lỗi khi hủy ghi danh: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi hủy ghi danh: {e}"
        )


@app.get("/api/classes/{class_id}/curriculum", response_model=list[ClassExerciseItem])
async def get_class_curriculum_endpoint(
    class_id: str,
    student_username: Optional[str] = None,
    token_data: dict = Depends(verify_token),
):
    """Lấy danh sách bài tập và cấu hình Lộ trình kỹ năng (Curriculum & Skill Matrix) của lớp học phần."""
    try:
        ensure_class_access(class_id, token_data)
        if student_username and student_username != token_data.get("sub"):
            raise HTTPException(status_code=403, detail="Không được xem tiến độ của tài khoản khác.")
        own_student = token_data["sub"] if token_data.get("role") == "student" else None
        exercises = get_class_exercises(class_id, student_username=own_student)
        return [ClassExerciseItem(**e) for e in exercises]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi tải chương trình học của lớp: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tải chương trình lớp: {e}"
        )


@app.post("/api/instructor/classes/{class_id}/exercises")
async def assign_exercise_to_class_endpoint(
    class_id: str,
    body: ClassExerciseAssignRequest,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên gán bài tập vào lớp học phần, có thể cấu hình bài tiên quyết."""
    try:
        ensure_class_access(class_id, token_data)
        if not instructor_can_use_exercise(body.exercise_id, token_data.get("sub", "")):
            raise HTTPException(status_code=403, detail="Bài tập thuộc giảng viên khác và chưa được chia sẻ với bạn.")
        success = add_exercise_to_class(
            class_id=class_id,
            exercise_id=body.exercise_id,
            module_name=body.module_name,
            order_idx=body.order_idx,
            prerequisite_id=body.prerequisite_id,
            skill_tag=body.skill_tag,
            weight_point=body.weight_point
        )
        if not success:
            raise HTTPException(status_code=400, detail="Không thể gán bài tập vào lớp.")
        return {
            "status": "success",
            "message": f"Đã gán bài tập '{body.exercise_id}' vào lớp {class_id} thành công."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi gán bài vào lớp: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi gán bài tập: {e}"
        )


@app.put("/api/instructor/classes/{class_id}/exercises/{exercise_id}")
async def update_class_exercise_endpoint(
    class_id: str,
    exercise_id: str,
    body: ClassExerciseUpdateRequest,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên cập nhật cấu hình bài tập trong lớp học phần."""
    try:
        ensure_class_access(class_id, token_data)
        updates = body.model_dump(exclude_unset=True)
        success = update_class_exercise(class_id=class_id, exercise_id=exercise_id, **updates)
        if not success:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài tập trong lớp để cập nhật.")
        return {
            "status": "success",
            "message": f"Đã cập nhật bài tập '{exercise_id}' trong lớp {class_id} thành công."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật bài tập của lớp: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi cập nhật bài tập lớp: {e}"
        )


@app.delete("/api/instructor/classes/{class_id}/exercises/{exercise_id}")
async def remove_exercise_from_class_endpoint(
    class_id: str,
    exercise_id: str,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên gỡ bỏ bài tập khỏi Lớp học phần."""
    try:
        ensure_class_access(class_id, token_data)
        success = remove_exercise_from_class(class_id=class_id, exercise_id=exercise_id)
        if not success:
            raise HTTPException(status_code=404, detail="Không tìm thấy bài tập trong lớp để gỡ bỏ.")
        return {
            "status": "success",
            "message": f"Đã gỡ bài tập '{exercise_id}' khỏi lớp {class_id} thành công."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi gỡ bài tập khỏi lớp: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi gỡ bài tập: {e}"
        )


@app.get("/api/instructor/classes/{class_id}/students", response_model=list[ClassStudentProgressItem])
async def get_class_students_endpoint(
    class_id: str,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên xem danh sách sinh viên trong lớp kèm bảng đo lường tiến độ học tập thực tế."""
    try:
        ensure_class_access(class_id, token_data)
        students = get_class_students_with_progress(class_id)
        return [ClassStudentProgressItem(**s) for s in students]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách sinh viên của lớp: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tải danh sách sinh viên: {e}"
        )


@app.get("/api/exam-sessions", response_model=list[ExamSessionItem])
async def list_exam_sessions(
    class_id: Optional[str] = None,
    session_type: Optional[str] = None,
    token_data: dict = Depends(verify_token),
):
    """Lấy danh sách các Đợt thực hành & Kỳ thi (hỗ trợ lọc theo class_id và session_type)."""
    try:
        username = token_data.get("sub", "")
        role = token_data.get("role")
        if class_id:
            ensure_class_access(class_id, token_data)
        sessions = get_exam_sessions(class_id=class_id, session_type=session_type)
        if role == "instructor":
            sessions = [s for s in sessions if instructor_owns_class(s["class_id"], username)]
        elif role == "student":
            enrolled_ids = {c["id"] for c in get_student_classes(username)}
            sessions = [s for s in sessions if s["class_id"] in enrolled_ids]
        else:
            raise HTTPException(status_code=403, detail="Vai trò không được phép truy cập các đợt học.")
        return [ExamSessionItem(**s) for s in sessions]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách đợt thực hành & kỳ thi: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tải danh sách đợt học / kỳ thi: {e}"
        )


@app.post("/api/instructor/exam-sessions", response_model=ExamSessionItem)
async def create_new_exam_session(
    session_data: ExamSessionCreateRequest,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên tạo mới một Kỳ thi hoặc Đợt thực hành cho lớp tín chỉ."""
    try:
        ensure_class_access(session_data.class_id, token_data)
        assigned_ids = {item["exercise_id"] for item in get_class_exercises(session_data.class_id)}
        if not set(session_data.exercise_ids).issubset(assigned_ids):
            raise HTTPException(status_code=400, detail="Chỉ được chọn bài tập đã gán cho lớp này.")
        created = create_exam_session(
            title=session_data.title,
            class_id=session_data.class_id,
            session_type=session_data.session_type,
            exercise_ids=session_data.exercise_ids,
            duration_minutes=session_data.duration_minutes,
            allow_ai_hints=session_data.allow_ai_hints,
            created_by=token_data.get("sub", "gv_tran")
        )
        return ExamSessionItem(**created)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi tạo kỳ thi / đợt thực hành: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể tạo kỳ thi / đợt thực hành: {e}"
        )


@app.delete("/api/instructor/exam-sessions/{session_id}")
async def delete_exam_session_endpoint(
    session_id: str,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên xóa một Kỳ thi / Đợt thực hành."""
    try:
        session_info = get_exam_session_by_id(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Không tìm thấy kỳ thi / đợt thực hành để xóa.")
        ensure_class_access(session_info["class_id"], token_data)
        deleted = delete_exam_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Không tìm thấy kỳ thi / đợt thực hành để xóa.")
        return {"status": "success", "message": f"Đã xóa đợt thi / thực hành {session_id}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi xóa exam session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi xóa đợt thi / thực hành: {e}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
