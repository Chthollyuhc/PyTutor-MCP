import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  School, BookOpen, Calendar, Award, Trophy, ChevronRight, 
  Lock, CheckCircle2, Star, ArrowLeft, Terminal, AlertTriangle, 
  Play, Sparkles, TrendingUp, Info, RefreshCw, Clock, ArrowRight,
  ShieldAlert, Layers, CheckSquare, Target, Search
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { 
  fetchClasses, 
  fetchMyClasses, 
  fetchClassCurriculum, 
  fetchExamSessions, 
  fetchSkillRoadmap, 
  fetchStudentProfile, 
  fetchLeaderboard 
} from '../services/api';
import MCPInspectorModal from '../components/MCPInspectorModal';
import StudentProfileModal from '../components/StudentProfileModal';

// Flag điều khiển hiển thị tab 'Thực hành & Kỳ thi' (đặt true khi muốn mở lại tính năng này)
const SHOW_EXAM_SESSIONS = false;

export default function StudentClassDetailPage() {
  const { classId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [currentClass, setCurrentClass] = useState(null);
  const [curriculum, setCurriculum] = useState([]);
  const [examSessions, setExamSessions] = useState([]);
  const [skillRoadmap, setSkillRoadmap] = useState(null);
  const [classProfile, setClassProfile] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Search bài tập trong lớp
  const [exerciseSearchQuery, setExerciseSearchQuery] = useState('');

  // Active Tab: 'curriculum' | 'sessions' | 'roadmap' | 'analytics'
  const [activeTab, setActiveTab] = useState('curriculum');

  // Modals
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const sessionId = user?.username || localStorage.getItem('pytutor_session_id') || 'student';

  const loadClassData = async () => {
    setIsLoading(true);
    try {
      const [allCls, myCls, curr, sessList, roadmap, prof, lb] = await Promise.all([
        fetchClasses().catch(() => []),
        fetchMyClasses().catch(() => []),
        fetchClassCurriculum(classId, sessionId).catch(() => []),
        fetchExamSessions().catch(() => []),
        fetchSkillRoadmap(sessionId, classId).catch(() => null),
        fetchStudentProfile(sessionId, '', classId).catch(() => null),
        fetchLeaderboard().catch(() => [])
      ]);

      const found = (myCls.find(c => c.id === classId)) || (allCls.find(c => c.id === classId)) || null;
      setCurrentClass(found);
      setCurriculum(curr || []);
      // Lọc kỳ thi của lớp này
      const classSessions = (sessList || []).filter(s => !s.class_id || s.class_id === classId);
      setExamSessions(classSessions);
      setSkillRoadmap(roadmap);
      setClassProfile(prof);
      // Đảm bảo an toàn: lb có thể là mảng hoặc object { leaderboard: [...] }
      const safeLeaderboard = Array.isArray(lb) ? lb : (lb?.leaderboard || []);
      setLeaderboard(safeLeaderboard);
    } catch (err) {
      console.error('Lỗi nạp dữ liệu chi tiết lớp học phần:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (classId) {
      loadClassData();
    }
  }, [classId]);

  // Lọc bài tập theo từ khóa tìm kiếm
  const filteredCurriculum = (curriculum || []).filter(item => {
    if (!exerciseSearchQuery.trim()) return true;
    const q = exerciseSearchQuery.toLowerCase();
    return (
      (item.title && item.title.toLowerCase().includes(q)) ||
      (item.exercise_id && item.exercise_id.toLowerCase().includes(q)) ||
      (item.skill_tag && item.skill_tag.toLowerCase().includes(q)) ||
      (item.module_name && item.module_name.toLowerCase().includes(q)) ||
      (item.difficulty && item.difficulty.toLowerCase().includes(q))
    );
  });

  // Gom nhóm Curriculum theo Module
  const modulesMap = {};
  filteredCurriculum.forEach(item => {
    const mod = item.module_name || 'Học phần chung';
    if (!modulesMap[mod]) modulesMap[mod] = [];
    modulesMap[mod].push(item);
  });
  // Sắp xếp bài tập trong mỗi module theo order_idx
  Object.keys(modulesMap).forEach(mod => {
    modulesMap[mod].sort((a, b) => (a.order_idx || 0) - (b.order_idx || 0));
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans select-none flex flex-col">
      {/* 1. TOP NAVBAR & BREADCRUMB */}
      <header className="sticky top-0 z-30 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => navigate('/student')}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all flex items-center space-x-1 text-xs cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="hidden sm:inline">Về Cổng Sinh Viên</span>
          </button>

          <div className="h-5 w-px bg-slate-800" />

          {/* Breadcrumb */}
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-400 hover:text-slate-300 cursor-pointer" onClick={() => navigate('/student')}>
              Cổng Sinh viên
            </span>
            <span className="text-slate-600">/</span>
            <span className="font-semibold text-emerald-400 flex items-center space-x-1.5">
              <School className="w-3.5 h-3.5" />
              <span>{currentClass ? `${currentClass.class_code} - ${currentClass.class_name}` : 'Không gian Lớp học phần'}</span>
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsProfileOpen(true)}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-medium text-amber-400 transition-all flex items-center space-x-1.5 cursor-pointer"
          >
            <Award className="w-3.5 h-3.5" />
            <span>Năng lực 4D</span>
          </button>

          <button
            onClick={() => setIsInspectorOpen(true)}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-mono text-emerald-400 transition-all flex items-center space-x-1.5 cursor-pointer"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>MCP (8)</span>
          </button>
        </div>
      </header>

      {/* 2. CLASS HERO BANNER */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/60 border-b border-slate-800 px-6 py-6 sm:px-12">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center space-x-2 text-xs">
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono font-semibold">
                {currentClass?.class_code || 'CNTT1116'}
              </span>
              <span className="text-slate-400 font-medium">• {currentClass?.credits || 3} Tín chỉ</span>
              <span className="text-slate-400 font-medium">• {currentClass?.semester || 'HK1 (2026-2027)'}</span>
              <span className="text-slate-400 font-medium">• Khoa CNTT - NEU</span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {currentClass?.class_name || 'Lớp Học Phần Lập Trình Python'}
            </h1>

            <p className="text-xs sm:text-sm text-slate-300 flex items-center space-x-4">
              <span>👨‍🏫 Giảng viên: <strong>{currentClass?.instructor_name || 'Nguyễn Văn A'}</strong></span>
              <span>• Mã tham gia: <strong className="text-emerald-400 font-mono">{currentClass?.enrollment_code}</strong></span>
            </p>
          </div>

          {/* Tiến độ tổng quan lớp */}
          {currentClass && (
            <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 shrink-0 w-full md:w-64 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Tiến độ học phần</span>
                <span className="font-bold text-emerald-400">
                  {currentClass.completed_in_class ?? currentClass.progress?.solved_count ?? 0}/{currentClass.exercise_count ?? currentClass.progress?.total_exercises ?? curriculum.length} bài ({Math.round(currentClass.progress_percent ?? currentClass.progress?.progress_percent ?? 0)}%)
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full"
                  style={{ width: `${Math.max(5, currentClass.progress_percent ?? currentClass.progress?.progress_percent ?? 0)}%` }}
                />
              </div>
              <div className="text-[10px] text-slate-400 text-right">
                Tích lũy: {curriculum.reduce((sum, item) => sum + (item.stars_earned || 0), 0)} ⭐ tự lực
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 3. TABS NAVIGATION */}
      <div className="bg-slate-900 border-b border-slate-800 px-6">
        <div className="max-w-7xl mx-auto flex items-center space-x-1 sm:space-x-2 overflow-x-auto py-2">
          <button
            onClick={() => setActiveTab('curriculum')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center space-x-2 cursor-pointer shrink-0 ${
              activeTab === 'curriculum'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>1. Chương Trình & Bài Tập ({curriculum.length})</span>
          </button>

          {SHOW_EXAM_SESSIONS && (
            <button
              onClick={() => setActiveTab('sessions')}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center space-x-2 cursor-pointer shrink-0 ${
                activeTab === 'sessions'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Calendar className="w-3.5 h-3.5" />
              <span>2. Thực Hành & Kỳ Thi ({examSessions.length})</span>
            </button>
          )}

          <button
            onClick={() => setActiveTab('roadmap')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center space-x-2 cursor-pointer shrink-0 ${
              activeTab === 'roadmap'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>{SHOW_EXAM_SESSIONS ? '3. Cây Kỹ Năng & Chuẩn Sao' : '2. Cây Kỹ Năng & Chuẩn Sao'}</span>
          </button>

          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center space-x-2 cursor-pointer shrink-0 ${
              activeTab === 'analytics'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Trophy className="w-3.5 h-3.5" />
            <span>{SHOW_EXAM_SESSIONS ? '4. Bảng Vàng & Đánh Giá Năng Lực' : '3. Bảng Vàng & Đánh Giá Năng Lực'}</span>
          </button>
        </div>
      </div>

      {/* 4. MAIN TAB CONTENT */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {isLoading ? (
          <div className="p-16 text-center text-slate-500 text-sm">Đang tải học liệu lớp học phần...</div>
        ) : (
          <>
            {/* TAB 1: CHƯƠNG TRÌNH & BÀI TẬP */}
            {activeTab === 'curriculum' && (
              <div className="space-y-6">
                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Info className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>
                      Lộ trình bài tập được thiết kế tuần tự. Mỗi bài tập yêu cầu đạt chuẩn số Sao Tự Lực (Mastery Rubric) tối thiểu để mở khóa bài tiếp theo.
                    </span>
                  </div>
                  <div className="text-slate-400 hidden sm:block">
                    Tổng số: <strong>{curriculum.length} bài tập</strong>
                  </div>
                </div>

                {/* Search Bar cho Bài Tập trong Lớp */}
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="relative flex-1">
                    <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-2.5" />
                    <input
                      type="text"
                      value={exerciseSearchQuery}
                      onChange={(e) => setExerciseSearchQuery(e.target.value)}
                      placeholder="Tìm kiếm bài tập theo tên bài, kỹ năng (skill tag), độ khó, mã bài..."
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-9 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all font-sans"
                    />
                    {exerciseSearchQuery && (
                      <button
                        onClick={() => setExerciseSearchQuery('')}
                        className="absolute right-3 top-2 text-xs text-slate-400 hover:text-white cursor-pointer px-1.5 py-0.5 rounded bg-slate-800"
                        title="Xóa tìm kiếm"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                  <div className="text-xs text-slate-400 shrink-0 font-medium px-2">
                    {exerciseSearchQuery ? (
                      <span>Khớp: <strong className="text-emerald-400">{filteredCurriculum.length}</strong>/{curriculum.length} bài</span>
                    ) : (
                      <span>Tổng: <strong className="text-emerald-400">{curriculum.length}</strong> bài tập</span>
                    )}
                  </div>
                </div>

                {curriculum.length === 0 ? (
                  <div className="p-12 text-center text-slate-500 text-sm bg-slate-900/40 rounded-xl border border-dashed border-slate-800">
                    Giảng viên phụ trách chưa gán bài tập nào vào lộ trình lớp này.
                  </div>
                ) : filteredCurriculum.length === 0 ? (
                  <div className="p-10 text-center text-slate-400 text-xs bg-slate-900/40 rounded-xl border border-dashed border-slate-800 space-y-2">
                    <p>Không tìm thấy bài tập nào khớp với từ khóa "{exerciseSearchQuery}".</p>
                    <button
                      onClick={() => setExerciseSearchQuery('')}
                      className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-emerald-400 rounded-lg transition-colors cursor-pointer"
                    >
                      Xóa bộ lọc
                    </button>
                  </div>
                ) : (
                  Object.keys(modulesMap).map((moduleName, modIdx) => (
                    <div key={modIdx} className="space-y-3">
                      <div className="flex items-center space-x-2.5">
                        <span className="w-6 h-6 rounded-md bg-emerald-500/10 text-emerald-400 font-mono text-xs flex items-center justify-center font-bold">
                          {modIdx + 1}
                        </span>
                        <h3 className="font-bold text-sm text-white">{moduleName}</h3>
                        <span className="text-xs text-slate-500 font-mono">({modulesMap[moduleName].length} bài)</span>
                      </div>

                      <div className="space-y-2.5">
                        {modulesMap[moduleName].map((item) => {
                          const minStars = item.min_stars_required || 1;
                          const earnedStars = item.stars_earned || 0;
                          const isMastered = item.status === 'MASTERED';
                          const isNeedsMoreStars = item.status === 'NEEDS_MORE_STARS';
                          const isLocked = item.status === 'LOCKED';
                          const isAvailable = item.status === 'AVAILABLE' || item.status === 'IN_PROGRESS';

                          // Trạng thái badge
                          let statusBadge = (
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-blue-500/10 text-blue-300 border border-blue-500/20">
                              Sẵn sàng làm bài
                            </span>
                          );
                          if (isMastered) {
                            statusBadge = (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center space-x-1">
                                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                                <span>Đã đạt chuẩn ({earnedStars} ⭐)</span>
                              </span>
                            );
                          } else if (isNeedsMoreStars) {
                            statusBadge = (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center space-x-1">
                                <AlertTriangle className="w-3 h-3 text-amber-400" />
                                <span>Cần nâng sao ({earnedStars}/{minStars} ⭐)</span>
                              </span>
                            );
                          } else if (isLocked) {
                            statusBadge = (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-500 border border-slate-700 flex items-center space-x-1">
                                <Lock className="w-3 h-3" />
                                <span>Khóa (Yêu cầu bài trước)</span>
                              </span>
                            );
                          }

                          return (
                            <div
                              key={item.id}
                              className={`p-4 rounded-xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                                isMastered 
                                  ? 'bg-slate-900/90 border-emerald-500/30 shadow-sm'
                                  : isLocked
                                  ? 'bg-slate-950/40 border-slate-800/60 opacity-60'
                                  : 'bg-slate-900/90 border-slate-800 hover:border-slate-700 shadow-md'
                              }`}
                            >
                              <div className="flex items-start space-x-3">
                                <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5 ${
                                  isMastered 
                                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                    : isLocked
                                    ? 'bg-slate-800 text-slate-500'
                                    : 'bg-slate-800 text-slate-300 border border-slate-700'
                                }`}>
                                  #{item.order_idx || 1}
                                </div>

                                <div className="space-y-1">
                                  <div className="flex items-center space-x-2">
                                    <h4 className="text-sm font-bold text-white hover:text-emerald-300 transition-colors">
                                      {item.title}
                                    </h4>
                                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                                      {item.skill_tag || 'Tổng quan'}
                                    </span>
                                  </div>

                                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-400">
                                    <span>Độ khó: <strong className="text-slate-300">{item.difficulty}</strong></span>
                                    <span>• Chuẩn đầu ra: <strong className="text-amber-400">Tối thiểu {minStars} ⭐</strong></span>
                                    {item.prerequisite_id && (
                                      <span className="text-slate-500 font-mono">• Tiên quyết: {item.prerequisite_id}</span>
                                    )}
                                  </div>
                                </div>
                              </div>

                              <div className="flex items-center space-x-3 self-end sm:self-center shrink-0">
                                {statusBadge}

                                <button
                                  onClick={() => {
                                    if (!isLocked) {
                                      navigate(`/student/ide/${item.exercise_id}?classId=${classId}`);
                                    }
                                  }}
                                  disabled={isLocked}
                                  className={`py-2 px-4 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer ${
                                    isLocked
                                      ? 'bg-slate-800 text-slate-600 border border-slate-700 cursor-not-allowed'
                                      : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-950'
                                  }`}
                                >
                                  <span>💻 Làm bài trên IDE</span>
                                  <Play className="w-3 h-3 fill-current" />
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* TAB: ĐỢT THỰC HÀNH & KỲ THI (Tạm ẩn theo yêu cầu) */}
            {SHOW_EXAM_SESSIONS && activeTab === 'sessions' && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 flex items-center space-x-2">
                  <Info className="w-4 h-4 text-blue-400 shrink-0" />
                  <span>
                    Chế độ <strong>Luyện tập (PRACTICE)</strong> cho phép trò chuyện với Gia sư AI. Chế độ <strong>Kỳ thi (EXAM)</strong> sẽ khóa tuyệt đối Gia sư AI và đếm ngược thời gian làm bài để bảo đảm công bằng.
                  </span>
                </div>

                {examSessions.length === 0 ? (
                  <div className="p-12 text-center text-slate-500 text-sm bg-slate-900/40 rounded-xl border border-dashed border-slate-800">
                    Hiện chưa có đợt thực hành hoặc kỳ thi nào được lên lịch cho lớp này.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {examSessions.map((sess) => {
                      const isExam = sess.session_type === 'EXAM';
                      const firstEx = (sess.exercise_ids && sess.exercise_ids.length > 0) ? sess.exercise_ids[0] : 'ex_01_sum_1_to_n';

                      return (
                        <div
                          key={sess.id}
                          className={`p-5 rounded-2xl border transition-all flex flex-col justify-between space-y-4 ${
                            isExam 
                              ? 'bg-gradient-to-br from-slate-900 to-rose-950/30 border-rose-500/30' 
                              : 'bg-gradient-to-br from-slate-900 to-emerald-950/30 border-slate-800'
                          }`}
                        >
                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase ${
                                isExam 
                                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' 
                                  : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                              }`}>
                                {isExam ? '🔒 KỲ THI / KIỂM TRA TÍN CHỈ' : '🎯 ĐỢT THỰC HÀNH TỰ DO'}
                              </span>

                              <span className="text-xs text-slate-400 flex items-center space-x-1">
                                <Clock className="w-3.5 h-3.5" />
                                <span>{sess.duration_minutes || 45} phút</span>
                              </span>
                            </div>

                            <h3 className="text-base font-bold text-white">{sess.title}</h3>
                            <p className="text-xs text-slate-400">
                              Bao gồm <strong>{sess.exercise_ids?.length || 0} bài tập</strong> được chọn lọc từ ngân hàng đề.
                            </p>

                            <div className="flex flex-wrap gap-1.5 pt-1">
                              {sess.exercise_ids?.map(eid => (
                                <span key={eid} className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-slate-300">
                                  {eid}
                                </span>
                              ))}
                            </div>
                          </div>

                          <div className="pt-2 border-t border-slate-800/80">
                            <button
                              onClick={() => navigate(`/student/ide/${firstEx}?classId=${classId}&sessionId=${sess.id}`)}
                              className={`w-full py-2.5 px-4 rounded-xl text-xs font-semibold flex items-center justify-center space-x-2 transition-all cursor-pointer ${
                                isExam
                                  ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-md shadow-rose-950'
                                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-950'
                              }`}
                            >
                              <span>{isExam ? '🚀 Vào Phòng Thi Tín Chỉ' : '💻 Bắt Đầu Thực Hành'}</span>
                              <ArrowRight className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: CÂY KỸ NĂNG HỌC PHẦN */}
            {activeTab === 'roadmap' && (
              <div className="space-y-6">
                {/* Giải thích Thang đo định lượng (Mastery Rubric) */}
                <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
                  <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                    <Target className="w-4 h-4 text-emerald-400" />
                    <span>Quy Chuẩn Thang Đo Năng Lực (Mastery Rubric NEU)</span>
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                    <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/20 space-y-1">
                      <div className="font-semibold text-emerald-400 flex items-center space-x-1">
                        <span>⭐⭐⭐ 3 Sao (Tự lực hoàn toàn)</span>
                      </div>
                      <p className="text-slate-400 text-[11px]">Pass 100% test cases mà không dùng gợi ý tầng 2-3 và không tra cứu code giải.</p>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-950 border border-blue-500/20 space-y-1">
                      <div className="font-semibold text-blue-400 flex items-center space-x-1">
                        <span>⭐⭐ 2 Sao (Gợi mở sư phạm)</span>
                      </div>
                      <p className="text-slate-400 text-[11px]">Pass test cases sau khi nhận gợi ý định hướng thuật toán tầng 1-2 từ Gia sư AI.</p>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-950 border border-amber-500/20 space-y-1">
                      <div className="font-semibold text-amber-400 flex items-center space-x-1">
                        <span>⭐ 1 Sao (Cần hướng dẫn chi tiết)</span>
                      </div>
                      <p className="text-slate-400 text-[11px]">Cần mở gợi ý tầng 3 hoặc hỏi đáp nhiều lượt mới hoàn thành bài tập.</p>
                    </div>
                  </div>
                </div>

                {/* Sơ đồ cây kỹ năng DAG */}
                <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-bold text-white">Bản Đồ Kỹ Năng Đồ Thị Định Hướng (DAG Matrix)</h4>
                      <p className="text-xs text-slate-400">Bấm vào bất kỳ node nào đã mở khóa để vào thẳng IDE làm bài</p>
                    </div>
                    <span className="text-xs text-emerald-400 font-mono font-semibold">
                      {skillRoadmap?.total_mastered ?? skillRoadmap?.mastered_count ?? 0}/{skillRoadmap?.total_exercises ?? skillRoadmap?.total_nodes ?? 0} Đã Làm Chủ
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
                    {skillRoadmap?.nodes?.map((node) => {
                      const isMastered = node.status === 'MASTERED';
                      const isNeedsMoreStars = node.status === 'NEEDS_MORE_STARS';
                      const isLocked = node.status === 'LOCKED';
                      const isAvailable = node.status === 'AVAILABLE' || node.status === 'IN_PROGRESS';

                      return (
                        <div
                          key={node.id}
                          onClick={() => {
                            if (!isLocked) {
                              navigate(`/student/ide/${node.id}?classId=${classId}`);
                            }
                          }}
                          className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2.5 ${
                            isMastered
                              ? 'bg-emerald-950/20 border-emerald-500/40 hover:border-emerald-400'
                              : isNeedsMoreStars
                              ? 'bg-amber-950/20 border-amber-500/40 hover:border-amber-400'
                              : isLocked
                              ? 'bg-slate-950/40 border-slate-800/80 opacity-50 cursor-not-allowed'
                              : 'bg-slate-950/80 border-blue-500/30 hover:border-blue-400 shadow-md'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 font-mono text-slate-300">
                              {node.skill_tag}
                            </span>
                            {isMastered && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                            {isNeedsMoreStars && <AlertTriangle className="w-4 h-4 text-amber-400" />}
                            {isLocked && <Lock className="w-4 h-4 text-slate-500" />}
                            {isAvailable && <Play className="w-3.5 h-3.5 text-blue-400 fill-blue-400" />}
                          </div>

                          <h5 className="font-bold text-sm text-white line-clamp-1">{node.title}</h5>

                          <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-800/60">
                            <span className="text-slate-400">Chuẩn: <strong>{node.min_stars_required || 1} ⭐</strong></span>
                            <span className="text-amber-400 font-semibold">Đạt: {node.stars_earned || 0} ⭐</span>
                          </div>

                          <div className="text-[11px] text-slate-400 font-medium">
                            {node.status_description || node.unlock_message}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 4: BẢNG VÀNG & ĐÁNH GIÁ NĂNG LỰC */}
            {activeTab === 'analytics' && (() => {
              const am = classProfile?.analytics_metrics || {};
              const diag = classProfile?.diagnostic_evaluation || {};
              const autonomyScore = am.autonomy_score !== undefined ? am.autonomy_score : (classProfile?.autonomy_score ?? 70);
              const firstTryPassRate = am.first_try_pass_rate !== undefined ? am.first_try_pass_rate : (classProfile?.first_try_pass_rate ?? 0);
              const avgAttempts = am.avg_attempts_to_solve !== undefined ? am.avg_attempts_to_solve : (classProfile?.avg_attempts_to_solve ?? 0);
              const strengths = diag.strengths_analysis || classProfile?.strengths_analysis || 'Chưa đủ dữ liệu nộp bài để phân tích điểm mạnh.';
              const weaknesses = diag.weaknesses_and_bottlenecks || classProfile?.weaknesses_and_bottlenecks || 'Chưa ghi nhận điểm nghẽn nghiêm trọng.';
              const recommendations = diag.recommended_next_action || classProfile?.recommended_next_action || 'Tiếp tục hoàn thành các bài tập trong lộ trình học phần.';
              const safeLb = Array.isArray(leaderboard) ? leaderboard : (leaderboard?.leaderboard || []);

              return (
                <div className="space-y-6">
                  {/* 4 Thẻ KPI của riêng lớp này */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                      <div className="text-xs text-slate-400 mb-1">Chỉ số Tự lực (Autonomy)</div>
                      <div className="text-2xl font-bold text-purple-400">{autonomyScore}<span className="text-sm font-normal text-slate-400">/100</span></div>
                      <div className="text-[11px] text-slate-500 mt-1">Đo lường tính độc lập</div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                      <div className="text-xs text-slate-400 mb-1">Vượt qua lần đầu</div>
                      <div className="text-2xl font-bold text-emerald-400">{firstTryPassRate}%</div>
                      <div className="text-[11px] text-slate-500 mt-1">First-try pass rate</div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                      <div className="text-xs text-slate-400 mb-1">Số lần thử trung bình</div>
                      <div className="text-2xl font-bold text-blue-400">{avgAttempts}</div>
                      <div className="text-[11px] text-slate-500 mt-1">Số lần nộp/bài đã giải</div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                      <div className="text-xs text-slate-400 mb-1">Tổng Sao Tự Lực Lớp</div>
                      <div className="text-2xl font-bold text-amber-400">{curriculum.reduce((sum, item) => sum + (item.stars_earned || 0), 0)} ⭐</div>
                      <div className="text-[11px] text-slate-500 mt-1">Tích lũy từ bài tập</div>
                    </div>
                  </div>

                  {/* 3 Thẻ Chẩn đoán sư phạm tự động */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-5 rounded-2xl bg-slate-900 border border-emerald-500/20 space-y-2">
                      <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>Điểm Mạnh Nổi Bật</span>
                      </h4>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {strengths}
                      </p>
                    </div>

                    <div className="p-5 rounded-2xl bg-slate-900 border border-amber-500/20 space-y-2">
                      <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center space-x-1.5">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        <span>Điểm Nghẽn Cần Khắc Phục</span>
                      </h4>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {weaknesses}
                      </p>
                    </div>

                    <div className="p-5 rounded-2xl bg-slate-900 border border-blue-500/20 space-y-2">
                      <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center space-x-1.5">
                        <Target className="w-3.5 h-3.5" />
                        <span>Khuyến Nghị Hành Động Kế Tiếp</span>
                      </h4>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {recommendations}
                      </p>
                    </div>
                  </div>

                  {/* Bảng Vàng Lớp Học */}
                  <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Trophy className="w-4 h-4 text-amber-400" />
                        <h4 className="text-sm font-bold text-white">Bảng Xếp Hạng Thành Tích Lớp Học Phần</h4>
                      </div>
                      <span className="text-xs text-slate-400">Xếp hạng theo Sao Tự Lực & Bài đã giải</span>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead>
                          <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                            <th className="py-2.5 px-3">Hạng</th>
                            <th className="py-2.5 px-3">Sinh viên</th>
                            <th className="py-2.5 px-3 text-center">Bài đã giải</th>
                            <th className="py-2.5 px-3 text-center">Sao tự lực (⭐)</th>
                            <th className="py-2.5 px-3 text-right">Điểm Clean Code</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60">
                          {safeLb.length === 0 ? (
                            <tr>
                              <td colSpan={5} className="py-6 text-center text-slate-500">
                                Chưa có dữ liệu bảng xếp hạng cho học kỳ này.
                              </td>
                            </tr>
                          ) : (
                            safeLb.slice(0, 10).map((row, idx) => (
                              <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                                <td className="py-3 px-3 font-mono font-bold">
                                  {idx === 0 ? '🥇 1' : idx === 1 ? '🥈 2' : idx === 2 ? '🥉 3' : `#${idx + 1}`}
                                </td>
                                <td className="py-3 px-3">
                                  <div className="font-semibold text-white">{row.full_name || row.username || row.session_id}</div>
                                  <div className="text-[10px] text-slate-500 font-mono">@{row.username || row.session_id}</div>
                                </td>
                                <td className="py-3 px-3 text-center font-bold text-emerald-400">
                                  {row.completed_exercises || 0}
                                </td>
                                <td className="py-3 px-3 text-center font-bold text-amber-400">
                                  {row.total_stars || 0} ⭐
                                </td>
                                <td className="py-3 px-3 text-right font-mono text-purple-400">
                                  {row.highest_clean_score || 0}/100
                                </td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              );
            })()}
          </>
        )}
      </main>

      {/* MODALS */}
      {isProfileOpen && (
        <StudentProfileModal
          isOpen={isProfileOpen}
          onClose={() => setIsProfileOpen(false)}
          sessionId={sessionId}
          classId={classId}
        />
      )}

      {isInspectorOpen && (
        <MCPInspectorModal
          isOpen={isInspectorOpen}
          onClose={() => setIsInspectorOpen(false)}
        />
      )}
    </div>
  );
}
