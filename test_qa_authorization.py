"""Isolated regression tests for role enforcement and class-level data boundaries."""
from __future__ import annotations

import json
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.auth import create_token
from backend.database import get_db_connection
from backend.main import app


def headers(username: str, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_token(username, role, username)}"}


class AuthorizationAndDataIsolationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.client.__enter__()
        self.student = headers("student", "student")
        self.instructor = headers("gv_tran", "instructor")
        self.other_instructor = headers("qa_other_instructor", "instructor")

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def create_private_class(self, class_id: str, instructor: str = "qa_other_instructor") -> None:
        conn = get_db_connection()
        try:
            conn.execute(
                """INSERT OR REPLACE INTO credit_classes
                   (id, class_code, class_name, instructor_username, enrollment_code)
                   VALUES (?, ?, ?, ?, ?)""",
                (class_id, f"QA-{class_id}", "QA private class", instructor, f"CODE-{class_id}"),
            )
            conn.commit()
        finally:
            conn.close()

    def test_sensitive_learning_routes_require_authentication(self):
        calls = [
            ("get", "/api/exercises"),
            ("get", "/api/exercises/ex_01_sum_1_to_n"),
            ("get", "/api/classes"),
            ("get", "/api/student/profile?session_id=student"),
            ("get", "/api/student-model/student"),
            ("get", "/api/student/model"),
            ("get", "/api/skill-roadmap"),
            ("get", "/api/student/achievements"),
            ("get", "/api/exam-sessions"),
            ("post", "/api/run-test", {"exercise_id": "ex_01_sum_1_to_n", "code": "print(1)"}),
            ("post", "/api/custom-run", {"code": "print(1)"}),
            ("post", "/api/trace-execution", {"code": "print(1)"}),
            ("post", "/api/submit", {"exercise_id": "ex_01_sum_1_to_n", "code": "print(1)"}),
            ("post", "/api/tutor/pythonic-review", {"exercise_id": "ex_01_sum_1_to_n", "code": "print(1)"}),
            ("post", "/api/tutor/feedback", {"interaction_id": "missing", "rating": 1}),
            ("post", "/api/instructor/ai/class-chat", {"class_id": "missing", "user_message": "Thống kê lớp"}),
        ]
        for method, url, *body in calls:
            response = getattr(self.client, method)(url, json=body[0]) if body else getattr(self.client, method)(url)
            self.assertEqual(response.status_code, 401, f"{method.upper()} {url} allowed anonymous access")

    def test_student_cannot_access_other_identity_or_instructor_controls(self):
        response = self.client.get("/api/student/profile?session_id=another_student", headers=self.student)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["session_id"], "student")

        response = self.client.get("/api/student/achievements?username=another_student", headers=self.student)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_stars"], 0)

        response = self.client.get("/api/instructor/dashboard", headers=self.student)
        self.assertEqual(response.status_code, 403)

    def test_submission_binds_learning_identity_to_authenticated_student(self):
        pipeline_result = {
            "exercise": {"id": "ex_01_sum_1_to_n", "title": "Sum", "description": "Sum numbers"},
            "test_results": {"total_tests": 1, "passed_tests": 0, "failed_tests": 1, "all_passed": False,
                             "summary": "One test failed", "results": []},
            "ast_analysis": {"valid": True}, "attempt_history": [], "student_model": {},
            "discovered_tools": [], "mcp_trace": [],
        }
        with patch("backend.main.execute_submission_pipeline", new_callable=AsyncMock, return_value=pipeline_result) as pipeline, \
             patch("backend.main.generate_tutor_hint", new_callable=AsyncMock,
                   return_value=("Hãy kiểm tra từng giá trị biên.", "MockTutor", None)), \
             patch("backend.main.save_learning_event_via_mcp", new_callable=AsyncMock) as save_event:
            response = self.client.post("/api/submit", headers=self.student, json={
                "exercise_id": "ex_01_sum_1_to_n", "code": "print(1)", "session_id": "victim",
                "action_type": "ask_ai",
            })
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(pipeline.await_args.kwargs["session_id"], "student")
        self.assertEqual(save_event.await_args.kwargs["session_id"], "student")

    def test_unenrolled_student_and_unrelated_instructor_cannot_read_private_class(self):
        class_id = "qa_private_boundary"
        self.create_private_class(class_id)
        student_response = self.client.get(f"/api/classes/{class_id}/curriculum", headers=self.student)
        self.assertEqual(student_response.status_code, 404)
        teacher_response = self.client.get(f"/api/instructor/classes/{class_id}/students", headers=self.instructor)
        self.assertEqual(teacher_response.status_code, 404)
        exam_list = self.client.get(f"/api/exam-sessions?class_id={class_id}", headers=self.student)
        self.assertEqual(exam_list.status_code, 404)

    def test_instructor_submission_queries_are_scoped_to_owned_class_and_roster(self):
        class_id = "qa_private_submissions"
        self.create_private_class(class_id)
        conn = get_db_connection()
        try:
            conn.execute("INSERT OR IGNORE INTO class_enrollments(class_id, student_username) VALUES (?, ?)",
                         (class_id, "qa_student"))
            conn.execute("INSERT OR IGNORE INTO class_exercises(class_id, exercise_id, module_name) VALUES (?, ?, ?)",
                         (class_id, "ex_01_sum_1_to_n", "QA"))
            conn.execute("""INSERT INTO submissions(session_id, exercise_id, code, passed_tests, total_tests,
                         all_passed, llm_source, tutor_hint) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                         ("qa_student", "ex_01_sum_1_to_n", "secret student code", 1, 5, 0, "Mock", "hint"))
            submission_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.commit()
        finally:
            conn.close()

        self.assertEqual(self.client.get("/api/instructor/submissions", headers=self.instructor).json(), [])
        self.assertEqual(self.client.get(f"/api/instructor/submissions/{submission_id}", headers=self.instructor).status_code, 404)
        own_list = self.client.get("/api/instructor/submissions", headers=self.other_instructor)
        self.assertEqual(own_list.status_code, 200)
        self.assertEqual([item["id"] for item in own_list.json()], [submission_id])

    def test_pythonic_review_rejects_unsolved_code_before_model_call(self):
        with patch("backend.main.run_test_only_pipeline", new_callable=AsyncMock,
                   return_value={"test_results": {"all_passed": False}}), \
             patch("backend.main.generate_pythonic_review", new_callable=AsyncMock) as reviewer:
            response = self.client.post("/api/tutor/pythonic-review", headers=self.student, json={
                "exercise_id": "ex_01_sum_1_to_n", "code": "print('not a solution')", "username": "victim",
            })
        self.assertEqual(response.status_code, 400)
        reviewer.assert_not_awaited()

    def test_foreign_exam_submission_is_rejected_before_code_execution(self):
        class_id = "qa_private_exam"
        self.create_private_class(class_id)
        conn = get_db_connection()
        try:
            conn.execute("""INSERT OR REPLACE INTO exam_sessions
                         (id, title, class_id, session_type, exercise_ids, is_active, allow_ai_hints)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                         ("qa_foreign_exam", "Private exam", class_id, "EXAM",
                          json.dumps(["ex_01_sum_1_to_n"]), 1, 0))
            conn.commit()
        finally:
            conn.close()
        with patch("backend.main.execute_submission_pipeline", new_callable=AsyncMock) as pipeline:
            response = self.client.post("/api/submit", headers=self.student, json={
                "exercise_id": "ex_01_sum_1_to_n", "code": "print(1)", "exam_session_id": "qa_foreign_exam",
            })
        self.assertEqual(response.status_code, 404)
        pipeline.assert_not_awaited()

    def test_instructor_class_chat_requires_class_ownership(self):
        class_id = "qa_private_analytics"
        self.create_private_class(class_id)
        request = {"class_id": class_id, "user_message": "Tổng hợp lỗi thường gặp", "days": 7}
        with patch("backend.main.generate_instructor_answer", new_callable=AsyncMock) as answer:
            denied = self.client.post("/api/instructor/ai/class-chat", headers=self.instructor, json=request)
            self.assertEqual(denied.status_code, 404)
            answer.assert_not_awaited()

            answer.return_value = ("Tổng hợp đã ẩn danh.", "MockTutor", {"model_name": "mock"})
            allowed = self.client.post("/api/instructor/ai/class-chat", headers=self.other_instructor, json=request)
        self.assertEqual(allowed.status_code, 200, allowed.text)
        self.assertEqual(allowed.json()["class_id"], class_id)

    def test_instructor_exercises_are_private_unless_owner_shares_them(self):
        owner_name = "qa_exercise_owner"
        recipient_name = "qa_exercise_recipient"
        exercise_id = "qa_private_exercise"
        class_id = "qa_share_target_class"
        owner_headers = headers(owner_name, "instructor")
        recipient_headers = headers(recipient_name, "instructor")
        conn = get_db_connection()
        try:
            conn.executemany(
                "INSERT OR REPLACE INTO users(username,password,role,full_name) VALUES(?,?,?,?)",
                [(owner_name, "test", "instructor", "QA Owner"),
                 (recipient_name, "test", "instructor", "QA Recipient")],
            )
            conn.execute(
                """INSERT OR REPLACE INTO exercises
                   (id,title,difficulty,category,description,starter_code,test_cases,created_by,is_active)
                   VALUES(?,?,?,?,?,?,?,?,1)""",
                (exercise_id, "Private QA Exercise", "Dễ", "QA", "Description", "", "[]", owner_name),
            )
            conn.commit()
        finally:
            conn.close()
        self.create_private_class(class_id, instructor=recipient_name)

        visible = self.client.get("/api/instructor/exercises", headers=recipient_headers)
        self.assertEqual(visible.status_code, 200, visible.text)
        self.assertNotIn(exercise_id, {exercise["id"] for exercise in visible.json()})

        assign_body = {"exercise_id": exercise_id, "module_name": "QA"}
        denied_assignment = self.client.post(
            f"/api/instructor/classes/{class_id}/exercises", headers=recipient_headers, json=assign_body
        )
        self.assertEqual(denied_assignment.status_code, 403)

        share = self.client.post(
            f"/api/instructor/exercises/{exercise_id}/shares",
            headers=owner_headers,
            json={"instructor_username": recipient_name},
        )
        self.assertEqual(share.status_code, 201, share.text)
        visible_after_share = self.client.get("/api/instructor/exercises", headers=recipient_headers)
        shared_item = next(item for item in visible_after_share.json() if item["id"] == exercise_id)
        self.assertEqual(shared_item["created_by"], owner_name)
        self.assertEqual(shared_item["created_by_name"], "QA Owner")
        self.assertFalse(shared_item["can_manage"])

        allowed_assignment = self.client.post(
            f"/api/instructor/classes/{class_id}/exercises", headers=recipient_headers, json=assign_body
        )
        self.assertEqual(allowed_assignment.status_code, 200, allowed_assignment.text)

        update = self.client.put(
            f"/api/instructor/exercises/{exercise_id}",
            headers=recipient_headers,
            json={"id": exercise_id, "title": "Hijack", "difficulty": "Dễ", "category": "QA",
                  "description": "", "starter_code": "", "test_cases": []},
        )
        self.assertEqual(update.status_code, 403)
        duplicate_create = self.client.post(
            "/api/instructor/exercises",
            headers=recipient_headers,
            json={"id": exercise_id, "title": "Hijack", "difficulty": "Dễ", "category": "QA",
                  "description": "", "starter_code": "", "test_cases": []},
        )
        self.assertEqual(duplicate_create.status_code, 409)
        deletion = self.client.delete(f"/api/instructor/exercises/{exercise_id}", headers=recipient_headers)
        self.assertEqual(deletion.status_code, 403)

        revoke = self.client.delete(
            f"/api/instructor/exercises/{exercise_id}/shares/{recipient_name}", headers=owner_headers
        )
        self.assertEqual(revoke.status_code, 200, revoke.text)
        revoked_list = self.client.get("/api/instructor/exercises", headers=recipient_headers)
        self.assertNotIn(exercise_id, {exercise["id"] for exercise in revoked_list.json()})


if __name__ == "__main__":
    unittest.main(verbosity=2)
