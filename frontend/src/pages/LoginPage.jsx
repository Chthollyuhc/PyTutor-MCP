import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, Lock, User, ArrowRight, ShieldCheck, GraduationCap, 
  School, Cpu, BookOpen, CheckCircle2, Terminal, Code2
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (u, p) => {
    setError('');
    setIsLoading(true);
    try {
      const userData = await login(u, p);
      if (userData.role === 'instructor') {
        navigate('/instructor');
      } else {
        navigate('/student');
      }
    } catch (err) {
      console.error('Lỗi đăng nhập:', err);
      setError(err.response?.data?.detail || 'Tên đăng nhập hoặc mật khẩu không chính xác.');
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmitForm = (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.');
      return;
    }
    handleLogin(username.trim(), password.trim());
  };

  return (
    <div className="min-h-screen w-screen flex items-stretch bg-slate-950 text-slate-100 font-sans select-none overflow-x-hidden">
      {/* CỘT TRÁI: HERO & ARCHITECTURE SHOWCASE */}
      <div className="hidden lg:flex lg:w-7/12 relative flex-col justify-between p-12 bg-gradient-to-br from-slate-900 via-slate-950 to-emerald-950/40 border-r border-slate-800/80">
        {/* Glow Effects */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Top Header info */}
        <div className="relative z-10">
          <div className="inline-flex items-center space-x-2.5 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-6 shadow-sm">
            <School className="w-4 h-4" />
            <span>KHOA CÔNG NGHỆ THÔNG TIN • ĐẠI HỌC KINH TẾ QUỐC DÂN (NEU)</span>
          </div>

          <div className="flex items-center space-x-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20">
              <Code2 className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center space-x-2">
                <span>PyTutor-MCP</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono font-medium">v5.0 Enterprise</span>
              </h1>
              <p className="text-sm text-slate-400 font-medium">Hệ thống Quản lý Học tập & Gia sư Lập trình Thông minh (LMS-ITS)</p>
            </div>
          </div>

          <p className="text-slate-300 text-sm max-w-xl leading-relaxed mt-4">
            Nền tảng đào tạo lập trình Python thích ứng theo học chế tín chỉ NEU, kết hợp mô hình lớp học phần chuyên nghiệp với Gia sư AI Socratic và động cơ 8 MCP Tools.
          </p>
        </div>

        {/* 3 Thẻ Trụ cột Cốt lõi */}
        <div className="relative z-10 space-y-4 my-8">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 hover:border-emerald-500/30 transition-all flex items-start space-x-4">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 shrink-0">
              <School className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
                <span>Quản lý Đào tạo theo Lớp Học phần Tín chỉ NEU</span>
                <span className="text-[10px] px-1.5 py-0.5 bg-blue-500/20 text-blue-300 rounded font-mono">CNTT1128 • CNTT1187</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Chuẩn hóa cấu trúc môn học, đa lớp học phần, ma trận kỹ năng DAG có thang đo định lượng (Mastery Rubrics) và phân tách rõ ràng chế độ Luyện tập vs Kỳ thi.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 hover:border-emerald-500/30 transition-all flex items-start space-x-4">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
                <span>Gia sư AI Thích ứng 3 Cấp độ (Scaffolding Pedagogy)</span>
                <span className="text-[10px] px-1.5 py-0.5 bg-emerald-500/20 text-emerald-300 rounded font-mono">Anti-Spoil Guard</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Gemini 3.5 Flash Lite gợi mở từng nấc tư duy sư phạm, chốt chặn không lộ code giải, khuyến khích sinh viên tự sửa lỗi để nhận trọn vẹn 3 Sao tự lực.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 hover:border-emerald-500/30 transition-all flex items-start space-x-4">
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 shrink-0">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
                <span>Động cơ 8 MCP Tools Chuẩn JSON-RPC 2.0</span>
                <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/20 text-purple-300 rounded font-mono">OS Sandbox 5s • Tracer</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Hộp cát thực thi cô lập chống vô hạn lặp, phân tích cây cú pháp AST tĩnh, truy vết từng dòng lệnh và lưu vết tiến bộ học viên vào SQLite WAL.
              </p>
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div className="relative z-10 pt-4 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-500">
          <span>Khoa Công nghệ thông tin • Đại học Kinh tế Quốc dân (NEU)</span>
          <span className="flex items-center space-x-1.5 text-emerald-400/80">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Multi-Stage LMS & IDE Architecture</span>
          </span>
        </div>
      </div>

      {/* CỘT PHẢI: FORM ĐĂNG NHẬP & 1-CLICK DEMO CHO HỘI ĐỒNG */}
      <div className="w-full lg:w-5/12 flex flex-col justify-center items-center p-6 sm:p-12 relative bg-slate-950">
        <div className="w-full max-w-md bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl backdrop-blur-sm">
          {/* Logo Mobile / Small screen header */}
          <div className="lg:hidden text-center mb-6">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white mx-auto mb-3 shadow-lg shadow-emerald-500/20">
              <Code2 className="w-6 h-6" />
            </div>
            <h1 className="text-xl font-bold tracking-wide text-white">
              PyTutor-MCP <span className="text-xs text-emerald-400 font-mono">v5.0</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Khoa Công nghệ thông tin • Đại học Kinh tế Quốc dân (NEU)
            </p>
          </div>

          <div className="mb-6">
            <h2 className="text-xl font-bold text-white tracking-tight">Cổng Đăng Nhập Đào Tạo</h2>
            <p className="text-xs text-slate-400 mt-1">Nhập tài khoản sinh viên hoặc giảng viên để truy cập không gian học tập.</p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
              {error}
            </div>
          )}

          {/* Form Login */}
          <form onSubmit={onSubmitForm} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Tên đăng nhập / Mã định danh</label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="student hoặc gv_tran"
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Mật khẩu</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-lg pl-9 pr-3 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-semibold text-sm transition-all shadow-lg shadow-emerald-900/30 flex items-center justify-center space-x-2 disabled:opacity-50 cursor-pointer"
            >
              {isLoading ? (
                <span>Đang xác thực tài khoản...</span>
              ) : (
                <>
                  <span>Đăng nhập Cổng NEU</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Access (1-Click Demo cho Hội đồng Chấm Đồ án) */}
          <div className="mt-6 pt-5 border-t border-slate-800/80">
            <div className="flex items-center justify-between mb-2.5">
              <span className="text-[11px] font-bold text-amber-400 uppercase tracking-wider flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                <span>1-Click Demo cho Hội Đồng Chấm:</span>
              </span>
              <span className="text-[10px] text-slate-500">Bấm để vào ngay</span>
            </div>

            <div className="space-y-2 text-xs">
              {/* Nút 1: Sinh viên NEU */}
              <button
                type="button"
                onClick={() => handleLogin('student', 'student123')}
                className="w-full p-2.5 rounded-lg border border-emerald-500/30 bg-emerald-500/5 hover:bg-emerald-500/15 text-slate-200 text-left transition-all cursor-pointer flex items-center justify-between group"
              >
                <div className="flex items-center space-x-2.5">
                  <div className="w-7 h-7 rounded-md bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                    <GraduationCap className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="font-semibold text-xs text-white group-hover:text-emerald-300 transition-colors">
                      Sinh viên NEU: Trần Minh Khánh
                    </div>
                    <div className="text-[10px] text-slate-400 font-mono">MSV: 11236131 • K65 CNTT (student / student123)</div>
                  </div>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-medium">/student ▶</span>
              </button>

              {/* Nút 2: Giảng viên 1 */}
              <button
                type="button"
                onClick={() => handleLogin('gv_tran', 'gv123')}
                className="w-full p-2.5 rounded-lg border border-amber-500/30 bg-amber-500/5 hover:bg-amber-500/15 text-slate-200 text-left transition-all cursor-pointer flex items-center justify-between group"
              >
                <div className="flex items-center space-x-2.5">
                  <div className="w-7 h-7 rounded-md bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="font-semibold text-xs text-white group-hover:text-amber-300 transition-colors">
                      Giảng viên 1: Nguyễn Văn A
                    </div>
                    <div className="text-[10px] text-slate-400 font-mono">Khoa CNTT - NEU (gv_tran / gv123)</div>
                  </div>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-medium">/instructor ▶</span>
              </button>

              {/* Nút 3: Giảng viên 2 */}
              <button
                type="button"
                onClick={() => handleLogin('gv_tuan', 'gv123')}
                className="w-full p-2.5 rounded-lg border border-cyan-500/30 bg-cyan-500/5 hover:bg-cyan-500/15 text-slate-200 text-left transition-all cursor-pointer flex items-center justify-between group"
              >
                <div className="flex items-center space-x-2.5">
                  <div className="w-7 h-7 rounded-md bg-cyan-500/20 text-cyan-400 flex items-center justify-center shrink-0">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="font-semibold text-xs text-white group-hover:text-cyan-300 transition-colors">
                      Giảng viên 2: Trần Văn B
                    </div>
                    <div className="text-[10px] text-slate-400 font-mono">Khoa CNTT - NEU (gv_tuan / gv123)</div>
                  </div>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-medium">/instructor ▶</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
