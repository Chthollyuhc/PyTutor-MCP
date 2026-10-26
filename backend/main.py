"""
FastAPI Backend Application cho PyTutor.
Đóng vai trò MCP Host, Điều phối Sư phạm (Orchestrator) & Phân quyền (Auth & Roles).
"""
import sys
import logging
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

# Cấu hình UTF-8 cho logging trên Windows
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("pytutor.api")

from backend.database import (
    init_db,
    get_db_connection,
    get_all_exercises as db_get_all_exercises,
    get_exercise_by_id as db_get_exercise_by_id,
    save_exercise as db_save_exercise,
    delete_exercise as db_delete_exercise,
    get_instructor_stats,
    get_all_submissions,
    get_submission_by_id,
    get_attempts,
    compute_student_model,
    calculate_autonomy_stars,
    save_exercise_stars,
    check_and_unlock_badges,
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
    get_class_exercises,
    add_exercise_to_class,
    update_class_exercise,
    remove_exercise_from_class,
    get_exam_sessions,
    get_exam_session_by_id,
    create_exam_session,
    delete_exam_session
)
from backend.auth import (
    authenticate_user,
    create_token,
    verify_token,
    require_instructor
)
from backend.schemas import (
    HealthResponse,
    CompilerConfig,
    ExerciseSummary,
    ExerciseDetail,
    ExerciseUpsertRequest,
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
    ExamSessionCreateRequest
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
    execute_trace_pipeline
)
from backend.llm_service import generate_tutor_hint, generate_chat_followup, generate_pythonic_review




@asynccontextmanager
async def lifespan(app: FastAPI):
    """Khởi tạo cơ sở dữ liệu SQLite khi khởi động ứng dụng."""
    try:
        init_db()
        logger.info("Cơ sở dữ liệu SQLite PyTutor đã sẵn sàng.")
    except Exception as e:
        logger.error(f"Lỗi khởi tạo DB: {e}")
    yield


app = FastAPI(
    title="PyTutor API",
    description="Hệ thống Gia sư Thông minh Hỗ trợ Học Lập trình Python Dựa trên Model Context Protocol (MCP)",
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
async def list_exercises():
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
async def get_exercise(exercise_id: str):
    """Lấy chi tiết một bài tập: đề bài, starter code, test cases chuẩn."""
    try:
        data = await get_exercise_details(exercise_id)
        if "error" in data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data["error"])
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
async def run_test_only(request: RunTestOnlyRequest):
    """
    Chạy thử nhanh: Thực thi Sandbox và phân tích AST qua MCP
    mà KHÔNG gọi LLM (tiết kiệm quota AI, phản hồi dưới 1 giây, kèm MCP Trace).
    """
    try:
        res = await run_test_only_pipeline(exercise_id=request.exercise_id, code=request.code)
        return RunTestOnlyResponse(
            exercise_id=request.exercise_id,
            test_results=TestResults(**res["test_results"]),
            ast_analysis=ASTAnalysis(**res["ast_analysis"]),
            mcp_trace=[MCPTraceItem(**t) for t in res.get("mcp_trace", [])]
        )
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
async def submit_solution(request: SubmitRequest):
    """
    Điểm chạm chính (Main E2E Route):
    1. Tiếp nhận mã nguồn, mức độ gợi ý và session_id
    2. Gọi MCP Server chạy Sandbox, phân tích AST, lấy lịch sử và student model (kèm MCP Trace)
    3. Đóng gói Context Bundle đa chiều và gọi AI Tutor sinh gợi ý sư phạm
    4. Lưu sự kiện học tập vào SQLite qua MCP Tool save_learning_event
    5. Trả về kết quả tổng hợp đầy đủ cho Frontend
    """
    try:
        # 1. Thực thi pipeline qua MCP stdio
        pipeline_res = await execute_submission_pipeline(
            exercise_id=request.exercise_id,
            code=request.code,
            session_id=request.session_id
        )

        exercise = pipeline_res["exercise"]
        test_results_raw = pipeline_res["test_results"]
        ast_analysis_raw = pipeline_res["ast_analysis"]
        attempt_history = pipeline_res.get("attempt_history", [])
        student_model = pipeline_res.get("student_model", None)
        discovered_tools = pipeline_res["discovered_tools"]
        mcp_trace = [MCPTraceItem(**t) for t in pipeline_res.get("mcp_trace", [])]

        # Kiểm tra Chốt chặn bảo mật Chế độ Thi (EXAM Mode Guard)
        is_exam_mode = False
        if request.exam_session_id:
            try:
                sess_info = get_exam_session_by_id(request.exam_session_id)
                if sess_info and (sess_info.get("allow_ai_hints") == 0 or sess_info.get("session_type") == "EXAM"):
                    is_exam_mode = True
            except Exception as e:
                logger.warning(f"Lỗi kiểm tra exam session {request.exam_session_id}: {e}")

        # 2. Sinh gợi ý sư phạm: Nếu ở chế độ thi thì khóa AI tutor, ngược lại xử lý theo action_type
        if is_exam_mode:
            tutor_hint = "🔒 **[Chế độ Kỳ thi / Kiểm tra nghiêm ngặt]** Hệ thống đã ghi nhận kết quả chấm điểm Test Cases của bạn. Trong chế độ Thi, tính năng gợi ý từ Gia sư AI được khóa để đảm bảo tính công bằng học thuật."
            llm_source = "Exam-Mode-Guard"
        elif request.action_type == "submit" and test_results_raw.get("all_passed", False):
            tutor_hint = "🎉 **Chúc mừng!** Bạn đã vượt qua 100% test cases và nộp bài thành công. Hãy tiếp tục thử thách với các bài tập tiếp theo trên lộ trình kỹ năng!"
            llm_source = "System-Celebration"
        else:
            tutor_hint, llm_source = await generate_tutor_hint(
                exercise=exercise,
                code=request.code,
                test_results=test_results_raw,
                ast_analysis=ast_analysis_raw,
                hint_level=request.hint_level,
                attempt_history=attempt_history,
                student_model=student_model
            )

        # 3. Ghi nhận sự kiện học tập vào cơ sở dữ liệu qua MCP Tool
        try:
            await save_learning_event_via_mcp(
                session_id=request.session_id,
                exercise_id=request.exercise_id,
                code=request.code,
                hint_level=request.hint_level,
                passed_tests=test_results_raw.get("passed_tests", 0),
                total_tests=test_results_raw.get("total_tests", 0),
                all_passed=test_results_raw.get("all_passed", False),
                llm_source=llm_source,
                tutor_hint=tutor_hint
            )
        except Exception as e:
            logger.warning(f"Không thể lưu learning event qua MCP: {e}")

        # 3.1. Tính sao tự lực & mở khóa huy hiệu
        stars_earned = 0
        new_badges = []
        # CHỈ tính và lưu sao khi là nộp bài chính thức (action_type == 'submit') và vượt qua toàn bộ test cases
        if request.action_type == "submit" and test_results_raw.get("all_passed", False):
            effective_user = request.session_id or "student"
            # Kiểm tra lịch sử các lần hỏi AI / thử trước đó của sinh viên ở bài tập này trong attempt_history
            max_hint_used = 1
            if attempt_history:
                for att in attempt_history:
                    h = att.get("hint_level", 1) or 1
                    if h > max_hint_used:
                        max_hint_used = h

            stars_earned = calculate_autonomy_stars(
                attempt_count=len(attempt_history) + 1,
                max_hint_level_used=max_hint_used,
                all_passed=True
            )
            try:
                star_res = save_exercise_stars(
                    username=effective_user,
                    exercise_id=request.exercise_id,
                    stars=stars_earned,
                    clean_score=0
                )
                new_badges = star_res.get("new_badges", [])
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
            new_badges=new_badges
        )

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
async def tutor_chat_endpoint(request: TutorChatRequest):
    """
    Trò chuyện làm rõ với Gia sư AI (Multi-turn Follow-up Chat):
    - Tiếp nhận câu hỏi làm rõ từ học viên kèm ngữ cảnh bài làm và lịch sử hội thoại
    - Gọi LLM sinh phản hồi thân thiện, Socratic, không lộ code giải
    - Trả về câu trả lời và lịch sử hội thoại đã cập nhật
    """
    try:
        # Kiểm tra Chốt chặn bảo mật Chế độ Thi (EXAM Mode Guard)
        if request.exam_session_id:
            try:
                sess_info = get_exam_session_by_id(request.exam_session_id)
                if sess_info and (sess_info.get("allow_ai_hints") == 0 or sess_info.get("session_type") == "EXAM"):
                    exam_reply = "🔒 **[Chế độ Kỳ thi / Kiểm tra nghiêm ngặt]** Bạn đang trong thời gian làm bài thi. Tính năng trò chuyện và gợi ý từ Gia sư AI bị khóa để đảm bảo tính công bằng học thuật. Vui lòng tự hoàn thành bài làm và sử dụng nút Chạy thử code / Nộp bài."
                    updated_history = list(request.history)
                    updated_history.append(ChatMessage(role="user", content=request.user_message))
                    updated_history.append(ChatMessage(role="assistant", content=exam_reply))
                    return TutorChatResponse(
                        reply=exam_reply,
                        llm_source="Exam-Mode-Guard",
                        updated_history=updated_history
                    )
            except Exception as e:
                logger.warning(f"Lỗi kiểm tra exam session trong chat: {e}")

        ex_details = {}
        if request.exercise_id:
            try:
                ex_details = db_get_exercise_by_id(request.exercise_id) or {}
            except Exception:
                pass

        reply, llm_source = await generate_chat_followup(
            exercise=ex_details,
            code=request.code,
            user_message=request.user_message,
            history=request.history
        )

        updated_history = list(request.history)
        updated_history.append(ChatMessage(role="user", content=request.user_message))
        updated_history.append(ChatMessage(role="assistant", content=reply))

        return TutorChatResponse(
            reply=reply,
            llm_source=llm_source,
            updated_history=updated_history
        )
    except Exception as e:
        logger.error(f"Lỗi khi xử lý tutor chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi trò chuyện với Gia sư AI: {e}"
        )


@app.post("/api/custom-run", response_model=CustomRunResponse)
async def custom_run_endpoint(request: CustomRunRequest):
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
async def trace_execution_endpoint(request: TraceExecutionRequest):
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
async def get_student_model_endpoint(session_id: str = "default_session"):
    """Lấy mô hình học sinh thích ứng theo session_id."""
    return compute_student_model(session_id)



@app.get("/api/student/profile", response_model=StudentProfileResponse)
async def get_student_profile_endpoint(
    session_id: str,
    exercise_id: str = "",
    class_id: Optional[str] = None
):
    """
    [Hồ sơ Thích ứng của Học viên - Phase 13/14 Quantitative Analytics]
    Gọi MCP Tool get_student_model và get_attempt_history qua giao thức MCP,
    trả về năng lực tổng hợp, 4D metrics, diagnostic evaluation và các lần nộp bài gần nhất.
    """
    try:
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
            recent_attempts=attempts
        )
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
            recent_attempts=attempts
        )


@app.get("/api/skill-roadmap", response_model=SkillRoadmapResponse)
async def get_skill_roadmap_endpoint(
    session_id: str = "default_session",
    class_id: Optional[str] = None
):
    """
    [Cây Lộ trình Kỹ năng Đồ họa - Skill Roadmap & Curriculum Matrix]
    - Hỗ trợ xem lộ trình kỹ năng theo Lớp học phần tín chỉ NEU (class_id) hoặc toàn cục.
    - Áp dụng Thang đo Định lượng (Mastery Rubric):
      + MASTERED: Giải thành công và đạt tối thiểu min_stars_required (1-3 sao).
      + NEEDS_MORE_STARS: Giải đúng nhưng chưa đủ số sao yêu cầu (dùng nhiều gợi ý AI).
      + IN_PROGRESS: Đã thử nộp nhưng chưa pass hoàn toàn.
      + AVAILABLE: Đã mở khóa (tiên quyết đã MASTERED).
      + LOCKED: Khóa do bài tiên quyết chưa MASTERED.
    """
    try:
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

                # 1. Xác định tập bài tập thực sự đạt chuẩn (True Mastered Set)
                min_stars_map = {item["exercise_id"]: item.get("min_stars_required", 1) for item in class_exercises}
                true_mastered_set = set()
                for item in class_exercises:
                    ex_id = item["exercise_id"]
                    min_stars = min_stars_map.get(ex_id, 1)
                    stars_earned = stars_by_ex.get(ex_id, 0)
                    has_solved = (ex_id in mastered_set) or (stars_earned > 0)
                    if has_solved and stars_earned >= min_stars:
                        true_mastered_set.add(ex_id)

                nodes = []
                for item in class_exercises:
                    ex_id = item["exercise_id"]
                    min_stars = item.get("min_stars_required", 1)
                    stars_earned = stars_by_ex.get(ex_id, 0)
                    prereq = item.get("prerequisite_id")
                    prereqs = [prereq] if prereq else []
                    has_solved = (ex_id in mastered_set) or (stars_earned > 0)

                    # Xác định trạng thái theo Mastery Rubric chuẩn
                    if ex_id in true_mastered_set:
                        st = "MASTERED"
                        desc = f"Đạt chuẩn xuất sắc ({stars_earned}/{min_stars} ⭐)"
                        unlocked = True
                    elif has_solved and stars_earned < min_stars:
                        st = "NEEDS_MORE_STARS"
                        desc = f"Đã giải đúng nhưng mới đạt {stars_earned}/{min_stars} ⭐. Hãy tự giải lại với ít gợi ý hơn để đạt chuẩn!"
                        unlocked = True
                    elif ex_id in in_prog_set or ex_id in struggling_set:
                        st = "IN_PROGRESS"
                        desc = "Đang thực hành (Chưa vượt qua tất cả test cases)"
                        unlocked = True
                    else:
                        prereq_met = (not prereq) or (prereq in true_mastered_set)
                        if prereq_met:
                            st = "AVAILABLE"
                            desc = f"Sẵn sàng thử thách (Yêu cầu {min_stars} ⭐)"
                            unlocked = True
                        else:
                            st = "LOCKED"
                            desc = f"Khóa - Cần hoàn thành đạt chuẩn bài tiên quyết ({prereq})"
                            unlocked = False

                    nodes.append(SkillNode(
                        id=ex_id,
                        title=item.get("title", ex_id),
                        category=item.get("category", "General"),
                        difficulty=item.get("difficulty", "EASY"),
                        prerequisites=prereqs,
                        status=st,
                        min_stars_required=min_stars,
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
    except Exception as e:
        logger.error(f"Lỗi khi xây dựng skill roadmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tải lộ trình kỹ năng: {e}"
        )


# ==============================================================================
# PHASE 10: GAMIFICATION, PYTHONIC REVIEW & LEADERBOARD ENDPOINTS
# ==============================================================================

@app.post("/api/tutor/pythonic-review", response_model=PythonicReviewResponse)
async def pythonic_review_endpoint(request: PythonicReviewRequest):
    """
    [Phase 10: Thử thách Tối ưu Code Chuẩn Pythonic]
    Gia sư AI đóng vai trò Senior Python Tech Lead đánh giá mã nguồn đã pass 100%:
    - Chấm điểm Clean Code (0-100, sàn 70 khích lệ)
    - Chỉ ra điểm mạnh & cơ hội tối ưu (idiomatic Python)
    - Cung cấp đoạn code chuẩn mực mẫu và giải thích chuyên sâu
    - Tự động mở khóa badge PYTHONIC_EXPLORER nếu điểm >= 90
    """
    try:
        ex_details = await get_exercise_details(request.exercise_id)
        if not ex_details or ex_details.get("error"):
            raise HTTPException(status_code=404, detail=f"Không tìm thấy bài tập '{request.exercise_id}'")

        review_dict, llm_source = await generate_pythonic_review(
            exercise=ex_details,
            student_code=request.code
        )

        clean_score = review_dict.get("clean_score", 85)
        username = request.username or "student"

        # Cập nhật điểm clean score và kiểm tra badge
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
async def get_leaderboard_endpoint(limit: int = 20):
    """
    [Phase 10: Bảng Xếp Hạng Lớp Học (Classroom Leaderboard)]
    Xếp hạng học viên theo tổng số sao tự lực, số bài đã làm chủ và điểm Clean Code.
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
async def get_student_achievements_endpoint(username: str = "student"):
    """
    [Phase 10: Hồ sơ Sao & Huy hiệu Thành tích]
    Lấy tổng số sao, danh sách số sao từng bài tập và bộ sưu tập huy hiệu đã mở khóa.
    """
    try:
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
    stats = get_instructor_stats()
    return InstructorDashboardStats(**stats)


@app.get("/api/instructor/submissions", response_model=list[SubmissionItem])
async def list_recent_submissions(token_data: dict = Depends(require_instructor)):
    """Xem toàn bộ lịch sử các lần nộp bài của sinh viên (kèm code & tutor hint)."""
    submissions = get_all_submissions(limit=100)
    return [SubmissionItem(**s) for s in submissions]


@app.get("/api/instructor/submissions/{submission_id}", response_model=SubmissionItem)
async def get_single_submission(
    submission_id: int,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên xem chi tiết một bài nộp cụ thể (mã nguồn + kết quả + phản hồi AI)."""
    sub = get_submission_by_id(submission_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài nộp.")
    return SubmissionItem(**sub)


@app.get("/api/instructor/exercises", response_model=list[ExerciseSummary])
async def instructor_list_all_exercises(token_data: dict = Depends(require_instructor)):
    """Lấy toàn bộ bài tập (bao gồm cả bài ẩn) cho Giảng viên quản lý."""
    return db_get_all_exercises(include_inactive=True)


@app.post("/api/instructor/exercises", response_model=ExerciseDetail)
async def create_new_exercise(
    exercise_data: ExerciseUpsertRequest,
    token_data: dict = Depends(require_instructor)
):
    """Giảng viên tạo mới một bài tập lập trình vào ngân hàng đề."""
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
    deleted = db_delete_exercise(exercise_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập để xóa.")
    return {"status": "success", "message": f"Đã xóa bài tập {exercise_id}"}


# ==============================================================================
# PHASE 12: QUẢN LÝ LỚP TÍN CHỈ & KỲ THI / ĐỢT THỰC HÀNH (CREDIT CLASSES & EXAMS)
# ==============================================================================

@app.get("/api/classes", response_model=list[CreditClassSummary])
async def list_credit_classes(
    instructor_username: Optional[str] = None,
    student_username: Optional[str] = None
):
    """Lấy danh sách các Lớp tín chỉ (kèm thông tin Học phần NEU, giảng viên, sĩ số, số bài tập và trạng thái ghi danh)."""
    try:
        classes = get_credit_classes(instructor_username=instructor_username, current_username=student_username)
        return [CreditClassSummary(**c) for c in classes]
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách lớp tín chỉ: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tải danh sách lớp tín chỉ: {e}"
        )


@app.get("/api/student/my-classes", response_model=list[CreditClassSummary])
async def get_my_classes_endpoint(token_data: dict = Depends(verify_token)):
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
        target_student = token_data.get("sub", "student")
        if token_data.get("role") == "instructor" and body and body.student_username:
            target_student = body.student_username

        success = enroll_student_in_class(class_id=class_id, student_username=target_student)
        return {
            "status": "success",
            "enrolled": success,
            "class_id": class_id,
            "student_username": target_student,
            "message": f"Đã ghi danh {target_student} vào lớp {class_id} thành công."
        }
    except Exception as e:
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
        target_student = token_data.get("sub", "student")
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
        target_student = token_data.get("sub", "student")
        success = unenroll_student_from_class(class_id=class_id, student_username=target_student)
        return {
            "status": "success",
            "unenrolled": success,
            "class_id": class_id,
            "student_username": target_student,
            "message": f"Đã hủy ghi danh khỏi lớp {class_id} thành công."
        }
    except Exception as e:
        logger.error(f"Lỗi khi hủy ghi danh: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi hủy ghi danh: {e}"
        )


@app.get("/api/classes/{class_id}/curriculum", response_model=list[ClassExerciseItem])
async def get_class_curriculum_endpoint(
    class_id: str,
    student_username: Optional[str] = None
):
    """Lấy danh sách bài tập và cấu hình Lộ trình kỹ năng (Curriculum & Skill Matrix) của lớp học phần."""
    try:
        exercises = get_class_exercises(class_id, student_username=student_username)
        return [ClassExerciseItem(**e) for e in exercises]
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
    """Giảng viên gán bài tập vào Lớp học phần với cấu hình Module, Thứ tự, Tiên quyết và Số sao tối thiểu."""
    try:
        success = add_exercise_to_class(
            class_id=class_id,
            exercise_id=body.exercise_id,
            module_name=body.module_name,
            order_idx=body.order_idx,
            prerequisite_id=body.prerequisite_id,
            min_stars_required=body.min_stars_required,
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
    """Giảng viên cập nhật cấu hình bài tập trong Lớp học phần (sửa Module, Thứ tự, Tiên quyết, Sao yêu cầu)."""
    try:
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
        students = get_class_students_with_progress(class_id)
        return [ClassStudentProgressItem(**s) for s in students]
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách sinh viên của lớp: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi tải danh sách sinh viên: {e}"
        )


@app.get("/api/exam-sessions", response_model=list[ExamSessionItem])
async def list_exam_sessions(
    class_id: Optional[str] = None,
    session_type: Optional[str] = None
):
    """Lấy danh sách các Đợt thực hành & Kỳ thi (hỗ trợ lọc theo class_id và session_type)."""
    try:
        sessions = get_exam_sessions(class_id=class_id, session_type=session_type)
        return [ExamSessionItem(**s) for s in sessions]
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
