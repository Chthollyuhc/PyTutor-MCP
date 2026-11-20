import React, { useId } from 'react';

const Input = React.forwardRef(function Input(
  { id: suppliedId, as: Control = 'input', label, icon: Icon, error, hint, pill = true, className = '', ...props },
  ref,
) {
  const generatedId = useId();
  const id = suppliedId || generatedId;
  const descriptionId = error ? `${id}-error` : hint ? `${id}-hint` : undefined;
  const roundedClass = pill ? 'rounded-full' : 'rounded-2xl';

  return (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={id} className="block text-xs font-semibold text-foreground pl-1">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <Icon aria-hidden="true" className="pointer-events-none absolute left-4 top-1/2 size-4 -translate-y-1/2 text-muted" />
        )}
        <Control
          ref={ref}
          id={id}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={descriptionId}
          className={`min-h-11 w-full ${roundedClass} border border-border/80 bg-surface px-4 py-2.5 text-sm text-foreground placeholder:text-muted/60 outline-none shadow-soft transition-all duration-200 focus:border-primary focus:ring-2 focus:ring-primary/20 ${Icon ? 'pl-11' : ''} ${error ? 'border-destructive focus:border-destructive focus:ring-destructive/20' : ''} ${className}`}
          {...props}
        />
      </div>
      {error && <p id={`${id}-error`} role="alert" className="text-xs text-rose-500 pl-2">{error}</p>}
      {!error && hint && <p id={`${id}-hint`} className="text-xs leading-relaxed text-muted pl-2">{hint}</p>}
    </div>
  );
});

export default Input;
