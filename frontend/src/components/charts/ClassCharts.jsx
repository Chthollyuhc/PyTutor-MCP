import React from 'react';

/** Biểu đồ SVG tự vẽ cho "Tình hình lớp". Màu dùng lớp Tailwind (tự đổi theo sáng/tối), không thư viện ngoài.
 *  Mọi biểu đồ có role="img" + aria-label tóm tắt và hiển thị "chưa đủ dữ liệu" khi mẫu rỗng. */

export function ChartEmpty({ children = 'Chưa đủ dữ liệu để vẽ biểu đồ này.' }) {
  return <p className="rounded-xl border border-dashed border-border p-3 text-center text-[11px] text-muted">{children}</p>;
}

export function Legend({ series, totals }) {
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-muted">
      {series.map((s) => (
        <li key={s.key} className="flex items-center gap-1.5">
          <span aria-hidden="true" className={`size-2.5 rounded-sm ${s.bg}`} />
          <span>{s.label}{totals ? <strong className="ml-1 font-mono tabular-nums text-foreground">{totals[s.key] || 0}</strong> : null}</span>
        </li>
      ))}
    </ul>
  );
}

/** Hàng thanh xếp chồng: rows=[{label, values:{key:n}}], series=[{key,label,fill,bg}] */
export function StackedBarRows({ rows, series, ariaLabel, minTotal = 1 }) {
  const usable = (rows || []).filter((r) => series.reduce((s, x) => s + (r.values?.[x.key] || 0), 0) >= minTotal);
  if (usable.length === 0) return <ChartEmpty />;
  const totals = Object.fromEntries(series.map((s) => [s.key, usable.reduce((a, r) => a + (r.values?.[s.key] || 0), 0)]));
  const summary = usable.map((r) => `${r.label}: ${series.map((s) => `${s.label} ${r.values?.[s.key] || 0}`).join(', ')}`).join('; ');
  return (
    <div className="space-y-2">
      <ul role="img" aria-label={`${ariaLabel}. ${summary}`} className="space-y-1.5">
        {usable.map((r) => {
          const total = series.reduce((s, x) => s + (r.values?.[x.key] || 0), 0);
          let offset = 0;
          return (
            <li key={r.key || r.label} className="grid gap-1 sm:grid-cols-[minmax(0,12rem)_1fr_2.5rem] sm:items-center sm:gap-3">
              <span className="truncate text-xs font-semibold text-foreground" title={r.label}>{r.label}</span>
              <svg viewBox="0 0 100 5" preserveAspectRatio="none" className="h-3 w-full rounded bg-slate-200 dark:bg-slate-800" aria-hidden="true">
                {series.map((s) => {
                  const v = r.values?.[s.key] || 0;
                  if (!v) return null;
                  const w = (v / total) * 100;
                  const el = <rect key={s.key} x={offset} y="0" width={w} height="5" className={s.fill}><title>{`${s.label}: ${v}`}</title></rect>;
                  offset += w;
                  return el;
                })}
              </svg>
              <span className="font-mono text-[11px] tabular-nums text-muted sm:text-right">{total}</span>
            </li>
          );
        })}
      </ul>
      <Legend series={series} totals={totals} />
    </div>
  );
}

/** Thanh ngang đơn: rows=[{label, value, max, text}] */
export function HBar({ rows, ariaLabel, fill = 'fill-emerald-600' }) {
  if (!rows || rows.length === 0) return <ChartEmpty />;
  const summary = rows.map((r) => `${r.label}: ${r.text ?? r.value}`).join('; ');
  return (
    <ul role="img" aria-label={`${ariaLabel}. ${summary}`} className="space-y-1.5">
      {rows.map((r) => {
        const max = r.max || 100;
        return (
          <li key={r.key || r.label} className="grid gap-1 sm:grid-cols-[minmax(0,12rem)_1fr_6rem] sm:items-center sm:gap-3">
            <span className="truncate text-xs font-semibold text-foreground" title={r.label}>{r.label}</span>
            <svg viewBox="0 0 100 5" preserveAspectRatio="none" className="h-3 w-full rounded bg-slate-200 dark:bg-slate-800" aria-hidden="true">
              <rect x="0" y="0" width={Math.max(0, Math.min(100, (r.value / max) * 100))} height="5" className={fill}><title>{r.text ?? r.value}</title></rect>
            </svg>
            <span className="font-mono text-[11px] tabular-nums text-muted sm:text-right">{r.text ?? r.value}</span>
          </li>
        );
      })}
    </ul>
  );
}

/** Đường xu hướng theo ngày: points=[{date, a, b}] (a: SV hoạt động, b: lượt đạt lần đầu). */
export function TrendLine({ points, ariaLabel, labelA, labelB }) {
  if (!points || points.length < 2) return <ChartEmpty>Cần dữ liệu từ ít nhất 2 ngày để vẽ xu hướng.</ChartEmpty>;
  const W = 300; const H = 80; const PAD = 6;
  const max = Math.max(1, ...points.map((p) => Math.max(p.a, p.b)));
  const x = (i) => PAD + (i / (points.length - 1)) * (W - 2 * PAD);
  const y = (v) => H - PAD - (v / max) * (H - 2 * PAD);
  const path = (key) => points.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(p[key]).toFixed(1)}`).join(' ');
  const summary = points.map((p) => `${p.date}: ${labelA} ${p.a}, ${labelB} ${p.b}`).join('; ');
  return (
    <div className="space-y-1.5">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${ariaLabel}. ${summary}`} className="h-24 w-full">
        <line x1={PAD} y1={H - PAD} x2={W - PAD} y2={H - PAD} className="stroke-slate-300 dark:stroke-slate-700" strokeWidth="1" />
        <path d={path('a')} fill="none" strokeWidth="2" className="stroke-sky-600" />
        <path d={path('b')} fill="none" strokeWidth="2" strokeDasharray="4 3" className="stroke-emerald-600" />
        {points.map((p, i) => (
          <g key={p.date}>
            <circle cx={x(i)} cy={y(p.a)} r="2.5" className="fill-sky-600"><title>{`${p.date} · ${labelA}: ${p.a}`}</title></circle>
            <circle cx={x(i)} cy={y(p.b)} r="2.5" className="fill-emerald-600"><title>{`${p.date} · ${labelB}: ${p.b}`}</title></circle>
          </g>
        ))}
      </svg>
      <div className="flex justify-between font-mono text-[10px] text-muted"><span>{points[0].date}</span><span>{points[points.length - 1].date}</span></div>
      <Legend series={[{ key: 'a', label: labelA, bg: 'bg-sky-600' }, { key: 'b', label: `${labelB} (nét đứt)`, bg: 'bg-emerald-600' }]} />
    </div>
  );
}
