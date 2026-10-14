import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import Header from './components/Header';
import ProblemPanel from './components/ProblemPanel';
import EditorPanel from './components/EditorPanel';
import TutorPanel from './components/TutorPanel';
import { checkHealth, fetchExercises, fetchExerciseDetail, submitCode } from './services/api';

export default function App() {
  const [health, setHealth] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [selectedExerciseId, setSelectedExerciseId] = useState('');
  const [exerciseDetail, setExerciseDetail] = useState(null);
  const [code, setCode] = useState('');
  const [hintLevel, setHintLevel] = useState(1);
  const [testResults, setTestResults] = useState(null);
  const [astAnalysis, setAstAnalysis] = useState(null);
  const [tutorHint, setTutorHint] = useState('');
  const [llmSource, setLlmSource] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingExercise, setIsLoadingExercise] = useState(false);
  const [isDarkTheme, setIsDarkTheme] = useState(true);

  // 1. Kiểm tra Health check khi tải trang
  useEffect(() => {
    const initApp = async () => {
      const healthData = await checkHealth();
      setHealth(healthData);

      try {
        const exList = await fetchExercises();
        setExercises(exList);
        if (exList.length > 0) {
          setSelectedExerciseId(exList[0].id);
        }
      } catch (err) {
        console.error('Không thể tải danh sách bài tập:', err);
      }
    };

    initApp();
  }, []);

  // 2. Tải chi tiết bài tập khi selectedExerciseId thay đổi
  useEffect(() => {
    if (!selectedExerciseId) return;

    const loadExercise = async () => {
      setIsLoadingExercise(true);
      try {
        const detail = await fetchExerciseDetail(selectedExerciseId);
        setExerciseDetail(detail);
        setCode(detail.starter_code || '');
        // Reset kết quả cũ
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

  // 3. Khôi phục code mẫu
  const handleResetCode = () => {
    if (exerciseDetail) {
      setCode(exerciseDetail.starter_code || '');
    }
  };

  // 4. Xử lý Chạy code & Nộp bài
  const handleSubmit = async () => {
    if (!selectedExerciseId || !code.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const res = await submitCode({
        exercise_id: selectedExerciseId,
        code,
        hint_level: hintLevel,
      });

      setTestResults(res.test_results);
      setAstAnalysis(res.ast_analysis);
      setTutorHint(res.tutor_hint);
      setLlmSource(res.llm_source);

      // Bắn pháo giấy chúc mừng nếu đạt 100% test cases
      if (res.test_results?.all_passed) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
        });
      }
    } catch (err) {
      console.error('Lỗi khi submit bài:', err);
      alert('Có lỗi xảy ra khi chấm bài. Vui lòng kiểm tra kết nối Backend.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`h-screen w-screen flex flex-col bg-slate-950 font-sans ${isDarkTheme ? 'dark' : ''}`}>
      {/* Header */}
      <Header
        health={health}
        isDarkTheme={isDarkTheme}
        setIsDarkTheme={setIsDarkTheme}
      />

      {/* Main 3-Column IDE Layout */}
      <main className="flex-1 grid grid-cols-1 md:grid-cols-12 overflow-hidden">
        {/* Column 1: Problem Panel (~28%) */}
        <section className="md:col-span-3 h-full overflow-hidden">
          <ProblemPanel
            exercises={exercises}
            selectedExerciseId={selectedExerciseId}
            onSelectExercise={setSelectedExerciseId}
            exerciseDetail={exerciseDetail}
            isLoading={isLoadingExercise}
          />
        </section>

        {/* Column 2: Editor & Test Results (~46%) */}
        <section className="md:col-span-6 h-full overflow-hidden">
          <EditorPanel
            code={code}
            setCode={setCode}
            onResetCode={handleResetCode}
            onSubmit={handleSubmit}
            isSubmitting={isSubmitting}
            testResults={testResults}
            isDarkTheme={isDarkTheme}
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
            isSubmitting={isSubmitting}
            testResults={testResults}
          />
        </section>
      </main>
    </div>
  );
}
