import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { 
  Plus, Edit2, Trash2, BookOpen, CheckCircle, Clock, 
  BarChart3, Users, Award, Code2, AlertCircle, RefreshCw,
  Eye, Download, X, Copy, Check, Sparkles,
  School, Calendar, GraduationCap, CheckSquare, Square,
  Layers, ShieldAlert, FileText, ArrowLeft, ArrowRight,
  LogOut, LayoutGrid, List, HardDrive, ShieldCheck, ChevronRight, Send
} from 'lucide-react';
import TableControls, { getPage, TableLoading } from '../components/TableControls';
import { 
  fetchInstructorDashboard, 
  fetchInstructorExercises, 
  fetchInstructorSubmissions, 
  deleteInstructorExercise,
  shareInstructorExercise,
  fetchClasses,
  createInstructorClass,
  fetchClassCurriculum,
  assignClassExercise,
  removeClassExercise,
  fetchClassStudents,
  askInstructorClassAI,
  fetchKnowledgeComponents,
  createKnowledgeComponent,
  deleteKnowledgeComponent
} from '../services/api';
import { useAuth } from '../context/AuthContext';
import ThemeToggle from '../components/ThemeToggle';
import { Button, Input } from '../components/ui';
import {
  ClassesAttentionList,
  ClassInsightsPanel,
  ClassKnowledgePanel,
  DaysSelect,
  KnowledgeBasePanel,
  TutorFeedbackPanel,
} from '../components/InstructorPedagogyPanels';

export default function InstructorDashboard() {
  const { user, isInstructor, logout } = useAuth();
  const navigate = useNavigate();
  const { classId: routeClassId } = useParams();

  const [stats, setStats] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [creditClasses, setCreditClasses] = useState([]);
  
  // Sidebar Tabs: 'classes' | 'exercises' | 'submissions'
  const [sidebarTab, setSidebarTab] = useState('classes');

  // Selected Class in Class Management View
  const [selectedClass, setSelectedClass] = useState(null);
  // Sub-tabs inside Selected Class: 'curriculum' | 'students'
  const [classSubTab, setClassSubTab] = useState('curriculum');
  const [classViewMode, setClassViewMode] = useState(() => {
    try { return localStorage.getItem('pytutor_class_view') === 'list' ? 'list' : 'grid'; } catch { return 'grid'; }
  });
  const changeClassView = (mode) => {
    setClassViewMode(mode);
    try { localStorage.setItem('pytutor_class_view', mode); } catch { /* sở thích hiển thị, không bắt buộc */ }
  };

  const [isLoading, setIsLoading] = useState(true);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [copiedCode, setCopiedCode] = useState(false);
  const [aiQuestion, setAiQuestion] = useState('');
  // v5.3 (S3.2): giữ nguyên phản hồi có cấu trúc (reply, days, data_status, sample, llm_source) hoặc { error }.
  const [aiResult, setAiResult] = useState(null);
  const [aiDays, setAiDays] = useState(7);
  const [aiClassId, setAiClassId] = useState('');
  const [isAskingClassAI, setIsAskingClassAI] = useState(false);

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
  // Lỗi form chỉ hiện sau khi rời ô (on blur) hoặc khi bấm gửi; không kiểm tra khi đang gõ.
  const [classFormErrors, setClassFormErrors] = useState({});
  const [assignFormErrors, setAssignFormErrors] = useState({});

  // Curriculum & Student Roster
  const [curriculumList, setCurriculumList] = useState([]);
  const [isLoadingCurriculum, setIsLoadingCurriculum] = useState(false);
  const [assignExerciseForm, setAssignExerciseForm] = useState({
    exercise_id: '',
    module_name: 'Chương 1: Biến & Vòng lặp cơ bản',
    order_idx: 1,
    prerequisite_id: '',
    skill_tag: 'Tư duy thuật toán',
    weight_point: 10
  });

  const [studentRoster, setStudentRoster] = useState([]);
  const [isLoadingRoster, setIsLoadingRoster] = useState(false);

  // Quản lý Đơn vị kiến thức (Knowledge Components - KCs)
  const [knowledgeComponents, setKnowledgeComponents] = useState([]);
  const [showKcModal, setShowKcModal] = useState(false);
  const [isLoadingKcs, setIsLoadingKcs] = useState(false);
  const [kcForm, setKcForm] = useState({ kc: '', label_vi: '', keywords: '' });
  const [isSubmittingKc, setIsSubmittingKc] = useState(false);
  const [kcMessage, setKcMessage] = useState(null);

  const loadKnowledgeComponents = async () => {
    setIsLoadingKcs(true);
    try {
      const data = await fetchKnowledgeComponents();
      setKnowledgeComponents(data || []);
    } catch (err) {
      console.error('Lỗi tải danh sách KC:', err);
    } finally {
      setIsLoadingKcs(false);
    }
  };

  const handleCreateKc = async (e) => {
    e.preventDefault();
    if (!kcForm.label_vi.trim()) return;
    setIsSubmittingKc(true);
    setKcMessage(null);
    try {
      const kws = kcForm.keywords.split(',').map(k => k.trim()).filter(Boolean);
      await createKnowledgeComponent({
        kc: kcForm.kc.trim() || undefined,
        label_vi: kcForm.label_vi.trim(),
        keywords: kws.length > 0 ? kws : [kcForm.label_vi.trim().toLowerCase()]
      });
      setKcMessage({ type: 'success', text: 'Đã thêm Đơn vị kiến thức mới thành công!' });
      setKcForm({ kc: '', label_vi: '', keywords: '' });
      await loadKnowledgeComponents();
    } catch (err) {
      setKcMessage({ type: 'error', text: err.response?.data?.detail || 'Không thể tạo Đơn vị kiến thức' });
    } finally {
      setIsSubmittingKc(false);
    }
  };

  const handleDeleteKc = async (kcSlug) => {
    if (!window.confirm(`Bạn có chắc muốn xóa đơn vị kiến thức '${kcSlug}' không?`)) return;
    try {
      await deleteKnowledgeComponent(kcSlug);
      await loadKnowledgeComponents();
    } catch (err) {
      alert(err.response?.data?.detail || 'Không thể xóa đơn vị kiến thức');
    }
  };

  // Filter Submissions
  const [submissionFilter, setSubmissionFilter] = useState('ALL');
  const [curriculumSearch, setCurriculumSearch] = useState('');
  const [curriculumPage, setCurriculumPage] = useState(1);
  const [rosterSearch, setRosterSearch] = useState('');
  const [rosterPage, setRosterPage] = useState(1);
  const [exerciseSearch, setExerciseSearch] = useState('');
  const [exercisePage, setExercisePage] = useState(1);
  const [submissionSearch, setSubmissionSearch] = useState('');
  const [submissionPage, setSubmissionPage] = useState(1);

  // Route protection
  useEffect(() => {
    if (!isInstructor && user) {
      navigate('/login');
    }
  }, [isInstructor, user, navigate]);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [sData, exData, subData, clsData, kcData] = await Promise.all([
        fetchInstructorDashboard(),
        fetchInstructorExercises(),
        fetchInstructorSubmissions(),
        fetchClasses(),
        fetchKnowledgeComponents().catch(() => [])
      ]);
      setStats(sData);
      setExercises(exData || []);
      setSubmissions(subData || []);
      setCreditClasses(clsData || []);
      setKnowledgeComponents(kcData || []);
      if (clsData?.length && !aiClassId) setAiClassId(clsData[0].id);
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
    setCurriculumSearch('');
    setCurriculumPage(1);
    setRosterSearch('');
    setRosterPage(1);
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

  const handleAskClassAI = async (event) => {
    event.preventDefault();
    const targetClassId = selectedClass?.id || aiClassId;
    if (!targetClassId || !aiQuestion.trim() || isAskingClassAI) return;
    setIsAskingClassAI(true);
    try {
      const result = await askInstructorClassAI({ class_id: targetClassId, user_message: aiQuestion.trim(), days: aiDays });
      setAiResult({ ...result, reply: result.reply || 'Chưa có phản hồi.', days: result.days ?? aiDays });
      setAiQuestion('');
    } catch (error) {
      const detail = error.response?.data?.detail;
      setAiResult({ error: typeof detail === 'string' ? detail : 'Không thể phân tích tình hình lớp lúc này.' });
    } finally {
      setIsAskingClassAI(false);
    }
  };

  // Form Submissions
  const validateClassField = (field, value) => {
    const v = (value || '').trim();
    if (field === 'class_code') {
      if (!v) return 'Nhập mã lớp học phần theo mẫu của Phòng Đào tạo, ví dụ CNTT1116(126)_03.';
    }
    if (field === 'class_name' && !v) return 'Nhập tên học phần, ví dụ “Lập trình Python cơ bản”.';
    if (field === 'enrollment_code' && /\s/.test(v)) {
      return 'Mã tham gia không chứa khoảng trắng; sinh viên sẽ gõ lại mã này. Ví dụ NEU-PY03, hoặc để trống để hệ thống tự sinh.';
    }
    return '';
  };
  const blurClassField = (field) => setClassFormErrors((prev) => ({ ...prev, [field]: validateClassField(field, classForm[field]) }));

  const handleCreateClass = async (e) => {
    e.preventDefault();
    const nextErrors = {
      class_code: validateClassField('class_code', classForm.class_code),
      class_name: validateClassField('class_name', classForm.class_name),
      enrollment_code: validateClassField('enrollment_code', classForm.enrollment_code),
    };
    setClassFormErrors(nextErrors);
    if (Object.values(nextErrors).some(Boolean)) return;
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

  const validateAssignField = (field, value) => {
    if (field === 'exercise_id' && !value) return 'Chọn một bài tập trong ngân hàng đề để gán vào lộ trình.';
    if (field === 'module_name' && !String(value || '').trim()) return 'Nhập tên chương, ví dụ “Chương 1: Cú pháp & Vòng lặp”.';
    if (field === 'order_idx' && (!Number.isInteger(Number(value)) || Number(value) < 1)) return 'Thứ tự là số nguyên từ 1 trở lên, ví dụ 1 cho bài đầu tiên.';
    return '';
  };
  const blurAssignField = (field) => setAssignFormErrors((prev) => ({ ...prev, [field]: validateAssignField(field, assignExerciseForm[field]) }));

  const handleAssignExercise = async (e) => {
    e.preventDefault();
    const nextErrors = {
      exercise_id: validateAssignField('exercise_id', assignExerciseForm.exercise_id),
      module_name: validateAssignField('module_name', assignExerciseForm.module_name),
      order_idx: validateAssignField('order_idx', assignExerciseForm.order_idx),
    };
    setAssignFormErrors(nextErrors);
    if (!selectedClass || Object.values(nextErrors).some(Boolean)) return;
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
  const matchingSubmissions = submissions.filter(s => {
    if (submissionFilter === 'PASSED') return s.all_passed;
    if (submissionFilter === 'FAILED') return !s.all_passed;
    return true;
  });

  const containsQuery = (values, query) => {
    const normalizedQuery = query.trim().toLocaleLowerCase('vi');
    return !normalizedQuery || values.some(value => String(value ?? '').toLocaleLowerCase('vi').includes(normalizedQuery));
  };
  const filteredCurriculum = curriculumList.filter(item => containsQuery(
    [item.order_idx, item.module_name, item.title, item.exercise_id, item.prerequisite_id, item.skill_tag], curriculumSearch,
  ));
  const filteredRoster = studentRoster.filter(student => containsQuery(
    [student.full_name, student.student_username, student.username], rosterSearch,
  ));
  const filteredExercises = exercises.filter(exercise => containsQuery(
    [exercise.id, exercise.title, exercise.difficulty, exercise.category], exerciseSearch,
  ));
  const filteredSubmissions = matchingSubmissions.slice(0, 50).filter(submission => containsQuery(
    [submission.session_id, submission.exercise_id, submission.llm_source, submission.timestamp, submission.submitted_at], submissionSearch,
  ));
  const curriculumPageData = getPage(filteredCurriculum, curriculumPage);
  const rosterPageData = getPage(filteredRoster, rosterPage);
  const exercisePageData = getPage(filteredExercises, exercisePage);
  const submissionPageData = getPage(filteredSubmissions, submissionPage);

  return (
    <div className="flex h-screen w-full select-text flex-col overflow-hidden bg-canvas text-foreground lg:flex-row">
      {/* 1. FIXED LEFT SIDEBAR */}
      <aside className="w-full lg:w-64 bg-surface border-b lg:border-b-0 lg:border-r border-border flex flex-row lg:flex-col lg:justify-between shrink-0 select-none z-20">
        <div className="min-w-0 flex-1 flex flex-col lg:block">
          {/* Logo & Portal Branding */}
          <div className="hidden lg:flex p-5 border-b border-border items-center space-x-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-600 flex items-center justify-center text-white font-bold shadow-soft">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-bold text-foreground tracking-tight text-sm">PyTutor</span>
              </div>
              <p className="text-[11px] text-muted">Khoa CNTT • NEU</p>
            </div>
          </div>

          {/* Lecturer Info Card */}
          <div className="hidden lg:block p-4 mx-3 my-3 rounded-2xl bg-surface-raised border border-border shadow-soft">
            <div className="text-[11px] text-muted font-medium">Giảng viên phụ trách:</div>
            <div className="text-xs font-bold text-foreground mt-0.5">{user?.full_name || 'Nguyễn Văn A'}</div>
            <div className="mt-0.5 text-[0.8125rem] text-muted">Khoa Công nghệ thông tin</div>
          </div>

          {/* 4 Main Navigation Buttons */}
          <nav aria-label="Khu vực giảng viên" className="flex min-w-0 items-center gap-1 overflow-x-auto p-1.5 text-xs font-semibold lg:block lg:space-y-1.5 lg:p-3">
            <button
              onClick={() => {
                setSidebarTab('classes');
                setSelectedClass(null);
              }}
              aria-current={sidebarTab === 'classes' ? 'page' : undefined}
              aria-label="Quản lý lớp học phần"
              title="Quản lý lớp học phần"
              className={`flex h-10 w-10 shrink-0 items-center justify-center gap-2.5 rounded-xl px-2 py-2.5 text-sm transition-colors cursor-pointer lg:w-full lg:justify-start lg:px-3 ${
                sidebarTab === 'classes'
                  ? 'bg-emerald-600 text-white font-bold shadow-soft dark:bg-emerald-500/20 dark:text-emerald-300 dark:border dark:border-emerald-500/30'
                  : 'text-muted hover:text-foreground hover:bg-surface-raised font-medium'
              }`}
            >
              <School className="w-4 h-4 shrink-0" />
              <span className="hidden lg:inline">Quản lý Lớp học phần</span>
            </button>

            <button
              onClick={() => setSidebarTab('exercises')}
              aria-current={sidebarTab === 'exercises' ? 'page' : undefined}
              aria-label="Ngân hàng bài tập"
              title="Ngân hàng bài tập"
              className={`flex h-10 w-10 shrink-0 items-center justify-center gap-2.5 rounded-xl px-2 py-2.5 text-sm transition-colors cursor-pointer lg:w-full lg:justify-start lg:px-3 ${
                sidebarTab === 'exercises'
                  ? 'bg-emerald-600 text-white font-bold shadow-soft dark:bg-emerald-500/20 dark:text-emerald-300 dark:border dark:border-emerald-500/30'
                  : 'text-muted hover:text-foreground hover:bg-surface-raised font-medium'
              }`}
            >
              <BookOpen className="w-4 h-4 shrink-0" />
              <span className="hidden lg:inline">Ngân hàng Bài tập ({exercises.length})</span>
            </button>

            <button
              onClick={() => setSidebarTab('submissions')}
              aria-current={sidebarTab === 'submissions' ? 'page' : undefined}
              aria-label="Giám sát bài nộp và AI"
              title="Giám sát bài nộp và AI"
              className={`flex h-10 w-10 shrink-0 items-center justify-center gap-2.5 rounded-xl px-2 py-2.5 text-sm transition-colors cursor-pointer lg:w-full lg:justify-start lg:px-3 ${
                sidebarTab === 'submissions'
                  ? 'bg-emerald-600 text-white font-bold shadow-soft dark:bg-emerald-500/20 dark:text-emerald-300 dark:border dark:border-emerald-500/30'
                  : 'text-muted hover:text-foreground hover:bg-surface-raised font-medium'
              }`}
            >
              <BarChart3 className="w-4 h-4 shrink-0" />
              <span className="hidden lg:inline">Giám sát Bài nộp & AI</span>
            </button>
          </nav>
        </div>

        {/* Bottom Actions */}
        <div className="flex shrink-0 items-center gap-1 border-l border-border p-1.5 lg:block lg:border-l-0 lg:border-t lg:p-4">
          <button
            onClick={() => {
              logout();
              navigate('/login');
            }}
            aria-label="Đăng xuất"
            title="Đăng xuất"
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition-all cursor-pointer shadow-soft lg:h-auto lg:w-full lg:justify-center lg:gap-2 lg:px-3 lg:py-2.5"
          >
            <LogOut className="w-3.5 h-3.5 text-white" />
            <span className="hidden lg:inline text-white">Đăng xuất</span>
          </button>
        </div>
      </aside>

      {/* 2. MAIN WORKSPACE CONTAINER */}
      <div className="min-h-0 min-w-0 flex-1 flex flex-col overflow-hidden lg:h-screen">
        {/* Top Workspace Header */}
        <header className="min-h-14 bg-surface border-b border-border px-2 sm:px-4 lg:px-6 py-2 flex items-center justify-between gap-2 shrink-0">
          <div className="min-w-0 flex items-center gap-2">
            <h2 className="truncate text-xs sm:text-sm font-semibold text-foreground flex items-center gap-2">
              {sidebarTab === 'classes' && <><School aria-hidden="true" className="size-4 shrink-0 text-emerald-600 dark:text-emerald-400" /><span>Quản lý Lớp học phần NEU</span></>}
              {sidebarTab === 'exercises' && <><BookOpen aria-hidden="true" className="size-4 shrink-0 text-emerald-600 dark:text-emerald-400" /><span>Ngân hàng Bài tập Python</span></>}
              {sidebarTab === 'submissions' && <><BarChart3 aria-hidden="true" className="size-4 shrink-0 text-emerald-600 dark:text-emerald-400" /><span>Giám sát Bài nộp & AI</span></>}
            </h2>
          </div>

          <div className="flex shrink-0 items-center gap-1 sm:gap-2">
            <ThemeToggle />
            <button
              type="button"
              onClick={loadDashboardData}
              aria-label="Làm mới dữ liệu"
              title="Làm mới dữ liệu"
              className="inline-flex size-10 items-center justify-center rounded-xl text-muted transition-colors hover:bg-surface-raised hover:text-foreground cursor-pointer"
            >
              <RefreshCw aria-hidden="true" className="size-4" />
            </button>

            <Link
              to="/instructor/exercises/new"
              aria-label="Thêm bài tập mới"
              className="inline-flex min-h-10 items-center justify-center gap-1.5 rounded-xl bg-emerald-600 px-3 text-sm font-semibold text-white transition-colors hover:bg-emerald-700 shadow-soft"
            >
              <Plus aria-hidden="true" className="size-4" />
              <span className="hidden sm:inline">Thêm bài tập mới</span>
            </Link>
          </div>
        </header>

        {/* Scrollable Workspace Body */}
        <main className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-6">
          {isLoading ? (
            <div className="rounded-2xl border border-border bg-surface shadow-soft" aria-busy="true">
              <TableLoading label="Đang tải dữ liệu giảng viên" />
            </div>
          ) : (
            <>
              {/* =========================================================================
                  SIDEBAR TAB 1: QUẢN LÝ LỚP HỌC PHẦN
              ========================================================================= */}
              {sidebarTab === 'classes' && (
                !selectedClass ? (
                  /* 1.1 DANH SÁCH LỚP HỌC PHẦN */
                  <div className="space-y-6">
                    <ClassesAttentionList classes={creditClasses} onOpen={handleSelectClass} />
                    {/* Top KPI row */}
                    {stats && (
                      <dl className="grid grid-cols-1 overflow-hidden rounded-xl border border-border bg-surface sm:grid-cols-3 sm:divide-x sm:divide-border">
                        {[
                          ['Lớp học phần phụ trách', creditClasses.length, 'Khoa Công nghệ thông tin'],
                          ['Sinh viên ghi danh', creditClasses.reduce((acc, c) => acc + (c.student_count || 0), 0), 'Tổng trên các lớp'],
                          ['Tỷ lệ đạt trung bình', `${stats.pass_rate_percentage}%`, `${stats.total_submissions} lượt nộp chính thức`],
                        ].map(([label, value, note]) => (
                          <div key={label} className="flex flex-col gap-1 border-b border-border p-4 last:border-b-0 sm:border-b-0">
                            <dt className="text-sm text-muted">{label}</dt>
                            <dd className="text-2xl font-semibold tabular-nums">{value}</dd>
                            <dd className="text-[0.8125rem] text-muted">{note}</dd>
                          </div>
                        ))}
                      </dl>
                    )}

                    {/* Button Mở Lớp Mới & Class Grid */}
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                      <div>
                        <h3 className="text-xl font-semibold tracking-tight">Lớp học phần tín chỉ</h3>
                        <p className="mt-1 text-sm text-muted">Chọn một lớp để quản lý lộ trình, tài liệu và danh sách sinh viên.</p>
                      </div>

                      <div className="flex flex-wrap items-center gap-2">
                        <div role="group" aria-label="Chế độ hiển thị danh sách lớp" className="flex items-center gap-1 rounded-lg bg-surface-raised p-1">
                          <button
                            type="button"
                            onClick={() => changeClassView('grid')}
                            aria-pressed={classViewMode === 'grid'}
                            title="Hiển thị dạng thẻ lưới"
                            className={`inline-flex min-h-9 items-center gap-1.5 rounded-md px-3 text-sm font-medium transition-colors ${classViewMode === 'grid' ? 'bg-surface text-foreground ring-1 ring-border' : 'text-muted hover:text-foreground'}`}
                          >
                            <LayoutGrid className="w-3.5 h-3.5" />
                            <span className="hidden sm:inline">Dạng lưới</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => changeClassView('list')}
                            aria-pressed={classViewMode === 'list'}
                            title="Hiển thị dạng danh sách"
                            className={`inline-flex min-h-9 items-center gap-1.5 rounded-md px-3 text-sm font-medium transition-colors ${classViewMode === 'list' ? 'bg-surface text-foreground ring-1 ring-border' : 'text-muted hover:text-foreground'}`}
                          >
                            <List className="w-3.5 h-3.5" />
                            <span className="hidden sm:inline">Dạng danh sách</span>
                          </button>
                        </div>
                        <button
                          type="button"
                          onClick={() => setIsCreatingClass(!isCreatingClass)}
                          aria-expanded={isCreatingClass}
                          aria-controls="create-class-form"
                          className={`inline-flex min-h-10 items-center gap-1.5 rounded-xl px-4 text-sm font-semibold transition-all shadow-soft cursor-pointer ${
                            isCreatingClass
                              ? 'border border-border bg-surface-raised hover:bg-surface text-foreground'
                              : 'bg-emerald-600 hover:bg-emerald-700 text-white'
                          }`}
                        >
                          <Plus aria-hidden="true" className={`size-4 transition-transform ${isCreatingClass ? 'rotate-45' : ''}`} />
                          <span>{isCreatingClass ? 'Đóng form' : 'Mở lớp học phần mới'}</span>
                        </button>
                      </div>
                    </div>

                    {/* Form Mở Lớp Học Phần Mới — một cột, label trên ô, kiểm tra khi rời ô */}
                    {isCreatingClass && (
                      <section id="create-class-form" aria-labelledby="create-class-title" className="rounded-xl border border-border bg-surface p-5">
                        <h4 id="create-class-title" className="text-base font-semibold">Thông tin lớp học phần mới</h4>
                        <p className="mt-1 text-sm text-muted">Trường có dấu * là bắt buộc.</p>
                        <form onSubmit={handleCreateClass} noValidate className="mt-4 max-w-xl space-y-4">
                          <Input
                            label="Mã lớp học phần"
                            required
                            placeholder="CNTT1116(126)_03"
                            value={classForm.class_code}
                            onChange={(e) => setClassForm({ ...classForm, class_code: e.target.value })}
                            onBlur={() => blurClassField('class_code')}
                            error={classFormErrors.class_code}
                            disabled={isSubmittingClass}
                            className="font-mono"
                            autoComplete="off"
                          />
                          <Input
                            label="Tên học phần"
                            required
                            placeholder="Lập trình Python cơ bản"
                            value={classForm.class_name}
                            onChange={(e) => setClassForm({ ...classForm, class_name: e.target.value })}
                            onBlur={() => blurClassField('class_name')}
                            error={classFormErrors.class_name}
                            disabled={isSubmittingClass}
                          />
                          <Input
                            label="Mã tham gia"
                            hint="Sinh viên dùng mã này để ghi danh. Để trống để hệ thống tự sinh."
                            placeholder="NEU-PY03"
                            value={classForm.enrollment_code}
                            onChange={(e) => setClassForm({ ...classForm, enrollment_code: e.target.value.toUpperCase() })}
                            onBlur={() => blurClassField('enrollment_code')}
                            error={classFormErrors.enrollment_code}
                            disabled={isSubmittingClass}
                            className="font-mono"
                            autoComplete="off"
                          />
                          <div className="flex flex-col-reverse gap-2 pt-1 sm:flex-row">
                            <Button type="submit" loading={isSubmittingClass}>
                              {isSubmittingClass ? 'Đang tạo lớp…' : 'Tạo lớp học phần'}
                            </Button>
                            <Button variant="secondary" onClick={() => { setIsCreatingClass(false); setClassFormErrors({}); }} disabled={isSubmittingClass}>
                              Hủy
                            </Button>
                          </div>
                        </form>
                      </section>
                    )}

                    {/* Class list view */}
                    {classViewMode === 'list' && (
                      creditClasses.length === 0 ? (
                        <p className="rounded-xl border border-dashed border-border bg-surface p-8 text-center text-sm text-muted">Bạn chưa có lớp học phần nào. Bấm “Mở lớp học phần mới” để tạo lớp đầu tiên.</p>
                      ) : (
                        <div className="overflow-x-auto rounded-xl border border-border bg-surface max-md:border-0 max-md:bg-transparent">
                          <table className="table-stack w-full min-w-[46rem] text-left text-sm">
                            <caption className="sr-only">Danh sách lớp học phần tín chỉ NEU</caption>
                            <thead>
                              <tr className="border-b border-slate-800 font-semibold text-slate-400">
                                <th scope="col" className="px-4 py-3">Mã lớp</th>
                                <th scope="col" className="px-4 py-3">Tên học phần</th>
                                <th scope="col" className="px-4 py-3 text-right">Tín chỉ</th>
                                <th scope="col" className="px-4 py-3">Học kỳ</th>
                                <th scope="col" className="px-4 py-3">Mã đăng ký</th>
                                <th scope="col" className="px-4 py-3 text-right">Sinh viên</th>
                                <th scope="col" className="px-4 py-3"><span className="sr-only">Thao tác</span></th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                              {creditClasses.map((cls) => (
                                <tr key={cls.id} className="transition-colors hover:bg-slate-800/60">
                                  <td className="whitespace-nowrap px-4 py-3 font-mono font-bold text-emerald-400">{cls.class_code}</td>
                                  <td className="px-4 py-3">
                                    <div className="font-semibold text-white">{cls.class_name}</div>
                                    <div className="text-[11px] text-slate-400">{cls.instructor_name || 'Nguyễn Văn A'}</div>
                                  </td>
                                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-200">{cls.credits || 3}</td>
                                  <td className="px-4 py-3 text-slate-300">{cls.semester || 'HK1 (2026-2027)'}</td>
                                  <td className="px-4 py-3 font-mono text-emerald-400">{cls.enrollment_code}</td>
                                  <td className="px-4 py-3 text-right font-mono tabular-nums text-slate-200">{cls.student_count || 0}</td>
                                  <td className="px-4 py-3 text-right">
                                    <button
                                      onClick={() => handleSelectClass(cls)}
                                      aria-label={`Quản lý chi tiết lớp ${cls.class_code}`}
                                      className="inline-flex min-h-9 items-center gap-1.5 whitespace-nowrap rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white px-3.5 text-xs font-semibold shadow-soft transition-colors cursor-pointer"
                                    >
                                      <span>Quản lý</span>
                                      <ChevronRight className="w-3.5 h-3.5" />
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )
                    )}

                    {/* Class Cards Grid */}
                    {classViewMode === 'grid' && (
                    <ul className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                      {creditClasses.map((cls) => (
                        <li key={cls.id} className="flex flex-col rounded-xl border border-border bg-surface transition-colors hover:border-muted/50">
                          <div className="flex-1 space-y-4 p-5">
                            <div>
                              <p className="flex items-center justify-between gap-3 text-[0.8125rem] text-muted">
                                <span className="font-mono">{cls.class_code}</span>
                                <span className="shrink-0">{cls.credits || 3} tín chỉ</span>
                              </p>
                              <h4 className="mt-2 text-base font-semibold leading-snug">{cls.class_name}</h4>
                              <p className="mt-1 text-sm text-muted">{cls.instructor_name || 'Nguyễn Văn A'}</p>
                            </div>
                            <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-sm">
                              <dt className="text-muted">Sinh viên</dt>
                              <dd className="text-right font-medium tabular-nums">{cls.student_count || 0}</dd>
                              <dt className="text-muted">Mã tham gia</dt>
                              <dd className="text-right font-mono">{cls.enrollment_code}</dd>
                              <dt className="text-muted">Học kỳ</dt>
                              <dd className="text-right">{cls.semester || 'HK1 (2026-2027)'}</dd>
                            </dl>
                          </div>
                          <div className="border-t border-border px-5 py-3">
                            <button
                              type="button"
                              className="inline-flex min-h-9 w-full items-center justify-center gap-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 text-sm font-semibold shadow-soft transition-colors cursor-pointer active:scale-95"
                              onClick={() => handleSelectClass(cls)}
                              aria-label={`Quản lý lớp ${cls.class_code} ${cls.class_name}`}
                            >
                              <span>Quản lý lớp</span>
                              <ChevronRight aria-hidden="true" className="size-4" />
                            </button>
                          </div>
                        </li>
                      ))}
                    </ul>
                    )}
                  </div>
                ) : (
                  /* 1.2 KHÔNG GIAN QUẢN TRỊ CHI TIẾT TỪNG LỚP HỌC PHẦN */
                  <div className="space-y-6">
                    {/* Header Chi tiết Lớp */}
                    <div className="rounded-xl border border-border bg-surface">
                      <div className="space-y-2 p-5 pb-0">
                        <button
                          type="button"
                          onClick={handleBackToClassList}
                          className="inline-flex min-h-9 items-center gap-1.5 rounded-lg border border-border bg-surface-raised hover:bg-surface px-3 text-xs font-semibold text-foreground transition-colors shadow-soft cursor-pointer"
                        >
                          <ArrowLeft aria-hidden="true" className="size-3.5" />
                          <span>Danh sách lớp</span>
                        </button>
                        <h3 className="text-2xl font-semibold tracking-tight">{selectedClass.class_name}</h3>
                        <p className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted">
                          <span className="font-mono">{selectedClass.class_code}</span>
                          <span>Mã tham gia <span className="font-mono text-foreground">{selectedClass.enrollment_code}</span></span>
                          <span>{selectedClass.credits || 3} tín chỉ</span>
                          <span>{selectedClass.semester}</span>
                        </p>
                      </div>

                      <div role="tablist" aria-label="Quản lý lớp học phần" className="mt-4 flex gap-1 overflow-x-auto border-t border-border px-3">
                        {[
                          ['insights', 'Góc nhìn sư phạm', BarChart3],
                          ['curriculum', `Lộ trình (${curriculumList.length})`, BookOpen],
                          ['knowledge', 'Tài liệu cho Gia sư AI', Sparkles],
                          ['students', `Sinh viên (${studentRoster.length})`, Users],
                        ].map(([id, label, Icon]) => (
                          <button
                            key={id}
                            type="button"
                            role="tab"
                            aria-selected={classSubTab === id}
                            onClick={() => setClassSubTab(id)}
                            className={`-mb-px inline-flex min-h-11 shrink-0 items-center gap-2 border-b-2 px-3 text-sm font-semibold transition-colors cursor-pointer ${
                              classSubTab === id
                                ? 'border-emerald-600 text-emerald-600 dark:border-emerald-400 dark:text-emerald-400 font-bold'
                                : 'border-transparent text-muted hover:text-foreground font-medium'
                            }`}
                          >
                            <Icon aria-hidden="true" className="size-4" />
                            {label}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Sub-tab v5.3 (S3.1): góc nhìn sư phạm theo lớp */}
                    {classSubTab === 'insights' && (
                      <ClassInsightsPanel key={selectedClass.id} classId={selectedClass.id} onOpenTab={setClassSubTab} />
                    )}

                    {/* Sub-tab v5.4 (C): tài liệu cho Gia sư AI theo lớp */}
                    {classSubTab === 'knowledge' && (
                      <ClassKnowledgePanel key={selectedClass.id} classId={selectedClass.id} />
                    )}

                    {/* Sub-tab 1: Curriculum & Skill Matrix */}
                    {classSubTab === 'curriculum' && (
                      <div className="space-y-6">
                        {/* Form gán bài tập — một cột, thứ tự trường giữ nguyên, kiểm tra khi rời ô */}
                        <section aria-labelledby="assign-title" className="rounded-xl border border-border bg-surface p-5">
                          <h4 id="assign-title" className="text-base font-semibold">Gán bài tập từ ngân hàng đề vào lộ trình</h4>
                          <p className="mt-1 text-sm text-muted">Trường có dấu * là bắt buộc.</p>
                          <form onSubmit={handleAssignExercise} noValidate className="mt-4 max-w-xl space-y-4">
                            <Input
                              as="select"
                              label="Bài tập trong ngân hàng"
                              required
                              value={assignExerciseForm.exercise_id}
                              onChange={(e) => setAssignExerciseForm({ ...assignExerciseForm, exercise_id: e.target.value })}
                              onBlur={() => blurAssignField('exercise_id')}
                              error={assignFormErrors.exercise_id}
                            >
                              {exercises.map(ex => (
                                <option key={ex.id} value={ex.id}>
                                  {ex.title} ({ex.difficulty} - {ex.category})
                                </option>
                              ))}
                            </Input>
                            <Input
                              label="Tên chương / module"
                              required
                              placeholder="Chương 1: Cú pháp & Vòng lặp"
                              value={assignExerciseForm.module_name}
                              onChange={(e) => setAssignExerciseForm({ ...assignExerciseForm, module_name: e.target.value })}
                              onBlur={() => blurAssignField('module_name')}
                              error={assignFormErrors.module_name}
                            />
                            <Input
                              label="Thứ tự trong lộ trình"
                              hint="Số nhỏ hiển thị trước. Bài đầu tiên là 1."
                              type="number"
                              min="1"
                              inputMode="numeric"
                              value={assignExerciseForm.order_idx}
                              onChange={(e) => setAssignExerciseForm({ ...assignExerciseForm, order_idx: Number(e.target.value) })}
                              onBlur={() => blurAssignField('order_idx')}
                              error={assignFormErrors.order_idx}
                              className="max-w-40 tabular-nums"
                            />
                            <Input
                              as="select"
                              label="Bài tiên quyết"
                              hint="Sinh viên phải hoàn thành bài này trước khi mở khóa bài đang gán."
                              value={assignExerciseForm.prerequisite_id}
                              onChange={(e) => setAssignExerciseForm({ ...assignExerciseForm, prerequisite_id: e.target.value })}
                            >
                              <option value="">(Không có tiên quyết)</option>
                              {curriculumList.map(c => (
                                <option key={c.exercise_id} value={c.exercise_id}>
                                  {c.title || c.exercise_id}
                                </option>
                              ))}
                            </Input>
                            <div>
                              <Input
                                label="Kỹ năng đầu ra (Khớp đơn vị kiến thức KC)"
                                placeholder="Ví dụ: Vòng lặp For & Biến tích lũy, Xử lý tệp tin..."
                                list="kc-skill-tags"
                                value={assignExerciseForm.skill_tag}
                                onChange={(e) => setAssignExerciseForm({ ...assignExerciseForm, skill_tag: e.target.value })}
                              />
                              <datalist id="kc-skill-tags">
                                {knowledgeComponents.map(k => (
                                  <option key={k.kc} value={k.label_vi} />
                                ))}
                              </datalist>
                            </div>
                            <Button type="submit">
                              <Plus aria-hidden="true" className="size-4" />
                              Gán vào lộ trình lớp
                            </Button>
                          </form>
                        </section>

                        {/* Curriculum Table */}
                        <div className="p-5 rounded-2xl bg-surface border border-border space-y-3 shadow-soft">
                          <h4 className="text-base font-semibold text-foreground">
                            Danh Sách Bài Tập Học Phần ({curriculumList.length} bài)
                          </h4>

                          {isLoadingCurriculum ? (
                            <TableLoading label="Đang tải bài tập trong lộ trình lớp" />
                          ) : curriculumList.length === 0 ? (
                            <div className="py-8 text-center text-muted text-xs">Chưa có bài tập nào trong lộ trình lớp.</div>
                          ) : (
                            <>
                            <TableControls
                              label="Tìm bài tập trong lộ trình lớp"
                              query={curriculumSearch}
                              onQueryChange={(value) => { setCurriculumSearch(value); setCurriculumPage(1); }}
                              placeholder="Tìm theo tên bài, mã bài, chương hoặc kỹ năng"
                              total={filteredCurriculum.length}
                              page={curriculumPageData.page}
                              pageCount={curriculumPageData.pageCount}
                              onPageChange={setCurriculumPage}
                            />
                            <div className="max-h-[min(60vh,36rem)] overflow-auto rounded-xl border border-border">
                              <table className="table-stack min-w-[52rem] w-full text-left text-xs">
                                <thead className="sticky top-0 z-10 bg-surface-raised">
                                  <tr className="border-b border-border text-muted font-semibold">
                                    <th className="py-2.5 px-3">#</th>
                                    <th className="py-2.5 px-3">Chương / Module</th>
                                    <th className="py-2.5 px-3">Bài tập</th>
                                    <th className="py-2.5 px-3">Tiên quyết</th>
                                    <th className="py-2.5 px-3">Kỹ năng</th>
                                    <th className="py-2.5 px-3 text-right">Thao tác</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-border">
                                  {curriculumPageData.items.length === 0 ? (
                                    <tr><td colSpan={6} className="px-3 py-8 text-center text-muted">Không tìm thấy bài tập phù hợp. Hãy thử từ khóa khác.</td></tr>
                                  ) : curriculumPageData.items.map((item) => (
                                    <tr key={item.id} className="transition-colors hover:bg-surface-raised">
                                      <td className="py-3 px-3 font-mono font-bold text-muted">#{item.order_idx}</td>
                                      <td className="py-3 px-3 font-medium text-emerald-600 dark:text-emerald-400">{item.module_name}</td>
                                      <td className="py-3 px-3">
                                        <div className="font-bold text-foreground">{item.title}</div>
                                        <div className="text-[10px] text-muted font-mono">{item.exercise_id}</div>
                                      </td>
                                      <td className="py-3 px-3 font-mono text-muted">
                                        {item.prerequisite_id || '(Không)'}
                                      </td>
                                      <td className="py-3 px-3 text-foreground">{item.skill_tag}</td>
                                      <td className="py-3 px-3 text-right">
                                        <button
                                          onClick={() => handleRemoveExercise(item.exercise_id)}
                                          className="p-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 dark:bg-rose-500/20 dark:hover:bg-rose-500/30 dark:text-rose-300 dark:border-rose-500/30 transition-colors cursor-pointer shadow-soft"
                                          title="Gỡ khỏi lớp"
                                          aria-label={`Gỡ ${item.title} khỏi lớp`}
                                        >
                                          <Trash2 className="w-3.5 h-3.5" />
                                        </button>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                            </>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Sub-tab 2: Exam & Practice Sessions */}
                    {false && classSubTab === 'sessions' && (
                      <div className="space-y-6">
                        {/* Form Tạo Kỳ Thi Mới cho Lớp */}
                        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
                          <h4 className="text-base font-semibold flex items-center space-x-1.5">
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
                      <div className="p-5 rounded-2xl bg-surface border border-border space-y-4 shadow-soft">
                        <div className="flex items-center justify-between">
                          <h4 className="text-base font-semibold text-foreground">
                            Danh Sách Sinh Viên Ghi Danh & Đo Lường Tiến Độ ({studentRoster.length} SV)
                          </h4>
                        </div>

                        {isLoadingRoster ? (
                          <TableLoading label="Đang tải danh sách sinh viên" />
                        ) : studentRoster.length === 0 ? (
                          <div className="py-8 text-center text-muted text-xs">Chưa có sinh viên nào ghi danh vào lớp.</div>
                        ) : (
                          <>
                          <TableControls
                            label="Tìm sinh viên trong lớp"
                            query={rosterSearch}
                            onQueryChange={(value) => { setRosterSearch(value); setRosterPage(1); }}
                            placeholder="Tìm theo tên hoặc tài khoản sinh viên"
                            total={filteredRoster.length}
                            page={rosterPageData.page}
                            pageCount={rosterPageData.pageCount}
                            onPageChange={setRosterPage}
                          />
                          <div className="max-h-[min(60vh,36rem)] overflow-auto rounded-xl border border-border">
                            <table className="table-stack min-w-[52rem] w-full text-left text-xs">
                              <thead className="sticky top-0 z-10 bg-surface-raised">
                                <tr className="border-b border-border text-muted font-semibold">
                                  <th className="py-2.5 px-3">#</th>
                                  <th className="py-2.5 px-3">Sinh Viên</th>
                                  <th className="py-2.5 px-3">Tài Khoản</th>
                                  <th className="py-2.5 px-3 text-center">Tiến Độ Giải Bài</th>
                                  <th className="py-2.5 px-3 text-center">Điểm nỗ lực</th>
                                  <th className="py-2.5 px-3 text-right">Thời Gian Tham Gia</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-border">
                                {rosterPageData.items.length === 0 ? (
                                  <tr><td colSpan={6} className="px-3 py-8 text-center text-muted">Không tìm thấy sinh viên phù hợp. Hãy thử tên hoặc tài khoản khác.</td></tr>
                                ) : rosterPageData.items.map((st, idx) => (
                                  <tr key={st.student_username || st.username || idx} className="transition-colors hover:bg-surface-raised">
                                    <td className="py-3 px-3 font-mono text-muted">{rosterPageData.startIndex + idx + 1}</td>
                                    <td className="py-3 px-3 font-semibold text-foreground">{st.full_name || st.student_username || st.username}</td>
                                    <td className="py-3 px-3 font-mono text-emerald-600 dark:text-emerald-400">@{st.student_username || st.username}</td>
                                    <td className="py-3 px-3 text-center">
                                      <span className="font-bold text-foreground">{st.completed_exercises ?? st.solved_count ?? 0}/{st.total_exercises ?? 0} bài</span>
                                      <span className="text-muted ml-1">({Math.round(st.progress_percent || 0)}%)</span>
                                    </td>
                                    <td className="py-3 px-3 text-center font-bold text-amber-600 dark:text-amber-400">
                                      {st.total_stars ?? st.stars_earned ?? 0} ⭐
                                    </td>
                                    <td className="py-3 px-3 text-right text-muted text-[11px]">
                                      {st.enrolled_at || 'Mới ghi danh'}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                          </>
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
                      <h3 className="text-sm font-bold text-foreground">Ngân Hàng Bài Tập Lập Trình Python ({exercises.length})</h3>
                      <p className="text-xs text-muted">Các bài tập trong cơ sở dữ liệu SQLite, sẵn sàng gán vào lớp học phần</p>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => { setShowKcModal(true); loadKnowledgeComponents(); }}
                        className="py-2 px-3.5 bg-surface hover:bg-slate-800 text-slate-200 border border-border rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow-soft transition-colors"
                      >
                        <Layers className="w-4 h-4 text-emerald-400" />
                        <span>Đơn vị kiến thức (KCs)</span>
                      </button>

                      <Link
                        to="/instructor/exercises/new"
                        className="py-2 px-3.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow-soft"
                      >
                        <Plus className="w-4 h-4" />
                        <span>Thêm bài tập mới</span>
                      </Link>
                    </div>
                  </div>

                  <div className="rounded-2xl bg-surface border border-border overflow-hidden shadow-soft">
                    <TableControls
                      label="Tìm trong ngân hàng bài tập"
                      query={exerciseSearch}
                      onQueryChange={(value) => { setExerciseSearch(value); setExercisePage(1); }}
                      placeholder="Tìm theo mã bài, tiêu đề, độ khó hoặc chủ đề"
                      total={filteredExercises.length}
                      page={exercisePageData.page}
                      pageCount={exercisePageData.pageCount}
                      onPageChange={setExercisePage}
                    />
                    <div className="max-h-[min(65vh,40rem)] overflow-auto">
                    <table className="table-stack min-w-[52rem] w-full text-left text-xs">
                      <thead className="sticky top-0 z-10 bg-surface-raised">
                        <tr className="border-b border-border text-muted font-semibold">
                          <th className="py-2.5 px-3">Mã Bài</th>
                          <th className="py-2.5 px-3">Tiêu Đề</th>
                          <th className="py-2.5 px-3">Độ Khó</th>
                          <th className="py-2.5 px-3">Chủ Đề</th>
                          <th className="py-2.5 px-3">Người thêm</th>
                          <th className="py-2.5 px-3 text-center">Test Cases</th>
                          <th className="py-2.5 px-3 text-right">Thao Tác</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                        {exercisePageData.items.length === 0 ? (
                          <tr><td colSpan={7} className="px-3 py-8 text-center text-muted">Không tìm thấy bài tập phù hợp. Hãy thử từ khóa khác.</td></tr>
                        ) : exercisePageData.items.map((ex) => (
                          <tr key={ex.id} className="transition-colors hover:bg-surface-raised">
                            <td className="py-3 px-3 font-mono text-emerald-600 dark:text-emerald-400 font-semibold">{ex.id}</td>
                            <td className="py-3 px-3 font-semibold text-foreground">{ex.title}</td>
                            <td className="py-3 px-3">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                ex.difficulty === 'Dễ' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-400' :
                                ex.difficulty === 'Trung bình' ? 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-400' : 'bg-rose-100 text-rose-800 dark:bg-rose-500/20 dark:text-rose-400'
                              }`}>
                                {ex.difficulty}
                              </span>
                            </td>
                            <td className="py-3 px-3 text-foreground">{ex.category}</td>
                            <td className="py-3 px-3 text-muted">{ex.created_by_name || (['system', 'seed', ''].includes(ex.created_by) ? 'Hệ thống' : ex.created_by)}</td>
                            <td className="py-3 px-3 text-center font-mono text-muted">{ex.test_cases_count}</td>
                            <td className="py-3 px-3 text-right space-x-2">
                              {ex.can_manage && <>
                              <Link
                                to={`/instructor/exercises/${ex.id}/edit`}
                                className="p-1.5 rounded-lg bg-surface-raised hover:bg-surface text-foreground border border-border inline-block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
                                title="Chỉnh sửa"
                                aria-label={`Chỉnh sửa ${ex.title}`}
                              >
                                <Edit2 className="w-3.5 h-3.5" />
                              </Link>
                              <button
                                onClick={() => handleDeleteExercise(ex.id)}
                                className="p-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 dark:bg-rose-500/20 dark:hover:bg-rose-500/30 dark:text-rose-300 dark:border-rose-500/30 transition-colors cursor-pointer shadow-soft"
                                title="Xóa"
                                aria-label={`Xóa bài tập ${ex.title}`}
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={async () => {
                                  const recipient = window.prompt('Nhập tài khoản giảng viên được phép sử dụng bài tập này:');
                                  if (!recipient?.trim()) return;
                                  try {
                                    await shareInstructorExercise(ex.id, recipient.trim());
                                    alert(`Đã chia sẻ bài tập với ${recipient.trim()}.`);
                                  } catch (error) {
                                    alert(error.response?.data?.detail || 'Không thể chia sẻ bài tập.');
                                  }
                                }}
                                className="p-1.5 rounded-lg bg-sky-50 hover:bg-sky-100 text-sky-700 border border-sky-200 dark:bg-sky-500/20 dark:hover:bg-sky-500/30 dark:text-sky-300 dark:border-sky-500/30 transition-colors cursor-pointer shadow-soft"
                                title="Cho phép giảng viên khác sử dụng"
                                aria-label={`Chia sẻ ${ex.title}`}
                              >
                                <Users className="w-3.5 h-3.5" />
                              </button>
                              </>}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    </div>
                  </div>
                </div>
              )}

              {/* =========================================================================
                  SIDEBAR TAB 3: GIÁM SÁT BÀI NỘP & AI
              ========================================================================= */}
              {sidebarTab === 'submissions' && (
                <div className="space-y-4">
                  {/* v5.3 (S1.2, S3.3): tổng hợp đánh giá phản hồi AI và nguồn kiến thức RAG */}
                  <TutorFeedbackPanel />
                  <KnowledgeBasePanel />

                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-bold text-foreground">Lịch Sử Nộp Bài Toàn Hệ Thống ({submissions.length})</h3>
                      <p className="text-xs text-muted">Theo dõi thời gian thực kết quả chạy sandbox và phản hồi sư phạm của AI</p>
                    </div>

                    <div className="flex items-center space-x-2">
                      <select
                        value={submissionFilter}
                        onChange={(e) => { setSubmissionFilter(e.target.value); setSubmissionPage(1); }}
                        className="bg-surface border border-border rounded-xl px-2.5 py-1.5 text-xs text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
                      >
                        <option value="ALL">Tất cả trạng thái</option>
                        <option value="PASSED">Chỉ bài ĐẠT (Passed)</option>
                        <option value="FAILED">Chỉ bài CHƯA ĐẠT (Failed)</option>
                      </select>

                      <button
                        onClick={handleExportCSV}
                        className="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs flex items-center space-x-1.5 shadow-soft cursor-pointer"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Xuất CSV (Excel)</span>
                      </button>
                    </div>
                  </div>

                  <div className="rounded-2xl bg-surface border border-border overflow-hidden shadow-soft">
                    <TableControls
                      label="Tìm trong lịch sử nộp bài"
                      query={submissionSearch}
                      onQueryChange={(value) => { setSubmissionSearch(value); setSubmissionPage(1); }}
                      placeholder="Tìm theo sinh viên, bài tập hoặc nguồn AI"
                      total={filteredSubmissions.length}
                      page={submissionPageData.page}
                      pageCount={submissionPageData.pageCount}
                      onPageChange={setSubmissionPage}
                    />
                    <div className="max-h-[min(65vh,40rem)] overflow-auto">
                    <table className="table-stack min-w-[60rem] w-full text-left text-xs">
                      <thead className="sticky top-0 z-10 bg-surface-raised">
                        <tr className="border-b border-border text-muted font-semibold">
                          <th className="py-2.5 px-3">Thời Gian</th>
                          <th className="py-2.5 px-3">Sinh Viên</th>
                          <th className="py-2.5 px-3">Bài Tập</th>
                          <th className="py-2.5 px-3 text-center">Kết quả chấm</th>
                          <th className="py-2.5 px-3 text-center">Điểm nỗ lực</th>
                          <th className="py-2.5 px-3">Nguồn AI</th>
                          <th className="py-2.5 px-3 text-right">Chi Tiết</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                        {submissionPageData.items.length === 0 ? (
                          <tr><td colSpan={7} className="px-3 py-8 text-center text-muted">Không tìm thấy bài nộp phù hợp. Hãy đổi từ khóa hoặc bộ lọc.</td></tr>
                        ) : submissionPageData.items.map((sub) => (
                          <tr key={sub.id} className="transition-colors hover:bg-surface-raised">
                            <td className="py-3 px-3 text-muted text-[11px] font-mono">
                              {(sub.timestamp || sub.submitted_at)?.slice(5, 16) || 'Vừa xong'}
                            </td>
                            <td className="py-3 px-3 font-semibold text-foreground">@{sub.session_id}</td>
                            <td className="py-3 px-3 font-mono text-emerald-600 dark:text-emerald-400 font-medium">{sub.exercise_id}</td>
                            <td className="py-3 px-3 text-center">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                sub.all_passed ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-400' : 'bg-rose-100 text-rose-800 dark:bg-rose-500/20 dark:text-rose-400'
                              }`}>
                                {sub.passed_tests}/{sub.total_tests} Pass
                              </span>
                            </td>
                            <td className="py-3 px-3 text-center font-bold text-amber-600 dark:text-amber-400">
                              {sub.stars_earned || 0} ⭐
                            </td>
                            <td className="py-3 px-3 text-muted text-[11px] font-mono">
                              {sub.llm_source || 'AI Tutor'}
                            </td>
                            <td className="py-3 px-3 text-right">
                              <button
                                onClick={() => setSelectedSubmission(sub)}
                                className="p-1.5 rounded-lg bg-surface-raised hover:bg-surface text-foreground border border-border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer"
                                title="Xem chi tiết"
                                aria-label={`Xem bài nộp của ${sub.session_id}`}
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
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {/* MODAL CHI TIẾT BÀI NỘP */}
      {selectedSubmission && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm select-text">
          <div className="w-full max-w-3xl max-h-[90vh] flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-bento overflow-hidden">
            <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-950">
              <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center space-x-2">
                <span>Chi tiết bài nộp của @{selectedSubmission.session_id}</span>
                <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400">({selectedSubmission.exercise_id})</span>
              </h3>
              <button
                onClick={() => setSelectedSubmission(null)}
                className="p-1 rounded-lg text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 shadow-soft">
                  <div className="text-slate-500 dark:text-slate-400 text-[10px] font-medium">Kết quả chấm</div>
                  <div className="font-bold text-sm mt-0.5 text-emerald-600 dark:text-emerald-400">
                    {selectedSubmission.passed_tests}/{selectedSubmission.total_tests} Pass
                  </div>
                </div>
                <div className="p-3 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 shadow-soft">
                  <div className="text-slate-500 dark:text-slate-400 text-[10px] font-medium">Điểm nỗ lực</div>
                  <div className="font-bold text-sm mt-0.5 text-amber-600 dark:text-amber-400">
                    {selectedSubmission.stars_earned || 0} ⭐
                  </div>
                </div>
                <div className="p-3 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 shadow-soft">
                  <div className="text-slate-500 dark:text-slate-400 text-[10px] font-medium">Nguồn AI</div>
                  <div className="font-mono text-xs mt-0.5 text-slate-700 dark:text-slate-300">
                    {selectedSubmission.llm_source || 'AI'}
                  </div>
                </div>
                <div className="p-3 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 shadow-soft">
                  <div className="text-slate-500 dark:text-slate-400 text-[10px] font-medium">Thời gian</div>
                  <div className="font-mono text-[11px] mt-0.5 text-slate-700 dark:text-slate-300">
                    {selectedSubmission.timestamp || selectedSubmission.submitted_at || 'Vừa xong'}
                  </div>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-semibold text-slate-800 dark:text-slate-300">Mã nguồn nộp bài:</span>
                  <button
                    onClick={() => handleCopyCode(selectedSubmission.code || selectedSubmission.submitted_code)}
                    className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold flex items-center space-x-1 cursor-pointer hover:underline"
                  >
                    {copiedCode ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedCode ? 'Đã chép' : 'Sao chép code'}</span>
                  </button>
                </div>
                <pre className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 font-mono text-xs text-emerald-700 dark:text-emerald-300 overflow-x-auto max-h-60 shadow-soft">
                  {selectedSubmission.code || selectedSubmission.submitted_code}
                </pre>
              </div>

              {selectedSubmission.tutor_hint && (
                <div className="p-4 rounded-2xl bg-amber-50/70 dark:bg-slate-950 border border-amber-200 dark:border-slate-800 space-y-1 shadow-soft">
                  <span className="font-semibold text-amber-800 dark:text-amber-300">Lời khuyên của Gia sư AI:</span>
                  <p className="text-slate-800 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {selectedSubmission.tutor_hint}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal Quản lý Đơn vị kiến thức (KCs) */}
      {showKcModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in">
          <div className="bg-surface border border-border w-full max-w-3xl rounded-3xl p-6 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                  <Layers className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-foreground">Quản Lý Đơn Vị Kiến Thức (Knowledge Components - KCs)</h3>
                  <p className="text-xs text-muted">Các đơn vị kỹ năng cốt lõi được Mô hình người học và Gia sư AI theo dõi thích ứng</p>
                </div>
              </div>
              <button
                onClick={() => { setShowKcModal(false); setKcMessage(null); }}
                className="p-1.5 text-muted hover:text-foreground rounded-lg hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {kcMessage && (
              <div className={`p-3 rounded-xl text-xs font-medium flex items-center space-x-2 ${
                kcMessage.type === 'success' 
                  ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400' 
                  : 'bg-rose-500/10 border border-rose-500/30 text-rose-400'
              }`}>
                {kcMessage.type === 'success' ? <CheckCircle className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
                <span>{kcMessage.text}</span>
              </div>
            )}

            {/* Form thêm KC mới */}
            <form onSubmit={handleCreateKc} className="p-4 rounded-2xl bg-surface-muted border border-border space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-foreground flex items-center space-x-1.5">
                  <Plus className="w-4 h-4 text-emerald-400" />
                  <span>Định nghĩa Đơn vị kiến thức mới</span>
                </h4>
                <span className="text-[11px] text-muted">Mở rộng động cho môn học</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-semibold text-muted block mb-1">Tên hiển thị (Tiếng Việt) *</label>
                  <input
                    type="text"
                    placeholder="Ví dụ: Xử lý tệp tin (File I/O)"
                    value={kcForm.label_vi}
                    onChange={(e) => setKcForm({ ...kcForm, label_vi: e.target.value })}
                    className="w-full text-xs rounded-xl bg-surface border border-border px-3 py-2 text-foreground focus:ring-1 focus:ring-emerald-500 outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-muted block mb-1">Mã định danh (Slug - Tùy chọn)</label>
                  <input
                    type="text"
                    placeholder="Tự sinh nếu để trống (ví dụ: file_io)"
                    value={kcForm.kc}
                    onChange={(e) => setKcForm({ ...kcForm, kc: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '') })}
                    className="w-full text-xs rounded-xl bg-surface border border-border px-3 py-2 text-foreground font-mono focus:ring-1 focus:ring-emerald-500 outline-none"
                  />
                </div>
              </div>
              <div>
                <label className="text-[11px] font-semibold text-muted block mb-1">Từ khóa nhận diện tự động (cách nhau bởi dấu phẩy) *</label>
                <input
                  type="text"
                  placeholder="Ví dụ: file, tep tin, open, doc ghi, ghi tep"
                  value={kcForm.keywords}
                  onChange={(e) => setKcForm({ ...kcForm, keywords: e.target.value })}
                  className="w-full text-xs rounded-xl bg-surface border border-border px-3 py-2 text-foreground focus:ring-1 focus:ring-emerald-500 outline-none"
                  required
                />
                <p className="text-[10px] text-muted mt-1">Khi giảng viên gán bài tập có chứa các từ khóa này ở tên chương, thẻ kỹ năng hay mô tả, hệ thống sẽ tự động gán vào KC này.</p>
              </div>
              <div className="flex justify-end pt-1">
                <Button type="submit" disabled={isSubmittingKc || !kcForm.label_vi.trim()}>
                  {isSubmittingKc ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                  <span>Lưu Đơn vị kiến thức</span>
                </Button>
              </div>
            </form>

            {/* Danh sách KCs hiện có */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-foreground">Danh mục KCs đang hoạt động ({knowledgeComponents.length})</h4>
              {isLoadingKcs ? (
                <TableLoading label="Đang tải danh sách đơn vị kiến thức" />
              ) : (
                <div className="rounded-2xl border border-border overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-surface-muted text-muted border-b border-border">
                      <tr>
                        <th className="py-2.5 px-3 font-semibold">Đơn vị kiến thức</th>
                        <th className="py-2.5 px-3 font-semibold">Nguồn gốc</th>
                        <th className="py-2.5 px-3 font-semibold">Từ khóa nhận diện</th>
                        <th className="py-2.5 px-3 font-semibold text-right">Thao tác</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border text-foreground">
                      {knowledgeComponents.map(k => (
                        <tr key={k.kc} className="hover:bg-surface-muted/50 transition-colors">
                          <td className="py-2.5 px-3">
                            <div className="font-semibold text-foreground">{k.label_vi}</div>
                            <div className="font-mono text-[10px] text-muted">{k.kc}</div>
                          </td>
                          <td className="py-2.5 px-3">
                            {k.created_by === 'system' ? (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                                Hạt nhân hệ thống
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
                                @{k.created_by}
                              </span>
                            )}
                          </td>
                          <td className="py-2.5 px-3">
                            <div className="flex flex-wrap gap-1 max-w-sm">
                              {k.keywords && k.keywords.length > 0 ? (
                                k.keywords.map((kw, idx) => (
                                  <span key={idx} className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-slate-300">
                                    {kw}
                                  </span>
                                ))
                              ) : (
                                <span className="text-[10px] text-muted italic">Mặc định mọi bài</span>
                              )}
                            </div>
                          </td>
                          <td className="py-2.5 px-3 text-right">
                            {k.created_by !== 'system' ? (
                              <button
                                onClick={() => handleDeleteKc(k.kc)}
                                className="p-1.5 text-muted hover:text-rose-400 rounded-lg hover:bg-rose-500/10 transition-colors"
                                title="Xóa đơn vị kiến thức"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            ) : (
                              <span className="text-[11px] text-muted italic">Mặc định</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
