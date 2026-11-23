import React, { useState } from 'react';
import { Check, ChevronRight } from 'lucide-react';

/**
 * Bản đồ khái niệm (v5.8): 6 khái niệm thành một lộ trình. Trạng thái mã hóa bằng cả hình lẫn chữ:
 * tô đầy = khá vững, nửa = đang hình thành, viền cam đậm = đang vướng, nét đứt = chưa có bằng chứng.
 * Bấm vào một khái niệm để xem "Vì sao hệ thống nghĩ vậy" kèm nút tới bài để luyện. Dưới 640px thành danh sách dọc.
 */
const STATE_TEXT = {
  secure: 'Khá vững', developing: 'Đang hình thành', struggling: 'Đang vướng', no_evidence: 'Chưa có bằng chứng',
};
const STATUS_TEXT = { passed: 'đã đạt', struggling: 'đã thử nhiều lần', attempted: 'đã thử' };

function StateGlyph({ state }) {
  const common = { width: 28, height: 28, viewBox: '0 0 28 28', 'aria-hidden': true, className: 'shrink-0' };
  if (state === 'secure') {
    return (
      <span className="inline-flex size-7 items-center justify-center rounded-full bg-emerald-600 text-white" aria-hidden="true"><Check className="size-4" /></span>
    );
  }
  if (state === 'developing') {
    return (
      <svg {...common}>
        <circle cx="14" cy="14" r="11" fill="none" strokeWidth="2.5" className="stroke-emerald-600" />
        <path d="M14 3 A11 11 0 0 1 14 25 Z" className="fill-emerald-600" />
      </svg>
    );
  }
  if (state === 'struggling') {
    return (
      <svg {...common}>
        <circle cx="14" cy="14" r="11" strokeWidth="4" className="fill-amber-50 stroke-amber-500 dark:fill-amber-950/40" />
        <rect x="12.6" y="7.5" width="2.8" height="8" rx="1.2" className="fill-amber-600" />
        <circle cx="14" cy="19.5" r="1.7" className="fill-amber-600" />
      </svg>
    );
  }
  return (
    <svg {...common}>
      <circle cx="14" cy="14" r="11" fill="none" strokeWidth="2" strokeDasharray="4 3" className="stroke-slate-400 dark:stroke-slate-500" />
    </svg>
  );
}

export default function ConceptMap({ concepts, onOpenExercise }) {
  const [openKc, setOpenKc] = useState(null);
  const items = Array.isArray(concepts) ? concepts : [];
  if (!items.length) return null;
  const active = items.find((c) => c.kc === openKc) || null;
  const summary = items.map((c) => `${c.label_vi}: ${STATE_TEXT[c.state] || c.state}`).join('; ');

  return (
    <div className="space-y-3">
      <ol aria-label={`Bản đồ khái niệm. ${summary}`} className="grid grid-cols-1 gap-2 sm:grid-cols-3 lg:grid-cols-6">
        {items.map((c) => {
          const isOpen = openKc === c.kc;
          return (
            <li key={c.kc}>
              <button
                type="button"
                aria-expanded={isOpen}
                aria-controls="concept-why-panel"
                onClick={() => setOpenKc(isOpen ? null : c.kc)}
                className={`flex w-full items-center gap-2.5 rounded-2xl border p-2.5 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer sm:flex-col sm:items-start ${
                  isOpen ? 'border-emerald-500 bg-emerald-500/10' : 'border-border bg-surface hover:bg-surface-raised'
                } ${c.state === 'no_evidence' ? 'border-dashed' : ''}`}
              >
                <StateGlyph state={c.state} />
                <span className="min-w-0">
                  <span className="block break-words text-xs font-semibold text-foreground">{c.label_vi}</span>
                  <span className="block text-[11px] text-muted">{STATE_TEXT[c.state] || c.state_label_vi}</span>
                </span>
              </button>
            </li>
          );
        })}
      </ol>
      {active && (
        <div id="concept-why-panel" role="region" aria-label={`Vì sao hệ thống nghĩ vậy về ${active.label_vi}`} className="space-y-2 rounded-2xl border border-border bg-surface-raised p-3 text-xs">
          <p className="font-semibold text-foreground">Vì sao hệ thống nghĩ vậy: {active.label_vi}</p>
          <p className="leading-relaxed text-muted">{active.explanation_vi}</p>
          {active.common_error_vi && <p className="leading-relaxed text-muted">{active.common_error_vi}</p>}
          {(active.exercise_details || []).length > 0 && (
            <ul className="space-y-1.5">
              {active.exercise_details.map((d) => (
                <li key={d.exercise_id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-border bg-surface px-2.5 py-1.5">
                  <span className="min-w-0 break-words text-foreground">{d.title || d.exercise_id} <span className="text-muted">· {STATUS_TEXT[d.status] || d.status}</span></span>
                  {onOpenExercise && (
                    <button
                      type="button"
                      onClick={() => onOpenExercise(d.exercise_id)}
                      className="inline-flex min-h-8 items-center gap-1 rounded-full border border-border px-3 text-[11px] font-semibold text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer"
                    >
                      Luyện bài này <ChevronRight aria-hidden="true" className="size-3.5" />
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      <p className="text-[11px] text-muted">Đây là ước lượng tạm thời, chưa hiệu chuẩn.</p>
    </div>
  );
}
