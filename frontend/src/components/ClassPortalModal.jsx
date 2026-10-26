import React, { useState, useEffect } from 'react';
import {
  fetchMyClasses,
  fetchClasses,
  enrollClass,
  enrollClassByCode,
  leaveClass
} from '../services/api';

/**
 * ClassPortalModal - Cổng Quản lý & Đăng ký Lớp học phần chuẩn NEU (Khoa Công nghệ thông tin)
 * Hỗ trợ sinh viên:
 * 1. Xem danh sách lớp học phần đã ghi danh, tiến độ học tập và chọn lớp đang học
 * 2. Ghi danh lớp mới bằng Mã tham gia lớp (Enrollment Code) hoặc đăng ký trực tiếp
 * 3. Hủy ghi danh / rời khỏi lớp học phần
 */
const ClassPortalModal = ({
  isOpen,
  onClose,
  currentClassId,
  onSelectClass,
  currentUsername = 'student'
}) => {
  const [activeTab, setActiveTab] = useState('my_classes'); // 'my_classes' | 'browse'
  const [myClasses, setMyClasses] = useState([]);
  const [allClasses, setAllClasses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [enrollCodeInput, setEnrollCodeInput] = useState('');
  const [actionMessage, setActionMessage] = useState(null);
  const [actionError, setActionError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setActionMessage(null);
    setActionError(null);
    try {
      const [myRes, allRes] = await Promise.all([
        fetchMyClasses().catch(() => []),
        fetchClasses(null, currentUsername).catch(() => [])
      ]);
      setMyClasses(myRes);
      setAllClasses(allRes);
    } catch (err) {
      console.error('Lỗi khi tải dữ liệu lớp học phần:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleEnrollByCode = async (e) => {
    e.preventDefault();
    if (!enrollCodeInput.trim()) return;

    setActionMessage(null);
    setActionError(null);
    try {
      const res = await enrollClassByCode(enrollCodeInput.trim());
      setActionMessage(res.message || 'Ghi danh thành công!');
      setEnrollCodeInput('');
      await loadData();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Không thể ghi danh bằng mã này.';
      setActionError(msg);
    }
  };

  const handleQuickEnroll = async (classId) => {
    setActionMessage(null);
    setActionError(null);
    try {
      const res = await enrollClass(classId);
      setActionMessage(res.message || 'Đã ghi danh vào lớp thành công!');
      await loadData();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Lỗi khi ghi danh.';
      setActionError(msg);
    }
  };

  const handleLeaveClass = async (classId, className) => {
    if (!window.confirm(`Bạn có chắc chắn muốn rời khỏi lớp "${className}"?`)) {
      return;
    }
    setActionMessage(null);
    setActionError(null);
    try {
      const res = await leaveClass(classId);
      setActionMessage(res.message || 'Đã rời lớp học phần.');
      await loadData();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Lỗi khi rời lớp.';
      setActionError(msg);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden animate-in fade-in zoom-in duration-200">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-xl shadow-lg shadow-sky-950/40">
              🏫
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white tracking-wide">
                  Cổng Quản lý Lớp Học Phần NEU
                </h2>
                <span className="text-xs px-2 py-0.5 rounded-full font-semibold bg-sky-950 text-sky-400 border border-sky-800">
                  Khoa CNTT - NEU
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Hệ thống Quản lý Học tập & Lộ trình Thực hành Tín chỉ (LMS + ITS)
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-slate-800 bg-slate-950/30 px-6 pt-2 gap-2">
          <button
            onClick={() => setActiveTab('my_classes')}
            className={`px-4 py-2.5 text-sm font-semibold rounded-t-lg transition-all flex items-center gap-2 ${
              activeTab === 'my_classes'
                ? 'bg-slate-800 text-sky-400 border-t-2 border-sky-500 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <span>📚 Lớp Học Phần Của Tôi</span>
            <span className="px-1.5 py-0.2 rounded-full text-xs bg-slate-700 text-slate-200">
              {myClasses.length}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('browse')}
            className={`px-4 py-2.5 text-sm font-semibold rounded-t-lg transition-all flex items-center gap-2 ${
              activeTab === 'browse'
                ? 'bg-slate-800 text-sky-400 border-t-2 border-sky-500 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <span>🔍 Đăng ký & Ghi danh Lớp Mới</span>
            <span className="px-1.5 py-0.2 rounded-full text-xs bg-slate-700 text-slate-200">
              {allClasses.length}
            </span>
          </button>
        </div>

        {/* Notification alerts */}
        {actionMessage && (
          <div className="mx-6 mt-4 p-3 bg-emerald-950/70 border border-emerald-800/80 rounded-xl text-emerald-300 text-xs flex items-center justify-between">
            <span className="flex items-center gap-2">
              <span>✅</span> {actionMessage}
            </span>
            <button onClick={() => setActionMessage(null)} className="text-emerald-400 hover:text-white">✕</button>
          </div>
        )}
        {actionError && (
          <div className="mx-6 mt-4 p-3 bg-rose-950/70 border border-rose-800/80 rounded-xl text-rose-300 text-xs flex items-center justify-between">
            <span className="flex items-center gap-2">
              <span>⚠️</span> {actionError}
            </span>
            <button onClick={() => setActionError(null)} className="text-rose-400 hover:text-white">✕</button>
          </div>
        )}

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-4">
          {loading ? (
            <div className="py-16 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
              <div className="w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin" />
              <span>Đang tải thông tin lớp học phần NEU...</span>
            </div>
          ) : activeTab === 'my_classes' ? (
            /* TAB 1: MY CLASSES */
            <div>
              {myClasses.length === 0 ? (
                <div className="text-center py-12 px-4 border border-dashed border-slate-800 rounded-2xl bg-slate-950/20">
                  <div className="text-4xl mb-3">🎓</div>
                  <h3 className="text-base font-semibold text-slate-300">
                    Bạn chưa ghi danh vào lớp học phần nào!
                  </h3>
                  <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                    Chuyển sang tab "Đăng ký & Ghi danh Lớp Mới" hoặc nhập Mã tham gia do Giảng viên cung cấp để bắt đầu thực hành.
                  </p>
                  <button
                    onClick={() => setActiveTab('browse')}
                    className="mt-4 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-sky-950/40"
                  >
                    🔍 Xem Danh Sách Lớp
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {myClasses.map((cls) => {
                    const isSelected = cls.id === currentClassId;
                    const progress = cls.progress_percent || 0;
                    return (
                      <div
                        key={cls.id}
                        className={`p-4 rounded-xl border transition-all flex flex-col justify-between ${
                          isSelected
                            ? 'bg-slate-800/90 border-sky-500 shadow-md shadow-sky-950/30'
                            : 'bg-slate-950/40 border-slate-800 hover:border-slate-700'
                        }`}
                      >
                        <div>
                          {/* Class header badge */}
                          <div className="flex items-start justify-between gap-2 mb-2">
                            <div>
                              <span className="font-mono text-xs px-2 py-0.5 rounded bg-sky-950 text-sky-300 font-bold border border-sky-800/80">
                                {cls.class_code}
                              </span>
                              <h4 className="text-sm font-bold text-white mt-1.5 line-clamp-1">
                                {cls.class_name}
                              </h4>
                            </div>
                            {isSelected && (
                              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 shrink-0">
                                Đang chọn
                              </span>
                            )}
                          </div>

                          {/* Instructor & Faculty Info */}
                          <div className="text-xs text-slate-400 space-y-1 my-2">
                            <div className="flex items-center gap-1.5">
                              <span className="text-slate-500">👨‍🏫</span>
                              <span className="text-slate-300 font-medium">{cls.instructor_name || 'Nguyễn Văn A'}</span>
                            </div>
                            <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                              <span>🏛️ {cls.faculty || 'Khoa Công nghệ thông tin - NEU'}</span>
                              <span>•</span>
                              <span>{cls.credits || 3} Tín chỉ</span>
                            </div>
                            <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                              <span>📅 {cls.semester || 'Học kỳ 1'}</span>
                              <span>•</span>
                              <span className="font-mono text-sky-400 font-semibold">Mã: {cls.enrollment_code}</span>
                            </div>
                          </div>

                          {/* Progress bar */}
                          <div className="mt-3 pt-3 border-t border-slate-800/80">
                            <div className="flex justify-between items-center text-xs mb-1">
                              <span className="text-slate-400">Tiến độ bài tập lớp</span>
                              <span className="font-semibold text-sky-300">
                                {cls.completed_in_class || 0} / {cls.exercise_count || 0} bài ({progress}%)
                              </span>
                            </div>
                            <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                              <div
                                className="bg-gradient-to-r from-sky-500 to-indigo-500 h-1.5 rounded-full transition-all duration-500"
                                style={{ width: `${Math.min(100, Math.max(progress, 0))}%` }}
                              />
                            </div>
                          </div>
                        </div>

                        {/* Card action buttons */}
                        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
                          <button
                            onClick={() => {
                              if (onSelectClass) onSelectClass(cls);
                              onClose();
                            }}
                            className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all ${
                              isSelected
                                ? 'bg-sky-600/30 text-sky-300 border border-sky-600/50 hover:bg-sky-600/40'
                                : 'bg-sky-600 hover:bg-sky-500 text-white shadow-md shadow-sky-950/30'
                            }`}
                          >
                            {isSelected ? '✓ Tiếp tục học lớp này' : '👉 Vào học lớp này'}
                          </button>
                          <button
                            onClick={() => handleLeaveClass(cls.id, cls.class_name)}
                            title="Rời khỏi lớp học phần"
                            className="p-1.5 text-slate-500 hover:text-rose-400 hover:bg-rose-950/30 rounded-lg transition-colors border border-transparent hover:border-rose-900/50 text-xs"
                          >
                            Rời lớp
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ) : (
            /* TAB 2: BROWSE & ENROLL */
            <div className="space-y-6">
              {/* Form Enroll by code */}
              <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl">
                <h4 className="text-xs font-bold uppercase tracking-wider text-sky-400 mb-2 flex items-center gap-1.5">
                  <span>🔑</span> Ghi danh bằng Mã Lớp (Enrollment Code)
                </h4>
                <p className="text-xs text-slate-400 mb-3">
                  Nhập mã tham gia do Giảng viên Khoa Công nghệ thông tin cấp (ví dụ: <code className="text-sky-300 font-mono">NEU-PY01</code>, <code className="text-sky-300 font-mono">NEU-PY02</code>, <code className="text-sky-300 font-mono">NEU-DA01</code>):
                </p>
                <form onSubmit={handleEnrollByCode} className="flex gap-2">
                  <input
                    type="text"
                    value={enrollCodeInput}
                    onChange={(e) => setEnrollCodeInput(e.target.value)}
                    placeholder="Nhập mã ghi danh (e.g. NEU-PY01)"
                    className="flex-1 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 uppercase font-mono"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-sky-950/40 transition-colors shrink-0"
                  >
                    Ghi danh ngay
                  </button>
                </form>
              </div>

              {/* List of all classes */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
                  <span>Tất cả Lớp học phần đang mở ({allClasses.length})</span>
                  <span className="text-[11px] text-slate-500 font-normal">Học kỳ 1 (2026-2027)</span>
                </h4>
                <div className="space-y-3">
                  {allClasses.map((cls) => {
                    const isEnrolled = cls.is_enrolled || myClasses.some((m) => m.id === cls.id);
                    return (
                      <div
                        key={cls.id}
                        className="p-4 bg-slate-950/40 border border-slate-800 hover:border-slate-700 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4 transition-colors"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-mono text-xs px-2 py-0.5 rounded bg-sky-950 text-sky-300 font-bold border border-sky-800/80">
                              {cls.class_code}
                            </span>
                            <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">
                              Môn: {cls.course_code || 'CNTT1116'} ({cls.credits || 3} TC)
                            </span>
                            <span className="text-[11px] text-slate-500">
                              Mã lớp: <span className="font-mono text-slate-300 font-bold">{cls.enrollment_code}</span>
                            </span>
                          </div>
                          <h4 className="text-sm font-bold text-white">
                            {cls.class_name}
                          </h4>
                          <p className="text-xs text-slate-400 flex items-center gap-2 flex-wrap">
                            <span>👨‍🏫 {cls.instructor_name || 'Nguyễn Văn A'}</span>
                            <span>•</span>
                            <span>🏛️ {cls.faculty || 'Khoa Công nghệ thông tin - NEU'}</span>
                            <span>•</span>
                            <span>👥 {cls.student_count || 0} SV</span>
                            <span>•</span>
                            <span>📖 {cls.exercise_count || 0} bài tập</span>
                          </p>
                        </div>

                        <div className="shrink-0 flex items-center gap-2">
                          {isEnrolled ? (
                            <span className="px-3 py-1.5 rounded-lg bg-emerald-950/60 text-emerald-400 border border-emerald-800/80 text-xs font-semibold flex items-center gap-1.5">
                              <span>✓</span> Đã ghi danh
                            </span>
                          ) : (
                            <button
                              onClick={() => handleQuickEnroll(cls.id)}
                              className="px-4 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-sky-950/30 transition-colors"
                            >
                              + Ghi danh lớp
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/60 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Đại học Kinh tế Quốc dân (NEU) • Khoa Công nghệ thông tin</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg font-medium transition-colors"
          >
            Đóng
          </button>
        </div>

      </div>
    </div>
  );
};

export default ClassPortalModal;
