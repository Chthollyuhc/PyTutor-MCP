import React from 'react';

const variants = {
  neutral: 'border-border/80 bg-surface-raised text-foreground',
  success: 'border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-500/30 dark:bg-emerald-500/15 dark:text-emerald-300 font-semibold',
  warning: 'border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/15 dark:text-amber-300 font-semibold',
  info: 'border-sky-300 bg-sky-50 text-sky-800 dark:border-sky-500/30 dark:bg-sky-500/15 dark:text-sky-300 font-semibold',
  danger: 'border-rose-300 bg-rose-50 text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/15 dark:text-rose-300 font-semibold',
  ai: 'border-purple-300 bg-purple-50 text-purple-800 dark:border-purple-500/30 dark:bg-purple-500/15 dark:text-purple-300 font-semibold',
  black: 'border-slate-800 bg-slate-950 text-white dark:bg-white dark:text-slate-950 dark:border-slate-200',
  pill: 'border-border/80 bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 font-medium',
};

export default function Badge({ variant = 'neutral', className = '', dot = false, children, ...props }) {
  return (
    <span
      className={`inline-flex min-h-6 items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium tracking-tight ${variants[variant] || variants.neutral} ${className}`}
      {...props}
    >
      {dot && <span aria-hidden="true" className="size-1.5 rounded-full bg-current" />}
      {children}
    </span>
  );
}
