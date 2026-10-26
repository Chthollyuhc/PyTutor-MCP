import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  School, BookOpen, Sparkles, Award, CheckCircle2, ArrowRight, 
  Plus, LogOut, FileText, Code2, Shield, Calendar, Users, 
  TrendingUp, Terminal, Star, Clock, AlertCircle, RefreshCw,
  Search, LayoutGrid, List, Trophy
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { 
  fetchMyClasses, 
  fetchClasses, 
  enrollClassByCode, 
  leaveClass, 
  fetchStudentProfile, 
  fetchExercises,
  fetchExamSessions,
  fetchUserAchievements
} from '../services/api';
import StudentProfileModal from '../components/StudentProfileModal';
import MCPInspectorModal from '../components/MCPInspectorModal';
import LeaderboardModal from '../components/LeaderboardModal';

// Flag điều khiển hiển thị 'Lịch Thi & Thực Hành' (đặt true khi muốn mở lại tính năng này)
const SHOW_EXAM_SESSIONS = false;

export default function StudentPortalPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

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
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);
  const [isLeaderboardOpen, setIsLeaderboardOpen] = useState(false);

  // Dữ liệu mở rộng: Đợt thi tín chỉ & Huy hiệu/sao thành tích
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
    if (!enrollCode.trim()) return;
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
  const totalClasses = myClasses.length;
  const totalSolved = achievements?.completed_count || profile?.mastered_exercises?.length || 0;
  const totalStars = achievements?.total_stars || 0;
  const autonomyScore = profile?.analytics_metrics?.autonomy_score ?? 85;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans select-none flex flex-col">
      {/* 1. TOP NAVIGATION BAR */}
      <header className="sticky top-0 z-30 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
            <School className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-base text-white tracking-tight">PyTutor-MCP</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono font-medium">NEU LMS</span>
            </div>
            <p className="text-[11px] text-slate-400">Khoa Công nghệ thông tin • ĐH Kinh tế Quốc dân</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Nút Hồ sơ Năng lực 4D */}
          <button
            onClick={() => setIsProfileOpen(true)}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-medium text-slate-200 hover:text-white transition-all flex items-center space-x-1.5 cursor-pointer"
          >
            <Award className="w-3.5 h-3.5 text-amber-400" />
            <span>Hồ sơ & Năng lực 4D</span>
          </button>

          {/* Nút Kết nối MCP */}
          <button
            onClick={() => setIsInspectorOpen(true)}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-mono text-emerald-400 transition-all flex items-center space-x-1.5 cursor-pointer"
          >
            <Terminal className="w-3.5 h-3.5 text-emerald-400" />
            <span>MCP (8)</span>
          </button>

          {/* User Info & Logout */}
          <div className="h-6 w-px bg-slate-800 mx-1" />
          <div className="text-right hidden sm:block">
            <div className="text-xs font-semibold text-white">Trần Minh Khánh</div>
            <div className="text-[10px] text-slate-400 font-mono">SV K65 CNTT • MSV: 11236131</div>
          </div>

          <button
            onClick={() => {
              logout();
              navigate('/login');
            }}
            title="Đăng xuất"
            className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition-all cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* 2. MAIN CONTAINER */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        {/* Banner Chào Mừng & KPIs */}
        <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/50 border border-slate-800 p-6 sm:p-8 overflow-hidden shadow-xl">
          <div className="absolute right-0 top-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-3xl mb-6">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>CỔNG HỌC TẬP TÍN CHỈ SINH VIÊN NEU</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Xin chào, Trần Minh Khánh! 👋
            </h1>
            <p className="text-sm text-slate-300 mt-2 leading-relaxed">
              Chào mừng bạn đến với môi trường rèn luyện lập trình thích ứng. Hãy chọn một lớp học phần bên dưới để tiếp tục lộ trình học tập hoặc tham gia các đợt thực hành & kỳ thi tín chỉ.
            </p>
          </div>

          {/* 4 Thẻ KPI */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-800/80">
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium">Lớp học phần</span>
                <School className="w-4 h-4 text-blue-400" />
              </div>
              <div className="text-2xl font-bold text-white">{totalClasses}</div>
              <div className="text-[11px] text-blue-400/90 mt-0.5">Đã ghi danh kỳ này</div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium">Bài đã hoàn thành</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-white">{totalSolved}</div>
              <div className="text-[11px] text-emerald-400/90 mt-0.5">Đạt 100% test cases</div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium">Sao tự lực</span>
                <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
              </div>
              <div className="text-2xl font-bold text-white">{totalStars} ⭐</div>
              <div className="text-[11px] text-amber-400/90 mt-0.5">Không dùng code giải</div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 mb-1">
                <span className="text-xs font-medium">Chỉ số Tự lực</span>
                <TrendingUp className="w-4 h-4 text-purple-400" />
              </div>
              <div className="text-2xl font-bold text-white">{autonomyScore}<span className="text-sm text-slate-400 font-normal">/100</span></div>
              <div className="text-[11px] text-purple-400/90 mt-0.5">Độc lập tư duy thuật toán</div>
            </div>
          </div>
        </div>

        {/* 3. KHU VỰC TRỌNG TÂM: CÁC LỚP HỌC PHẦN ĐANG HỌC */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-7 h-7 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center">
                <School className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white tracking-tight">Các Lớp Học Phần Của Tôi</h2>
                <p className="text-xs text-slate-400">Danh sách các lớp tín chỉ bạn đã ghi danh trong học kỳ này</p>
              </div>
            </div>
            <button 
              onClick={loadData}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-all cursor-pointer"
              title="Làm mới"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {/* Thanh Tìm kiếm & Nút Đổi Chế Độ Xem (Lưới vs Cột) */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-3 rounded-2xl bg-slate-900 border border-slate-800">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Tìm kiếm lớp học phần theo tên môn, mã lớp (CNTT...), giảng viên..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-9 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all font-sans"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-2 text-xs text-slate-400 hover:text-white cursor-pointer px-1.5 py-0.5 rounded bg-slate-800"
                  title="Xóa tìm kiếm"
                >
                  ✕
                </button>
              )}
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center space-x-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 shrink-0 self-end sm:self-auto">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-all cursor-pointer ${
                  viewMode === 'grid'
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
                title="Hiển thị dạng thẻ lưới (Grid)"
              >
                <LayoutGrid className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Dạng Lưới</span>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-all cursor-pointer ${
                  viewMode === 'list'
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white'
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

                // Xác định màu gradient theo mã môn
                const isPythonBasic = cls.course_code?.includes('CNTT1116') || cls.course_code?.includes('CNTT1128');
                const gradHeader = isPythonBasic
                  ? 'from-emerald-700 via-teal-800 to-slate-900'
                  : 'from-blue-700 via-indigo-800 to-slate-900';

                return (
                  <div
                    key={cls.id}
                    className="flex flex-col justify-between rounded-2xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all shadow-lg overflow-hidden group hover:-translate-y-0.5 duration-200"
                  >
                    {/* Header Card */}
                    <div className={`p-5 bg-gradient-to-r ${gradHeader} border-b border-slate-800/80`}>
                      <div className="flex items-center justify-between text-xs text-slate-200/90 mb-2 font-mono">
                        <span className="font-bold px-2 py-0.5 bg-black/30 rounded border border-white/10">{cls.class_code}</span>
                        <span>{cls.credits || 3} Tín chỉ</span>
                      </div>
                      <h3 className="text-base font-bold text-white line-clamp-1 group-hover:text-emerald-200 transition-colors">
                        {cls.class_name}
                      </h3>
                      <p className="text-xs text-slate-300 mt-1 flex items-center space-x-1.5">
                        <span>👨‍🏫 {cls.instructor_name || 'Nguyễn Văn A'}</span>
                      </p>
                    </div>

                    {/* Body Card */}
                    <div className="p-5 space-y-4 flex-1 flex flex-col justify-between">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between text-xs text-slate-400">
                          <span>Tiến độ học phần</span>
                          <span className="font-semibold text-white">{solved}/{total} bài ({progressPct}%)</span>
                        </div>
                        {/* Progress bar */}
                        <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all duration-500"
                            style={{ width: `${Math.max(5, progressPct)}%` }}
                          />
                        </div>

                        <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1">
                          <span>Mã tham gia: <strong className="text-emerald-400 font-mono">{cls.enrollment_code}</strong></span>
                          <span>{cls.semester || 'HK1 2026-2027'}</span>
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div className="pt-3 border-t border-slate-800/80 flex items-center space-x-2">
                        <button
                          onClick={() => navigate(`/student/classes/${cls.id}`)}
                          className="flex-1 py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-md shadow-emerald-950 flex items-center justify-center space-x-1.5 cursor-pointer"
                        >
                          <span>👉 Vào Lớp Học Phần</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleLeaveClass(cls.id, cls.class_name)}
                          className="py-2 px-2.5 rounded-xl bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 text-xs transition-all border border-slate-700/60 cursor-pointer"
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
                    className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 group shadow-md"
                  >
                    <div className="flex items-start space-x-3.5 flex-1 min-w-0">
                      <div className="w-10 h-10 rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-center text-emerald-400 font-mono text-xs font-bold shrink-0 mt-0.5">
                        {cls.credits || 3}TC
                      </div>
                      <div className="min-w-0 flex-1 space-y-1">
                        <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-mono text-xs font-semibold">
                            {cls.class_code}
                          </span>
                          <h3 className="font-bold text-sm text-white truncate group-hover:text-emerald-300 transition-colors">
                            {cls.class_name}
                          </h3>
                        </div>
                        <div className="flex items-center space-x-3 text-xs text-slate-400 flex-wrap">
                          <span>👨‍🏫 {cls.instructor_name || 'Nguyễn Văn A'}</span>
                          <span>•</span>
                          <span>Mã tham gia: <strong className="text-emerald-400 font-mono">{cls.enrollment_code}</strong></span>
                          <span>•</span>
                          <span>{cls.semester || 'HK1 2026-2027'}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-6 shrink-0 justify-between md:justify-end">
                      {/* Progress */}
                      <div className="w-36 space-y-1.5">
                        <div className="flex items-center justify-between text-[11px] text-slate-400">
                          <span>Tiến độ</span>
                          <span className="text-white font-semibold">{solved}/{total} ({progressPct}%)</span>
                        </div>
                        <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
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
                          className="py-1.5 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all flex items-center space-x-1 cursor-pointer shadow-sm"
                        >
                          <span>Vào lớp</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => handleLeaveClass(cls.id, cls.class_name)}
                          className="py-1.5 px-2.5 rounded-lg bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 text-xs transition-all border border-slate-700/60 cursor-pointer"
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
            <div className="flex items-center space-x-2 text-white font-bold text-sm">
              <Plus className="w-4 h-4 text-emerald-400" />
              <span>Đăng Ký & Ghi Danh Lớp Học Phần Mới</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
              {/* Form mã code */}
              <form onSubmit={handleEnrollByCode} className="flex flex-col sm:flex-row items-center gap-3">
                <input
                  type="text"
                  value={enrollCode}
                  onChange={(e) => setEnrollCode(e.target.value.toUpperCase())}
                  placeholder="Nhập Mã tham gia (vd: NEU-PY02, NEU-DA01...)"
                  className="w-full sm:flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                />
                <button
                  type="submit"
                  disabled={isEnrolling || !enrollCode.trim()}
                  className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold text-xs transition-all shadow-md shadow-emerald-950 cursor-pointer shrink-0"
                >
                  {isEnrolling ? 'Đang ghi danh...' : 'Ghi Danh Ngay'}
                </button>
              </form>

              {enrollMsg.text && (
                <div className={`p-3 rounded-lg text-xs ${
                  enrollMsg.type === 'success' 
                    ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300' 
                    : 'bg-rose-500/10 border border-rose-500/30 text-rose-300'
                }`}>
                  {enrollMsg.text}
                </div>
              )}

              {/* Danh sách lớp mở chưa ghi danh */}
              {filteredAvailableClasses.length > 0 && (
                <div className="pt-3 border-t border-slate-800/80 space-y-2">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                    <span>Các Lớp Học Phần Đang Mở Tại Khoa:</span>
                    <span className="text-[10px] text-emerald-400 font-mono">{filteredAvailableClasses.length} lớp</span>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                    {filteredAvailableClasses.map((ac) => (
                      <div
                        key={ac.id}
                        className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 transition-all flex items-center justify-between"
                      >
                        <div className="space-y-0.5">
                          <div className="text-xs font-semibold text-white flex items-center space-x-2">
                            <span>{ac.class_name}</span>
                            <span className="font-mono text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">{ac.class_code}</span>
                          </div>
                          <div className="text-[11px] text-slate-400">
                            👨‍🏫 {ac.instructor_name || 'Nguyễn Văn A'} • Mã: <span className="font-mono text-emerald-400">{ac.enrollment_code}</span>
                          </div>
                        </div>

                        <button
                          onClick={() => handleEnrollClass(ac.enrollment_code)}
                          disabled={isEnrolling}
                          className="px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-medium transition-all cursor-pointer"
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
            <div className="flex items-center justify-between text-white font-bold text-sm">
              <div className="flex items-center space-x-2">
                {SHOW_EXAM_SESSIONS ? (
                  <>
                    <Calendar className="w-4 h-4 text-emerald-400" />
                    <span>Lịch Thi & Thực Hành</span>
                  </>
                ) : (
                  <>
                    <Trophy className="w-4 h-4 text-amber-400" />
                    <span>Vinh Danh & Năng Lực</span>
                  </>
                )}
              </div>
              {SHOW_EXAM_SESSIONS ? (
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-mono">
                  {examSessions.filter(s => s.is_active).length} ca đang mở
                </span>
              ) : (
                <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 font-mono">
                  SV K65 CNTT
                </span>
              )}
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-lg">
              {SHOW_EXAM_SESSIONS ? (
                /* Danh sách các ca thi / đợt thực hành */
                examSessions && examSessions.length > 0 ? (
                  <div className="space-y-2.5">
                    {examSessions.slice(0, 3).map((sess) => {
                      const isExam = sess.session_type === 'EXAM';
                      return (
                        <div
                          key={sess.id}
                          className={`p-3 rounded-xl border transition-all ${
                            isExam 
                              ? 'bg-rose-950/20 border-rose-500/30 hover:border-rose-500/50' 
                              : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="space-y-1">
                              <div className="flex items-center space-x-1.5 flex-wrap">
                                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase font-mono ${
                                  isExam ? 'bg-rose-500/20 text-rose-300' : 'bg-blue-500/20 text-blue-300'
                                }`}>
                                  {isExam ? 'Kỳ Thi' : 'Thực Hành'}
                                </span>
                                <span className="text-xs font-bold text-white line-clamp-1">{sess.title}</span>
                              </div>
                              <div className="flex items-center space-x-2 text-[11px] text-slate-400">
                                <span className="flex items-center space-x-1">
                                  <Clock className="w-3 h-3 text-slate-500" />
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
                              className={`p-1.5 rounded-lg text-xs font-semibold shrink-0 cursor-pointer transition-all ${
                                isExam 
                                  ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-sm' 
                                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm'
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
                  <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-center space-y-2">
                    <Clock className="w-6 h-6 text-slate-500 mx-auto" />
                    <p className="text-xs text-slate-400 font-medium">Hiện không có đợt thi nào đang mở.</p>
                    <p className="text-[11px] text-slate-500">Giảng viên sẽ thông báo khi có đợt kiểm tra mới.</p>
                  </div>
                )
              ) : (
                /* Card tóm tắt thành tích & vinh danh khi ẩn lịch thi */
                <div className="space-y-3">
                  <div className="p-3.5 rounded-xl bg-gradient-to-br from-amber-500/10 via-slate-950 to-slate-950 border border-amber-500/20 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-amber-300 flex items-center space-x-1.5">
                        <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                        <span>Thành Tích Học Phần</span>
                      </span>
                      <span className="text-xs font-mono font-bold text-white">{totalStars} ⭐</span>
                    </div>
                    <p className="text-[11px] text-slate-400 leading-relaxed">
                      Bạn đã hoàn thành <strong>{totalSolved} bài tập</strong> với độ tự lực thuật toán đạt <strong>{autonomyScore}%</strong>.
                    </p>
                  </div>
                </div>
              )}

              {/* Tóm tắt năng lực tích lũy & Nút mở nhanh */}
              <div className="pt-3 border-t border-slate-800/80 space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Huy hiệu đạt được:</span>
                  <div className="flex items-center space-x-1 text-base">
                    {achievements?.badges && achievements.badges.length > 0 ? (
                      achievements.badges.slice(0, 4).map((b, i) => (
                        <span key={i} title={b.badge_title || b.title} className="cursor-default hover:scale-125 transition-transform">
                          {b.badge_icon || b.icon || '🏅'}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-500 text-xs">Chưa có huy hiệu</span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-1">
                  <button
                    onClick={() => setIsLeaderboardOpen(true)}
                    className="py-2 px-2.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold flex items-center justify-center space-x-1.5 transition-all cursor-pointer"
                  >
                    <Trophy className="w-3.5 h-3.5 text-amber-400" />
                    <span>Bảng Vàng K65</span>
                  </button>

                  <button
                    onClick={() => setIsProfileOpen(true)}
                    className="py-2 px-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center justify-center space-x-1.5 transition-all cursor-pointer"
                  >
                    <Award className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Hồ Sơ 4D</span>
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

      {isInspectorOpen && (
        <MCPInspectorModal
          isOpen={isInspectorOpen}
          onClose={() => setIsInspectorOpen(false)}
        />
      )}
    </div>
  );
}
