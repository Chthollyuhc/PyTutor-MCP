import React from 'react';
import { ArrowRight } from 'lucide-react';

/** Câu tóm tắt lớn + một nút chính + dòng "Tuần này / tuần trước" (chỉ số đếm, không phần trăm). */
export default function JourneyHeadline({ headline, week, onOpenExercise }) {
  if (!headline) return null;
  const cta = headline.cta;
  const showWeek = week && (week.this > 0 || week.prev > 0);
  return (
    <section aria-label="Việc nên làm tiếp" className="space-y-3 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 sm:p-5">
      <h3 className="text-lg font-bold leading-snug tracking-tight text-foreground sm:text-xl">{headline.headline_vi}</h3>
      {headline.detail_vi && <p className="text-xs leading-relaxed text-muted sm:text-sm">{headline.detail_vi}</p>}
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
        {cta && onOpenExercise && (
          <button
            type="button"
            onClick={() => onOpenExercise(cta.exercise_id)}
            className="inline-flex min-h-10 items-center gap-2 rounded-full bg-emerald-600 px-5 text-sm font-semibold text-white shadow-soft transition-colors hover:bg-emerald-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2 cursor-pointer"
          >
            Làm bài này: {cta.title} <ArrowRight aria-hidden="true" className="size-4" />
          </button>
        )}
        {showWeek && (
          <p className="text-xs text-muted">
            Bài đạt lần đầu: tuần này <strong className="font-mono tabular-nums text-foreground">{week.this}</strong> · tuần trước <strong className="font-mono tabular-nums text-foreground">{week.prev}</strong>
          </p>
        )}
      </div>
    </section>
  );
}
