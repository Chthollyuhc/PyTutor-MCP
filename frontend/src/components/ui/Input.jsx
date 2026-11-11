import React, { useId } from 'react';

const Input = React.forwardRef(function Input(
  { id: suppliedId, label, icon: Icon, error, hint, className = '', ...props },
  ref,
) {
  const generatedId = useId();
  const id = suppliedId || generatedId;
  const descriptionId = error ? `${id}-error` : hint ? `${id}-hint` : undefined;

  return (
    <div className="space-y-2">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-foreground">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <Icon aria-hidden="true" className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted" />
        )}
        <input
          ref={ref}
          id={id}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={descriptionId}
          className={`min-h-11 w-full rounded-md border border-border bg-canvas px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted/80 outline-none transition-colors duration-200 focus:border-primary focus:ring-2 focus:ring-primary/20 ${Icon ? 'pl-10' : ''} ${error ? 'border-destructive focus:border-destructive focus:ring-destructive/20' : ''} ${className}`}
          {...props}
        />
      </div>
      {error && <p id={`${id}-error`} role="alert" className="text-sm text-rose-300">{error}</p>}
      {!error && hint && <p id={`${id}-hint`} className="text-xs leading-relaxed text-muted">{hint}</p>}
    </div>
  );
});

export default Input;
