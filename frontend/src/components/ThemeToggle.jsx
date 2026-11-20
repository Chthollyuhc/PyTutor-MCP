import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function ThemeToggle({ className = '', variant = 'default' }) {
  const { theme, toggleTheme } = useTheme();
  const nextThemeLabel = theme === 'dark' ? 'sáng' : 'tối';
  const variantClasses = variant === 'onBrand'
    ? 'border-header-foreground/20 bg-header-foreground/15 text-on-solid hover:bg-header-foreground/25'
    : 'border-border/80 bg-surface text-foreground hover:bg-surface-raised shadow-soft';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={`Chuyển sang giao diện ${nextThemeLabel}`}
      title={`Chuyển sang giao diện ${nextThemeLabel}`}
      aria-pressed={theme === 'dark'}
      className={`inline-flex size-9 shrink-0 items-center justify-center rounded-full border transition-all duration-200 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-canvas cursor-pointer ${variantClasses} ${className}`}
    >
      {theme === 'dark'
        ? <Sun aria-hidden="true" className="size-4 text-amber-400" />
        : <Moon aria-hidden="true" className="size-4 text-slate-700" />}
    </button>
  );
}
