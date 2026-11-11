import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  ArrowLeft, BookOpen, Code2, LayoutDashboard, UserRound,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Badge, Button } from './ui';
import ThemeToggle from './ThemeToggle';

export default function Header({
  health,
  onOpenInspector,
  onOpenProfile,
  mcpTraceCount = 0,
  backUrl = null,
  backLabel = 'Quay lại Lớp học phần',
}) {
  const { user, isInstructor } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isConnected = health?.mcp_server_connected;
  const tools = health?.discovered_tools || [];
  const isInstructorPage = location.pathname.startsWith('/instructor');
  const homeUrl = isInstructor ? '/instructor' : '/student';
  const displayName = user?.role === 'student'
    ? (user?.full_name || user?.username || 'Sinh viên').split(' - ')[0]
    : user?.full_name;
  const initials = user?.role === 'student'
    ? 'TK'
    : (user?.full_name || 'GV').split(/\s+/).slice(-2).map((part) => part[0]).join('').toUpperCase();

  return (
    <header className="relative z-20 flex min-h-16 shrink-0 items-center justify-between gap-3 border-b border-border bg-surface px-3 sm:px-5 lg:px-6">
      <div className="flex min-w-0 items-center gap-3">
        {backUrl ? (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => navigate(backUrl)}
            title={backLabel}
            aria-label={backLabel}
            className="shrink-0 px-2.5 sm:px-3"
          >
            <ArrowLeft aria-hidden="true" className="size-4" />
            <span className="hidden sm:inline">{backLabel}</span>
          </Button>
        ) : (
          <Link
            to={homeUrl}
            aria-label="PyTutor - Trang chủ"
          className="flex size-9 shrink-0 items-center justify-center rounded-md border border-border bg-surface-raised text-primary transition-colors hover:bg-surface focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          >
            <BookOpen aria-hidden="true" className="size-4" />
          </Link>
        )}

        <div className="flex min-w-0 items-center gap-2.5">
          <Link to={homeUrl} className="truncate text-sm font-bold tracking-tight text-white transition-colors hover:text-emerald-200 sm:text-base">
            PyTutor
          </Link>
          <Badge variant="success" className="hidden min-h-5 whitespace-nowrap px-2 py-0.5 text-[10px] sm:inline-flex">
            v5.0 Enterprise LMS
          </Badge>
        </div>
      </div>

      <Button
        variant="secondary"
        size="sm"
        onClick={onOpenInspector}
        title={`Mở công cụ MCP và nhật ký JSON-RPC${mcpTraceCount ? ` · ${mcpTraceCount} bản ghi` : ''}`}
        aria-label={`Trạng thái MCP ${isConnected ? 'đã kết nối' : 'chưa kết nối'}, ${tools.length || 8} công cụ`}
        className="shrink-0 rounded-full px-2.5 sm:px-3"
      >
        <span aria-hidden="true" className={`size-2 rounded-full ${isConnected ? 'bg-emerald-400 shadow-[0_0_0_3px_rgba(16,185,129,0.12)]' : 'bg-rose-400'}`} />
        <span className={isConnected ? 'text-emerald-200' : 'text-rose-200'}>MCP {tools.length || 8}</span>
        <span className="hidden text-xs font-normal text-muted lg:inline">JSON-RPC</span>
      </Button>

      <nav aria-label="Tài khoản và điều hướng" className="flex shrink-0 items-center gap-1.5 sm:gap-2">
        {onOpenProfile && (
          <Button
            variant="success"
            size="sm"
            onClick={onOpenProfile}
            title="Xem nhật ký học tập, số bài hoàn thành và lịch sử nạp lại code"
            aria-label="Mở nhật ký học tập"
            className="px-2.5 sm:px-3"
          >
            <BookOpen aria-hidden="true" className="size-4" />
            <span className="hidden md:inline">Nhật ký học tập</span>
          </Button>
        )}

        {isInstructor && (
          isInstructorPage ? (
            <Link
              to="/"
              title="Vào màn hình làm bài của sinh viên"
              aria-label="Mở IDE làm bài"
              className="inline-flex min-h-9 items-center gap-2 rounded-xl border border-primary/30 bg-primary/10 px-2.5 text-xs font-medium text-emerald-200 transition-colors hover:bg-primary/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary sm:px-3"
            >
              <Code2 aria-hidden="true" className="size-4" />
              <span className="hidden md:inline">IDE làm bài</span>
            </Link>
          ) : (
            <Link
              to="/instructor"
              title="Vào Dashboard quản lý bài tập của Giảng viên"
              aria-label="Mở Dashboard giảng viên"
              className="inline-flex min-h-9 items-center gap-2 rounded-xl border border-warning/30 bg-warning/10 px-2.5 text-xs font-medium text-amber-100 transition-colors hover:bg-warning/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-warning sm:px-3"
            >
              <LayoutDashboard aria-hidden="true" className="size-4" />
              <span className="hidden md:inline">Dashboard GV</span>
            </Link>
          )
        )}

        {user ? (
          <div className="flex min-h-10 items-center gap-2 rounded-xl border border-border bg-canvas px-2 sm:gap-2.5 sm:px-3" title={displayName}>
            <span aria-hidden="true" className="flex size-7 shrink-0 items-center justify-center rounded-full bg-surface-raised text-[10px] font-semibold text-slate-200">
              {initials}
            </span>
            <span className="hidden max-w-44 truncate text-xs font-medium text-slate-200 lg:inline">{displayName}</span>
            <Badge variant={user.role === 'instructor' ? 'warning' : 'success'} className="min-h-5 px-2 py-0.5 text-[10px]">
              <UserRound aria-hidden="true" className="size-3 sm:hidden" />
              <span className="hidden sm:inline">{user.role === 'instructor' ? 'Giảng viên' : 'Sinh viên'}</span>
            </Badge>
          </div>
        ) : (
          <Link
            to="/login"
            className="inline-flex min-h-9 items-center rounded-xl bg-primary px-3 text-xs font-semibold text-primary-foreground transition-colors hover:bg-primary-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-surface"
          >
            Đăng nhập
          </Link>
        )}

        <ThemeToggle className="size-9" />
      </nav>
    </header>
  );
}
