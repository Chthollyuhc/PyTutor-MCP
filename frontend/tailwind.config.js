/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      borderRadius: {
        lg: '0.75rem',
        xl: '1rem',
        '2xl': '1.25rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      boxShadow: {
        soft: '0 2px 10px rgba(0, 0, 0, 0.03), 0 1px 3px rgba(0, 0, 0, 0.02)',
        bento: '0 4px 20px -2px rgba(0, 0, 0, 0.04), 0 2px 6px -1px rgba(0, 0, 0, 0.02)',
        'bento-hover': '0 10px 30px -4px rgba(0, 0, 0, 0.08), 0 4px 12px -2px rgba(0, 0, 0, 0.03)',
        'dark-bento': '0 4px 24px -2px rgba(0, 0, 0, 0.45)',
        pill: '0 2px 8px rgba(0, 0, 0, 0.04)',
      },
      colors: {
        canvas: 'rgb(var(--canvas-rgb) / <alpha-value>)',
        surface: 'rgb(var(--surface-rgb) / <alpha-value>)',
        'surface-raised': 'rgb(var(--surface-raised-rgb) / <alpha-value>)',
        border: 'rgb(var(--border-rgb) / <alpha-value>)',
        foreground: 'rgb(var(--foreground-rgb) / <alpha-value>)',
        muted: 'rgb(var(--muted-rgb) / <alpha-value>)',
        primary: {
          DEFAULT: 'rgb(var(--primary-rgb) / <alpha-value>)',
          foreground: 'rgb(var(--primary-foreground-rgb) / <alpha-value>)',
          hover: 'rgb(var(--primary-hover-rgb) / <alpha-value>)',
        },
        success: {
          DEFAULT: 'rgb(var(--success-rgb) / <alpha-value>)',
          soft: 'rgb(var(--success-soft-rgb) / <alpha-value>)',
          line: 'rgb(var(--success-line-rgb) / <alpha-value>)',
          strong: 'rgb(var(--success-strong-rgb) / <alpha-value>)',
        },
        warning: {
          DEFAULT: 'rgb(var(--warning-rgb) / <alpha-value>)',
          soft: 'rgb(var(--warning-soft-rgb) / <alpha-value>)',
          line: 'rgb(var(--warning-line-rgb) / <alpha-value>)',
          strong: 'rgb(var(--warning-strong-rgb) / <alpha-value>)',
        },
        destructive: {
          DEFAULT: 'rgb(var(--destructive-rgb) / <alpha-value>)',
          soft: 'rgb(var(--destructive-soft-rgb) / <alpha-value>)',
          line: 'rgb(var(--destructive-line-rgb) / <alpha-value>)',
          strong: 'rgb(var(--destructive-strong-rgb) / <alpha-value>)',
        },
        info: {
          DEFAULT: 'rgb(var(--info-rgb) / <alpha-value>)',
          soft: 'rgb(var(--info-soft-rgb) / <alpha-value>)',
          line: 'rgb(var(--info-line-rgb) / <alpha-value>)',
          strong: 'rgb(var(--info-strong-rgb) / <alpha-value>)',
        },
        ai: {
          DEFAULT: 'rgb(var(--ai-rgb) / <alpha-value>)',
          soft: 'rgb(var(--ai-soft-rgb) / <alpha-value>)',
          line: 'rgb(var(--ai-line-rgb) / <alpha-value>)',
          strong: 'rgb(var(--ai-strong-rgb) / <alpha-value>)',
        },
        tone: {
          DEFAULT: 'rgb(var(--tone-rgb) / <alpha-value>)',
          soft: 'rgb(var(--tone-soft-rgb) / <alpha-value>)',
          line: 'rgb(var(--tone-line-rgb) / <alpha-value>)',
          strong: 'rgb(var(--tone-strong-rgb) / <alpha-value>)',
        },
        'on-solid': 'rgb(var(--on-solid-rgb) / <alpha-value>)',
        'header-foreground': 'rgb(var(--header-foreground-rgb) / <alpha-value>)',
        brand: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          900: '#14532d',
        }
      }
    },
  },
  plugins: [],
}
