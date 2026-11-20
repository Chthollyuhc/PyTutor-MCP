import React from 'react';

const TONE_CHIPS = [
  'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20',
  'bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20',
  'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20',
  'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20',
  'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20',
];

/**
 * Thẻ Bento hiển thị một chỉ số tóm tắt kèm biểu tượng hình tròn và ghi chú ngắn.
 */
export default function Stat({
  tone = 0,
  icon: Icon,
  label,
  value,
  note = '',
  variant = 'default',
  className = '',
}) {
  const isDark = variant === 'dark';
  const chipStyle = isDark
    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
    : TONE_CHIPS[Math.abs(Number(tone) || 0) % TONE_CHIPS.length];

  const cardClasses = isDark
    ? 'keep-dark bg-slate-950 text-white rounded-3xl p-5 border border-slate-800/80 shadow-bento'
    : 'rounded-3xl border border-border/80 bg-surface p-5 shadow-bento hover:shadow-bento-hover text-foreground';

  return (
    <div
      data-keep-dark={isDark ? 'true' : undefined}
      className={`flex items-start gap-4 transition-all duration-200 ${cardClasses} ${className}`}
    >
      {Icon && (
        <span aria-hidden="true" className={`flex size-11 shrink-0 items-center justify-center rounded-full border ${chipStyle}`}>
          <Icon className="size-5" />
        </span>
      )}
      <div className="min-w-0 flex-1">
        <p className={`text-xs font-medium ${isDark ? 'text-slate-400' : 'text-muted'}`}>{label}</p>
        <p className="mt-1 text-2xl font-bold tracking-tight">{value}</p>
        {note && <p className={`mt-0.5 text-xs ${isDark ? 'text-slate-400' : 'text-muted'}`}>{note}</p>}
      </div>
    </div>
  );
}
