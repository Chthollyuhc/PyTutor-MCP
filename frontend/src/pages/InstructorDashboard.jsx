import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { 
  Plus, Edit2, Trash2, BookOpen, CheckCircle, Clock, 
  BarChart3, Users, Award, Code2, AlertCircle, RefreshCw,
  Eye, Download, X, Copy, Check, Sparkles, Terminal,
  School, Calendar, GraduationCap, CheckSquare, Square,
  Layers, ShieldAlert, FileText, ArrowLeft, ArrowRight,
  LogOut, Cpu, HardDrive, ShieldCheck, ChevronRight
} from 'lucide-react';
import MCPInspectorModal from '../components/MCPInspectorModal';
import { 
  checkHealth, 
  fetchInstructorDashboard, 
  fetchInstructorExercises, 
  fetchInstructorSubmissions, 
  deleteInstructorExercise,
  fetchClasses,
  createInstructorClass,
  fetchExamSessions,
  createInstructorExamSession,
  deleteInstructorExamSession,
  fetchClassCurriculum,
  assignClassExercise,
  updateClassExercise,
  removeClassExercise,
  fetchClassStudents
} from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function InstructorDashboard() {
  const { user, isInstructor, logout } = useAuth();
  const navigate = useNavigate();
  const { classId: routeClassId } = useParams();

  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [creditClasses, setCreditClasses] = useState([]);
  const [examSessions, setExamSessions] = useState([]);
  
  // Sidebar Tabs: 'classes' | 'exercises' | 'submissions' | 'system'
  const [sidebarTab, setSidebarTab] = useState('classes');

  // Selected Class in Class Management View
  const [selectedClass, setSelectedClass] = useState(null);
  // Sub-tabs inside Selected Class: 'curriculum' | 'sessions' | 'students'
  const [classSubTab, setClassSubTab] = useState('curriculum');

  const [isLoading, setIsLoading] = useState(true);
  const [isMCPInspectorOpen, setIsMCPInspectorOpen] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [copiedCode, setCopiedCode] = useState(false);

  // Forms state
  const [isCreatingClass, setIsCreatingClass] = useState(false);
  const [classForm, setClassForm] = useState({
    class_code: '',
    class_name: '',
    course_code: 'CNTT1116',
    credits: 3,
    faculty: 'Khoa Công nghệ thông tin - NEU',
    semester: 'Học kỳ 1 (2026-2027)',
    enrollment_code: '',
    description: ''
  });
  const [isSubmittingClass, setIsSubmittingClass] = useState(false);

  // Curriculum & Student Roster
  const [curriculumList, setCurriculumList] = useState([]);
  const [isLoadingCurriculum, setIsLoadingCurriculum] = useState(false);
  const [assignExerciseForm, setAssignExerciseForm] = useState({
    exercise_id: '',
    module_name: 'Chương 1: Biến & Vòng lặp cơ bản',
    order_idx: 1,
    prerequisite_id: '',
    min_stars_required: 2,
    skill_tag: 'Tư duy thuật toán',
    weight_point: 10
  });

  const [studentRoster, setStudentRoster] = useState([]);
  const [isLoadingRoster, setIsLoadingRoster] = useState(false);

  // Session Form
  const [sessionForm, setSessionForm] = useState({
    title: '',
    class_id: '',
    session_type: 'PRACTICE',
    duration_minutes: 45,
    exercise_ids: []
  });
  const [isSubmittingSession, setIsSubmittingSession] = useState(false);

  // Filter Submissions
  const [submissionFilter, setSubmissionFilter] = useState('ALL');

  // Route protection
  useEffect(() => {
    if (!isInstructor && user) {
      navigate('/login');
    }
  }, [isInstructor, user, navigate]);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [hData, sData, exData, subData, clsData, sessData] = await Promise.all([
        checkHealth(),
        fetchInstructorDashboard(),
        fetchInstructorExercises(),
        fetchInstructorSubmissions(),
        fetchClasses(),
        fetchExamSessions()
      ]);
      setHealth(hData);
      setStats(sData);
      setExercises(exData || []);
      setSubmissions(subData || []);
      setCreditClasses(clsData || []);
      setExamSessions(sessData || []);

      if (clsData && clsData.length > 0 && !sessionForm.class_id) {
        setSessionForm(prev => ({ ...prev, class_id: clsData[0].id }));
      }
      if (exData && exData.length > 0 && !assignExerciseForm.exercise_id) {
        setAssignExerciseForm(prev => ({ ...prev, exercise_id: exData[0].id }));
      }

      // Nếu có routeClassId, chọn lớp đó
      if (routeClassId && clsData) {
        const found = clsData.find(c => c.id === routeClassId);
        if (found) {
          handleSelectClass(found);
        }
      }
    } catch (err) {
      console.error('Lỗi khi nạp dữ liệu Instructor Dashboard:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [routeClassId]);

  const handleSelectClass = async (cls) => {
    setSelectedClass(cls);
    setSessionForm(prev => ({ ...prev, class_id: cls.id }));
    setIsLoadingCurriculum(true);
    setIsLoadingRoster(true);
    try {
      const [curr, students] = await Promise.all([
        fetchClassCurriculum(cls.id).catch(() => []),
        fetchClassStudents(cls.id).catch(() => [])
      ]);
      setCurriculumList(curr || []);
      setStudentRoster(students || []);
    } catch (err) {
      console.error('Lỗi nạp thông tin lớp:', err);
    } finally {
      setIsLoadingCurriculum(false);
      setIsLoadingRoster(false);
    }
  };

  const handleBackToClassList = () => {
    setSelectedClass(null);
    if (routeClassId) {
      navigate('/instructor');
    }
  };

  // Form Submissions
  const handleCreateClass = async (e) => {
    e.preventDefault();
    if (!classForm.class_code.trim() || !classForm.class_name.trim()) return;
    setIsSubmittingClass(true);
    try {
      await createInstructorClass(classForm);
      setClassForm({
        class_code: '',
        class_name: '',
        course_code: 'CNTT1116',
        credits: 3,
        faculty: 'Khoa Công nghệ thông tin - NEU',
        semester: 'Học kỳ 1 (2026-2027)',
        enrollment_code: '',
        description: ''
      });
      setIsCreatingClass(false);
      await loadDashboardData();
      alert('Đã mở lớp học phần mới thành công!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể tạo lớp học phần.');
    } finally {
      setIsSubmittingClass(false);
    }
  };

  const handleAssignExercise = async (e) => {
    e.preventDefault();
    if (!selectedClass || !assignExerciseForm.exercise_id) return;
    try {
      await assignClassExercise(selectedClass.id, assignExerciseForm);
      const [updatedCurr, updatedClasses] = await Promise.all([
        fetchClassCurriculum(selectedClass.id),
        fetchClasses().catch(() => [])
      ]);
      setCurriculumList(updatedCurr || []);
      if (updatedClasses && updatedClasses.length > 0) setCreditClasses(updatedClasses);
      alert('Đã gán bài tập vào lộ trình lớp thành công!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể gán bài tập.');
    }
  };

  const handleUpdateClassExercise = async (exerciseId, minStars) => {
    if (!selectedClass) return;
    try {
      await updateClassExercise(selectedClass.id, exerciseId, { min_stars_required: minStars });
      const updatedCurr = await fetchClassCurriculum(selectedClass.id);
      setCurriculumList(updatedCurr || []);
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể cập nhật số sao.');
    }
  };

  const handleRemoveExercise = async (exerciseId) => {
    if (!selectedClass || !window.confirm('Bạn có chắc chắn muốn gỡ bài tập này khỏi lộ trình lớp?')) return;
    try {
      await removeClassExercise(selectedClass.id, exerciseId);
      const [updatedCurr, updatedClasses] = await Promise.all([
        fetchClassCurriculum(selectedClass.id),
        fetchClasses().catch(() => [])
      ]);
      setCurriculumList(updatedCurr || []);
      if (updatedClasses && updatedClasses.length > 0) setCreditClasses(updatedClasses);
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể gỡ bài tập.');
    }
  };

  const handleCreateSession = async (e) => {
    e.preventDefault();
    if (!sessionForm.title.trim() || sessionForm.exercise_ids.length === 0) {
      alert('Vui lòng nhập tên đợt và chọn ít nhất 1 bài tập!');
      return;
    }
    setIsSubmittingSession(true);
    try {
      await createInstructorExamSession(sessionForm);
      setSessionForm(prev => ({
        ...prev,
        title: '',
        exercise_ids: []
      }));
      const sessList = await fetchExamSessions();
      setExamSessions(sessList || []);
      alert('Tạo đợt thực hành / kỳ thi thành công!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể tạo kỳ thi.');
    } finally {
      setIsSubmittingSession(false);
    }
  };

  const handleDeleteSession = async (sessId) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa kỳ thi / đợt thực hành này?')) return;
    try {
      await deleteInstructorExamSession(sessId);
      const sessList = await fetchExamSessions();
      setExamSessions(sessList || []);
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể xóa kỳ thi.');
    }
  };

  const handleDeleteExercise = async (id) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa bài tập này khỏi ngân hàng đề?')) return;
    try {
      await deleteInstructorExercise(id);
      await loadDashboardData();
    } catch (err) {
      alert('Không thể xóa bài tập.');
    }
  };

  const handleExportCSV = () => {
    if (submissions.length === 0) {
      alert('Chưa có dữ liệu bài nộp để xuất!');
      return;
    }
    const headers = ['Mã Nộp', 'Sinh Viên', 'Mã Bài', 'Số Test Pass', 'Tổng Test', 'Sao Đạt', 'Nguồn AI', 'Thời Gian'];
    const rows = submissions.map(s => [
      s.id,
      s.session_id,
      s.exercise_id,
      s.passed_tests,
      s.total_tests,
      s.stars_earned || 0,
      `"${(s.llm_source || '').replace(/"/g, '""')}"`,
      `"${s.timestamp || s.submitted_at || ''}"`
    ]);
    const csvContent = '\uFEFF' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `pytutor_submissions_report_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
  };

  const handleCopyCode = (codeText) => {
    navigator.clipboard.writeText(codeText);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  // Filtered submissions
  const filteredSubmissions = submissions.filter(s => {
    if (submissionFilter === 'PASSED') return s.all_passed;
    if (submissionFilter === 'FAILED') return !s.all_passed;
    return true;
  });

  // Sessions of selected class
  const classSessions = selectedClass
    ? examSessions.filter(s => !s.class_id || s.class_id === selectedClass.id)
    : examSessions;

  return (
    <div className="h-screen w-screen flex bg-slate-950 font-sans text-slate-100 select-text overflow-hidden">
      {/* 1. FIXED LEFT SIDEBAR */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 select-none z-20">
        <div>
          {/* Logo & Portal Branding */}
          <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 to-emerald-500 flex items-center justify-center text-white font-bold shadow-lg shadow-amber-950/30">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-bold text-white tracking-tight text-sm">PyTutor</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 font-mono">Lecturer</span>
              </div>
              <p className="text-[11px] text-slate-400">Khoa CNTT • NEU</p>
            </div>
          </div>

          {/* Lecturer Info Card */}
          <div className="p-4 mx-3 my-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
            <div className="text-[11px] text-slate-400 font-medium">Giảng viên phụ trách:</div>
            <div className="text-xs font-bold text-white mt-0.5">{user?.full_name || 'Nguyễn Văn A'}</div>
            <div className="text-[10px] text-amber-400 font-mono mt-0.5">Khoa Công nghệ thông tin</div>
          </div>

          {/* 4 Main Navigation Buttons */}
          <nav className="p-3 space-y-1.5 text-xs font-semibold">
            <button
              onClick={() => {
                setSidebarTab('classes');
                setSelectedClass(null);
              }}
              className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-xl transition-all cursor-pointer ${
                sidebarTab === 'classes'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <School className="w-4 h-4 shrink-0" />
              <span>1. Quản lý Lớp học phần</span>
            </button>

            <button
              onClick={() => setSidebarTab('exercises')}
              className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-xl transition-all cursor-pointer ${
                sidebarTab === 'exercises'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <BookOpen className="w-4 h-4 shrink-0" />
              <span>2. Ngân hàng Bài tập ({exercises.length})</span>
            </button>

            <button
              onClick={() => setSidebarTab('submissions')}
              className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-xl transition-all cursor-pointer ${
                sidebarTab === 'submissions'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <BarChart3 className="w-4 h-4 shrink-0" />
              <span>3. Giám sát Bài nộp & AI</span>
            </button>

            <button
              onClick={() => setSidebarTab('system')}
              className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-xl transition-all cursor-pointer ${
                sidebarTab === 'system'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Terminal className="w-4 h-4 shrink-0" />
              <span>4. Hạ tầng MCP & Trình biên dịch</span>
            </button>
          </nav>
        </div>

        {/* Bottom Actions */}
        <div className="p-4 border-t border-slate-800 space-y-2">
          <Link
            to="/student"
            className="w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-all"
          >
            <Code2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Xem Cổng Sinh Viên</span>
          </Link>

          <button
            onClick={() => {
              logout();
              navigate('/login');
            }}
            className="w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 text-xs font-semibold transition-all cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Đăng xuất</span>
          </button>
        </div>
      </aside>

      {/* 2. MAIN WORKSPACE CONTAINER */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Workspace Header */}
        <header className="h-14 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              {sidebarTab === 'classes' && <span>🏫 Quản Lý Lớp Học Phần Tín Chỉ NEU</span>}
              {sidebarTab === 'exercises' && <span>📚 Ngân Hàng Câu Hỏi & Bài Tập Lập Trình Python</span>}
              {sidebarTab === 'submissions' && <span>📊 Giám Sát Lịch Sử Nộp Bài & Lời Khuyên Gia Sư AI</span>}
              {sidebarTab === 'system' && <span>🔌 Trạng Thái Hạ Tầng MCP & Cấu Hình Trình Biên Dịch</span>}
            </h2>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={loadDashboardData}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all cursor-pointer"
              title="Làm mới dữ liệu"
            >
              <RefreshCw className="w-4 h-4" />
            </button>

            <Link
              to="/instructor/exercises/new"
              className="py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-emerald-950 flex items-center space-x-1.5 cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Thêm bài tập mới</span>
            </Link>

            <button
              onClick={() => setIsMCPInspectorOpen(true)}
              className="py-1.5 px-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-mono text-emerald-400 transition-all flex items-center space-x-1 cursor-pointer"
            >
              <Terminal className="w-3.5 h-3.5" />
              <span>MCP (8)</span>
            </button>
          </div>
        </header>

        {/* Scrollable Workspace Body */}
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {isLoading ? (
            <div className="p-16 text-center text-slate-500 text-sm">Đang tải dữ liệu giảng viên...</div>
          ) : (
            <>
              {/* =========================================================================
                  SIDEBAR TAB 1: QUẢN LÝ LỚP HỌC PHẦN
              ========================================================================= */}
              {sidebarTab === 'classes' && (
                !selectedClass ? (
                  /* 1.1 DANH SÁCH LỚP HỌC PHẦN */
                  <div className="space-y-6">
                    {/* Top KPI row */}
                    {stats && (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                          <div className="text-xs text-slate-400 mb-1">Lớp học phần phụ trách</div>
                          <div className="text-2xl font-bold text-white font-mono">{creditClasses.length}</div>
                          <p className="text-[11px] text-slate-500 mt-0.5">Khoa Công nghệ thông tin</p>
                        </div>
                        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                          <div className="text-xs text-slate-400 mb-1">Kỳ thi & Thực hành</div>
                          <div className="text-2xl font-bold text-cyan-400 font-mono">{examSessions.length}</div>
                          <p className="text-[11px] text-slate-500 mt-0.5">Đã lên lịch</p>
                        </div>
                        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                          <div className="text-xs text-slate-400 mb-1">Tổng SV ghi danh</div>
                          <div className="text-2xl font-bold text-amber-400 font-mono">
                            {creditClasses.reduce((acc, c) => acc + (c.student_count || 0), 0)}
                          </div>
                          <p className="text-[11px] text-slate-500 mt-0.5">Sinh viên đang học</p>
                        </div>
                        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                          <div className="text-xs text-slate-400 mb-1">Tỷ lệ Pass trung bình</div>
                          <div className="text-2xl font-bold text-emerald-400 font-mono">{stats.pass_rate_percentage}%</div>
                          <p className="text-[11px] text-slate-500 mt-0.5">{stats.total_submissions} lượt nộp</p>
                        </div>
                      </div>
                    )}

                    {/* Button Mở Lớp Mới & Class Grid */}
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-bold text-white">Danh Sách Lớp Học Phần Tín Chỉ NEU</h3>
                        <p className="text-xs text-slate-400">Chọn một lớp để quản lý chương trình học, đề thi và danh sách sinh viên</p>
                      </div>

                      <button
                        onClick={() => setIsCreatingClass(!isCreatingClass)}
                        className="py-2 px-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-md flex items-center space-x-1.5 cursor-pointer"
                      >
                        <Plus className="w-4 h-4" />
                        <span>{isCreatingClass ? 'Đóng Form' : 'Mở Lớp Học Phần Mới'}</span>
                      </button>
                    </div>

                    {/* Form Mở Lớp Học Phần Mới */}
                    {isCreatingClass && (
                      <div className="p-5 rounded-2xl bg-slate-900 border border-emerald-500/30 space-y-4">
                        <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                          <School className="w-4 h-4" />
                          <span>Thông Tin Lớp Học Phần Mới (Chuẩn NEU)</span>
                        </h4>

                        <form onSubmit={handleCreateClass} className="space-y-4 text-xs">
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            <div>
                              <label className="block text-slate-400 mb-1">Mã Lớp Học Phần *</label>
                              <input
                                type="text"
                                placeholder="vd: CNTT1116(126)_03"
                                value={classForm.class_code}
                                onChange={(e) => setClassForm({ ...classForm, class_code: e.target.value })}
                                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-emerald-500"
                                required
                              />
                            </div>
                            <div>
                              <label className="block text-slate-400 mb-1">Tên Học Phần *</label>
                              <input
                                type="text"
                                placeholder="vd: Lập trình Python cơ bản"
                                value={classForm.class_name}
                                onChange={(e) => setClassForm({ ...classForm, class_name: e.target.value })}
                                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                                required
                              />
                            </div>
                            <div>
                              <label className="block text-slate-400 mb-1">Mã Tham Gia (Enrollment Code)</label>
                              <input
                                type="text"
                                placeholder="vd: NEU-PY03 (để trống sẽ tự sinh)"
                                value={classForm.enrollment_code}
                                onChange={(e) => setClassForm({ ...classForm, enrollment_code: e.target.value.toUpperCase() })}
                                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-emerald-500"
                              />
                            </div>
                          </div>

                          <div className="flex justify-end space-x-2">
                            <button
                              type="button"
                              onClick={() => setIsCreatingClass(false)}
                              className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
                            >
                              Hủy
                            </button>
                            <button
                              type="submit"
                              disabled={isSubmittingClass}
                              className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold disabled:opacity-50"
                            >
                              {isSubmittingClass ? 'Đang tạo...' : 'Tạo Lớp Học Phần'}
                            </button>
                          </div>
                        </form>
                      </div>
                    )}

                    {/* Class Cards Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {creditClasses.map((cls) => (
                        <div
                          key={cls.id}
                          className="rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between shadow-lg overflow-hidden group"
                        >
                          <div className="p-5 bg-gradient-to-r from-slate-800 via-slate-900 to-emerald-950/40 border-b border-slate-800">
                            <div className="flex items-center justify-between text-xs font-mono text-slate-300 mb-2">
                              <span className="font-bold px-2 py-0.5 rounded bg-black/40 border border-white/10 text-emerald-400">
                                {cls.class_code}
                              </span>
                              <span>{cls.credits || 3} Tín chỉ</span>
                            </div>
                            <h4 className="text-base font-bold text-white group-hover:text-emerald-300 transition-colors">
                              {cls.class_name}
                            </h4>
                            <p className="text-xs text-slate-400 mt-1">
                              👨‍🏫 {cls.instructor_name || 'Nguyễn Văn A'}
                            </p>
                          </div>

                          <div className="p-5 space-y-4 flex-1 flex flex-col justify-between">
                            <div className="space-y-2 text-xs text-slate-400">
                              <div className="flex justify-between">
                                <span>Mã đăng ký sinh viên:</span>
                                <strong className="text-emerald-400 font-mono">{cls.enrollment_code}</strong>
                              </div>
                              <div className="flex justify-between">
                                <span>Sinh viên ghi danh:</span>
                                <strong className="text-white font-mono">{cls.student_count || 0} sinh viên</strong>
                              </div>
                              <div className="flex justify-between">
                                <span>Học kỳ:</span>
                                <span>{cls.semester || 'HK1 (2026-2027)'}</span>
                              </div>
                            </div>

                            <button
                              onClick={() => handleSelectClass(cls)}
                              className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-md shadow-emerald-950 flex items-center justify-center space-x-2 cursor-pointer"
                            >
                              <span>👉 Quản Lý Chi Tiết Lớp</span>
                              <ChevronRight className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  /* 1.2 KHÔNG GIAN QUẢN TRỊ CHI TIẾT TỪNG LỚP HỌC PHẦN */
                  <div className="space-y-6">
                    {/* Header Chi tiết Lớp */}
                    <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/60 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="space-y-1">
                        <button
                          onClick={handleBackToClassList}
                          className="inline-flex items-center space-x-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-semibold mb-1 cursor-pointer"
                        >
                          <ArrowLeft className="w-3.5 h-3.5" />
                          <span>Quay lại Danh sách Lớp</span>
                        </button>

                        <div className="flex items-center space-x-2">
                          <h3 className="text-xl font-bold text-white">{selectedClass.class_name}</h3>
                          <span className="font-mono text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">
                            {selectedClass.class_code}
                          </span>
                        </div>

                        <p className="text-xs text-slate-400">
                          Mã tham gia: <strong className="text-emerald-400 font-mono">{selectedClass.enrollment_code}</strong> • {selectedClass.credits || 3} Tín chỉ • {selectedClass.semester}
                        </p>
                      </div>

                      {/* 3 Sub-tabs Pills */}
                      <div className="flex items-center space-x-2 bg-slate-950/80 p-1.5 rounded-xl border border-slate-800 shrink-0">
                        <button
                          onClick={() => setClassSubTab('curriculum')}
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                            classSubTab === 'curriculum'
                              ? 'bg-emerald-600 text-white shadow'
                              : 'text-slate-400 hover:text-white'
                          }`}
                        >
                          📚 Lộ trình ({curriculumList.length})
                        </button>
                        <button
                          onClick={() => setClassSubTab('sessions')}
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                            classSubTab === 'sessions'
                              ? 'bg-emerald-600 text-white shadow'
                              : 'text-slate-400 hover:text-white'
                          }`}
                        >
                          📝 Kỳ thi ({classSessions.length})
                        </button>
                        <button
                          onClick={() => setClassSubTab('students')}
                          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                            classSubTab === 'students'
                              ? 'bg-emerald-600 text-white shadow'
                              : 'text-slate-400 hover:text-white'
                          }`}
                        >
                          👨‍🎓 Sinh viên ({studentRoster.length})
                        </button>
                      </div>
                    </div>

                    {/* Sub-tab 1: Curriculum & Skill Matrix */}
                    {classSubTab === 'curriculum' && (
                      <div className="space-y-6">
                        {/* Form gán bài tập */}
                        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
                          <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                            <Plus className="w-4 h-4" />
                            <span>Gán Bài Tập từ Ngân Hàng Đề vào Lộ Trình Lớp</span>
                          </h4>

                          <form onSubmit={handleAssignExercise} className="space-y-3 text-xs">
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                              <div>
                                <label className="block text-slate-400 mb-1">Chọn bài tập từ ngân hàng *</label>
                                <select
                                  value={assignExerciseForm.exercise_id}
                                  onChange={(e) => setAssignExerciseForm({ ...assignExerciseForm, exercise_id: e.target.value })}
                                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white"
                                  required
                                >
                                  {exercises.map(ex => (
                                    <option key={ex.id} value={ex.id}>
                                      {ex.title} ({ex.difficulty} - {ex.category})
                                    </option>
                                  ))}
                                </select>
                              </div>

                              <div>
                                <label className="block text-slate-400 mb-1">Tên Chương / Module *</label>
                                <input
                                  type="text"
                                  placeholder="ví dụ: Chương 1: Cú pháp & Vòng lặp"
                                  value={assignExerciseForm.module_name}
                                  onChange={(e) => setAssignExerciseForm({ ...assignExerciseForm, module_name: e.target.value })}
                                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white"
                                  required
                                />
                              </div>
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                              <div>
                                <label className="block text-slate-400 mb-1">Thứ tự (# Order)</label>
                                <input
                                  type="number"
                                  min="1"
                                  value={assignExerciseForm.order_idx}
                                  onChange={(e) => setAssignExerciseForm({ ...assignExerciseForm, order_idx: Number(e.target.value) })}
                                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white font-mono"
                                />
                              </div>

                              <div>
                                <label className="block text-slate-400 mb-1">Bài tiên quyết</label>
                                <select
                                  value={assignExerciseForm.prerequisite_id}
                                  onChange={(e) => setAssignExerciseForm({ ...assignExerciseForm, prerequisite_id: e.target.value })}
                                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white"
                                >
                                  <option value="">(Không có tiên quyết)</option>
                                  {curriculumList.map(c => (
                                    <option key={c.exercise_id} value={c.exercise_id}>
                                      {c.title || c.exercise_id}
                                    </option>
                                  ))}
                                </select>
                              </div>

                              <div>
                                <label className="block text-slate-400 mb-1">Sao tối thiểu (Rubric)</label>
                                <select
                                  value={assignExerciseForm.min_stars_required}
                                  onChange={(e) => setAssignExerciseForm({ ...assignExerciseForm, min_stars_required: Number(e.target.value) })}
                                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-amber-300 font-bold"
                                >
                                  <option value={1}>⭐ (1 Sao)</option>
                                  <option value={2}>⭐⭐ (2 Sao)</option>
                                  <option value={3}>⭐⭐⭐ (3 Sao - Tự lực 100%)</option>
                                </select>
                              </div>

                              <div>
                                <label className="block text-slate-400 mb-1">Kỹ năng đầu ra</label>
                                <input
                                  type="text"
                                  placeholder="ví dụ: Đệ quy cơ bản"
                                  value={assignExerciseForm.skill_tag}
                                  onChange={(e) => setAssignExerciseForm({ ...assignExerciseForm, skill_tag: e.target.value })}
                                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white"
                                />
                              </div>
                            </div>

                            <div className="flex justify-end pt-2">
                              <button
                                type="submit"
                                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-semibold flex items-center space-x-1.5 cursor-pointer"
                              >
                                <Plus className="w-4 h-4" />
                                <span>Gán Vào Lớp Học Phần</span>
                              </button>
                            </div>
                          </form>
                        </div>

                        {/* Curriculum Table */}
                        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
                          <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                            Lộ Trình Kỹ Năng & Thang Đo Sao Hiện Tại ({curriculumList.length} bài)
                          </h4>

                          {isLoadingCurriculum ? (
                            <div className="py-8 text-center text-slate-500 text-xs">Đang tải ma trận kỹ năng...</div>
                          ) : curriculumList.length === 0 ? (
                            <div className="py-8 text-center text-slate-500 text-xs">Chưa có bài tập nào trong lộ trình lớp.</div>
                          ) : (
                            <div className="overflow-x-auto">
                              <table className="w-full text-left text-xs">
                                <thead>
                                  <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                                    <th className="py-2.5 px-3">#</th>
                                    <th className="py-2.5 px-3">Chương / Module</th>
                                    <th className="py-2.5 px-3">Bài tập</th>
                                    <th className="py-2.5 px-3">Tiên quyết</th>
                                    <th className="py-2.5 px-3">Sao tối thiểu (Inline Edit)</th>
                                    <th className="py-2.5 px-3">Kỹ năng</th>
                                    <th className="py-2.5 px-3 text-right">Thao tác</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800">
                                  {curriculumList.map((item) => (
                                    <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                                      <td className="py-3 px-3 font-mono font-bold text-slate-400">#{item.order_idx}</td>
                                      <td className="py-3 px-3 font-medium text-emerald-400">{item.module_name}</td>
                                      <td className="py-3 px-3">
                                        <div className="font-bold text-white">{item.title}</div>
                                        <div className="text-[10px] text-slate-500 font-mono">{item.exercise_id}</div>
                                      </td>
                                      <td className="py-3 px-3 font-mono text-slate-400">
                                        {item.prerequisite_id || '(Không)'}
                                      </td>
                                      <td className="py-3 px-3">
                                        <select
                                          value={item.min_stars_required || 1}
                                          onChange={(e) => handleUpdateClassExercise(item.exercise_id, Number(e.target.value))}
                                          className="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-amber-300 font-bold"
                                        >
                                          <option value={1}>⭐ (1 Sao)</option>
                                          <option value={2}>⭐⭐ (2 Sao)</option>
                                          <option value={3}>⭐⭐⭐ (3 Sao)</option>
                                        </select>
                                      </td>
                                      <td className="py-3 px-3 text-slate-300">{item.skill_tag}</td>
                                      <td className="py-3 px-3 text-right">
                                        <button
                                          onClick={() => handleRemoveExercise(item.exercise_id)}
                                          className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition-colors"
                                          title="Gỡ khỏi lớp"
                                        >
                                          <Trash2 className="w-3.5 h-3.5" />
                                        </button>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Sub-tab 2: Exam & Practice Sessions */}
                    {classSubTab === 'sessions' && (
                      <div className="space-y-6">
                        {/* Form Tạo Kỳ Thi Mới cho Lớp */}
                        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
                          <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                            <Plus className="w-4 h-4" />
                            <span>Tạo Kỳ Thi Hoặc Đợt Thực Hành Mới Cho Lớp Này</span>
                          </h4>

                          <form onSubmit={handleCreateSession} className="space-y-3 text-xs">
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                              <div>
                                <label className="block text-slate-400 mb-1">Tên Đợt Thi / Thực Hành *</label>
                                <input
                                  type="text"
                                  placeholder="ví dụ: Kiểm tra Giữa kỳ Python"
                                  value={sessionForm.title}
                                  onChange={(e) => setSessionForm({ ...sessionForm, title: e.target.value })}
                                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white"
                                  required
                                />
                              </div>

                              <div>
                                <label className="block text-slate-400 mb-1">Chế Độ Giảng Dạy *</label>
                                <select
                                  value={sessionForm.session_type}
                                  onChange={(e) => setSessionForm({ ...sessionForm, session_type: e.target.value })}
                                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white font-semibold"
                                >
                                  <option value="PRACTICE">🎯 Luyện Tập (BẬT Gia sư AI)</option>
                                  <option value="EXAM">🔒 Kỳ Thi / Kiểm Tra (KHÓA Gia sư AI)</option>
                                </select>
                              </div>

                              <div>
                                <label className="block text-slate-400 mb-1">Thời Lượng (Phút)</label>
                                <input
                                  type="number"
                                  min="5"
                                  max="180"
                                  value={sessionForm.duration_minutes}
                                  onChange={(e) => setSessionForm({ ...sessionForm, duration_minutes: Number(e.target.value) })}
                                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white font-mono"
                                />
                              </div>
                            </div>

                            <div>
                              <label className="block text-slate-400 mb-1.5">
                                Chọn bài tập đưa vào đề ({sessionForm.exercise_ids.length} bài đã chọn):
                              </label>
                              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 max-h-48 overflow-y-auto p-2 bg-slate-950 border border-slate-800 rounded-xl">
                                {exercises.map(ex => {
                                  const isChecked = sessionForm.exercise_ids.includes(ex.id);
                                  return (
                                    <label
                                      key={ex.id}
                                      className={`flex items-center space-x-2 p-2 rounded-lg border cursor-pointer transition-colors ${
                                        isChecked ? 'bg-emerald-500/10 border-emerald-500/30 text-white' : 'border-slate-800 text-slate-400 hover:bg-slate-900'
                                      }`}
                                    >
                                      <input
                                        type="checkbox"
                                        checked={isChecked}
                                        onChange={() => {
                                          setSessionForm(prev => ({
                                            ...prev,
                                            exercise_ids: isChecked
                                              ? prev.exercise_ids.filter(id => id !== ex.id)
                                              : [...prev.exercise_ids, ex.id]
                                          }));
                                        }}
                                        className="rounded text-emerald-600 focus:ring-0"
                                      />
                                      <span className="text-xs truncate">{ex.title}</span>
                                    </label>
                                  );
                                })}
                              </div>
                            </div>

                            <div className="flex justify-end pt-2">
                              <button
                                type="submit"
                                disabled={isSubmittingSession}
                                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-semibold disabled:opacity-50"
                              >
                                {isSubmittingSession ? 'Đang tạo...' : 'Lưu Đợt Thi'}
                              </button>
                            </div>
                          </form>
                        </div>

                        {/* Danh sách Sessions của Lớp */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {classSessions.map(sess => {
                            const isExam = sess.session_type === 'EXAM';
                            return (
                              <div
                                key={sess.id}
                                className={`p-4 rounded-xl border flex flex-col justify-between space-y-3 ${
                                  isExam ? 'bg-rose-950/20 border-rose-500/30' : 'bg-slate-900 border-slate-800'
                                }`}
                              >
                                <div className="space-y-1">
                                  <div className="flex items-center justify-between">
                                    <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                                      isExam ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
                                    }`}>
                                      {isExam ? '🔒 KỲ THI (KHÓA AI)' : '🎯 LUYỆN TẬP'}
                                    </span>
                                    <span className="text-xs text-slate-400">{sess.duration_minutes} phút</span>
                                  </div>
                                  <h5 className="font-bold text-sm text-white">{sess.title}</h5>
                                  <div className="text-[11px] text-slate-400">
                                    Đề thi gồm: {sess.exercise_ids?.join(', ')}
                                  </div>
                                </div>

                                <div className="flex justify-end pt-2 border-t border-slate-800/80">
                                  <button
                                    onClick={() => handleDeleteSession(sess.id)}
                                    className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                  </button>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Sub-tab 3: Student Roster & Progress */}
                    {classSubTab === 'students' && (
                      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
                        <div className="flex items-center justify-between">
                          <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                            Danh Sách Sinh Viên Ghi Danh & Đo Lường Tiến Độ ({studentRoster.length} SV)
                          </h4>
                        </div>

                        {isLoadingRoster ? (
                          <div className="py-8 text-center text-slate-500 text-xs">Đang tải danh sách sinh viên...</div>
                        ) : studentRoster.length === 0 ? (
                          <div className="py-8 text-center text-slate-500 text-xs">Chưa có sinh viên nào ghi danh vào lớp.</div>
                        ) : (
                          <div className="overflow-x-auto">
                            <table className="w-full text-left text-xs">
                              <thead>
                                <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                                  <th className="py-2.5 px-3">#</th>
                                  <th className="py-2.5 px-3">Sinh Viên</th>
                                  <th className="py-2.5 px-3">Tài Khoản</th>
                                  <th className="py-2.5 px-3 text-center">Tiến Độ Giải Bài</th>
                                  <th className="py-2.5 px-3 text-center">Sao Tự Lực</th>
                                  <th className="py-2.5 px-3 text-right">Thời Gian Tham Gia</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-slate-800">
                                {studentRoster.map((st, idx) => (
                                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                                    <td className="py-3 px-3 font-mono text-slate-500">{idx + 1}</td>
                                    <td className="py-3 px-3 font-semibold text-white">{st.full_name || st.student_username || st.username}</td>
                                    <td className="py-3 px-3 font-mono text-emerald-400">@{st.student_username || st.username}</td>
                                    <td className="py-3 px-3 text-center">
                                      <span className="font-bold text-white">{st.completed_exercises ?? st.solved_count ?? 0}/{st.total_exercises ?? 0} bài</span>
                                      <span className="text-slate-500 ml-1">({Math.round(st.progress_percent || 0)}%)</span>
                                    </td>
                                    <td className="py-3 px-3 text-center font-bold text-amber-400">
                                      {st.total_stars ?? st.stars_earned ?? 0} ⭐
                                    </td>
                                    <td className="py-3 px-3 text-right text-slate-500 text-[11px]">
                                      {st.enrolled_at || 'Mới ghi danh'}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              )}

              {/* =========================================================================
                  SIDEBAR TAB 2: NGÂN HÀNG CÂU HỎI & BÀI TẬP
              ========================================================================= */}
              {sidebarTab === 'exercises' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-white">Ngân Hàng Bài Tập Lập Trình Python ({exercises.length})</h3>
                      <p className="text-xs text-slate-400">Các bài tập trong cơ sở dữ liệu SQLite, sẵn sàng gán vào lớp học phần</p>
                    </div>

                    <Link
                      to="/instructor/exercises/new"
                      className="py-2 px-3.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow-md"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Thêm bài tập mới</span>
                    </Link>
                  </div>

                  <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 overflow-hidden">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                          <th className="py-2.5 px-3">Mã Bài</th>
                          <th className="py-2.5 px-3">Tiêu Đề</th>
                          <th className="py-2.5 px-3">Độ Khó</th>
                          <th className="py-2.5 px-3">Chủ Đề</th>
                          <th className="py-2.5 px-3 text-center">Test Cases</th>
                          <th className="py-2.5 px-3 text-right">Thao Tác</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {exercises.map((ex) => (
                          <tr key={ex.id} className="hover:bg-slate-800/40 transition-colors">
                            <td className="py-3 px-3 font-mono text-emerald-400">{ex.id}</td>
                            <td className="py-3 px-3 font-semibold text-white">{ex.title}</td>
                            <td className="py-3 px-3">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                ex.difficulty === 'Dễ' ? 'bg-emerald-500/20 text-emerald-400' :
                                ex.difficulty === 'Trung bình' ? 'bg-amber-500/20 text-amber-400' : 'bg-rose-500/20 text-rose-400'
                              }`}>
                                {ex.difficulty}
                              </span>
                            </td>
                            <td className="py-3 px-3 text-slate-300">{ex.category}</td>
                            <td className="py-3 px-3 text-center font-mono text-slate-400">{ex.test_cases_count}</td>
                            <td className="py-3 px-3 text-right space-x-2">
                              <Link
                                to={`/instructor/exercises/${ex.id}/edit`}
                                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 inline-block"
                                title="Chỉnh sửa"
                              >
                                <Edit2 className="w-3.5 h-3.5" />
                              </Link>
                              <button
                                onClick={() => handleDeleteExercise(ex.id)}
                                className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition-colors cursor-pointer"
                                title="Xóa"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* =========================================================================
                  SIDEBAR TAB 3: GIÁM SÁT BÀI NỘP & AI
              ========================================================================= */}
              {sidebarTab === 'submissions' && (
                <div className="space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-bold text-white">Lịch Sử Nộp Bài Toàn Hệ Thống ({submissions.length})</h3>
                      <p className="text-xs text-slate-400">Theo dõi thời gian thực kết quả chạy sandbox và phản hồi sư phạm của AI</p>
                    </div>

                    <div className="flex items-center space-x-2">
                      <select
                        value={submissionFilter}
                        onChange={(e) => setSubmissionFilter(e.target.value)}
                        className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
                      >
                        <option value="ALL">Tất cả trạng thái</option>
                        <option value="PASSED">Chỉ bài ĐẠT (Passed)</option>
                        <option value="FAILED">Chỉ bài CHƯA ĐẠT (Failed)</option>
                      </select>

                      <button
                        onClick={handleExportCSV}
                        className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center space-x-1.5 shadow"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Xuất CSV (Excel)</span>
                      </button>
                    </div>
                  </div>

                  <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 overflow-hidden">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                          <th className="py-2.5 px-3">Thời Gian</th>
                          <th className="py-2.5 px-3">Sinh Viên</th>
                          <th className="py-2.5 px-3">Bài Tập</th>
                          <th className="py-2.5 px-3 text-center">Kết Quả Sandbox</th>
                          <th className="py-2.5 px-3 text-center">Sao Tự Lực</th>
                          <th className="py-2.5 px-3">Nguồn AI</th>
                          <th className="py-2.5 px-3 text-right">Chi Tiết</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {filteredSubmissions.slice(0, 50).map((sub) => (
                          <tr key={sub.id} className="hover:bg-slate-800/40 transition-colors">
                            <td className="py-3 px-3 text-slate-400 text-[11px] font-mono">
                              {(sub.timestamp || sub.submitted_at)?.slice(5, 16) || 'Vừa xong'}
                            </td>
                            <td className="py-3 px-3 font-semibold text-white">@{sub.session_id}</td>
                            <td className="py-3 px-3 font-mono text-emerald-400">{sub.exercise_id}</td>
                            <td className="py-3 px-3 text-center">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                sub.all_passed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                              }`}>
                                {sub.passed_tests}/{sub.total_tests} Pass
                              </span>
                            </td>
                            <td className="py-3 px-3 text-center font-bold text-amber-400">
                              {sub.stars_earned || 0} ⭐
                            </td>
                            <td className="py-3 px-3 text-slate-400 text-[11px] font-mono">
                              {sub.llm_source || 'AI Tutor'}
                            </td>
                            <td className="py-3 px-3 text-right">
                              <button
                                onClick={() => setSelectedSubmission(sub)}
                                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
                                title="Xem chi tiết"
                              >
                                <Eye className="w-3.5 h-3.5" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* =========================================================================
                  SIDEBAR TAB 4: HẠ TẦNG MCP & TRÌNH BIÊN DỊCH
              ========================================================================= */}
              {sidebarTab === 'system' && (
                <div className="space-y-6">
                  {/* Compiler Specifications Grid */}
                  <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
                    <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                      <Cpu className="w-4 h-4 text-emerald-400" />
                      <span>Thông Số Môi Trường Thực Thi (Python Compiler & Sandbox Specs)</span>
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
                      <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                        <div className="text-slate-400 font-medium">Trình thông dịch Python</div>
                        <div className="font-mono text-emerald-400 text-[11px] truncate">
                          {health?.compiler_config?.executable_path || 'python.exe'}
                        </div>
                        <div className="text-[10px] text-slate-500">Phiên bản: {health?.compiler_config?.python_version || health?.compiler_config?.version || '3.14.0'}</div>
                      </div>

                      <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                        <div className="text-slate-400 font-medium">Cờ thực thi (Execution Flags)</div>
                        <div className="font-mono text-blue-400 text-[11px]">
                          -u (Unbuffered I/O), -c (In-memory Bytecode)
                        </div>
                        <div className="text-[10px] text-slate-500">Bảng mã: UTF-8 (PYTHONIOENCODING)</div>
                      </div>

                      <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                        <div className="text-slate-400 font-medium">Cơ chế cô lập (Process Isolation)</div>
                        <div className="font-mono text-purple-400 text-[11px]">
                          OS Subprocess Popen via MCP JSON-RPC 2.0
                        </div>
                        <div className="text-[10px] text-slate-500">Hộp cát an toàn chống crash</div>
                      </div>

                      <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                        <div className="text-slate-400 font-medium">Giới hạn thời gian (Sandbox Timeout)</div>
                        <div className="font-mono text-amber-400 font-bold text-sm">
                          5.0 giây (Time Limit Exceeded)
                        </div>
                        <div className="text-[10px] text-slate-500">Tự động ngắt vòng lặp vô hạn</div>
                      </div>

                      <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                        <div className="text-slate-400 font-medium">Bộ truy vết lệnh (Tracer Limit)</div>
                        <div className="font-mono text-cyan-400 font-bold text-sm">
                          150 bước / 3.0s timeout
                        </div>
                        <div className="text-[10px] text-slate-500">Bảo đảm bộ nhớ trực quan mượt mà</div>
                      </div>

                      <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                        <div className="text-slate-400 font-medium">Cơ sở dữ liệu (Database Engine)</div>
                        <div className="font-mono text-emerald-400 text-[11px]">
                          SQLite3 WAL Mode (timeout=20.0s)
                        </div>
                        <div className="text-[10px] text-slate-500">Giao dịch đồng thời không lock</div>
                      </div>
                    </div>
                  </div>

                  {/* 8 MCP Tools Grid */}
                  <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
                    <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                      <Terminal className="w-4 h-4 text-cyan-400" />
                      <span>Danh Sách 8 Công Cụ MCP (Model Context Protocol Engine)</span>
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                      {[
                        { name: 'run_test_cases', desc: 'Sandbox chạy test cases độc lập (timeout 5s)', group: 'Thực thi' },
                        { name: 'analyze_code_ast', desc: 'Phân tích cây cú pháp tĩnh AST Python', group: 'Thực thi' },
                        { name: 'trace_code_execution', desc: 'Truy vết biến và luồng lệnh từng bước', group: 'Thực thi' },
                        { name: 'get_exercise_list', desc: 'Truy xuất danh mục bài tập từ SQLite', group: 'Học liệu' },
                        { name: 'get_exercise_details', desc: 'Lấy đề bài, starter code & test cases', group: 'Học liệu' },
                        { name: 'save_learning_event', desc: 'Lưu vết lịch sử nộp bài vào SQLite WAL', group: 'Trí nhớ' },
                        { name: 'get_attempt_history', desc: 'Lấy 5 lần nộp bài gần nhất của học viên', group: 'Trí nhớ' },
                        { name: 'get_student_model', desc: 'Phân tích năng lực 4D & sinh thẻ chẩn đoán', group: 'Trí nhớ' },
                      ].map((tool, idx) => (
                        <div key={idx} className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-mono font-bold text-emerald-400 text-xs">#{idx + 1} {tool.name}</span>
                            <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">{tool.group}</span>
                          </div>
                          <p className="text-[11px] text-slate-400 leading-relaxed">{tool.desc}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {/* MODAL CHI TIẾT BÀI NỘP */}
      {selectedSubmission && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm select-text">
          <div className="w-full max-w-3xl max-h-[90vh] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
              <h3 className="font-bold text-sm text-white flex items-center space-x-2">
                <span>Chi tiết bài nộp của @{selectedSubmission.session_id}</span>
                <span className="text-xs font-mono text-emerald-400">({selectedSubmission.exercise_id})</span>
              </h3>
              <button
                onClick={() => setSelectedSubmission(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">Kết quả Sandbox</div>
                  <div className="font-bold text-sm mt-0.5 text-emerald-400">
                    {selectedSubmission.passed_tests}/{selectedSubmission.total_tests} Pass
                  </div>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">Sao Tự Lực</div>
                  <div className="font-bold text-sm mt-0.5 text-amber-400">
                    {selectedSubmission.stars_earned || 0} ⭐
                  </div>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">Nguồn AI</div>
                  <div className="font-mono text-xs mt-0.5 text-slate-300">
                    {selectedSubmission.llm_source || 'AI'}
                  </div>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <div className="text-slate-400 text-[10px]">Thời gian</div>
                  <div className="font-mono text-[11px] mt-0.5 text-slate-300">
                    {selectedSubmission.timestamp || selectedSubmission.submitted_at || 'Vừa xong'}
                  </div>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-slate-300">Mã nguồn nộp bài:</span>
                  <button
                    onClick={() => handleCopyCode(selectedSubmission.code || selectedSubmission.submitted_code)}
                    className="text-[10px] text-emerald-400 flex items-center space-x-1"
                  >
                    {copiedCode ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    <span>{copiedCode ? 'Đã chép' : 'Sao chép code'}</span>
                  </button>
                </div>
                <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-emerald-300 overflow-x-auto max-h-60">
                  {selectedSubmission.code || selectedSubmission.submitted_code}
                </pre>
              </div>

              {selectedSubmission.tutor_hint && (
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <span className="font-semibold text-amber-300">Lời khuyên của Gia sư AI:</span>
                  <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {selectedSubmission.tutor_hint}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* MCP INSPECTOR MODAL */}
      <MCPInspectorModal
        isOpen={isMCPInspectorOpen}
        onClose={() => setIsMCPInspectorOpen(false)}
        discoveredTools={health?.discovered_tools || []}
        mcpTrace={[]}
      />
    </div>
  );
}
