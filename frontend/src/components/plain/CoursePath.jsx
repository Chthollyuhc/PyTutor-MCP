import React from 'react';
import { CheckCircle2, Lock, MapPin } from 'lucide-react';
import { windowSteps } from '../../utils/path';

const KIND_TEXT = { done: 'đã xong', current: 'bạn đang ở đây', open: 'chưa làm', locked: 'chưa mở, cần xong bài trước' };

function StationIcon({ step }) {
  const base = 'flex size-9 shrink-0 items-center justify-center rounded-full';
  if (step.kind === 'done') return <span className={`${base} bg-success-soft text-success-strong`}><CheckCircle2 aria-hidden="true" className="size-5" /></span>;
  if (step.kind === 'current') return <span className={`${base} bg-primary text-primary-foreground`}><MapPin aria-hidden="true" className="size-5" /></span>;
  if (step.kind === 'locked') return <span className={`${base} border border-border bg-surface-raised text-muted`}><Lock aria-hidden="true" className="size-4" /></span>;
  return <span className={`${base} border border-border bg-surface text-sm font-bold text-foreground`}>{step.number}</span>;
}

function Stars({ count }) {
  if (!count) return null;
  return (
    <span aria-label={`${count} trên 3 sao`} className="block text-xs tracking-wide text-amber-500">
      {'★'.repeat(count)}{'☆'.repeat(Math.max(0, 3 - count))}
    </span>
  );
}

/** Chặng đường học phần: mỗi bài là một trạm. Dưới 640px thành danh sách dọc. */
export default function CoursePath({ path, onOpenExercise }) {
  const { visible, hiddenBefore, hiddenAfter } = windowSteps(path?.steps, 8);
  if (!visible.length) return null;
  const cls = 'flex w-full items-center gap-3 rounded-2xl p-2 text-left sm:flex-col sm:gap-1.5 sm:text-center';
  return (
    <div className="space-y-2">
      {path.class_name && <p className="text-xs font-semibold text-muted">{path.class_name}</p>}
      <ol aria-label={`Chặng đường học phần ${path.class_name || ''}`.trim()} className="grid gap-2 sm:grid-flow-col sm:auto-cols-fr">
        {visible.map((step) => {
          const label = `${step.title}: ${KIND_TEXT[step.kind]}`;
          const body = (
            <>
              <StationIcon step={step} />
              <span className="min-w-0">
                <span className={`line-clamp-2 block break-words text-xs font-semibold ${step.kind === 'locked' ? 'text-muted' : 'text-foreground'}`}>{step.title}</span>
                {step.kind === 'current' && <span className="block text-[11px] font-semibold text-primary">Bạn ở đây</span>}
                {step.kind === 'done' && <Stars count={step.stars} />}
              </span>
            </>
          );
          return (
            <li key={step.exercise_id}>
              {step.kind !== 'locked' && onOpenExercise ? (
                <button type="button" aria-label={label} onClick={() => onOpenExercise(step.exercise_id, path.class_id)} className={`${cls} cursor-pointer hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400`}>
                  {body}
                </button>
              ) : (
                <div role="group" aria-label={label} className={cls}>{body}</div>
              )}
            </li>
          );
        })}
      </ol>
      <p className="text-center text-sm text-muted">
        {hiddenBefore > 0 && <span>+{hiddenBefore} bài trước · </span>}
        {path.caption_vi}
        {hiddenAfter > 0 && <span> · +{hiddenAfter} bài sau</span>}
      </p>
    </div>
  );
}
