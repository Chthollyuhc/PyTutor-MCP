import React from 'react';

const variants = {
  neutral: 'border-border bg-surface-raised text-foreground',
  success: 'border-success/30 bg-success/10 text-emerald-200',
  warning: 'border-warning/30 bg-warning/10 text-amber-100',
  info: 'border-info/30 bg-info/10 text-sky-100',
  danger: 'border-destructive/30 bg-destructive/10 text-rose-200',
};

export default function Badge({ variant = 'neutral', className = '', dot = false, children, ...props }) {
  return (
    <span
      className={`inline-flex min-h-6 items-center gap-2 rounded-md border px-2 py-1 text-xs font-medium ${variants[variant] || variants.neutral} ${className}`}
      {...props}
    >
      {dot && <span aria-hidden="true" className="size-1.5 rounded-full bg-current" />}
      {children}
    </span>
  );
}
