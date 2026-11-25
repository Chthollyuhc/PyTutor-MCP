import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import confetti from 'canvas-confetti';
import { Sparkles, ArrowLeft, CheckCircle2, Star } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import Header from '../components/Header';
import ProblemPanel from '../components/ProblemPanel';
import EditorPanel from '../components/EditorPanel';
import TutorPanel from '../components/TutorPanel';
import StudentProfileModal from '../components/StudentProfileModal';
import ExecutionVisualizerModal from '../components/ExecutionVisualizerModal';
import { isBlankCode } from '../utils/blankCode';
import { rememberLastClassId } from '../utils/lastClass';
import { 
  fetchExercises, 
  fetchExerciseDetail, 
  runTestOnly, 
  submitCode,
  fetchClasses,
  fetchMyClasses,
  fetchClassCurriculum,
  fetchExamSessions,
  fetchStudentJourney
} from '../services/api';

const STAR_MEANING = {
  3: 'Bạn tự làm, không cần gợi ý lớn.',
  2: 'Bạn có dùng gợi ý mức 2.',
  1: 'Bạn có dùng gợi ý mức 3.',
};

export default function StudentIDE() {
  const { exerciseId: paramExerciseId } = useParams();
  const [searchParams] = useSearchParams();
  const classIdParam = searchParams.get('classId');
  useEffect(() => { rememberLastClassId(classIdParam); }, [classIdParam]);
  const sessionIdParam = searchParams.get('sessionId');
  const navigate = useNavigate();

  const [exercises, setExercises] = useState([]);
  const [selectedExerciseId, setSelectedExerciseId] = useState(paramExerciseId || '');
  const [exerciseDetail, setExerciseDetail] = useState(null);
  const [code, setCode] = useState('');
  const [codeBeforeInsert, setCodeBeforeInsert] = useState(null); // bản code trước khi dán khung mẫu, để hoàn tác
  const [hintLevel, setHintLevel] = useState(1);
  const [testResults, setTestResults] = useState(null);
  const [astAnalysis, setAstAnalysis] = useState(null);
  const [tutorHint, setTutorHint] = useState('');
  const [adaptiveStrategy, setAdaptiveStrategy] = useState(null);
  const [llmSource, setLlmSource] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAskingAI, setIsAskingAI] = useState(false);
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [isLoadingExercise, setIsLoadingExercise] = useState(false);
  const { theme } = useTheme();

  // Phase 12, 13 & 14: NEU Credit Classes & Exam/Practice Sessions State
  const [creditClasses, setCreditClasses] = useState([]);
  const [currentClass, setCurrentClass] = useState(null);
  const [examSessions, setExamSessions] = useState([]);
  const [allExamSessions, setAllExamSessions] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState(sessionIdParam || '');
  const [remainingSeconds, setRemainingSeconds] = useState(45 * 60);

  // Modal States
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isVisualizerOpen, setIsVisualizerOpen] = useState(false);
  // null = chưa có lượt "Nộp bài" đạt trong phiên này ở bài đang mở (không mặc định 3 sao).
  const [starsEarned, setStarsEarned] = useState(null);
  // v5.3: ID phản hồi AI của gợi ý hiện tại (để đánh giá 👍/👎) và lý do số sao của lượt nộp chính thức gần nhất.
  const [hintInteractionId, setHintInteractionId] = useState(null);
  const [starRationale, setStarRationale] = useState(null);
  // Đã có lượt "Nộp bài" đạt ở bài này (từ API chi tiết bài hoặc vừa nộp đạt) → chat mở phạm vi code đã nộp.
  const [hasPassedExercise, setHasPassedExercise] = useState(false);

  const { user } = useAuth();
  // Khởi tạo session_id: Ưu tiên tài khoản đang đăng nhập (student) để đồng bộ dữ liệu lớp học phần và bảng vàng
  const sessionId = user?.username || localStorage.getItem('pytutor_session_id') || 'student';
  const [submissionSuccess, setSubmissionSuccess] = useState(null);
  const [successMoment, setSuccessMoment] = useState(null);

  // Đồng bộ paramExerciseId khi đổi URL
  useEffect(() => {
    if (paramExerciseId && paramExerciseId !== selectedExerciseId) {
      setSelectedExerciseId(paramExerciseId);
    }
  }, [paramExerciseId]);

  // 1. Kiểm tra Health check & Tải danh mục bài tập, Lớp tín chỉ NEU & Đợt thi
  useEffect(() => {
    const initData = async () => {
      try {
        const [exList, myClsList, allClsList, sessList] = await Promise.all([
          fetchExercises(),
          fetchMyClasses().catch(() => []),
          fetchClasses().catch(() => []),
          fetchExamSessions()
        ]);
        setExercises(exList || []);

        const activeClasses = (myClsList && myClsList.length > 0) ? myClsList : (allClsList || []);
        setCreditClasses(activeClasses);
        setAllExamSessions(sessList || []);

        // Xác định class active: ưu tiên classIdParam nếu có
        let activeCls = null;
        if (classIdParam) {
          activeCls = activeClasses.find(c => c.id === classIdParam) || null;
        }
        if (!activeCls && !paramExerciseId && activeClasses.length > 0) {
          activeCls = activeClasses[0];
        }
        if (activeCls) {
          setCurrentClass(activeCls);
        } else if (paramExerciseId) {
          // Nếu loadExercise đã chạy xong và set currentClass, đối chiếu để lấy object đầy đủ từ activeClasses
          setCurrentClass((prev) => {
            if (prev?.id) {
              const full = activeClasses.find((c) => c.id === prev.id);
              if (full) return full;
            }
            return prev;
          });
        }

        // Lọc sessions theo class
        if (activeCls) {
          const classSess = (sessList || []).filter(s => !s.class_id || s.class_id === activeCls.id);
          setExamSessions(classSess.length > 0 ? classSess : (sessList || []));
        } else {
          setExamSessions(sessList || []);
        }

        // Chọn bài tập: ưu tiên paramExerciseId, nếu không có lấy bài đầu tiên
        if (paramExerciseId) {
          setSelectedExerciseId(paramExerciseId);
        } else if (exList && exList.length > 0) {
          setSelectedExerciseId(exList[0].id);
        }
      } catch (err) {
        console.error('Không thể nạp dữ liệu ban đầu cho Student IDE:', err);
      }
    };

    initData();
  }, [classIdParam]);

  // Tự động lọc examSessions khi currentClass thay đổi
  useEffect(() => {
    if (!currentClass) {
      setExamSessions(allExamSessions);
      return;
    }
    const classSess = allExamSessions.filter(s => !s.class_id || s.class_id === currentClass.id);
    setExamSessions(classSess.length > 0 ? classSess : allExamSessions);
  }, [currentClass?.id, allExamSessions]);

  const handleSelectExercise = (exId) => {
    setSelectedExerciseId(exId);
    const q = new URLSearchParams();
    if (currentClass?.id) q.set('classId', currentClass.id);
    if (selectedSessionId) q.set('sessionId', selectedSessionId);
    const qs = q.toString() ? `?${q.toString()}` : '';
    navigate(`/student/ide/${exId}${qs}`, { replace: true });
  };

  const currentSession = examSessions.find(s => s.id === selectedSessionId) || null;
  const isExamMode = currentSession?.session_type === 'EXAM';

  const displayedExercises = currentSession && currentSession.exercise_ids?.length > 0
    ? exercises.filter(ex => currentSession.exercise_ids.includes(ex.id))
    : exercises;

  // Khi học viên chọn Chế độ / Đợt làm bài
  const handleSelectSession = (sessionId) => {
    setSelectedSessionId(sessionId);
    if (!sessionId) {
      if (exercises.length > 0) {
        setSelectedExerciseId(exercises[0].id);
      }
      return;
    }
    const sess = examSessions.find(s => s.id === sessionId);
    if (sess && sess.exercise_ids && sess.exercise_ids.length > 0) {
      if (!sess.exercise_ids.includes(selectedExerciseId)) {
        setSelectedExerciseId(sess.exercise_ids[0]);
      }
    }
  };

  // Đồng hồ đếm ngược cho Chế độ Kỳ thi (EXAM Mode)
  useEffect(() => {
    if (isExamMode && currentSession) {
      setRemainingSeconds((currentSession.duration_minutes || 45) * 60);
    }
  }, [selectedSessionId, isExamMode]);

  useEffect(() => {
    if (!isExamMode) return;
    const timer = setInterval(() => {
      setRemainingSeconds(prev => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [isExamMode]);

  const formatTimer = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // 2. Tải chi tiết bài tập khi selectedExerciseId thay đổi (Có khôi phục code nháp từ localStorage)
  useEffect(() => {
    if (!selectedExerciseId) return;

    const loadExercise = async () => {
      setIsLoadingExercise(true);
      try {
        const detail = await fetchExerciseDetail(selectedExerciseId, classIdParam);
        setExerciseDetail(detail);

        // Đồng bộ lớp học phần khớp với bài tập đang mở
        if (detail?.class_id) {
          setCurrentClass((prev) => {
            if (prev?.id === detail.class_id) {
              return prev;
            }
            const matchingCls = (creditClasses || []).find((c) => c.id === detail.class_id);
            return matchingCls || {
              id: detail.class_id,
              class_code: detail.class_code || detail.class_id,
              class_name: detail.class_name,
              semester: detail.semester || '',
            };
          });
        }

        // Khôi phục code nháp đã lưu tự động nếu có
        const savedDraft = localStorage.getItem(`pytutor_draft_${selectedExerciseId}`);
        if (savedDraft !== null) {
          setCode(savedDraft);
        } else {
          setCode(detail.starter_code || '');
        }

        // Reset kết quả cũ khi đổi bài tập
        setTestResults(null);
        setAstAnalysis(null);
        setTutorHint('');
        setAdaptiveStrategy(null);
        setLlmSource('');
        setHintInteractionId(null);
        setStarRationale(null);
        setHasPassedExercise(Boolean(detail.has_passed));
        setStarsEarned(null);
      } catch (err) {
        console.error('Lỗi tải chi tiết bài tập:', err);
      } finally {
        setIsLoadingExercise(false);
      }
    };

    loadExercise();
  }, [selectedExerciseId]);

  // 3. Tự động lưu nháp khi sinh viên chỉnh sửa code
  const handleCodeChange = (newCode) => {
    setCode(newCode);
    setCodeBeforeInsert(null); // gõ tiếp thì thôi cho hoàn tác khung mẫu
    if (selectedExerciseId) {
      localStorage.setItem(`pytutor_draft_${selectedExerciseId}`, newCode);
    }
  };

  // 4. Khôi phục code gốc (xóa bản nháp lưu tạm)
  const handleResetCode = () => {
    if (selectedExerciseId) {
      localStorage.removeItem(`pytutor_draft_${selectedExerciseId}`);
    }
    if (exerciseDetail) {
      setCode(exerciseDetail.starter_code || '');
    }
  };

  // 5. Chạy thử nhanh (Run Test Only - Không gọi AI)
  const handleRunTest = async () => {
    if (!selectedExerciseId || !code.trim() || isRunningTest || isSubmitting) return;

    setIsRunningTest(true);
    try {
      const res = await runTestOnly({
        exercise_id: selectedExerciseId,
        code,
      });

      setTestResults(res.test_results);
      setAstAnalysis(res.ast_analysis);
      // Chạy thử không phải lượt nộp chính thức: bỏ thẻ lý do sao của lần nộp trước để không hiện nhầm.
      setStarRationale(null);

      if (res.test_results?.all_passed) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
          disableForReducedMotion: true,
        });
      }
    } catch (err) {
      console.error('Lỗi khi chạy thử code:', err);
      alert('Có lỗi xảy ra khi chạy thử. Vui lòng kiểm tra kết nối Backend.');
    } finally {
      setIsRunningTest(false);
    }
  };

  // Dán khung code Mức 3 vào editor; có code sẵn thì hỏi xác nhận và cho hoàn tác.
  const handleInsertSkeleton = (skeleton) => {
    if (!skeleton || !selectedExerciseId) return;
    const hasWork = !isBlankCode(code, exerciseDetail?.starter_code);
    if (hasWork && !window.confirm('Thay code hiện tại bằng khung mẫu này? Bạn có thể hoàn tác ngay sau đó.')) return;
    const previous = code;
    setCode(skeleton);
    localStorage.setItem(`pytutor_draft_${selectedExerciseId}`, skeleton);
    setCodeBeforeInsert(hasWork ? previous : null);
  };

  const handleUndoInsert = () => {
    if (codeBeforeInsert === null) return;
    handleCodeChange(codeBeforeInsert);
  };

  // 6. Hỏi Gia sư AI (Chỉ xin gợi ý sư phạm, không lưu sao, không mở modal chúc mừng)
  // Chưa có code vẫn được xin gợi ý: backend chuyển sang gợi ý giúp hiểu đề.
  const handleAskAI = async (overrideHintLevel = null) => {
    if (!selectedExerciseId || isAskingAI || isSubmitting || isRunningTest) return;
    const noCodeYet = isBlankCode(code, exerciseDetail?.starter_code);

    const targetLevel = overrideHintLevel !== null ? overrideHintLevel : hintLevel;
    setIsAskingAI(true);
    try {
      const res = await submitCode({
        exercise_id: selectedExerciseId,
        code,
        hint_level: targetLevel,
        session_id: sessionId,
        exam_session_id: currentSession?.id || null,
        action_type: 'ask_ai',
        class_id: currentClass?.id || null,
      });

      if (!noCodeYet) { // chưa có code thì kết quả kiểm thử vô nghĩa, không hiện bảng "trượt hết"
        setTestResults(res.test_results);
        setAstAnalysis(res.ast_analysis);
      }
      setTutorHint(res.tutor_hint);
      setAdaptiveStrategy(res.adaptive_strategy || null);
      setLlmSource(res.llm_source);
      setHintInteractionId(res.interaction_id || null);
      setStarRationale(null); // hỏi AI không sinh sao: không giữ thẻ lý do sao của lần nộp trước
    } catch (err) {
      console.error('Lỗi khi hỏi Gia sư AI:', err);
      alert('Có lỗi xảy ra khi xin gợi ý từ Gia sư AI. Vui lòng kiểm tra kết nối Backend.');
    } finally {
      setIsAskingAI(false);
    }
  };

  // 7. Nộp bài chính thức & Ghi nhận Sao năng lực
  const handleSubmit = async () => {
    if (!selectedExerciseId || !code.trim() || isSubmitting || isAskingAI || isRunningTest) return;

    setIsSubmitting(true);
    try {
      const res = await submitCode({
        exercise_id: selectedExerciseId,
        code,
        hint_level: hintLevel,
        session_id: sessionId,
        exam_session_id: currentSession?.id || null,
        action_type: 'submit',
        class_id: currentClass?.id || null,
      });

      setTestResults(res.test_results);
      setAstAnalysis(res.ast_analysis);
      setTutorHint(res.tutor_hint);
      setAdaptiveStrategy(res.adaptive_strategy || null);
      setLlmSource(res.llm_source);
      setHintInteractionId(res.interaction_id || null);
      setStarRationale(res.star_rationale || null);
      if (res.stars_earned !== undefined && res.stars_earned > 0) {
        setStarsEarned(res.stars_earned);
      }

      // Bắn pháo hoa chúc mừng nếu đạt 100% test cases
      if (res.test_results?.all_passed) {
        setHasPassedExercise(true);
        confetti({
          particleCount: 100,
          spread: 80,
          origin: { y: 0.6 },
          disableForReducedMotion: true,
        });
        setSubmissionSuccess({
          allPassed: true,
          starsEarned: res.stars_earned || 3,
        });
        setSuccessMoment(null);
        fetchStudentJourney(currentClass?.id || null, selectedExerciseId)
          .then((d) => setSuccessMoment(d?.today?.moments?.[0]?.text_vi || null))
          .catch(() => {});
      }
    } catch (err) {
      console.error('Lỗi khi nộp bài:', err);
      alert('Có lỗi xảy ra khi chấm bài. Vui lòng kiểm tra kết nối Backend.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // 8. Xử lý leo thang gợi ý (Escalation)
  const handleEscalate = (nextLevel) => {
    handleAskAI(nextLevel);
  };

  return (
    <div className="flex h-screen w-full flex-col bg-canvas text-foreground">
      {/* Header */}
      <Header
        onOpenProfile={() => setIsProfileOpen(true)}
        backUrl={(classIdParam || currentClass?.id) ? `/student/classes/${classIdParam || currentClass?.id}` : '/student'}
        backLabel="Quay lại Lớp học phần"
      />

      {/* EXAM Mode Countdown Banner */}
      {isExamMode && currentSession && (
        <div role="status" className="flex shrink-0 flex-col gap-2 border-b border-destructive/40 bg-destructive/10 px-4 py-2 text-sm sm:flex-row sm:items-center sm:justify-between">
          <p className="flex flex-wrap items-center gap-x-2 gap-y-1">
            <span className="font-semibold text-danger">Đang trong kỳ thi: {currentSession.title} ({currentSession.duration_minutes} phút)</span>
            <span className="hidden text-muted md:inline">· Gia sư AI bị khóa để đảm bảo công bằng</span>
          </p>
          <p className="flex items-center gap-2 self-end sm:self-auto">
            <span className="text-muted">Thời gian còn lại</span>
            <span className="rounded-md border border-destructive/40 bg-surface px-2.5 py-0.5 font-mono text-base font-semibold tabular-nums text-danger">
              {formatTimer(remainingSeconds)}
            </span>
          </p>
        </div>
      )}

      {/* Main 3-Column IDE Layout */}
      <main className="flex-1 min-h-0 grid grid-cols-1 xl:grid-cols-12 overflow-y-auto xl:overflow-hidden">
        {/* Column 1: Problem Panel (~28%) */}
        <section className="min-w-0 min-h-[60vh] xl:col-span-3 xl:h-full overflow-hidden">
          <ProblemPanel
            exercises={displayedExercises}
            selectedExerciseId={selectedExerciseId}
            onSelectExercise={handleSelectExercise}
            exerciseDetail={exerciseDetail}
            isLoading={isLoadingExercise}
            currentClass={currentClass}
            examSessions={examSessions}
            selectedSessionId={selectedSessionId}
            onSelectSession={handleSelectSession}
            isExamMode={isExamMode}
          />
        </section>

        {/* Column 2: Editor & Test Results (~46%) */}
        <section className="min-w-0 min-h-[75vh] xl:col-span-6 xl:h-full overflow-hidden">
          <EditorPanel
            code={code}
            setCode={handleCodeChange}
            exerciseId={selectedExerciseId}
            onResetCode={handleResetCode}
            onRunTest={handleRunTest}
            isRunningTest={isRunningTest}
            onAskAI={() => handleAskAI()}
            askAiLabel={isBlankCode(code, exerciseDetail?.starter_code) ? 'Mình chưa biết bắt đầu' : 'Hỏi gia sư AI'}
            isAskingAI={isAskingAI}
            onSubmit={() => handleSubmit()}
            isSubmitting={isSubmitting}
            testResults={testResults}
            isDarkTheme={theme === 'dark'}
            onOpenVisualizer={() => setIsVisualizerOpen(true)}
            isExamMode={isExamMode}
          />
        </section>

        {/* Column 3: AI Tutor Panel (~26%) */}
        <section className="min-w-0 min-h-[60vh] xl:col-span-3 xl:h-full overflow-hidden">
          <TutorPanel
            classId={currentClass?.id || classIdParam || null}
            hintLevel={hintLevel}
            setHintLevel={setHintLevel}
            astAnalysis={astAnalysis}
            tutorHint={tutorHint}
            adaptiveStrategy={adaptiveStrategy}
            llmSource={llmSource}
            isAskingAI={isAskingAI}
            isSubmitting={isSubmitting}
            testResults={testResults}
            onAskAI={handleAskAI}
            onEscalate={handleEscalate}
            onInsertSkeleton={handleInsertSkeleton}
            canUndoInsert={codeBeforeInsert !== null}
            onUndoInsert={handleUndoInsert}
            exerciseId={selectedExerciseId}
            code={code}
            sessionId={sessionId}
            starsEarned={starsEarned}
            hintInteractionId={hintInteractionId}
            starRationale={starRationale}
            isExamMode={isExamMode}
            currentSession={currentSession}
            hasPassedBefore={hasPassedExercise}
          />
        </section>
      </main>

      {/* Modal 2: Student Profile / Nhật ký học tập & Hồ sơ học tập */}
      <StudentProfileModal
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        sessionId={sessionId}
        classId={currentClass?.id}
        currentExerciseId={selectedExerciseId}
        onLoadCode={(loadedCode) => handleCodeChange(loadedCode)}
      />

      {/* Modal 3: Execution Step Visualizer */}
      <ExecutionVisualizerModal
        isOpen={isVisualizerOpen}
        onClose={() => setIsVisualizerOpen(false)}
        initialCode={code}
        defaultStdin={exerciseDetail?.test_cases?.[0]?.input || ''}
      />

      {/* Modal 5: Thông báo nộp bài thành công & Điều hướng */}
      {submissionSuccess && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          onKeyDown={(e) => { if (e.key === 'Escape') setSubmissionSuccess(null); }}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="submit-success-title"
            aria-describedby="submit-success-desc"
            className="w-full max-w-md space-y-5 rounded-xl border border-border bg-surface p-6 text-center"
          >
            <CheckCircle2 aria-hidden="true" className="mx-auto size-10 text-emerald-600 dark:text-emerald-400" />
            <div>
              <h2 id="submit-success-title" className="text-xl font-semibold">Đúng hết rồi!</h2>
              <p id="submit-success-desc" className="mt-2 text-sm leading-relaxed text-muted">
                Bạn làm đúng hết bài này và có <strong className="font-semibold text-foreground">{submissionSuccess.starsEarned} sao</strong>. {STAR_MEANING[submissionSuccess.starsEarned] || ''}
              </p>
            </div>
            {successMoment && (
              <p className="rounded-2xl border border-success-line bg-success-soft px-3 py-2 text-sm text-success-strong">{successMoment}</p>
            )}
            <p aria-hidden="true" className="flex items-center justify-center gap-1">
              {[...Array(submissionSuccess.starsEarned)].map((_, i) => (
                <Star key={i} className="size-6 fill-amber-400 text-amber-500" />
              ))}
            </p>
            <div className="flex flex-col gap-2 sm:flex-row">
              {currentClass && (
                <button
                  type="button"
                  autoFocus
                  onClick={() => navigate(`/student/classes/${currentClass.id}`)}
                  className="inline-flex min-h-11 flex-1 items-center justify-center gap-2 rounded-lg bg-primary px-4 text-sm font-semibold text-primary-foreground hover:bg-primary-hover"
                >
                  <ArrowLeft aria-hidden="true" className="size-4" />
                  Về lớp học phần
                </button>
              )}
              <button
                type="button"
                autoFocus={!currentClass}
                onClick={() => setSubmissionSuccess(null)}
                className="inline-flex min-h-11 flex-1 items-center justify-center rounded-lg border border-border bg-surface px-4 text-sm font-semibold hover:bg-surface-raised"
              >
                Ở lại IDE
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
