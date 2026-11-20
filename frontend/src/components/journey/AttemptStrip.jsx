import React, { useMemo, useState } from 'react';
import { RotateCcw } from 'lucide-react';

/**
 * Dấu chân của một bài (v5.8): trục dọc là số test đạt trên tổng.
 * Chạy thử = chấm nhỏ · hỏi Gia sư AI = ô vuông kèm mức (hàng trên) · nộp = vòng (đạt thì tô đầy).
 * Điểm đạt cao nhất mới được nhấn bằng vòng ngoài. Hình dạng đi kèm màu để không chỉ dựa vào màu.
 */
const MAX_POINTS_BEFORE_MERGE = 20;
const STEP = 26;
const TOP = 26;
const H = 70;
const PAD_X = 22;

/** Gộp các đoạn chạy thử liên tiếp (>= 3) thành một nút khi có quá nhiều điểm. */
export function condensePoints(points) {
  if (!Array.isArray(points) || points.length <= MAX_POINTS_BEFORE_MERGE) return points || [];
  const out = [];
  let i = 0;
  while (i < points.length) {
    if (points[i].kind !== 'run') { out.push(points[i]); i += 1; continue; }
    let j = i;
    while (j < points.length && points[j].kind === 'run') j += 1;
    const group = points.slice(i, j);
    if (group.length >= 3) {
      out.push({
        kind: 'runs', count: group.length, total: group[0].total,
        passed: Math.max(...group.map((p) => p.passed || 0)), is_new_best: group.some((p) => p.is_new_best),
        all_passed: false, format_only: false, timestamp: group[0].timestamp,
      });
    } else {
      out.push(...group);
    }
    i = j;
  }
  return out;
}

function pointLabel(p, idx) {
  const n = idx + 1;
  if (p.kind === 'ask') return `Lượt ${n}: hỏi Gia sư AI, Mức ${p.hint_level}`;
  if (p.kind === 'runs') return `Lượt ${n}: ${p.count} lần chạy thử liên tiếp, tốt nhất ${p.passed}/${p.total}`;
  const base = p.kind === 'run' ? 'chạy thử' : 'nộp bài';
  return `Lượt ${n}: ${base}, đạt ${p.passed}/${p.total}${p.all_passed ? ', đạt toàn bộ' : ''}${p.is_new_best ? ', cao nhất tới lúc này' : ''}${p.format_only ? ', chỉ sai định dạng đầu ra' : ''}`;
}

export default function AttemptStrip({ points, summary, description, onLoadCode, notes = [], ariaTitle = 'Dấu chân luyện tập' }) {
  const shown = useMemo(() => condensePoints(points), [points]);
  const [selected, setSelected] = useState(null);

  if (!shown.length) {
    return <p className="rounded-xl border border-dashed border-border p-3 text-center text-[11px] text-muted">Chưa có lượt nào ở bài này.</p>;
  }
  const total = Math.max(1, ...shown.map((p) => p.total || 0));
  const width = PAD_X * 2 + Math.max(1, shown.length - 1) * STEP;
  const x = (i) => PAD_X + i * STEP;
  const y = (p) => TOP + (1 - (p.passed || 0) / total) * H;
  const line = shown.map((p, i) => (p.kind === 'ask' ? null : [x(i), y(p)])).filter(Boolean);
  const path = line.map(([px, py], i) => `${i ? 'L' : 'M'}${px.toFixed(1)},${py.toFixed(1)}`).join(' ');
  const counts = summary?.counts || {};
  const aria = `${ariaTitle}. ${counts.run || 0} lần chạy thử, ${counts.ask || 0} lần hỏi Gia sư AI, ${counts.submit || 0} lần nộp. Tốt nhất ${summary?.best?.passed ?? 0}/${summary?.best?.total ?? 0} test.`;
  const selectedPoint = selected != null ? shown[selected] : null;

  return (
    <div className="space-y-2">
      {description && <p className="text-xs leading-relaxed text-foreground">{description}</p>}
      <div className="overflow-x-auto rounded-xl border border-border bg-surface-raised p-2">
        <svg role="img" aria-label={aria} viewBox={`0 0 ${width} ${TOP + H + 18}`} style={{ minWidth: Math.min(width, 640), width: '100%', height: 'auto', maxHeight: 190 }}>
          <line x1={PAD_X - 10} x2={width - PAD_X + 10} y1={TOP + H} y2={TOP + H} className="stroke-slate-300 dark:stroke-slate-700" strokeWidth="1" />
          <line x1={PAD_X - 10} x2={width - PAD_X + 10} y1={TOP} y2={TOP} className="stroke-slate-300 dark:stroke-slate-700" strokeDasharray="3 3" strokeWidth="1" />
          <text x={2} y={TOP + 3} className="fill-slate-500 text-[8px]">{total}</text>
          <text x={2} y={TOP + H + 3} className="fill-slate-500 text-[8px]">0</text>
          {path && <path d={path} fill="none" strokeWidth="1.5" className="stroke-slate-400 dark:stroke-slate-500" />}
          {shown.map((p, i) => {
            const cx = x(i);
            if (p.kind === 'ask') {
              return (
                <g key={i} aria-hidden="true">
                  <rect x={cx - 8} y={4} width="16" height="14" rx="3" className="fill-violet-500/20 stroke-violet-500" strokeWidth="1.2" />
                  <text x={cx} y={14.5} textAnchor="middle" className="fill-violet-700 text-[8px] font-bold dark:fill-violet-300">M{p.hint_level}</text>
                </g>
              );
            }
            const cy = y(p);
            const halo = p.is_new_best && <circle cx={cx} cy={cy} r="9" fill="none" strokeWidth="1.5" className="stroke-amber-500" />;
            const fmt = p.format_only && <line x1={cx - 5} x2={cx + 5} y1={cy + 10} y2={cy + 10} strokeWidth="1.5" strokeDasharray="2 2" className="stroke-sky-500" />;
            if (p.kind === 'runs') {
              return (
                <g key={i} aria-hidden="true">
                  <rect x={cx - 10} y={cy - 6} width="20" height="12" rx="6" className="fill-slate-300 dark:fill-slate-600" />
                  <text x={cx} y={cy + 3} textAnchor="middle" className="fill-slate-800 text-[8px] font-semibold dark:fill-slate-100">×{p.count}</text>
                  {halo}
                </g>
              );
            }
            if (p.kind === 'run') {
              return (
                <g key={i} aria-hidden="true">
                  <circle cx={cx} cy={cy} r="2.8" className="fill-slate-500 dark:fill-slate-400" />
                  {halo}{fmt}
                </g>
              );
            }
            const clickable = Boolean(p.code && onLoadCode);
            return (
              <g key={i} aria-hidden={clickable ? undefined : 'true'}>
                <circle
                  cx={cx} cy={cy} r="5.5" strokeWidth="2"
                  className={`${p.all_passed ? 'fill-emerald-600 stroke-emerald-700' : 'fill-surface stroke-slate-600 dark:stroke-slate-300'} ${clickable ? 'cursor-pointer outline-none focus-visible:stroke-amber-500' : ''}`}
                  {...(clickable ? { role: 'button', tabIndex: 0, 'aria-label': pointLabel(p, i), onClick: () => setSelected(i), onKeyDown: (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setSelected(i); } } } : {})}
                >
                  <title>{pointLabel(p, i)}</title>
                </circle>
                {halo}{fmt}
              </g>
            );
          })}
        </svg>
      </div>
      <ul className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-muted" aria-hidden="true">
        <li className="flex items-center gap-1.5"><span className="size-2 rounded-full bg-slate-500" /> chạy thử</li>
        <li className="flex items-center gap-1.5"><span className="inline-block h-2.5 w-3 rounded-sm border border-violet-500 bg-violet-500/20" /> hỏi Gia sư AI (mức)</li>
        <li className="flex items-center gap-1.5"><span className="size-2.5 rounded-full border-2 border-slate-600" /> nộp, <span className="size-2.5 rounded-full bg-emerald-600" /> nộp đạt</li>
        <li className="flex items-center gap-1.5"><span className="size-3 rounded-full border-2 border-amber-500" /> số test đạt cao nhất mới</li>
      </ul>
      {selectedPoint && selectedPoint.code && (
        <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-border bg-surface p-2.5 text-xs">
          <span className="text-foreground">Lượt nộp {selected + 1}: đạt {selectedPoint.passed}/{selectedPoint.total} test{selectedPoint.timestamp ? ` · ${selectedPoint.timestamp}` : ''}</span>
          <button
            type="button"
            onClick={() => onLoadCode(selectedPoint.code)}
            className="inline-flex min-h-8 items-center gap-1.5 rounded-full border border-border bg-surface px-3 text-xs font-semibold text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer"
          >
            <RotateCcw aria-hidden="true" className="size-3.5 text-emerald-600" /> Nạp lại code này
          </button>
        </div>
      )}
      {notes.map((n) => <p key={n} className="text-[11px] leading-relaxed text-muted">{n}</p>)}
      <table className="sr-only">
        <caption>{ariaTitle}: danh sách từng lượt</caption>
        <thead><tr><th scope="col">Lượt</th><th scope="col">Mô tả</th></tr></thead>
        <tbody>{shown.map((p, i) => <tr key={i}><td>{i + 1}</td><td>{pointLabel(p, i)}</td></tr>)}</tbody>
      </table>
    </div>
  );
}
