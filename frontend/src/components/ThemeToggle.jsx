import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function ThemeToggle({ className = '' }) {
  const { theme, toggleTheme } = useTheme();
  const nextThemeLabel = theme === 'dark' ? 'sáng' : 'tối';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={`Chuyển sang giao diện ${nextThemeLabel}`}
      title={`Chuyển sang giao diện ${nextThemeLabel}`}
      aria-pressed={theme === 'dark'}
      className={`inline-flex size-10 shrink-0 items-center justify-center rounded-md border border-border bg-surface text-foreground transition-colors hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-canvas ${className}`}
    >
      {theme === 'dark'
        ? <Sun aria-hidden="true" className="size-4" />
        : <Moon aria-hidden="true" className="size-4" />}
    </button>
  );
}
