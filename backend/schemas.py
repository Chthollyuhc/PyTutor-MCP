"""
Pydantic Schemas định nghĩa cấu trúc dữ liệu cho PyTutor Backend.
Bao gồm các mô hình cho Exercise, Submission, TestResults, ASTAnalysis và TutorHint.
"""
from typing import Optional, Any
from pydantic import BaseModel, Field


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


class SubmitRequest(BaseModel):
    exercise_id: str = Field(..., description="Mã định danh bài tập (ví dụ: ex_01_sum_1_to_n)")
    code: str = Field(..., description="Mã nguồn Python sinh viên nhập vào")
    hint_level: int = Field(1, ge=1, le=3, description="Mức độ gợi ý sư phạm: 1 (Gợi mở), 2 (Chẩn đoán), 3 (Mã giả)")


class SubmitResponse(BaseModel):
    exercise_id: str
    test_results: TestResults
    ast_analysis: ASTAnalysis
    tutor_hint: str
    hint_level: int
    discovered_mcp_tools: list[str] = Field(default_factory=list)
    llm_source: str = Field("qwen2.5:14b-instruct-ctx16k", description="Nguồn sinh gợi ý (Qwen hoặc Pedagogical Fallback)")


class ExerciseSummary(BaseModel):
    id: str
    title: str
    difficulty: str
    category: str
    test_cases_count: int


class ExerciseDetail(BaseModel):
    id: str
    title: str
    difficulty: str
    category: str
    description: str
    starter_code: str
    test_cases: list[TestCase]


class HealthResponse(BaseModel):
    status: str = "ok"
    mcp_server_connected: bool
    discovered_tools: list[str]
    version: str = "2.0"
