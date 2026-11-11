import unittest
from backend.adaptive_policy import select_hint_strategy
from backend.database import init_db, compute_student_model, get_db_connection
from backend.llm_service import build_scaffolding_prompt

class Phase17Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_strategy_uses_repeated_attempts_without_escalating_level(self):
        result = select_hint_strategy(1, {"results":[{"status":"FAIL"}]},
                                      [{"hint_level":2},{"hint_level":3}], {})
        self.assertEqual(result["strategy"], "recurring_difficulty")
        self.assertEqual(result["requested_level"], 1)
        self.assertEqual(result["previous_hint_levels"], [2,3])

    def test_strategy_has_safe_no_data_fallback(self):
        result = select_hint_strategy(2, {"results":[]}, [], {})
        self.assertEqual(result["strategy"], "conceptual_start")
        self.assertEqual(result["data_status"], "insufficient")
        self.assertEqual(result["evidence"], [])

    def test_passed_code_uses_review_strategy(self):
        self.assertEqual(select_hint_strategy(1,{"all_passed":True},[],{})["reason_code"],"solution_review")

    def test_analytics_distinguishes_no_data_and_limited_sample(self):
        user="phase17_synthetic_limited"
        empty=compute_student_model("phase17_synthetic_empty")
        self.assertEqual(empty["analytics_metrics"]["data_status"],"no_data")
        conn=get_db_connection()
        conn.execute("DELETE FROM submissions WHERE session_id=?",(user,))
        conn.execute("INSERT INTO submissions(session_id,exercise_id,code,hint_level,passed_tests,total_tests,all_passed,action_type) VALUES(?,?,?,?,?,?,?,?)",(user,"ex_01_sum_1_to_n","x=1",1,2,5,0,"ask_ai"))
        conn.commit(); conn.close()
        model=compute_student_model(user)
        self.assertEqual(model["analytics_metrics"]["total_submissions"],0)
        self.assertEqual(model["analytics_metrics"]["data_status"],"no_data")
        conn=get_db_connection()
        conn.execute("INSERT INTO submissions(session_id,exercise_id,code,hint_level,passed_tests,total_tests,all_passed,action_type) VALUES(?,?,?,?,?,?,?,?)",(user,"ex_01_sum_1_to_n","x=1",1,1,5,0,"submit"))
        conn.commit(); conn.close()
        limited=compute_student_model(user)
        self.assertEqual(limited["analytics_metrics"]["data_status"],"limited")
        self.assertIn("Chưa đủ dữ liệu",limited["diagnostic_evaluation"]["level_classification"])

    def test_prompt_includes_reason_but_keeps_requested_hint_level(self):
        prompt=build_scaffolding_prompt({"title":"Test","description":"Loop"},"x=1",
            {"results":[{"status":"FAIL"}]},{"structural_summary":"assignment"},1,
            adaptive_strategy={"strategy":"failed_case_diagnosis","reason_code":"failed_case_diagnosis","evidence":["failed_test_cases"],"data_status":"sufficient"})
        self.assertIn("failed_case_diagnosis",prompt)
        self.assertIn("Level 1",prompt)
        self.assertIn("không tự tăng mức tiết lộ",prompt.lower())

if __name__ == "__main__":
    unittest.main()
