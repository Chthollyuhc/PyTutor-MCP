import React from 'react';

export default function Card({ as: Element = 'section', variant = 'default', className = '', children, ...props }) {
  const isDark = variant === 'dark';
  const baseClasses = isDark
    ? 'keep-dark bg-slate-950 text-white rounded-3xl p-5 border border-slate-800/80 shadow-bento'
    : 'rounded-3xl border border-border/80 bg-surface text-foreground shadow-bento';

  return (
    <Element
      data-keep-dark={isDark ? 'true' : undefined}
      className={`${baseClasses} ${className}`}
      {...props}
    >
      {children}
    </Element>
  );
}
