import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  ArrowLeft, BookOpen, Code2, LayoutDashboard, UserRound, Sparkles,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Badge, Button } from './ui';
import ThemeToggle from './ThemeToggle';

export default function Header({
  onOpenProfile,
  backUrl = null,
  backLabel = 'Quay lại Lớp học phần',
}) {
  const { user, isInstructor } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isInstructorPage = location.pathname.startsWith('/instructor');
  const homeUrl = isInstructor ? '/instructor' : '/student';
  const displayName = user?.role === 'student'
    ? (user?.full_name || user?.username || 'Sinh viên').split(' - ')[0]
    : user?.full_name;
  const initials = user?.role === 'student'
    ? 'TK'
    : (user?.full_name || 'GV').split(/\s+/).slice(-2).map((part) => part[0]).join('').toUpperCase();

  return (
    <header className="sticky top-0 z-30 flex min-h-16 shrink-0 items-center justify-between gap-3 border-b border-border/80 bg-surface/90 backdrop-blur-md px-3 sm:px-6">
      <div className="flex min-w-0 items-center gap-3">
        {backUrl ? (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => navigate(backUrl)}
            title={backLabel}
            aria-label={backLabel}
            className="shrink-0 px-3"
          >
            <ArrowLeft aria-hidden="true" className="size-4" />
            <span className="hidden sm:inline">{backLabel}</span>
          </Button>
        ) : (
          <Link
            to={homeUrl}
            aria-label="PyTutor - Trang chủ"
            className="flex size-9 shrink-0 items-center justify-center rounded-full bg-emerald-500 text-white shadow-soft transition-transform active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          >
            <BookOpen aria-hidden="true" className="size-4" />
          </Link>
        )}

        <div className="flex min-w-0 items-center gap-2.5">
          <Link to={homeUrl} className="truncate text-base font-bold tracking-tight text-foreground transition-colors hover:text-emerald-500">
            PyTutor
          </Link>
          <Badge variant="success" className="hidden min-h-5 whitespace-nowrap px-2.5 py-0.5 text-[10px] sm:inline-flex">
            NEU LMS
          </Badge>
        </div>
      </div>

      <nav aria-label="Tài khoản và điều hướng" className="flex shrink-0 items-center gap-2">
        {onOpenProfile && (
          <Button
            variant="secondary"
            size="sm"
            onClick={onOpenProfile}
            title="Xem hành trình học của bạn"
            aria-label="Mở Hành trình học"
            className="px-3"
          >
            <BookOpen aria-hidden="true" className="size-3.5 text-emerald-500" />
            <span className="hidden md:inline">Hành trình học</span>
          </Button>
        )}

        {isInstructor && (
          isInstructorPage ? (
            <Link
              to="/"
              title="Vào màn hình làm bài của sinh viên"
              aria-label="Mở IDE làm bài"
              className="inline-flex min-h-8 items-center gap-1.5 rounded-full border border-emerald-300 bg-emerald-50 px-3 text-xs font-semibold text-emerald-800 hover:bg-emerald-100 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary shadow-soft"
            >
              <Code2 aria-hidden="true" className="size-3.5" />
              <span className="hidden md:inline">IDE làm bài</span>
            </Link>
          ) : (
            <Link
              to="/instructor"
              title="Vào Dashboard quản lý bài tập của Giảng viên"
              aria-label="Mở Dashboard giảng viên"
              className="inline-flex min-h-8 items-center gap-1.5 rounded-full border border-amber-300 bg-amber-50 px-3 text-xs font-semibold text-amber-800 hover:bg-amber-100 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-warning shadow-soft"
            >
              <LayoutDashboard aria-hidden="true" className="size-3.5" />
              <span className="hidden md:inline">Dashboard GV</span>
            </Link>
          )
        )}

        {user ? (
          <div className="flex min-h-9 items-center gap-2 rounded-full border border-border/80 bg-surface-raised px-2.5 py-1 shadow-soft" title={displayName}>
            <span aria-hidden="true" className="flex size-6 shrink-0 items-center justify-center rounded-full bg-slate-950 text-[10px] font-bold text-white dark:bg-emerald-500">
              {initials}
            </span>
            <span className="hidden max-w-36 truncate text-xs font-semibold text-foreground lg:inline">{displayName}</span>
            <Badge variant={user.role === 'instructor' ? 'warning' : 'neutral'} className="min-h-5 px-2 py-0 text-[10px]">
              <UserRound aria-hidden="true" className="size-3 sm:hidden" />
              <span className="hidden sm:inline">{user.role === 'instructor' ? 'Giảng viên' : 'Sinh viên'}</span>
            </Badge>
          </div>
        ) : (
          <Link
            to="/login"
            className="inline-flex min-h-8 items-center rounded-full bg-emerald-500 px-4 text-xs font-semibold text-white transition-colors hover:bg-emerald-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary shadow-soft"
          >
            Đăng nhập
          </Link>
        )}

        <ThemeToggle />
      </nav>
    </header>
  );
}
