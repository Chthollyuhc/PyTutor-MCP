import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, ChevronDown, RotateCcw, X } from 'lucide-react';
import { fetchStudentJourney } from '../services/api';
import { useAuth } from '../context/AuthContext';
import TodayCard from './plain/TodayCard';
import StorySteps from './plain/StorySteps';

/** Hành trình học (v5.9, lời thường): thẻ hôm nay, bài đang mở, các bài gần đây. Mọi câu nhận xét lấy từ backend. */

function RecentExercise({ item, classId, onOpenExercise }) {
  const [open, setOpen] = useState(false);
  const [state, setState] = useState({ loading: false, error: false, story: null });
  const toggle = () => {
    const next = !open;
    setOpen(next);
    if (next && !state.story && !state.loading) {
      setState({ loading: true, error: false, story: null });
      fetchStudentJourney(classId, item.exercise_id)
        .then((res) => setState({ loading: false, error: false, story: res.current?.story || null }))
        .catch(() => setState({ loading: false, error: true, story: null }));
    }
  };
  return (
    <li className="rounded-2xl border border-border bg-surface">
      <button
        type="button"
        aria-expanded={open}
        onClick={toggle}
        className="flex w-full cursor-pointer items-center justify-between gap-3 rounded-2xl p-3 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
      >
        <span className="min-w-0">
          <span className="block break-words text-sm font-semibold text-foreground">{item.title}</span>
          <span className="block text-xs text-muted">{item.story_vi}</span>
        </span>
        <ChevronDown aria-hidden="true" className={`size-4 shrink-0 text-muted transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="space-y-3 border-t border-border p-3">
          {state.loading && <p className="text-xs text-muted">Đang tải…</p>}
          {state.error && <p role="alert" className="text-xs text-destructive-strong">Chưa tải được bài này. Thử lại sau.</p>}
          {state.story && <StorySteps story={state.story} />}
          {onOpenExercise && (
            <button
              type="button"
              onClick={() => onOpenExercise(item.exercise_id)}
              className="inline-flex min-h-8 cursor-pointer items-center rounded-full border border-border px-3 text-xs font-semibold text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
            >
              Mở bài này
            </button>
          )}
        </div>
      )}
    </li>
  );
}

export default function StudentProfileModal({ isOpen, onClose, classId, currentExerciseId, onLoadCode }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [journey, setJourney] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const closeRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return undefined;
    let cancelled = false;
    setIsLoading(true);
    setLoadError(false);
    fetchStudentJourney(classId, currentExerciseId || '')
      .then((data) => { if (!cancelled) setJourney(data); })
      .catch((err) => {
        console.error('Lỗi khi tải Hành trình học:', err);
        if (!cancelled) { setJourney(null); setLoadError(true); }
      })
      .finally(() => { if (!cancelled) setIsLoading(false); });
    return () => { cancelled = true; };
  }, [isOpen, classId, currentExerciseId, reloadKey]);

  useEffect(() => {
    if (!isOpen) return undefined;
    closeRef.current?.focus();
    const onKey = (event) => { if (event.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  const openExercise = useCallback((exerciseId, pathClassId) => {
    const cid = classId || pathClassId;
    onClose();
    navigate(`/student/ide/${encodeURIComponent(exerciseId)}${cid ? `?classId=${encodeURIComponent(cid)}` : ''}`);
  }, [classId, navigate, onClose]);

  const loadCode = useCallback((code) => {
    if (onLoadCode) onLoadCode(code);
    onClose();
  }, [onLoadCode, onClose]);

  if (!isOpen) return null;

  const current = journey?.current;
  const others = (journey?.recent_exercises || []).filter((e) => e.exercise_id !== current?.exercise_id);
  const noActivity = journey && !current?.points?.length && others.length === 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-3 backdrop-blur-sm animate-fade-in sm:p-6" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div role="dialog" aria-modal="true" aria-labelledby="journey-title" className="flex max-h-[92vh] w-full max-w-3xl select-text flex-col overflow-hidden rounded-3xl border border-border bg-surface shadow-bento">
        <div className="flex shrink-0 items-center justify-between border-b border-border bg-surface-raised px-5 py-3.5 sm:px-6">
          <div className="min-w-0">
            <h2 id="journey-title" className="text-sm font-bold tracking-wide text-foreground sm:text-base">Hành trình học</h2>
            <p className="truncate text-[11px] text-muted">{user?.full_name || 'Sinh viên'}</p>
          </div>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            aria-label="Đóng Hành trình học"
            className="cursor-pointer rounded-xl bg-surface p-2 text-muted transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
          >
            <X aria-hidden="true" className="size-4" />
          </button>
        </div>

        <div className="flex-1 space-y-6 overflow-y-auto p-5 sm:p-6" aria-busy={isLoading}>
          {isLoading ? (
            <div role="status" className="space-y-2 py-16 text-center text-sm text-muted">
              <div className="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-emerald-500" />
              <p>Đang tải hành trình học…</p>
            </div>
          ) : journey ? (
            <>
              <TodayCard today={journey.today} onOpenExercise={openExercise} />

              {current?.points?.length > 0 && (
                <section aria-labelledby="journey-current" className="space-y-3 rounded-2xl border border-border bg-surface p-4">
                  <h3 id="journey-current" className="break-words text-sm font-bold text-foreground">Bài bạn đang mở: {current.title}</h3>
                  <StorySteps story={current.story} onLoadCode={loadCode} />
                </section>
              )}

              {noActivity ? (
                <p className="rounded-2xl border border-dashed border-border p-4 text-center text-sm text-muted">
                  Bạn chưa làm bài nào. Mở một bài và bấm “Chạy thử” để bắt đầu.
                </p>
              ) : others.length > 0 && (
                <section aria-labelledby="journey-recent" className="space-y-3">
                  <h3 id="journey-recent" className="text-sm font-bold text-foreground">Các bài gần đây</h3>
                  <ul className="space-y-2">
                    {others.map((item) => (
                      <RecentExercise key={item.exercise_id} item={item} classId={classId} onOpenExercise={openExercise} />
                    ))}
                  </ul>
                </section>
              )}
            </>
          ) : loadError ? (
            <div role="alert" className="space-y-3 rounded-2xl border border-destructive-line bg-destructive-soft px-4 py-8 text-center">
              <AlertCircle aria-hidden="true" className="mx-auto size-6 text-destructive-strong" />
              <p className="font-medium text-foreground">Không tải được Hành trình học.</p>
              <p className="text-sm text-muted">Có thể do mất kết nối tới máy chủ. Dữ liệu học tập của bạn không bị ảnh hưởng.</p>
              <button
                type="button"
                onClick={() => setReloadKey((k) => k + 1)}
                className="inline-flex min-h-9 cursor-pointer items-center gap-1.5 rounded-full border border-border bg-surface px-4 font-medium text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
              >
                <RotateCcw aria-hidden="true" className="size-3.5" /> Thử lại
              </button>
            </div>
          ) : null}
        </div>

        <div className="flex shrink-0 items-center justify-between border-t border-border bg-surface-raised px-5 py-3 text-xs text-muted sm:px-6">
          <span className="hidden sm:inline">Khoa Công nghệ thông tin - Đại học Kinh tế Quốc dân (NEU)</span>
          <button
            type="button"
            onClick={onClose}
            className="cursor-pointer rounded-full bg-surface px-4 py-1.5 font-medium text-foreground hover:bg-canvas focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
}
