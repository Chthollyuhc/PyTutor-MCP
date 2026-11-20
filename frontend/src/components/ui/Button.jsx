import React from 'react';

const variants = {
  primary: 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-soft',
  black: 'bg-slate-950 text-white hover:bg-black dark:bg-white dark:text-slate-950 dark:hover:bg-slate-100 shadow-soft',
  secondary: 'border border-border/80 bg-surface text-foreground hover:bg-surface-raised shadow-soft',
  outline: 'border border-border bg-surface text-foreground hover:bg-surface-raised shadow-soft',
  success: 'border border-emerald-300 bg-emerald-50 text-emerald-800 hover:bg-emerald-100 dark:border-emerald-500/30 dark:bg-emerald-500/20 dark:text-emerald-300 dark:hover:bg-emerald-500/30 font-semibold shadow-soft',
  warning: 'border border-amber-300 bg-amber-50 text-amber-800 hover:bg-amber-100 dark:border-amber-500/30 dark:bg-amber-500/20 dark:text-amber-300 dark:hover:bg-amber-500/30 font-semibold shadow-soft',
  info: 'border border-sky-300 bg-sky-50 text-sky-800 hover:bg-sky-100 dark:border-sky-500/30 dark:bg-sky-500/20 dark:text-sky-300 dark:hover:bg-sky-500/30 font-semibold shadow-soft',
  ghost: 'text-muted hover:bg-surface-raised hover:text-foreground',
  tone: 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-soft',
  onBrand: 'border border-header-foreground/20 bg-header-foreground/15 text-on-solid hover:bg-header-foreground/25',
};

const sizes = {
  xs: 'min-h-7 px-2.5 py-0.5 text-xs',
  sm: 'min-h-8 px-3.5 py-1 text-xs',
  md: 'min-h-10 px-4 py-2 text-sm',
  lg: 'min-h-12 px-6 py-2.5 text-base',
  icon: 'size-9 p-0',
  'icon-sm': 'size-8 p-0',
};

const Button = React.forwardRef(function Button(
  { children, className = '', variant = 'primary', size = 'md', loading = false, disabled, type = 'button', pill = true, ...props },
  ref,
) {
  const isDisabled = disabled || loading;
  const roundedClass = pill ? 'rounded-full' : 'rounded-2xl';

  return (
    <button
      ref={ref}
      type={type}
      disabled={isDisabled}
      aria-busy={loading || undefined}
      className={`inline-flex items-center justify-center gap-2 font-semibold transition-all duration-200 ease-out active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-canvas disabled:pointer-events-none disabled:opacity-50 cursor-pointer ${roundedClass} ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${className}`}
      {...props}
    >
      {loading && (
        <span aria-hidden="true" className="size-4 animate-spin rounded-full border-2 border-current/30 border-t-current" />
      )}
      {children}
    </button>
  );
});

export default Button;
