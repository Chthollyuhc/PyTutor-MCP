import React, { useEffect, useRef } from 'react';
import { CheckCircle2, Lock, MapPin } from 'lucide-react';

// Quá ngưỡng này thì dãy trạm có thanh kéo ngang (từ 640px trở lên); dưới 640px vẫn là danh sách dọc.
const MAX_VISIBLE = 8;

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
  const steps = Array.isArray(path?.steps) ? path.steps : [];
  const scrollable = steps.length > MAX_VISIBLE;
  const visible = steps;
  const listRef = useRef(null);
  useEffect(() => {
    const ol = listRef.current;
    if (!ol || !scrollable) return;
    const cur = ol.querySelector('[data-current="true"]');
    if (cur) ol.scrollLeft = Math.max(0, cur.offsetLeft - (ol.clientWidth - cur.clientWidth) / 2);
  }, [scrollable, path?.class_id, steps.length]);
  if (!visible.length) return null;
  const cls = 'flex w-full items-center gap-3 rounded-2xl p-2 text-left sm:flex-col sm:gap-1.5 sm:text-center';
  return (
    <div className="space-y-2">
      {path.class_name && <p className="text-xs font-semibold text-muted">{path.class_name}</p>}
      <ol
        ref={listRef}
        aria-label={`Chặng đường học phần ${path.class_name || ''}`.trim()}
        className={`relative grid gap-2 sm:grid-flow-col ${scrollable ? 'sm:auto-cols-[8.5rem] sm:overflow-x-auto sm:pb-2' : 'sm:auto-cols-fr'}`}
      >
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
            <li key={step.exercise_id} data-current={step.kind === 'current' ? 'true' : undefined}>
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
    </div>
  );
}
