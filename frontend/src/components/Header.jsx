import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Sparkles, BookOpen, User, LayoutDashboard, Code2, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Header({
  health,
  isDarkTheme,
  setIsDarkTheme,
  onOpenInspector,
  onOpenProfile,
  mcpTraceCount = 0,
  backUrl = null,
  backLabel = 'Quay lại Lớp học phần'
}) {
  const { user, isInstructor } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isConnected = health?.mcp_server_connected;
  const tools = health?.discovered_tools || [];

  const isInstructorPage = location.pathname.startsWith('/instructor');
  const homeUrl = isInstructor ? '/instructor' : '/student';

  return (
    <header className="h-14 bg-slate-950 border-b border-slate-800 px-4 flex items-center justify-between select-none shrink-0 z-20">
      {/* Left: Brand & Optional Back button */}
      <div className="flex items-center space-x-3">
        {backUrl ? (
          <button
            onClick={() => navigate(backUrl)}
            type="button"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 font-semibold text-xs transition-all cursor-pointer shadow-sm"
            title="Quay lại không gian lớp học phần"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>⬅️ {backLabel}</span>
          </button>
        ) : (
          <Link to={homeUrl} className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-bold hover:opacity-90 transition-opacity">
            <Sparkles className="w-4 h-4" />
          </Link>
        )}

        <div className="flex items-center space-x-2">
          <Link to={homeUrl} className="font-bold text-white tracking-wide text-sm sm:text-base hover:text-emerald-400 transition-colors">
            PyTutor
          </Link>
          <span className="text-[10.5px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
            v5.0 Enterprise LMS
          </span>
        </div>
      </div>

      {/* Center: MCP Connection (Compact Pill Button) */}
      <div className="flex items-center space-x-2">
        <button
          onClick={onOpenInspector}
          type="button"
          className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/50 text-xs text-slate-300 transition-all cursor-pointer shadow-sm group"
          title="Bấm để xem chi tiết 8 công cụ MCP và nhật ký giao thức JSON-RPC"
        >
          <span
            className={`w-2 h-2 rounded-full transition-all ${
              isConnected
                ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)] animate-pulse'
                : 'bg-rose-500'
            }`}
          />
          <span className="font-medium text-emerald-400 group-hover:text-emerald-300">
            ⚡ MCP ({tools.length || 8})
          </span>
          <span className="text-[10px] text-slate-500 group-hover:text-slate-400 font-mono hidden lg:inline">
            🔍 JSON-RPC
          </span>
        </button>
      </div>

      {/* Right: Nhật ký học tập, Thông tin sinh viên & Theme Toggle */}
      <div className="flex items-center space-x-2 sm:space-x-2.5">
        {/* Nút Nhật ký học tập (Màn hình Sinh viên) */}
        {onOpenProfile && (
          <button
            onClick={onOpenProfile}
            type="button"
            className="flex items-center space-x-1.5 px-2.5 py-1 text-xs font-medium text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 rounded-lg transition-colors cursor-pointer"
            title="Xem nhật ký học tập, số bài hoàn thành và lịch sử nạp lại code"
          >
            <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden sm:inline">📒 Nhật ký học tập</span>
            <span className="sm:hidden">📒 Nhật ký</span>
          </button>
        )}

        {/* Chuyển đổi giữa IDE Làm bài & Bảng điều khiển Giảng viên (chỉ hiện khi là Giảng viên) */}
        {isInstructor && (
          isInstructorPage ? (
            <Link
              to="/"
              className="flex items-center space-x-1.5 px-2.5 py-1 text-xs font-medium text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 rounded-lg transition-colors"
              title="Vào màn hình làm bài của sinh viên"
            >
              <Code2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">IDE Làm bài</span>
            </Link>
          ) : (
            <Link
              to="/instructor"
              className="flex items-center space-x-1.5 px-2.5 py-1 text-xs font-medium text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 rounded-lg transition-colors"
              title="Vào Dashboard quản lý bài tập của Giảng viên"
            >
              <LayoutDashboard className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Dashboard GV</span>
            </Link>
          )
        )}

        {/* Thông tin Người dùng & Vai trò (Không có nút đăng xuất trong giao diện code) */}
        {user ? (
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-lg text-xs">
            <User className="w-3.5 h-3.5 text-slate-400" />
            <span className="font-medium text-slate-200 hidden md:inline">
              {user.role === 'student' ? 'Trần Minh Khánh - SV K65 CNTT (MSV: 11236131)' : user.full_name}
            </span>
            <span
              className={`text-[10px] px-1.5 py-0.2 rounded font-bold uppercase ${
                user.role === 'instructor'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
              }`}
            >
              {user.role === 'instructor' ? 'Giảng viên' : 'Sinh viên'}
            </span>
          </div>
        ) : (
          <Link
            to="/login"
            className="text-xs px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition-colors"
          >
            Đăng nhập
          </Link>
        )}

        {/* Nút Đổi Theme Editor */}
        <button
          onClick={() => setIsDarkTheme(!isDarkTheme)}
          className="text-xs px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 transition-colors cursor-pointer"
          title="Đổi giao diện Editor Tối / Sáng"
        >
          {isDarkTheme ? '🌙' : '☀️'}
        </button>
      </div>
    </header>
  );
}
