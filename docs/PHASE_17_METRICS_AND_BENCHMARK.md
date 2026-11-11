# Phase 17 — Metric definitions and offline replay

## Metric contract (definition version 1)

Analytics use official `action_type=submit` events only. `ask_ai` remains in attempt history so the tutor can avoid repeating guidance, but it is excluded from official submission counts, pass-rate calculations, autonomy, and class submission aggregates. Existing rows are migrated with `action_type='submit'` to preserve their historic interpretation.

| Metric | Definition | Empty / sparse data |
|---|---|---|
| `total_submissions` | Count of official submissions in the selected student/class scope | 0 with `data_status=no_data` when none |
| `distinct_exercises_attempted` | Distinct exercise IDs with an official submission | Used as sample size for learner-level classification |
| `first_try_pass_rate` | Exercises whose first official submission passed all tests / distinct attempted exercises × 100 | Numeric zero when the denominator is nonzero and none passed; no-data separately signals denominator zero |
| `avg_attempts_to_solve` | Official submissions / distinct attempted exercises | Descriptive; denominator zero means no data |
| `average_hint_level` | Mean of each attempted exercise's maximum requested hint level | Descriptive of requested support, not a measure of ability by itself |
| `autonomy_score` | Existing star/pass-based score on a 0–100 scale | Existing formula retained; sparse profiles are not classified |
| `error_breakdown` | Official submissions grouped as pass, partial-test logic failure, or zero-pass syntax/runtime failure | Percentages use official submissions as denominator |

`data_status` is `no_data` for zero official submissions, `limited` below three distinct exercises, otherwise `sufficient`. Three distinct exercises is a conservative product threshold for showing a classification, not a validated educational cutoff. The class chatbot reports the requested time window, active-student sample count, and `no_data` when the window has no submissions. No individual student code or identity enters the aggregate response.

## Deterministic strategy policy

The strategy selector is a pure function. Passing work selects `solution_review`; otherwise repeated prior attempts select `recurring_difficulty`; failing tests select `failed_case_diagnosis`; absent evidence selects `conceptual_start`. It records evidence keys and prior hint levels. The user's requested hint level remains unchanged and continues to govern disclosure.

## Offline replay rubric

`evaluate_phase17_adaptive.py` replays synthetic cases against a simple current-style static baseline and the deterministic selector. It reports per-case expected strategy, evidence, no-data handling, and requested-level preservation. This benchmark measures policy behavior only; it is not a user study and cannot establish learning gains. No provider call is made.

## Research-informed adaptation principles

Treat adaptation as **evidence-based scaffolding**, not as an ability diagnosis:

1. Start with an on-demand conceptual/process cue at the requested hint level. Preserve student agency; do not force a hint merely because an attempt failed.
2. If the learner returns with a repeated failure, make the next cue more diagnostic and tied to observable evidence (failed tests, code region, or prior hint), but do not repeat the same wording or jump directly to a complete solution.
3. After a correct solution, fade task scaffolding: acknowledge the successful approach, invite a short self-check/reflection, then offer an optional extension rather than another corrective hint.
4. Prefer feedback about task, strategy/process, and self-monitoring over generic praise. Address “What is the goal?”, “What does the current evidence show?”, and “What is a useful next step?”.
5. Treat accuracy and hint use as distinct evidence. Hint requests can reflect help-seeking preference, uncertainty, or motivation; they must not be interpreted alone as low ability. A small pilot cannot validate an ability score.

These are design principles adapted from feedback and assessment research, not validated thresholds for this product. Existing autonomy and data-sufficiency cutoffs remain operational heuristics and must not be described as educationally validated.

## Pilot with 2–3 students and instructors

### Scope and privacy

- Recruit 2–3 volunteers across student and instructor roles. Participation is optional and does not affect grades.
- Prefer synthetic profiles and seeded code errors. If participants use their own accounts, explain what is logged, obtain consent, and anonymize notes. Do not collect passwords, unrelated personal details, or real submissions unless essential and explicitly agreed.
- Use the configured mock tutor by default. A live provider is unnecessary to evaluate deterministic strategy selection, analytics comprehension, and protocol usability. If live AI is later enabled, disclose external processing and use only non-identifying code.
- Record only participant role, scenario ID, condition/order, task completion, short ratings, and anonymized comments.

### Matched before/after procedure

Compare two conditions on the same scripted scenario set:

- **Baseline:** fixed conceptual Level 1 feedback policy.
- **Adaptive:** current selector using pass status, repeated attempts, failed-test evidence, and history while preserving the requested disclosure level.

Reset code and attempt history between conditions. Alternate order between participants (baseline-first, then adaptive-first) to reduce order effects; use identical facilitator instructions. Because the same cases are repeated, practice effects remain possible. With 2–3 participants, this is descriptive usability evidence, not a controlled efficacy study: report paired observations and examples, not statistical significance or causal learning gains.

### Student cases and scoring

| Case | Starting evidence | Expected adaptation |
|---|---|---|
| New learner, no history | One boundary-condition error | Small conceptual cue; no diagnosis from absent history |
| Repeated logic error | Same failing test after earlier hint | More specific, test-grounded next step; do not repeat or reveal the full solution |
| Syntax/runtime failure | Zero tests pass with an error | Explain error category and focus attention on relevant code |
| Successful first attempt | All tests pass at low hint use | Fade corrective scaffold; offer process reflection or optional extension |
| Successful after help | All tests pass after hints | Recognize success while distinguishing assisted from first-try success |
| Sparse profile | Fewer than three exercises attempted | Show observations and sample size; avoid stable skill labels |

Use fixed starter-code fixtures and prompts. Score each feedback on: (a) grounded in evidence, (b) suitable specificity, (c) actionable next step, (d) learner agency, (e) avoids complete-answer leakage, and (f) understandable. Rate each 0 = no, 1 = partly, 2 = yes. Report individual case results rather than statistical claims.

After each case, ask students to rate 1–5: “I understand what to try next”; “The hint matched my problem”; “The hint gave away too much”; “I could still solve it myself.” Include “not sure” and one short free-text response.

### Instructor cases

Have instructors review the same synthetic class-progress snapshots in both conditions (baseline summary vs. analytics with sample-size/data-status context). Ask them to state: (1) the apparent class difficulty, (2) the number of observations supporting it, (3) one reasonable teaching action, and (4) one conclusion that cannot safely be drawn. Compare answers with a prepared key and note overclaims. Ask whether `no_data`, `limited`, and `sufficient` are clear and whether the report informs a teaching decision.

### Analysis and completion criteria

- Compare paired rubric scores, time-to-next-action, instructor interpretation, and participant ratings between baseline and adaptive conditions.
- Treat answer leakage, unsupported claims, repeated/irrelevant hints, incorrect attribution, and confusion about sparse data as failures: fix and rerun that case.
- Keep notes anonymized; state what was and was not tested, including sample limitations.
- Automated tests and offline replay establish technical implementation only. Call the user pilot complete only after sessions are run and observations recorded. Do not claim learning gains from 2–3 participants.

## Research basis

- Hattie and Timperley frame feedback around goal, current progress, and next step; they distinguish task-, process-, and self-regulation-level feedback and note that effects depend on its form and context. [The Power of Feedback (2007)](https://doi.org/10.3102/003465430298487).
- Nicol and Macfarlane-Dick describe formative assessment as supporting learner self-regulation and active use of feedback, not merely delivering corrections. [Formative assessment and self-regulated learning (2006)](https://doi.org/10.1080/03075070600572090).
- Bolsinova et al. model response accuracy and on-demand hint use as related but distinct evidence and discuss individual differences in hint-seeking. This supports not equating hint frequency with ability; their language-learning application is not directly imported into PyTutor. [Measurement of Ability…when Learners Use On-Demand Hints (2022)](https://doi.org/10.1177/01466216221084208).
- A counterbalanced study of immediate computer feedback and optional hints found benefits in secondary mathematics, but its subject and age differ from this project; it motivates testing timely optional support, not claiming the same effect for Python. [Effect of Immediate Feedback on Math Achievement (2020)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7334720/).
- Research on personalized feedback in an intelligent tutoring system for a machine-learning course is closer to technical learning, but does not establish that PyTutor's current heuristic selector improves outcomes. [Automated Personalized Feedback Improves Learning Gains in an ITS (2020)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7334734/).
