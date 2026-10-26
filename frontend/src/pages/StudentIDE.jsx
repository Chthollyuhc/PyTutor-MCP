import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import confetti from 'canvas-confetti';
import { Sparkles, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import ProblemPanel from '../components/ProblemPanel';
import EditorPanel from '../components/EditorPanel';
import TutorPanel from '../components/TutorPanel';
import MCPInspectorModal from '../components/MCPInspectorModal';
import StudentProfileModal from '../components/StudentProfileModal';
import ExecutionVisualizerModal from '../components/ExecutionVisualizerModal';
import PythonicReviewModal from '../components/PythonicReviewModal';
import { 
  checkHealth, 
  fetchExercises, 
  fetchExerciseDetail, 
  runTestOnly, 
  submitCode,
  fetchClasses,
  fetchMyClasses,
  fetchClassCurriculum,
  fetchExamSessions
} from '../services/api';

export default function StudentIDE() {
  const { exerciseId: paramExerciseId } = useParams();
  const [searchParams] = useSearchParams();
  const classIdParam = searchParams.get('classId');
  const sessionIdParam = searchParams.get('sessionId');
  const navigate = useNavigate();

  const [health, setHealth] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [selectedExerciseId, setSelectedExerciseId] = useState(paramExerciseId || '');
  const [exerciseDetail, setExerciseDetail] = useState(null);
  const [code, setCode] = useState('');
  const [hintLevel, setHintLevel] = useState(1);
  const [testResults, setTestResults] = useState(null);
  const [astAnalysis, setAstAnalysis] = useState(null);
  const [tutorHint, setTutorHint] = useState('');
  const [llmSource, setLlmSource] = useState('');
  const [mcpTrace, setMcpTrace] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAskingAI, setIsAskingAI] = useState(false);
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [isLoadingExercise, setIsLoadingExercise] = useState(false);
  const [isDarkTheme, setIsDarkTheme] = useState(true);

  // Phase 12, 13 & 14: NEU Credit Classes & Exam/Practice Sessions State
  const [creditClasses, setCreditClasses] = useState([]);
  const [currentClass, setCurrentClass] = useState(null);
  const [examSessions, setExamSessions] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState(sessionIdParam || '');
  const [remainingSeconds, setRemainingSeconds] = useState(45 * 60);

  // Modal States
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isVisualizerOpen, setIsVisualizerOpen] = useState(false);
  const [isPythonicReviewOpen, setIsPythonicReviewOpen] = useState(false);
  const [starsEarned, setStarsEarned] = useState(3);

  const { user } = useAuth();
  // Khởi tạo session_id: Ưu tiên tài khoản đang đăng nhập (student) để đồng bộ dữ liệu lớp học phần và bảng vàng
  const sessionId = user?.username || localStorage.getItem('pytutor_session_id') || 'student';
  const [submissionSuccess, setSubmissionSuccess] = useState(null);

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
        const [healthData, exList, myClsList, allClsList, sessList] = await Promise.all([
          checkHealth(),
          fetchExercises(),
          fetchMyClasses().catch(() => []),
          fetchClasses().catch(() => []),
          fetchExamSessions()
        ]);
        setHealth(healthData);
        setExercises(exList || []);

        const activeClasses = (myClsList && myClsList.length > 0) ? myClsList : (allClsList || []);
        setCreditClasses(activeClasses);

        // Xác định class active: ưu tiên classIdParam nếu có
        let activeCls = null;
        if (classIdParam) {
          activeCls = activeClasses.find(c => c.id === classIdParam) || null;
        }
        if (!activeCls && activeClasses.length > 0) {
          activeCls = activeClasses[0];
        }
        setCurrentClass(activeCls);

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
        const detail = await fetchExerciseDetail(selectedExerciseId);
        setExerciseDetail(detail);

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
        setLlmSource('');
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
      if (res.mcp_trace) {
        setMcpTrace(res.mcp_trace);
      }

      if (res.test_results?.all_passed) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
        });
      }
    } catch (err) {
      console.error('Lỗi khi chạy thử code:', err);
      alert('Có lỗi xảy ra khi chạy thử. Vui lòng kiểm tra kết nối Backend.');
    } finally {
      setIsRunningTest(false);
    }
  };

  // 6. Hỏi Gia sư AI (Chỉ xin gợi ý sư phạm, không lưu sao, không mở modal chúc mừng)
  const handleAskAI = async (overrideHintLevel = null) => {
    if (!selectedExerciseId || !code.trim() || isAskingAI || isSubmitting || isRunningTest) return;

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
      });

      setTestResults(res.test_results);
      setAstAnalysis(res.ast_analysis);
      setTutorHint(res.tutor_hint);
      setLlmSource(res.llm_source);
      if (res.mcp_trace) {
        setMcpTrace(res.mcp_trace);
      }
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
      });

      setTestResults(res.test_results);
      setAstAnalysis(res.ast_analysis);
      setTutorHint(res.tutor_hint);
      setLlmSource(res.llm_source);
      if (res.mcp_trace) {
        setMcpTrace(res.mcp_trace);
      }
      if (res.stars_earned !== undefined && res.stars_earned > 0) {
        setStarsEarned(res.stars_earned);
      }

      // Bắn pháo hoa chúc mừng nếu đạt 100% test cases
      if (res.test_results?.all_passed) {
        confetti({
          particleCount: 100,
          spread: 80,
          origin: { y: 0.6 },
        });
        setSubmissionSuccess({
          allPassed: true,
          starsEarned: res.stars_earned || 3,
        });
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
    <div className={`h-screen w-screen flex flex-col bg-slate-950 font-sans ${isDarkTheme ? 'dark' : ''}`}>
      {/* Header */}
      <Header
        health={health}
        isDarkTheme={isDarkTheme}
        setIsDarkTheme={setIsDarkTheme}
        onOpenInspector={() => setIsInspectorOpen(true)}
        onOpenProfile={() => setIsProfileOpen(true)}
        mcpTraceCount={mcpTrace.length}
        backUrl={(classIdParam || currentClass?.id) ? `/student/classes/${classIdParam || currentClass?.id}` : '/student'}
        backLabel="Quay lại Lớp học phần"
      />

      {/* EXAM Mode Countdown Banner */}
      {isExamMode && currentSession && (
        <div className="bg-gradient-to-r from-rose-950 via-slate-900 to-amber-950 border-b border-rose-500/40 px-4 py-2 flex flex-col sm:flex-row sm:items-center justify-between text-xs text-rose-200 shrink-0 gap-2 shadow-lg">
          <div className="flex items-center space-x-2">
            <span className="flex h-2.5 w-2.5 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500"></span>
            </span>
            <span className="font-bold text-rose-300">
              ⏱️ ĐANG TRONG KỲ THI: {currentSession.title} ({currentSession.duration_minutes} phút)
            </span>
            <span className="text-slate-500 hidden md:inline">•</span>
            <span className="text-slate-400 hidden md:inline">
              Chế độ chấm điểm độc lập qua Sandbox (Gia sư AI bị khóa để đảm bảo công bằng)
            </span>
          </div>
          <div className="flex items-center space-x-3 self-end sm:self-auto font-mono">
            <span className="text-slate-400">Thời gian còn lại:</span>
            <span className="px-2.5 py-0.5 rounded-lg bg-rose-950 border border-rose-500/50 font-bold text-rose-400 text-sm tracking-wider shadow-inner">
              {formatTimer(remainingSeconds)}
            </span>
          </div>
        </div>
      )}

      {/* Main 3-Column IDE Layout */}
      <main className="flex-1 grid grid-cols-1 md:grid-cols-12 overflow-hidden">
        {/* Column 1: Problem Panel (~28%) */}
        <section className="md:col-span-3 h-full overflow-hidden">
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
        <section className="md:col-span-6 h-full overflow-hidden">
          <EditorPanel
            code={code}
            setCode={handleCodeChange}
            exerciseId={selectedExerciseId}
            onResetCode={handleResetCode}
            onRunTest={handleRunTest}
            isRunningTest={isRunningTest}
            onAskAI={() => handleAskAI()}
            isAskingAI={isAskingAI}
            onSubmit={() => handleSubmit()}
            isSubmitting={isSubmitting}
            testResults={testResults}
            isDarkTheme={isDarkTheme}
            onOpenVisualizer={() => setIsVisualizerOpen(true)}
            isExamMode={isExamMode}
          />
        </section>

        {/* Column 3: AI Tutor Panel (~26%) */}
        <section className="md:col-span-3 h-full overflow-hidden">
          <TutorPanel
            hintLevel={hintLevel}
            setHintLevel={setHintLevel}
            astAnalysis={astAnalysis}
            tutorHint={tutorHint}
            llmSource={llmSource}
            isAskingAI={isAskingAI}
            isSubmitting={isSubmitting}
            testResults={testResults}
            onAskAI={handleAskAI}
            onEscalate={handleEscalate}
            exerciseId={selectedExerciseId}
            code={code}
            sessionId={sessionId}
            onOpenPythonicReview={() => setIsPythonicReviewOpen(true)}
            starsEarned={starsEarned}
            isExamMode={isExamMode}
            currentSession={currentSession}
          />
        </section>
      </main>

      {/* Modal 1: MCP Protocol Inspector */}
      <MCPInspectorModal
        isOpen={isInspectorOpen}
        onClose={() => setIsInspectorOpen(false)}
        discoveredTools={health?.discovered_tools || []}
        mcpTrace={mcpTrace}
      />

      {/* Modal 2: Student Profile / Nhật ký học tập & Chẩn đoán 4D */}
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

      {/* Modal 4: Pythonic Code Review */}
      <PythonicReviewModal
        isOpen={isPythonicReviewOpen}
        onClose={() => setIsPythonicReviewOpen(false)}
        exerciseId={selectedExerciseId}
        code={code}
        username={sessionId}
        starsEarned={starsEarned}
      />

      {/* Modal 5: Thông báo nộp bài thành công & Điều hướng */}
      {submissionSuccess && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-emerald-500/60 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95 text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 mx-auto flex items-center justify-center text-white shadow-lg shadow-emerald-900/50">
              <Sparkles className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Nộp Bài Thành Công! 🎉</h3>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                Xin chúc mừng! Hệ thống đã ghi nhận <strong>{submissionSuccess.starsEarned} ⭐</strong> tự lực vào Hồ sơ năng lực và cập nhật Cây lộ trình kỹ năng của bạn.
              </p>
            </div>

            <div className="flex items-center justify-center space-x-1.5 py-1">
              {[...Array(submissionSuccess.starsEarned)].map((_, i) => (
                <span key={i} className="text-2xl drop-shadow-md">⭐</span>
              ))}
            </div>

            <div className="pt-2 flex flex-col sm:flex-row gap-2.5">
              {currentClass && (
                <button
                  onClick={() => navigate(`/student/classes/${currentClass.id}`)}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-md shadow-emerald-950 flex items-center justify-center space-x-1.5 cursor-pointer"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Về Lớp Học Phần</span>
                </button>
              )}
              <button
                onClick={() => setSubmissionSuccess(null)}
                className="flex-1 py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-all border border-slate-700 cursor-pointer"
              >
                Tiếp Tục Ở Lại IDE
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
