import React, { useCallback, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  School, BookOpen, Sparkles, Award, CheckCircle2, ArrowRight, 
  Plus, LogOut, FileText, Code2, Shield, Calendar, Users, 
  TrendingUp, Star, Clock, AlertCircle, RefreshCw,
  Search, LayoutGrid, List, Trophy, UserRound
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import ThemeToggle from '../components/ThemeToggle';
import { Badge, Button, Card } from '../components/ui';
import { 
  fetchMyClasses, 
  fetchClasses, 
  enrollClassByCode, 
  leaveClass, 
  fetchStudentProfile, 
  fetchExercises,
  fetchExamSessions,
  fetchUserAchievements,
  fetchStudentJourney
} from '../services/api';
import TodayCard from '../components/plain/TodayCard';
import StudentProfileModal from '../components/StudentProfileModal';
import LeaderboardModal from '../components/LeaderboardModal';

// Flag điều khiển hiển thị 'Lịch Thi & Thực Hành' (đặt true khi muốn mở lại tính năng này)
const SHOW_EXAM_SESSIONS = false;

import { readLastClassId } from '../utils/lastClass';

export default function StudentPortalPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [today, setToday] = useState({ loading: true, error: false, data: null });
  const loadToday = useCallback(() => {
    setToday((s) => ({ ...s, loading: true, error: false }));
    fetchStudentJourney(null, '', readLastClassId())
      .then((res) => setToday({ loading: false, error: false, data: res.today || null }))
      .catch(() => setToday({ loading: false, error: true, data: null }));
  }, []);
  useEffect(() => { loadToday(); }, [loadToday]);
  const openExerciseFromToday = (exerciseId, classId) =>
    navigate(`/student/ide/${encodeURIComponent(exerciseId)}${classId ? `?classId=${encodeURIComponent(classId)}` : ''}`);

  const [myClasses, setMyClasses] = useState([]);
  const [allClasses, setAllClasses] = useState([]);
  const [exercises, setExercises] = useState([]);
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Tìm kiếm lớp học phần & Chế độ xem (Lưới vs Cột)
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'list'

  // Enrollment Code input
  const [enrollCode, setEnrollCode] = useState('');
  const [enrollMsg, setEnrollMsg] = useState({ type: '', text: '' });
  const [isEnrolling, setIsEnrolling] = useState(false);

  // Modals
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isLeaderboardOpen, setIsLeaderboardOpen] = useState(false);

  // Dữ liệu mở rộng: Đợt thi tín chỉ và sao tự làm
  const [examSessions, setExamSessions] = useState([]);
  const [achievements, setAchievements] = useState(null);

  const sessionId = user?.username || localStorage.getItem('pytutor_session_id') || 'student';

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [myCls, allCls, exList, prof, achs, sessions] = await Promise.all([
        fetchMyClasses().catch(() => []),
        fetchClasses().catch(() => []),
        fetchExercises().catch(() => []),
        fetchStudentProfile(sessionId).catch(() => null),
        fetchUserAchievements(sessionId).catch(() => null),
        fetchExamSessions().catch(() => [])
      ]);
      setMyClasses(myCls || []);
      setAllClasses(allCls || []);
      setExercises(exList || []);
      setProfile(prof);
      setAchievements(achs);
      setExamSessions(sessions || []);
    } catch (err) {
      console.error('Lỗi nạp dữ liệu Student Portal:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleEnrollByCode = async (e) => {
    e.preventDefault();
    if (!enrollCode.trim()) {
      setEnrollMsg({ type: 'error', text: 'Vui lòng nhập Mã tham gia của lớp học phần (ví dụ: NEU-PY02).' });
      return;
    }
    setIsEnrolling(true);
    setEnrollMsg({ type: '', text: '' });
    try {
      const res = await enrollClassByCode(enrollCode.trim().toUpperCase());
      setEnrollMsg({ type: 'success', text: res.message || 'Ghi danh thành công!' });
      setEnrollCode('');
      await loadData();
    } catch (err) {
      setEnrollMsg({ 
        type: 'error', 
        text: err.response?.data?.detail || 'Mã ghi danh không chính xác hoặc bạn đã tham gia lớp này.' 
      });
    } finally {
      setIsEnrolling(false);
    }
  };

  const handleEnrollClass = async (code) => {
    setIsEnrolling(true);
    setEnrollMsg({ type: '', text: '' });
    try {
      const res = await enrollClassByCode(code);
      setEnrollMsg({ type: 'success', text: res.message || 'Ghi danh thành công!' });
      await loadData();
    } catch (err) {
      setEnrollMsg({ 
        type: 'error', 
        text: err.response?.data?.detail || 'Ghi danh thất bại.' 
      });
    } finally {
      setIsEnrolling(false);
    }
  };

  const handleLeaveClass = async (classId, className) => {
    if (!window.confirm(`Bạn có chắc chắn muốn rút khỏi lớp học phần "${className}"?`)) return;
    try {
      await leaveClass(classId);
      await loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể rút khỏi lớp.');
    }
  };

  // Tính toán các lớp mở chưa ghi danh
  const myClassIds = new Set(myClasses.map(c => c.id));
  const availableClasses = allClasses.filter(c => !myClassIds.has(c.id));

  // Lọc lớp theo từ khóa tìm kiếm (searchQuery)
  const filterByQuery = (list) => {
    if (!searchQuery.trim()) return list;
    const q = searchQuery.toLowerCase().trim();
    return list.filter(c => 
      (c.class_name && c.class_name.toLowerCase().includes(q)) ||
      (c.class_code && c.class_code.toLowerCase().includes(q)) ||
      (c.instructor_name && c.instructor_name.toLowerCase().includes(q)) ||
      (c.enrollment_code && c.enrollment_code.toLowerCase().includes(q)) ||
      (c.course_code && c.course_code.toLowerCase().includes(q))
    );
  };

  const filteredMyClasses = filterByQuery(myClasses);
  const filteredAvailableClasses = filterByQuery(availableClasses);

  // Thống kê KPIs chính thức
  const totalSolved = achievements?.completed_count || profile?.mastered_exercises?.length || 0;
  const totalStars = achievements?.total_stars || 0;
  const studentDisplayName = (user?.full_name || user?.username || 'bạn').split(' - ')[0];

  return (
    <div className="min-h-screen bg-canvas text-foreground font-sans select-text flex flex-col">
      {/* 1. TOP NAVIGATION BAR */}
      <header className="sticky top-0 z-30 flex min-h-16 shrink-0 items-center justify-between gap-3 border-b border-border/80 bg-surface/90 backdrop-blur-md px-4 sm:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <div className="size-9 shrink-0 rounded-full bg-emerald-500 flex items-center justify-center text-white shadow-soft">
            <School className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center space-x-2">
              <span className="truncate font-bold text-base text-foreground tracking-tight">PyTutor</span>
              <Badge variant="success" className="hidden sm:inline-flex text-[10px]">NEU LMS</Badge>
            </div>
            <p className="hidden md:block text-[11px] text-muted">Khoa Công nghệ thông tin • ĐH Kinh tế Quốc dân</p>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <ThemeToggle />
          
          {/* Nút Hành trình học */}
          <button
            onClick={() => setIsProfileOpen(true)}
            aria-label="Mở Hành trình học"
            title="Mở Hành trình học"
            className="px-3.5 py-1.5 rounded-full bg-surface hover:bg-surface-raised border border-border/80 text-xs font-semibold text-foreground transition-all flex items-center gap-1.5 cursor-pointer shadow-soft active:scale-95"
          >
            <Award className="w-3.5 h-3.5 text-amber-500" />
            <span className="hidden xl:inline">Hành trình học</span>
          </button>

          {/* User Capsule */}
          <div className="flex min-h-9 items-center gap-2 rounded-full border border-border/80 bg-surface-raised px-2.5 py-1 shadow-soft" title={studentDisplayName}>
            <span aria-hidden="true" className="flex size-6 shrink-0 items-center justify-center rounded-full bg-slate-950 text-[10px] font-bold text-white dark:bg-emerald-500">
              TK
            </span>
            <div className="text-left hidden sm:block">
              <div className="text-xs font-semibold text-foreground leading-none">{studentDisplayName}</div>
            </div>
            <Badge variant="neutral" className="min-h-5 px-2 py-0 text-[10px]">
              <UserRound aria-hidden="true" className="size-3 sm:hidden" />
              <span className="hidden sm:inline">Sinh viên</span>
            </Badge>
          </div>

          <button
            onClick={() => {
              logout();
              navigate('/login');
            }}
            aria-label="Đăng xuất"
            title="Đăng xuất"
            className="size-9 rounded-full bg-rose-600 hover:bg-rose-700 text-white transition-all flex items-center justify-center cursor-pointer active:scale-95 shadow-soft"
          >
            <LogOut className="w-4 h-4 text-white" />
          </button>
        </div>
      </header>

      {/* 2. MAIN CONTAINER */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 sm:px-6 sm:py-8 space-y-8">
        {/* Banner Chào Mừng & KPIs */}
        <div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-foreground tracking-tight">Xin chào, {studentDisplayName}</h1>
              <p className="mt-1 text-sm text-muted">Tiếp tục bài học của bạn hoặc tham gia một lớp học phần.</p>
            </div>
          </div>

          {/* Bento KPIs Grid */}
          <div className="mt-6">
            {today.loading ? (
              <div aria-hidden="true" className="h-40 animate-pulse rounded-3xl bg-surface-raised" />
            ) : today.error ? (
              <p className="flex items-center gap-2 text-sm text-muted">
                Chưa tải được phần này.
                <button type="button" onClick={loadToday} className="cursor-pointer font-semibold text-primary hover:underline">Thử lại</button>
              </p>
            ) : (
              <TodayCard today={today.data} onOpenExercise={openExerciseFromToday} showGreeting={false} />
            )}
          </div>
        </div>

        {/* 3. KHU VỰC TRỌNG TÂM: CÁC LỚP HỌC PHẦN ĐANG HỌC */}
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="size-8 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center justify-center">
                <School className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-foreground tracking-tight">Các Lớp Học Phần Của Tôi</h2>
                <p className="text-xs text-muted">Danh sách các lớp tín chỉ bạn đã ghi danh trong học kỳ này</p>
              </div>
            </div>
            <button 
              onClick={loadData}
              className="size-8 rounded-full bg-surface hover:bg-surface-raised border border-border/80 text-muted hover:text-foreground flex items-center justify-center transition-all cursor-pointer shadow-soft active:scale-95"
              title="Làm mới"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Thanh Tìm kiếm & Nút Đổi Chế Độ Xem (Lưới vs Cột) */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-2 rounded-full bg-surface border border-border/80 shadow-soft">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-muted absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm kiếm lớp học phần theo tên môn, mã lớp (CNTT...), giảng viên..."
                className="w-full bg-transparent border-0 rounded-full pl-11 pr-9 py-2 text-xs text-foreground placeholder:text-muted/60 focus:outline-none focus:ring-0 font-sans"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted hover:text-foreground cursor-pointer px-1.5 py-0.5 rounded-full bg-surface-raised"
                  title="Xóa tìm kiếm"
                >
                  ✕
                </button>
              )}
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center space-x-1 bg-surface-raised p-1 rounded-full border border-border/80 shrink-0 self-end sm:self-auto">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer ${
                  viewMode === 'grid'
                    ? 'bg-surface text-foreground shadow-sm'
                    : 'text-muted hover:text-foreground'
                }`}
                title="Hiển thị dạng thẻ lưới (Grid)"
              >
                <LayoutGrid className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Dạng Lưới</span>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer ${
                  viewMode === 'list'
                    ? 'bg-surface text-foreground shadow-sm'
                    : 'text-muted hover:text-foreground'
                }`}
                title="Hiển thị dạng cột / danh sách dọc (List)"
              >
                <List className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Dạng Cột</span>
              </button>
            </div>
          </div>

          {isLoading ? (
            <div className="p-12 text-center text-slate-500 text-sm">Đang tải dữ liệu lớp học phần...</div>
          ) : myClasses.length === 0 ? (
            <div className="p-10 rounded-2xl bg-slate-900/60 border border-dashed border-slate-800 text-center space-y-3">
              <School className="w-10 h-10 text-slate-600 mx-auto" />
              <p className="text-sm text-slate-400">Bạn chưa ghi danh vào lớp học phần nào.</p>
              <p className="text-xs text-slate-500">Hãy nhập mã ghi danh hoặc chọn một lớp đang mở ở bên dưới để bắt đầu.</p>
            </div>
          ) : filteredMyClasses.length === 0 ? (
            <div className="p-10 rounded-2xl bg-slate-900/60 border border-dashed border-slate-800 text-center space-y-3">
              <School className="w-10 h-10 text-slate-600 mx-auto" />
              <p className="text-sm text-slate-400">Không tìm thấy lớp học phần nào khớp với từ khóa "{searchQuery}".</p>
              <button
                onClick={() => setSearchQuery('')}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs transition-colors cursor-pointer"
              >
                Xóa bộ lọc tìm kiếm
              </button>
            </div>
          ) : viewMode === 'grid' ? (
            /* DẠNG LƯỚI (GRID VIEW) */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredMyClasses.map((cls) => {
                const progressPct = cls.progress_percent !== undefined ? Math.round(cls.progress_percent) : (cls.progress ? Math.round(cls.progress.progress_percent) : 0);
                const solved = cls.completed_in_class !== undefined ? cls.completed_in_class : (cls.progress ? cls.progress.solved_count : 0);
                const total = cls.exercise_count !== undefined ? cls.exercise_count : (cls.progress ? cls.progress.total_exercises : 0);

                return (
                  <div
                    key={cls.id}
                    className="flex flex-col justify-between rounded-3xl bg-surface border border-border/80 shadow-bento hover:shadow-bento-hover transition-all duration-300 p-6 group"
                  >
                    <div>
                      <div className="flex items-center justify-between text-xs mb-3">
                        <Badge variant="pill" className="font-mono font-semibold">
                          {cls.class_code}
                        </Badge>
                        <span className="text-xs font-medium text-muted">{cls.credits || 3} Tín chỉ</span>
                      </div>
                      <h3 className="text-base font-bold text-foreground line-clamp-1 group-hover:text-emerald-500 transition-colors">
                        {cls.class_name}
                      </h3>
                      <p className="text-xs text-muted mt-1.5 flex items-center space-x-1.5">
                        <span>{cls.instructor_name || 'Nguyễn Văn A'}</span>
                      </p>
                    </div>

                    <div className="mt-5 space-y-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs text-muted">
                          <span>Tiến độ học phần</span>
                          <span className="font-semibold text-foreground tabular-nums">{solved}/{total} bài ({progressPct}%)</span>
                        </div>
                        {/* Progress bar */}
                        <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                          <div 
                            className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                            style={{ width: `${Math.max(5, progressPct)}%` }}
                          />
                        </div>

                        <div className="text-[11px] text-muted flex items-center justify-between pt-1">
                          <span>Mã: <strong className="text-emerald-500 font-mono font-semibold">{cls.enrollment_code}</strong></span>
                          <span>{cls.semester || 'HK1 2026-2027'}</span>
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div className="pt-3 border-t border-border/80 flex items-center space-x-2">
                        <button
                          onClick={() => navigate(`/student/classes/${cls.id}`)}
                          className="flex-1 py-2.5 px-4 rounded-full bg-slate-950 hover:bg-black text-white dark:bg-emerald-500 dark:hover:bg-emerald-600 font-semibold text-xs transition-all shadow-soft active:scale-95 flex items-center justify-center space-x-1.5 cursor-pointer"
                        >
                          <span>Vào lớp học phần</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleLeaveClass(cls.id, cls.class_name)}
                          className="py-2.5 px-3 rounded-full hover:bg-rose-500/10 text-muted hover:text-rose-500 text-xs transition-all cursor-pointer font-medium"
                          title="Rút khỏi lớp"
                        >
                          Rút lớp
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            /* DẠNG CỘT / DANH SÁCH DỌC (COLUMN / LIST VIEW) */
            <div className="space-y-3">
              {filteredMyClasses.map((cls) => {
                const progressPct = cls.progress_percent !== undefined ? Math.round(cls.progress_percent) : (cls.progress ? Math.round(cls.progress.progress_percent) : 0);
                const solved = cls.completed_in_class !== undefined ? cls.completed_in_class : (cls.progress ? cls.progress.solved_count : 0);
                const total = cls.exercise_count !== undefined ? cls.exercise_count : (cls.progress ? cls.progress.total_exercises : 0);

                return (
                  <div
                    key={cls.id}
                    className="p-4 rounded-2xl bg-surface border border-border/80 shadow-soft hover:shadow-bento transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 group"
                  >
                    <div className="flex items-start space-x-3.5 flex-1 min-w-0">
                      <div className="size-10 rounded-full bg-surface-raised border border-border/80 flex items-center justify-center text-emerald-500 font-mono text-xs font-bold shrink-0 mt-0.5">
                        {cls.credits || 3}TC
                      </div>
                      <div className="min-w-0 flex-1 space-y-1">
                        <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                          <Badge variant="pill" className="font-mono text-xs font-semibold">
                            {cls.class_code}
                          </Badge>
                          <h3 className="font-bold text-sm text-foreground truncate group-hover:text-emerald-500 transition-colors">
                            {cls.class_name}
                          </h3>
                        </div>
                        <div className="flex items-center space-x-3 text-xs text-muted flex-wrap">
                          <span>{cls.instructor_name || 'Nguyễn Văn A'}</span>
                          <span>•</span>
                          <span>Mã: <strong className="text-emerald-500 font-mono">{cls.enrollment_code}</strong></span>
                          <span>•</span>
                          <span>{cls.semester || 'HK1 2026-2027'}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-6 shrink-0 justify-between md:justify-end">
                      {/* Progress */}
                      <div className="w-36 space-y-1.5">
                        <div className="flex items-center justify-between text-[11px] text-muted">
                          <span>Tiến độ</span>
                          <span className="text-foreground font-semibold">{solved}/{total} ({progressPct}%)</span>
                        </div>
                        <div className="w-full h-1.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                          <div 
                            className="h-full bg-emerald-500 rounded-full transition-all duration-300"
                            style={{ width: `${Math.max(5, progressPct)}%` }}
                          />
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => navigate(`/student/classes/${cls.id}`)}
                          className="py-2 px-4 rounded-full bg-slate-950 hover:bg-black text-white dark:bg-emerald-500 dark:hover:bg-emerald-600 font-semibold text-xs transition-all flex items-center space-x-1 cursor-pointer shadow-soft active:scale-95"
                        >
                          <span>Vào lớp</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => handleLeaveClass(cls.id, cls.class_name)}
                          className="py-2 px-3 rounded-full hover:bg-rose-500/10 text-muted hover:text-rose-500 text-xs transition-all cursor-pointer font-medium"
                          title="Rút khỏi lớp"
                        >
                          Rút
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* 4. KHU VỰC ĐĂNG KÝ LỚP MỚI & PHÒNG TỰ LUYỆN TẬP TỰ DO */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-2">
          {/* Cột 1 & 2: Ghi danh bằng mã & Danh sách lớp đang mở */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center space-x-2 text-foreground font-bold text-sm">
              <Plus className="w-4 h-4 text-emerald-500" />
              <span>Đăng Ký & Ghi Danh Lớp Học Phần Mới</span>
            </div>

            <div className="p-6 rounded-3xl bg-surface border border-border/80 shadow-bento space-y-4">
              {/* Form mã code */}
              <form onSubmit={handleEnrollByCode} className="flex flex-col sm:flex-row items-center gap-3">
                <input
                  type="text"
                  value={enrollCode}
                  onChange={(e) => setEnrollCode(e.target.value.toUpperCase())}
                  placeholder="Nhập Mã tham gia (vd: NEU-PY02, NEU-DA01...)"
                  className="w-full sm:flex-1 bg-surface border border-border/80 rounded-full px-4 py-2.5 text-xs text-foreground placeholder:text-muted/60 font-mono shadow-soft focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                />
                <button
                  type="submit"
                  disabled={isEnrolling}
                  className="w-full sm:w-auto px-6 py-2.5 rounded-full bg-slate-950 hover:bg-black text-white dark:bg-emerald-600 dark:hover:bg-emerald-700 disabled:opacity-50 font-bold text-xs transition-all shadow-soft active:scale-95 cursor-pointer shrink-0"
                >
                  {isEnrolling ? 'Đang ghi danh...' : 'Ghi Danh Ngay'}
                </button>
              </form>

              {enrollMsg.text && (
                <div className={`p-3 rounded-2xl text-xs ${
                  enrollMsg.type === 'success' 
                    ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400' 
                    : 'bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400'
                }`}>
                  {enrollMsg.text}
                </div>
              )}

              {/* Danh sách lớp mở chưa ghi danh */}
              {filteredAvailableClasses.length > 0 && (
                <div className="pt-3 border-t border-border/80 space-y-2">
                  <div className="text-[11px] font-semibold text-muted uppercase tracking-wider flex items-center justify-between">
                    <span>Các Lớp Học Phần Đang Mở Tại Khoa:</span>
                    <span className="text-[10px] text-emerald-500 font-mono font-semibold">{filteredAvailableClasses.length} lớp</span>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                    {filteredAvailableClasses.map((ac) => (
                      <div
                        key={ac.id}
                        className="p-3 rounded-2xl bg-surface-raised border border-border/60 hover:border-border transition-all flex items-center justify-between"
                      >
                        <div className="space-y-0.5">
                          <div className="text-xs font-semibold text-foreground flex items-center space-x-2">
                            <span>{ac.class_name}</span>
                            <Badge variant="pill" className="font-mono text-[10px]">{ac.class_code}</Badge>
                          </div>
                          <div className="text-[11px] text-muted">
                            {ac.instructor_name || 'Nguyễn Văn A'} • Mã: <span className="font-mono text-emerald-500 font-semibold">{ac.enrollment_code}</span>
                          </div>
                        </div>

                        <button
                          onClick={() => handleEnrollClass(ac.enrollment_code)}
                          disabled={isEnrolling}
                          className="px-4 py-1.5 rounded-full bg-slate-950 hover:bg-black text-white dark:bg-emerald-600 dark:hover:bg-emerald-700 text-xs font-semibold shadow-soft transition-all cursor-pointer active:scale-95"
                        >
                          Ghi danh
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Cột 3: Trung Tâm Vinh Danh & Năng Lực Học Viên (Tạm ẩn Lịch Thi theo yêu cầu) */}
          <div className="space-y-4">
            <div className="flex items-center justify-between text-foreground font-bold text-sm">
              <div className="flex items-center space-x-2">
                {SHOW_EXAM_SESSIONS ? (
                  <>
                    <Calendar className="w-4 h-4 text-emerald-500" />
                    <span>Lịch Thi & Thực Hành</span>
                  </>
                ) : (
                  <>
                    <Trophy className="w-4 h-4 text-amber-500" />
                    <span>Tiến độ & bảng xếp hạng</span>
                  </>
                )}
              </div>
              {SHOW_EXAM_SESSIONS ? (
                <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-mono font-semibold">
                  {examSessions.filter(s => s.is_active).length} ca đang mở
                </span>
              ) : (
                <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 font-mono font-semibold">
                  SV K65 CNTT
                </span>
              )}
            </div>

            <div className="p-6 rounded-3xl bg-surface border border-border/80 shadow-bento space-y-4">
              {SHOW_EXAM_SESSIONS ? (
                /* Danh sách các ca thi / đợt thực hành */
                examSessions && examSessions.length > 0 ? (
                  <div className="space-y-2.5">
                    {examSessions.slice(0, 3).map((sess) => {
                      const isExam = sess.session_type === 'EXAM';
                      return (
                        <div
                          key={sess.id}
                          className={`p-3 rounded-2xl border transition-all ${
                            isExam 
                              ? 'bg-rose-500/10 border-rose-500/20 hover:border-rose-500/40' 
                              : 'bg-surface-raised border-border/80 hover:border-border'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="space-y-1">
                              <div className="flex items-center space-x-1.5 flex-wrap">
                                <Badge variant={isExam ? 'danger' : 'info'} className="text-[10px]">
                                  {isExam ? 'Kỳ Thi' : 'Thực Hành'}
                                </Badge>
                                <span className="text-xs font-bold text-foreground line-clamp-1">{sess.title}</span>
                              </div>
                              <div className="flex items-center space-x-2 text-[11px] text-muted">
                                <span className="flex items-center space-x-1">
                                  <Clock className="w-3 h-3" />
                                  <span>{sess.duration_minutes || 45} phút</span>
                                </span>
                                {sess.class_name && <span className="line-clamp-1">• {sess.class_name}</span>}
                              </div>
                            </div>

                            <button
                              onClick={() => {
                                if (sess.class_id) {
                                  navigate(`/student/classes/${sess.class_id}`);
                                } else {
                                  const firstEx = sess.exercise_ids?.[0] || 'ex_01_sum_1_to_n';
                                  navigate(`/student/ide/${firstEx}?sessionId=${sess.id}`);
                                }
                              }}
                              className={`size-8 rounded-full text-xs font-semibold shrink-0 cursor-pointer transition-all flex items-center justify-center active:scale-95 shadow-soft ${
                                isExam 
                                  ? 'bg-rose-500 hover:bg-rose-600 text-white' 
                                  : 'bg-emerald-500 hover:bg-emerald-600 text-white'
                              }`}
                              title="Vào ca thi / đợt thực hành"
                            >
                              <ArrowRight className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="p-4 rounded-2xl bg-surface-raised border border-border/80 text-center space-y-2">
                    <Clock className="w-6 h-6 text-muted mx-auto" />
                    <p className="text-xs text-muted font-medium">Hiện không có đợt thi nào đang mở.</p>
                    <p className="text-[11px] text-muted/70">Giảng viên sẽ thông báo khi có đợt kiểm tra mới.</p>
                  </div>
                )
              ) : (
                /* Card tóm tắt thành tích & vinh danh khi ẩn lịch thi */
                <div className="space-y-3">
                  <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-amber-600 dark:text-amber-400 flex items-center space-x-1.5">
                        <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-500" />
                        <span>Tiến độ học tập</span>
                      </span>
                      <span className="text-xs font-mono font-bold text-foreground">{totalStars} ⭐</span>
                    </div>
                    <p className="text-xs text-muted leading-relaxed">
                      Bạn đã làm xong <strong className="text-foreground">{totalSolved} bài</strong>{totalStars > 0 ? <> và có <strong className="text-foreground">{totalStars} sao</strong></> : null}.
                    </p>
                  </div>
                </div>
              )}

              {/* Tóm tắt năng lực tích lũy & Nút mở nhanh */}
              <div className="pt-3 border-t border-border/80 space-y-3">
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <button
                    onClick={() => setIsLeaderboardOpen(true)}
                    className="py-2.5 px-3 rounded-full bg-amber-500/10 hover:bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/20 text-xs font-semibold flex items-center justify-center space-x-1.5 transition-all cursor-pointer active:scale-95"
                  >
                    <Trophy className="w-3.5 h-3.5 text-amber-500" />
                    <span>Bảng Vàng K65</span>
                  </button>

                  <button
                    onClick={() => setIsProfileOpen(true)}
                    className="py-2.5 px-3 rounded-full bg-surface-raised hover:bg-border/60 text-foreground border border-border/80 text-xs font-semibold flex items-center justify-center space-x-1.5 transition-all cursor-pointer active:scale-95 shadow-soft"
                  >
                    <Award className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Hành trình học</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 5. MODALS */}
      {isProfileOpen && (
        <StudentProfileModal
          isOpen={isProfileOpen}
          onClose={() => setIsProfileOpen(false)}
          sessionId={sessionId}
          classId={myClasses.length > 0 ? myClasses[0].id : null}
        />
      )}

      {isLeaderboardOpen && (
        <LeaderboardModal
          isOpen={isLeaderboardOpen}
          onClose={() => setIsLeaderboardOpen(false)}
        />
      )}
    </div>
  );
}
