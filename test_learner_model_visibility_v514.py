"""v5.14 - Mô hình người học bằng lời thường: hàm thuần, từ cấm, hợp đồng trường, chính sách không đổi quyết định.

Chạy: .\\.claude\\run_isolated.ps1 test_learner_model_visibility_v514
"""
import unittest

from backend.adaptive_policy import select_hint_strategy
from backend.plain_language import (
    BANNED_WORDS, build_class_plain_view, concept_focus_line, concept_plain, enrich_concepts,
)


def det(eid, title, status, failed=0, err=None, auto=None):
    return {"exercise_id": eid, "title": title, "status": status, "submits": failed + (1 if status == "passed" else 0),
            "failed_submits": failed, "dominant_error_class": err, "autonomy": auto}


def concept(kc, state, details, err=None):
    return {"kc": kc, "label_vi": kc, "state": state, "exercise_details": details, "dominant_error_class": err,
            "exercises": [d["exercise_id"] for d in details]}


def lm_fixture():
    return {
        "exercise_kcs": {"cur": ["loop"], "cur2": ["string"]},
        "concepts": [
            concept("loop", "struggling", [det("a", "Tổng dãy", "struggling", 2, "logic_partial"),
                                           det("b", "Đếm chẵn", "attempted", 1, "logic_partial")], "logic_partial"),
            concept("string", "secure", [det("s1", "Đảo chuỗi", "passed", 0, None, 90),
                                         det("s2", "Đếm từ", "passed", 0, None, 80)]),
        ],
        "support_profile": {"hint_reliance": "low"},
    }


def sm_fixture():
    return {"analytics_metrics": {"distinct_exercises_attempted": 3, "first_try_pass_rate": 0.3,
                                  "autonomy_score": 60, "data_status": "sufficient"},
            "learner_model": lm_fixture()}


FAIL = {"all_passed": False, "results": [{"status": "FAIL", "passed": False, "expected": "1", "actual": "2"}]}


def all_text(d):
    return " ".join(str(v) for v in d.values() if isinstance(v, str)).lower()


class ConceptPlainTests(unittest.TestCase):
    def test_no_evidence_says_so(self):
        out = concept_plain(concept("loop", "no_evidence", []))
        self.assertIn("chưa có bài nộp chính thức", out["explanation_vi"])
        self.assertIsNone(out["common_error_vi"])

    def test_struggling_cites_counts(self):
        out = concept_plain(lm_fixture()["concepts"][0])
        self.assertIn("1 bài", out["explanation_vi"])
        self.assertIn("2 lần nộp chưa đạt", out["explanation_vi"])
        self.assertIn("Tổng dãy", out["explanation_vi"])
        self.assertIn("đúng ở một số trường hợp", out["common_error_vi"])

    def test_secure_and_developing(self):
        c = lm_fixture()["concepts"][1]
        self.assertIn("2 bài", concept_plain(c)["explanation_vi"])
        dev = concept("loop", "developing", [det("a", "A", "attempted", 1), det("b", "B", "passed")])
        self.assertIn("làm đúng 1 bài", concept_plain(dev)["explanation_vi"])

    def test_error_profile_fallback_only_without_passes(self):
        c = concept("loop", "developing", [det("a", "A", "attempted", 1)])
        self.assertIsNotNone(concept_plain(c, {"dominant_error_class": "syntax"})["common_error_vi"])
        c2 = concept("loop", "developing", [det("a", "A", "passed")])
        self.assertIsNone(concept_plain(c2, {"dominant_error_class": "syntax"})["common_error_vi"])

    def test_banned_words(self):
        samples = []
        for state in ("no_evidence", "developing", "struggling", "secure"):
            for err in (None, "syntax", "runtime", "timeout", "logic_partial", "logic_none", "zero_pass"):
                for dets in ([], [det("a", "A", "passed")], [det("a", "A", "struggling", 3, err)],
                             [det("a", "A", "attempted", 1, err)]):
                    samples.append(concept_plain(concept("loop", state, dets, err), {"dominant_error_class": err}))
        samples.append({"x": concept_focus_line({"items": [{"kc": "loop", "label_vi": "x", "students": {"struggling": 3}}]})})
        for s in samples:
            text = all_text(s)
            for w in BANNED_WORDS:
                self.assertNotIn(w, text, f"{w!r} trong {text!r}")

    def test_enrich_adds_only(self):
        src = lm_fixture()["concepts"]
        out = enrich_concepts(src)
        self.assertEqual(len(out), 2)
        for a, b in zip(src, out):
            self.assertNotIn("explanation_vi", a)
            self.assertTrue(set(a) <= set(b))
            self.assertTrue(b["explanation_vi"])
            self.assertIn("common_error_vi", b)


class ClassFocusTests(unittest.TestCase):
    def test_focus_picks_most_struggling(self):
        kc = {"items": [{"kc": "loop", "label_vi": "Vòng lặp", "students": {"struggling": 2, "secure": 1}},
                        {"kc": "string", "label_vi": "Xử lý chuỗi", "students": {"struggling": 4}}]}
        self.assertIn("Xử lý chuỗi", concept_focus_line(kc))
        self.assertIsNone(concept_focus_line({"items": [{"kc": "loop", "students": {"secure": 3}}]}))
        self.assertIsNone(concept_focus_line(None))

    def test_class_view_has_key(self):
        v = build_class_plain_view({"matrix": {"exercises": [], "rows": []},
                                    "kc_overview": {"items": [{"kc": "loop", "label_vi": "Vòng lặp",
                                                               "students": {"struggling": 2}}]}})
        self.assertIn("Vòng lặp", v["concept_focus_vi"])
        self.assertIsNone(build_class_plain_view({})["concept_focus_vi"])


class PolicyUnchangedTests(unittest.TestCase):
    def test_recurring_difficulty_decision_and_reason(self):
        out = select_hint_strategy(2, FAIL, [], sm_fixture(), exercise_id="cur")
        self.assertEqual(out["strategy"], "recurring_difficulty")
        self.assertEqual(out["requested_level"], 2)
        self.assertEqual(out["adaptation_codes"], ["concept_recurring_difficulty"])
        a = out["adaptations"][0]
        self.assertEqual(a["concept_label_vi"], "Vòng lặp")
        self.assertEqual(a["concept_state_label_vi"], "đang vướng")
        self.assertIn("Vòng lặp", a["reason_vi"])
        self.assertIn("đang vướng", a["reason_vi"])
        self.assertIn("2 lần nộp chưa đạt", a["reason_vi"])

    def test_bridge_and_non_model_adaptations(self):
        ok = {"all_passed": False, "results": []}
        out = select_hint_strategy(1, ok, [], sm_fixture(), exercise_id="cur2")
        self.assertEqual(out["strategy"], "conceptual_start")
        self.assertEqual(out["adaptation_codes"], ["bridge_from_mastered"])
        self.assertEqual(out["adaptations"][0]["concept_state_label_vi"], "khá vững")
        hist = [{"action_type": "submit", "hint_level": 1}, {"action_type": "ask_ai", "hint_level": 1}]
        out2 = select_hint_strategy(1, FAIL, hist, sm_fixture(), exercise_id="cur")
        self.assertEqual(out2["strategy"], "recurring_difficulty")
        self.assertIsNone(out2["adaptations"][0]["concept_label_vi"])
        self.assertIsNone(out2["adaptations"][0]["concept_state_label_vi"])

    def test_level_never_raised(self):
        for lvl in (1, 2, 3):
            self.assertEqual(select_hint_strategy(lvl, FAIL, [], sm_fixture(), exercise_id="cur")["requested_level"], lvl)

    def test_reason_banned_words(self):
        for ex in ("cur", "cur2"):
            for t in (FAIL, {"all_passed": False, "results": []}):
                for a in select_hint_strategy(1, t, [], sm_fixture(), exercise_id=ex)["adaptations"]:
                    for w in ("bằng chứng", "heuristic", "trạng thái", "khái niệm", " kc"):
                        self.assertNotIn(w, a["reason_vi"].lower())


if __name__ == "__main__":
    unittest.main()
