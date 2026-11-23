import React from 'react';
import { ArrowRight, CheckCircle2, School, Trophy } from 'lucide-react';
import CoursePath from './CoursePath';

/** Thẻ "Hôm nay của bạn": lời chào, một câu chính, tin vui, chặng đường, một việc tiếp theo. Câu chữ lấy nguyên văn từ backend. */
export default function TodayCard({ today, onOpenExercise, showGreeting = true }) {
  if (!today) return null;
  const next = today.next_step;
  const nextInPath = Boolean(next && today.path?.steps?.some((s) => s.exercise_id === next.exercise_id));
  const className = next?.class_name || (nextInPath ? today.path?.class_name : null);
  const classCode = next?.class_code;
  return (
    <section aria-labelledby="today-title" className="space-y-4 rounded-3xl border border-border bg-surface p-5 shadow-bento sm:p-6">
      <div>
        {showGreeting && <p className="text-sm text-muted">{today.greeting_vi}</p>}
        <h2 id="today-title" className="mt-1 text-xl font-bold leading-snug tracking-tight text-foreground sm:text-2xl">{today.headline_vi}</h2>
      </div>
      {(today.moments || []).length > 0 && (
        <ul className="space-y-2">
          {today.moments.map((m) => (
            <li key={m.kind} className="flex items-start gap-2 rounded-2xl border border-success-line bg-success-soft px-3 py-2 text-sm text-success-strong">
              <Trophy aria-hidden="true" className="mt-0.5 size-4 shrink-0" />
              <span>{m.text_vi}</span>
            </li>
          ))}
        </ul>
      )}
      {today.path && <CoursePath path={today.path} onOpenExercise={onOpenExercise} />}
      {next && (
        <div className="flex flex-col gap-3 border-t border-border pt-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <p className="break-words text-base font-bold text-foreground">{next.title}</p>
            {className && (
              <p className="mt-0.5 flex items-center gap-1.5 text-xs text-muted">
                <School aria-hidden="true" className="size-3.5 shrink-0" />
                <span>{classCode ? `${classCode} · ` : ''}{className}</span>
              </p>
            )}
            <p className="mt-1 text-sm text-muted">{next.reason_vi}</p>
          </div>
          {onOpenExercise && (
            <button
              type="button"
              onClick={() => onOpenExercise(next.exercise_id, next.class_id || (nextInPath ? today.path.class_id : undefined))}
              className="inline-flex min-h-11 shrink-0 cursor-pointer items-center justify-center gap-2 rounded-full bg-primary px-5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2"
            >
              {next.button_vi} <ArrowRight aria-hidden="true" className="size-4" />
            </button>
          )}
        </div>
      )}
      {today.skills_vi && (
        <p className="flex items-start gap-2 text-sm text-foreground">
          <CheckCircle2 aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-success" />
          <span>{today.skills_vi}</span>
        </p>
      )}
    </section>
  );
}
