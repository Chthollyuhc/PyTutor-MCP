import React from 'react';

const BTN = 'cursor-pointer rounded-full border border-border bg-surface px-2.5 py-0.5 text-[11px] font-semibold text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 disabled:cursor-default disabled:opacity-60';

/** Hai nút đánh dấu một việc nên xem. "Đã xử lý": thầy/cô đã làm gì đó. "Không cần": nhận xét tự động không đúng. */
export function MarkButtons({ keys, onMark, busy, who = '' }) {
  if (!keys || keys.length === 0 || !onMark) return null;
  return (
    <span className="inline-flex flex-wrap items-center gap-1.5">
      <button type="button" disabled={busy} onClick={() => onMark(keys, 'handled')} className={BTN} aria-label={`Đánh dấu đã xử lý${who ? ` cho ${who}` : ''}`}>Đã xử lý</button>
      <button type="button" disabled={busy} onClick={() => onMark(keys, 'dismissed')} className={BTN} aria-label={`Đánh dấu không cần${who ? ` cho ${who}` : ''}`}>Không cần</button>
    </span>
  );
}

/** Dòng báo một việc đang được đánh dấu, kèm nút hoàn tác. */
export function MarkedNote({ mark, keys, onUndo, busy }) {
  if (!mark) return null;
  const when = mark.marked_at ? String(mark.marked_at).slice(0, 10).split('-').reverse().slice(0, 2).join('/') : '';
  return (
    <span className="inline-flex flex-wrap items-center gap-1.5 text-[11px] text-muted">
      <span>Đã đánh dấu “{mark.status_vi}”{when ? ` ngày ${when}` : ''}</span>
      {onUndo && (
        <button type="button" disabled={busy} onClick={() => onUndo(keys)} className="cursor-pointer font-semibold text-foreground underline underline-offset-2 hover:no-underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 disabled:opacity-60">Hoàn tác</button>
      )}
    </span>
  );
}
