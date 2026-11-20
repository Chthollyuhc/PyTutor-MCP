import React from 'react';

/** Bài tập của lớp: thanh tiến độ có ghi chữ ngay bên dưới, lỗi hay gặp nói bằng ví dụ. */
export default function ExerciseProgressList({ exercises, onOpenExercise }) {
  const items = exercises || [];
  if (!items.length) return null;
  return (
    <section aria-labelledby="class-exercises" className="space-y-3">
      <h5 id="class-exercises" className="text-sm font-bold text-foreground">Bài tập của lớp</h5>
      <ul className="space-y-2">
        {items.map((e) => {
          const pct = e.enrolled ? Math.round((e.done / e.enrolled) * 100) : 0;
          return (
            <li key={e.exercise_id} className="space-y-1.5 rounded-2xl border border-border bg-surface-raised p-3">
              <div className="flex items-start justify-between gap-3">
                <p className="min-w-0 break-words text-sm font-semibold text-foreground">
                  <span className="text-muted">Bài {e.number}.</span> {e.title}
                  {e.hardest && <span className="ml-2 inline-block rounded-full bg-warning-soft px-2 py-0.5 text-[11px] font-semibold text-warning-strong">Khó nhất</span>}
                </p>
                {onOpenExercise && (
                  <button type="button" onClick={() => onOpenExercise(e.exercise_id)} className="shrink-0 cursor-pointer text-xs font-semibold text-primary hover:underline">
                    Xem bài
                  </button>
                )}
              </div>
              <div role="progressbar" aria-label={e.done_vi} aria-valuemin={0} aria-valuemax={e.enrolled} aria-valuenow={e.done} className="h-2 overflow-hidden rounded-full bg-border">
                <div className="h-full rounded-full bg-success" style={{ width: `${pct}%` }} />
              </div>
              <p className="text-xs text-foreground">{e.done_vi}</p>
              {e.mistake_vi && <p className="text-xs text-muted">{e.mistake_vi}</p>}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
