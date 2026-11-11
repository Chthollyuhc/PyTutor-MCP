import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { getValidTheme, resolveTheme } from './themePreference';

export const THEME_STORAGE_KEY = 'pytutor_theme';
const ThemeContext = createContext(null);

function readStoredPreference() {
  try {
    return getValidTheme(window.localStorage.getItem(THEME_STORAGE_KEY));
  } catch {
    return null;
  }
}

function getSystemTheme() {
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function ThemeProvider({ children }) {
  const [preference, setPreference] = useState(readStoredPreference);
  const [systemTheme, setSystemTheme] = useState(getSystemTheme);
  const theme = resolveTheme(preference, systemTheme);

  useEffect(() => {
    const media = window.matchMedia?.('(prefers-color-scheme: dark)');
    if (!media) return undefined;

    const updateSystemTheme = (event) => setSystemTheme(event.matches ? 'dark' : 'light');
    if (media.addEventListener) media.addEventListener('change', updateSystemTheme);
    else media.addListener?.(updateSystemTheme);
    return () => {
      if (media.removeEventListener) media.removeEventListener('change', updateSystemTheme);
      else media.removeListener?.(updateSystemTheme);
    };
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.classList.toggle('dark', theme === 'dark');
    document.documentElement.style.colorScheme = theme;
  }, [theme]);

  const toggleTheme = useCallback(() => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setPreference(nextTheme);
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    } catch {
      // Theme still changes for this session when storage is unavailable.
    }
  }, [theme]);

  const value = useMemo(() => ({ theme, toggleTheme }), [theme, toggleTheme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
