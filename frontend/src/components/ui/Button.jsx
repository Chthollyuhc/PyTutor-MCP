import React from 'react';

const variants = {
  primary: 'bg-primary text-primary-foreground hover:bg-primary-hover',
  secondary: 'border border-border bg-surface text-foreground hover:bg-surface-raised',
  success: 'border border-success/30 bg-success/10 text-emerald-200 hover:bg-success/15',
  warning: 'border border-warning/30 bg-warning/10 text-amber-100 hover:bg-warning/15',
  info: 'border border-info/30 bg-info/10 text-sky-100 hover:bg-info/15',
  ghost: 'text-muted hover:bg-surface-raised hover:text-foreground',
};

const sizes = {
  sm: 'min-h-9 px-3 text-xs',
  md: 'min-h-11 px-4 text-sm',
  icon: 'size-10 p-0',
};

const Button = React.forwardRef(function Button(
  { children, className = '', variant = 'primary', size = 'md', loading = false, disabled, type = 'button', ...props },
  ref,
) {
  const isDisabled = disabled || loading;
  return (
    <button
      ref={ref}
      type={type}
      disabled={isDisabled}
      aria-busy={loading || undefined}
      className={`inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-colors duration-200 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-canvas disabled:pointer-events-none disabled:opacity-60 ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${className}`}
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
