"""
FastAPI Backend Application cho PyTutor.
Đóng vai trò MCP Host & Điều phối Sư phạm (Orchestrator).
"""
import sys
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Cấu hình UTF-8 cho logging trên Windows
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("pytutor.api")

from backend.schemas import (
    HealthResponse,
    ExerciseSummary,
    ExerciseDetail,
    SubmitRequest,
    SubmitResponse,
    TestResults,
    ASTAnalysis
)
from backend.mcp_client import (
    discover_tools,
    get_exercise_list,
    get_exercise_details,
    execute_submission_pipeline
)
from backend.llm_service import generate_tutor_hint

app = FastAPI(
    title="PyTutor API",
    description="Hệ thống Gia sư Thông minh Hỗ trợ Học Lập trình Python Dựa trên Model Context Protocol (MCP)",
    version="2.0"
)

# Bật CORS cho phép kết nối từ Frontend (Vite / React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Kiểm tra sức khỏe Backend và xác nhận kết nối tới MCP Server qua True Discovery."""
    try:
        tools = await discover_tools()
        return HealthResponse(
            status="ok",
            mcp_server_connected=True,
            discovered_tools=tools,
            version="2.0"
        )
    except Exception as e:
        logger.error(f"Lỗi kiểm tra sức khỏe MCP Server: {e}")
        return HealthResponse(
            status="degraded",
            mcp_server_connected=False,
            discovered_tools=[],
            version="2.0"
        )


@app.get("/api/exercises", response_model=list[ExerciseSummary])
async def list_exercises():
    """Lấy danh sách các bài tập lập trình Python có sẵn từ MCP Server."""
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
    """Lấy chi tiết một bài tập: đề bài, starter code, test cases mẫu."""
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


@app.post("/api/submit", response_model=SubmitResponse)
async def submit_solution(request: SubmitRequest):
    """
    Điểm chạm chính (Main E2E Route):
    1. Tiếp nhận mã nguồn và mức độ gợi ý từ sinh viên
    2. Gọi MCP Server chạy Sandbox và phân tích AST
    3. Đóng gói Context Bundle và gọi AI Tutor (Qwen2.5-14B)
    4. Trả về kết quả tổng hợp đầy đủ cho Frontend
    """
    try:
        # 1 & 2: Thực thi pipeline qua MCP stdio
        pipeline_res = await execute_submission_pipeline(
            exercise_id=request.exercise_id,
            code=request.code
        )
        
        exercise = pipeline_res["exercise"]
        test_results_raw = pipeline_res["test_results"]
        ast_analysis_raw = pipeline_res["ast_analysis"]
        discovered_tools = pipeline_res["discovered_tools"]
        
        # 3: Gọi AI Tutor sinh gợi ý sư phạm
        tutor_hint, llm_source = await generate_tutor_hint(
            exercise=exercise,
            code=request.code,
            test_results=test_results_raw,
            ast_analysis=ast_analysis_raw,
            hint_level=request.hint_level
        )
        
        # 4: Đóng gói phản hồi
        return SubmitResponse(
            exercise_id=request.exercise_id,
            test_results=TestResults(**test_results_raw),
            ast_analysis=ASTAnalysis(**ast_analysis_raw),
            tutor_hint=tutor_hint,
            hint_level=request.hint_level,
            discovered_mcp_tools=discovered_tools,
            llm_source=llm_source
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        logger.error(f"Lỗi xử lý submission: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi chấm bài: {e}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
