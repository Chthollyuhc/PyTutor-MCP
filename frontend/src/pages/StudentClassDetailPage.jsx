import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  School, BookOpen, Calendar, Award, Trophy, ChevronRight, 
  Lock, CheckCircle2, Star, ArrowLeft, AlertTriangle, 
  Play, Sparkles, TrendingUp, Info, RefreshCw, Clock, ArrowRight, RotateCcw,
  ShieldAlert, Layers, CheckSquare, Target, Search
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import ThemeToggle from '../components/ThemeToggle';
import { Badge, Button, Stat } from '../components/ui';
import { toneIndex, difficultyVariant } from '../utils/tone';
import { 
  fetchClasses, 
  fetchMyClasses, 
  fetchClassCurriculum, 
  fetchExamSessions, 
  fetchStudentProfile, 
  fetchLeaderboard 
} from '../services/api';
import StudentProfileModal from '../components/StudentProfileModal';
import { rememberLastClassId } from '../utils/lastClass';

// Flag điều khiển hiển thị tab 'Thực hành & Kỳ thi' (đặt true khi muốn mở lại tính năng này)
const SHOW_EXAM_SESSIONS = false;

export default function StudentClassDetailPage() {
  const { classId } = useParams();
  const navigate = useNavigate();
  useEffect(() => { rememberLastClassId(classId); }, [classId]);
  const { user } = useAuth();

  const [currentClass, setCurrentClass] = useState(null);
  const [myClassList, setMyClassList] = useState([]);
  const [curriculum, setCurriculum] = useState([]);
  const [examSessions, setExamSessions] = useState([]);
  const [classProfile, setClassProfile] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Search bài tập trong lớp
  const [exerciseSearchQuery, setExerciseSearchQuery] = useState('');

  // Active Tab: 'curriculum' | 'sessions' | 'analytics'
  const [activeTab, setActiveTab] = useState('curriculum');

  // Modals
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const sessionId = user?.username || localStorage.getItem('pytutor_session_id') || 'student';

  const loadClassData = async () => {
    setIsLoading(true);
    try {
      const [allCls, myCls, curr, sessList, prof, lb] = await Promise.all([
        fetchClasses().catch(() => []),
        fetchMyClasses().catch(() => []),
        fetchClassCurriculum(classId, sessionId).catch(() => []),
        fetchExamSessions().catch(() => []),
        fetchStudentProfile(sessionId, '', classId).catch(() => null),
        fetchLeaderboard().catch(() => [])
      ]);

      const found = (myCls.find(c => c.id === classId)) || (allCls.find(c => c.id === classId)) || null;
      setCurrentClass(found);
      setMyClassList(myCls || []);
      setCurriculum(curr || []);
      // Lọc kỳ thi của lớp này
      const classSessions = (sessList || []).filter(s => !s.class_id || s.class_id === classId);
      setExamSessions(classSessions);
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

  const totalClassStars = curriculum.reduce((sum, item) => sum + (item.stars_earned || 0), 0);
  const solvedInClass = currentClass?.completed_in_class ?? currentClass?.progress?.solved_count ?? 0;
  const totalInClass = currentClass?.exercise_count ?? currentClass?.progress?.total_exercises ?? curriculum.length;
  const classPct = Math.round(currentClass?.progress_percent ?? currentClass?.progress?.progress_percent ?? 0);
  const tone = toneIndex(myClassList, classId);

  const tabs = [
    { id: 'curriculum', label: `Chương trình & bài tập (${curriculum.length})`, Icon: BookOpen },
    ...(SHOW_EXAM_SESSIONS ? [{ id: 'sessions', label: `Thực hành & kỳ thi (${examSessions.length})`, Icon: Calendar }] : []),
    { id: 'analytics', label: 'Bảng xếp hạng & năng lực', Icon: Trophy },
  ];

  return (
    <div className={`tone-${tone} flex min-h-screen flex-col bg-canvas text-foreground`}>
      {/* 1. Thanh điều hướng + thông tin lớp trên nền màu của lớp */}
      <div className="on-brand bg-tone text-on-solid">
        <header className="sticky top-0 z-30 border-b border-header-foreground/20 bg-tone">
          <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6">
            <div className="flex min-w-0 items-center gap-3">
              <Button variant="onBrand" size="sm" onClick={() => navigate('/student')} aria-label="Về Cổng Sinh viên" className="min-h-10 shrink-0 px-2.5 sm:px-3">
                <ArrowLeft aria-hidden="true" className="size-4" />
                <span className="hidden sm:inline">Cổng Sinh viên</span>
              </Button>
              <nav aria-label="Breadcrumb" className="min-w-0">
                <ol className="flex min-w-0 items-center gap-2 text-sm">
                  <li className="hidden md:block"><button type="button" onClick={() => navigate('/student')} className="hover:underline">Cổng Sinh viên</button></li>
                  <li aria-hidden="true" className="hidden md:block">/</li>
                  <li aria-current="page" className="min-w-0 truncate font-semibold">
                    {currentClass ? `${currentClass.class_code} · ${currentClass.class_name}` : 'Lớp học phần'}
                  </li>
                </ol>
              </nav>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <ThemeToggle variant="onBrand" />
              <Button variant="onBrand" size="sm" onClick={() => setIsProfileOpen(true)} aria-label="Mở hồ sơ học tập" className="min-h-10">
                <Award aria-hidden="true" className="size-4" />
                <span className="hidden lg:inline">Hành trình học</span>
              </Button>
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-7xl px-4 pt-6 sm:px-6">
          <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
            <div className="min-w-0">
              <p className="flex flex-wrap gap-x-3 gap-y-1 text-[0.8125rem] font-semibold">
                <span className="font-mono">{currentClass?.class_code || 'CNTT1116'}</span>
                <span>{currentClass?.credits || 3} tín chỉ</span>
                <span>{currentClass?.semester || 'HK1 (2026-2027)'}</span>
                <span>Khoa CNTT · NEU</span>
              </p>
              <h1 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">
                {currentClass?.class_name || 'Lớp Học Phần Lập Trình Python'}
              </h1>
              <p className="mt-2 flex flex-wrap items-center gap-x-5 gap-y-1 text-sm">
                <span>Giảng viên <strong className="font-bold">{currentClass?.instructor_name || 'Nguyễn Văn A'}</strong></span>
                <span>Mã tham gia <span className="rounded bg-header-foreground/20 px-1.5 py-0.5 font-mono font-semibold">{currentClass?.enrollment_code}</span></span>
              </p>
            </div>

            {currentClass && (
              <div className="w-full shrink-0 space-y-2 rounded-xl bg-header-foreground/15 p-4 md:w-72">
                <p className="flex items-center justify-between text-sm font-semibold">
                  <span>Tiến độ học phần</span>
                  <span className="tabular-nums">{solvedInClass}/{totalInClass} bài · {classPct}%</span>
                </p>
                <div role="progressbar" aria-label="Tiến độ học phần" aria-valuemin={0} aria-valuemax={100} aria-valuenow={classPct} className="h-2.5 overflow-hidden rounded-full bg-header-foreground/25">
                  <div className="h-full rounded-full bg-header-foreground" style={{ width: `${classPct}%` }} />
                </div>
                <p className="flex items-center justify-end gap-1 text-[0.8125rem] font-medium">
                  <Star aria-hidden="true" className="size-3.5" />
                  {totalClassStars} sao đã nhận
                </p>
              </div>
            )}
          </div>

          <div role="tablist" aria-label="Nội dung lớp học phần" className="mt-6 inline-flex p-1 bg-header-foreground/15 rounded-full overflow-x-auto gap-1">
            {tabs.map(({ id, label, Icon }) => (
              <button
                key={id}
                type="button"
                role="tab"
                id={`tab-${id}`}
                aria-selected={activeTab === id}
                aria-controls={`panel-${id}`}
                onClick={() => setActiveTab(id)}
                className={`inline-flex min-h-9 shrink-0 items-center gap-2 rounded-full px-4 text-xs font-semibold transition-all ${
                  activeTab === id ? 'bg-surface text-foreground shadow-sm' : 'text-on-solid hover:bg-header-foreground/20'
                }`}
              >
                <Icon aria-hidden="true" className="size-3.5" />
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 2. Nội dung tab */}
      <main id={`panel-${activeTab}`} role="tabpanel" aria-labelledby={`tab-${activeTab}`} className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6">
        {isLoading ? (
          <p role="status" className="py-16 text-center text-sm text-muted">Đang tải học liệu lớp học phần…</p>
        ) : (
          <>
            {activeTab === 'curriculum' && (
              <div className="space-y-8">
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <p className="flex max-w-2xl items-start gap-2 rounded-lg border border-info-line bg-info-soft px-3 py-2 text-sm text-info-strong">
                    <Info aria-hidden="true" className="mt-0.5 size-4 shrink-0" />
                    Hoàn thành bài tiên quyết để mở khóa bài tiếp theo. Sao tự lực ghi nhận mức độ độc lập khi giải bài, không ảnh hưởng đến quyền truy cập.
                  </p>
                  <div className="relative w-full md:w-80">
                    <label htmlFor="exercise-search" className="sr-only">Tìm bài tập trong lớp</label>
                    <Search aria-hidden="true" className="pointer-events-none absolute left-4 top-1/2 size-4 -translate-y-1/2 text-muted" />
                    <input
                      id="exercise-search"
                      type="search"
                      value={exerciseSearchQuery}
                      onChange={(e) => setExerciseSearchQuery(e.target.value)}
                      placeholder="Tìm theo tên bài, kỹ năng, độ khó"
                      className="min-h-11 w-full rounded-full border border-border/80 bg-surface pl-11 pr-4 text-sm text-foreground placeholder:text-muted/60 outline-none shadow-soft focus:border-primary focus:ring-2 focus:ring-primary/20"
                    />
                  </div>
                </div>
                <p aria-live="polite" className="sr-only">
                  {exerciseSearchQuery ? `${filteredCurriculum.length} trên ${curriculum.length} bài khớp` : ''}
                </p>

                {curriculum.length === 0 ? (
                  <p className="rounded-3xl border-2 border-dashed border-border bg-surface px-6 py-12 text-center text-sm text-muted">
                    Giảng viên phụ trách chưa gán bài tập nào vào lộ trình lớp này.
                  </p>
                ) : filteredCurriculum.length === 0 ? (
                  <div className="rounded-3xl border-2 border-dashed border-border bg-surface px-6 py-10 text-center">
                    <p className="text-sm">Không có bài tập nào khớp với “{exerciseSearchQuery}”.</p>
                    <Button variant="secondary" size="sm" className="mt-4" onClick={() => setExerciseSearchQuery('')}>Xóa từ khóa</Button>
                  </div>
                ) : (
                  Object.keys(modulesMap).map((moduleName, modIdx) => (
                    <section key={moduleName} aria-labelledby={`module-${modIdx}`} className="space-y-3">
                      <h2 id={`module-${modIdx}`} className="flex items-center gap-3 text-lg font-bold">
                        <span aria-hidden="true" className="flex size-8 shrink-0 items-center justify-center rounded-full bg-slate-950 text-white dark:bg-emerald-500 text-xs font-bold">{modIdx + 1}</span>
                        <span className="min-w-0">{moduleName}</span>
                        <Badge variant="pill">{modulesMap[moduleName].length} bài</Badge>
                      </h2>

                      <ul className="space-y-3">
                        {modulesMap[moduleName].map((item) => {
                          const earnedStars = item.stars_earned || 0;
                          const isMastered = item.status === 'MASTERED';
                          const isLocked = item.status === 'LOCKED';

                          const status = isMastered
                            ? { Icon: CheckCircle2, text: `Đã hoàn thành · ${earnedStars} sao`, variant: 'success' }
                            : isLocked
                              ? { Icon: Lock, text: 'Khóa · cần hoàn thành bài trước', variant: 'neutral' }
                              : { Icon: Play, text: 'Sẵn sàng làm bài', variant: 'info' };

                          return (
                            <li
                              key={item.id}
                              className={`flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6 rounded-2xl border border-border/80 bg-surface shadow-soft hover:shadow-bento transition-all ${
                                isLocked ? 'opacity-70 bg-surface-raised/60' : ''
                              }`}
                            >
                              <div className="flex min-w-0 items-start gap-3.5">
                                <span
                                  aria-hidden="true"
                                  className={`mt-0.5 flex size-10 shrink-0 items-center justify-center rounded-full text-sm font-bold shadow-soft ${
                                    isMastered ? 'bg-emerald-500 text-white' : isLocked ? 'bg-surface-raised text-muted border border-border/80' : 'bg-slate-950 text-white dark:bg-emerald-500'
                                  }`}
                                >
                                  {isMastered ? <CheckCircle2 className="size-5" /> : isLocked ? <Lock className="size-4" /> : (item.order_idx || 1)}
                                </span>
                                <div className="min-w-0">
                                  <h3 className={`text-base font-bold leading-snug ${isLocked ? 'text-muted' : 'text-foreground'}`}>{item.title}</h3>
                                  <p className="mt-1.5 flex flex-wrap items-center gap-1.5">
                                    <Badge variant={difficultyVariant(item.difficulty)}>{item.difficulty}</Badge>
                                    <Badge variant="info">{item.skill_tag || 'Tổng quan'}</Badge>
                                    <Badge variant="warning"><Star aria-hidden="true" className="size-3 fill-amber-400 text-amber-500" />{earnedStars} sao</Badge>
                                    {item.prerequisite_id && <span className="text-[0.8125rem] text-muted">Tiên quyết <span className="font-mono">{item.prerequisite_id}</span></span>}
                                  </p>
                                </div>
                              </div>

                              <div className="flex shrink-0 items-center justify-between gap-4 pl-[3.25rem] sm:pl-0">
                                <Badge variant={status.variant}>
                                  <status.Icon aria-hidden="true" className="size-3.5" />
                                  {status.text}
                                </Badge>
                                <Button
                                  variant={isMastered ? 'black' : 'primary'}
                                  size="sm"
                                  disabled={isLocked}
                                  onClick={() => { if (!isLocked) navigate(`/student/ide/${item.exercise_id}?classId=${classId}`); }}
                                  aria-label={`${isMastered ? 'Ôn lại' : 'Làm bài'} ${item.title} trên IDE`}
                                  className="shadow-soft"
                                >
                                  {isMastered ? (
                                    <>
                                      <RotateCcw aria-hidden="true" className="size-3.5" />
                                      <span>Ôn lại</span>
                                    </>
                                  ) : (
                                    <>
                                      <span>Làm bài</span>
                                      <ArrowRight aria-hidden="true" className="size-4" />
                                    </>
                                  )}
                                </Button>
                              </div>
                            </li>
                          );
                        })}
                      </ul>
                    </section>
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
                                {isExam ? 'KỲ THI / KIỂM TRA TÍN CHỈ' : 'ĐỢT THỰC HÀNH TỰ DO'}
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
                              <span>{isExam ? 'Vào phòng thi tín chỉ' : 'Bắt đầu thực hành'}</span>
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

            {/* TAB 4: BẢNG VÀNG & ĐÁNH GIÁ NĂNG LỰC */}
            {activeTab === 'analytics' && (() => {
              const am = classProfile?.analytics_metrics || {};
              const diag = classProfile?.diagnostic_evaluation || {};
              const dataStatus = classProfile?.data_status || am.data_status || (classProfile?.total_submissions ? 'limited' : 'no_data');
              const autonomyScore = dataStatus === 'no_data' ? null : (am.autonomy_score ?? classProfile?.autonomy_score ?? null);
              const firstTryPassRate = dataStatus === 'no_data' ? null : (am.first_try_pass_rate ?? classProfile?.first_try_pass_rate ?? null);
              const avgAttempts = dataStatus === 'no_data' ? null : (am.avg_attempts_to_solve ?? classProfile?.avg_attempts_to_solve ?? null);
              const strengths = diag.strengths_analysis || classProfile?.strengths_analysis || 'Chưa đủ dữ liệu nộp bài để phân tích điểm mạnh.';
              const weaknesses = diag.weaknesses_and_bottlenecks || classProfile?.weaknesses_and_bottlenecks || 'Chưa ghi nhận điểm nghẽn nghiêm trọng.';
              const safeLb = Array.isArray(leaderboard) ? leaderboard : (leaderboard?.leaderboard || []);

              const rankChip = (idx) => (
                idx === 0 ? 'bg-warning text-on-solid'
                  : idx === 1 ? 'bg-info text-on-solid'
                    : idx === 2 ? 'bg-ai text-on-solid'
                      : 'bg-surface-raised text-foreground'
              );

              return (
                <div className="space-y-8">
                  {dataStatus !== 'sufficient' && (
                    <p role="status" className="flex items-start gap-2 rounded-md border border-warning-line bg-warning-soft px-4 py-3 text-sm font-medium text-warning-strong">
                      <AlertTriangle aria-hidden="true" className="mt-0.5 size-4 shrink-0" />
                      {dataStatus === 'no_data' ? 'Chưa có bài nộp để tính chỉ số tiến độ.' : `Mẫu còn hạn chế: ${am.sample_size ?? classProfile?.total_exercises_attempted ?? 0} bài đã thử; chưa đủ cơ sở kết luận năng lực.`}
                    </p>
                  )}

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    <Stat tone={0} icon={Target} label="Mức tự lực" value={autonomyScore == null ? '—' : `${autonomyScore}/100`} note="Mức độ tự giải bài" />
                    <Stat tone={1} icon={CheckSquare} label="Đạt ngay lần nộp đầu" value={firstTryPassRate == null ? '—' : `${firstTryPassRate}%`} note="Tỷ lệ bài đạt ở lần nộp đầu" />
                    <Stat tone={2} icon={RefreshCw} label="Số lần thử trung bình" value={avgAttempts ?? '—'} note="Số lần nộp / bài đã giải" />
                    <Stat tone={4} icon={Star} label="Tổng sao của lớp" value={totalClassStars} note="Tích lũy từ bài tập" />
                  </div>

                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <section className="space-y-2 rounded-xl border border-success-line bg-success-soft p-5">
                      <h2 className="flex items-center gap-2 text-base font-bold text-success-strong">
                        <span aria-hidden="true" className="flex size-8 items-center justify-center rounded-lg bg-success text-on-solid"><Sparkles className="size-4" /></span>
                        Điểm mạnh nổi bật
                      </h2>
                      <p className="text-sm leading-relaxed text-foreground">{strengths}</p>
                    </section>
                    <section className="space-y-2 rounded-xl border border-warning-line bg-warning-soft p-5">
                      <h2 className="flex items-center gap-2 text-base font-bold text-warning-strong">
                        <span aria-hidden="true" className="flex size-8 items-center justify-center rounded-lg bg-warning text-on-solid"><AlertTriangle className="size-4" /></span>
                        Điểm nghẽn cần khắc phục
                      </h2>
                      <p className="text-sm leading-relaxed text-foreground">{weaknesses}</p>
                    </section>
                  </div>

                  <section aria-labelledby="class-leaderboard" className="space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h2 id="class-leaderboard" className="flex items-center gap-3 text-xl font-bold tracking-tight">
                        <span aria-hidden="true" className="flex size-10 items-center justify-center rounded-lg bg-warning text-on-solid"><Trophy className="size-5" /></span>
                        Bảng xếp hạng lớp học phần
                      </h2>
                      <p className="text-sm text-muted">Xếp theo sao tự lực và số bài đã giải</p>
                    </div>
                    <div className="overflow-x-auto rounded-xl border border-tone-line bg-surface max-md:border-0 max-md:bg-transparent">
                      <table className="table-stack w-full text-left text-sm">
                        <thead>
                          <tr className="bg-tone-soft text-[0.8125rem] text-tone-strong">
                            <th scope="col" className="px-4 py-3 font-bold">Hạng</th>
                            <th scope="col" className="px-4 py-3 font-bold">Sinh viên</th>
                            <th scope="col" className="px-4 py-3 text-right font-bold">Bài đã giải</th>
                            <th scope="col" className="px-4 py-3 text-right font-bold">Sao tự lực</th>
                            <th scope="col" className="px-4 py-3 text-right font-bold">Điểm Clean Code</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                          {safeLb.length === 0 ? (
                            <tr>
                              <td colSpan={5} className="px-4 py-8 text-center text-muted">Chưa có dữ liệu bảng xếp hạng cho học kỳ này.</td>
                            </tr>
                          ) : (
                            safeLb.slice(0, 10).map((row, idx) => (
                              <tr key={idx}>
                                <td className="px-4 py-3"><span className={`inline-flex size-8 items-center justify-center rounded-full text-sm font-bold tabular-nums ${rankChip(idx)}`}>{idx + 1}</span></td>
                                <td className="px-4 py-3">
                                  <span className="block font-semibold">{row.full_name || row.username || row.session_id}</span>
                                  <span className="block font-mono text-[0.8125rem] text-muted">@{row.username || row.session_id}</span>
                                </td>
                                <td className="px-4 py-3 text-right font-semibold tabular-nums">{row.completed_exercises || 0}</td>
                                <td className="px-4 py-3 text-right font-semibold tabular-nums text-warning-strong">{row.total_stars || 0}</td>
                                <td className="px-4 py-3 text-right font-semibold tabular-nums">{row.highest_clean_score || 0}/100</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </section>
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
    </div>
  );
}
