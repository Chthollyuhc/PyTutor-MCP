---
name: PyTutor Minimalist Bento
description: A sleek, modern soft-minimalist Bento UI with iOS / Dynamic Island aesthetic for PyTutor NEU.
colors:
  primary: "#10B981"
  primary-hover: "#059669"
  canvas-light: "#F4F5F7"
  surface-light: "#FFFFFF"
  surface-raised-light: "#F8F9FA"
  border-light: "#E5E7EB"
  foreground-light: "#0F172A"
  muted-light: "#64748B"
  canvas-dark: "#090D16"
  surface-dark: "#131926"
  surface-raised-dark: "#1C2436"
  border-dark: "#263248"
  foreground-dark: "#F8FAFC"
  muted-dark: "#94A3B8"
  dark-island: "#0B0F17"
typography:
  display: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif"
  body: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Roboto, sans-serif"
  code: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
rounded:
  pill: "9999px"
  card: "24px"
  card-sm: "18px"
  circle: "9999px"
---

# Design System: PyTutor Minimalist Bento

## 1. Overview & North Star

**Creative North Star: Sleek Bento Minimalism (iOS / Dynamic Island Aesthetic)**

PyTutor's interface embraces the clean, airy, high-contrast aesthetic of modern Bento grids:
- **Soft Canvas & Pure White Surfaces:** Generous spacing, soft off-white canvas (`#F4F5F7`), pure white cards (`#FFFFFF`) with subtle hairline boundaries (`border-slate-200/80`).
- **High-Contrast Dark Island Accents:** Designated focus widgets (e.g. Autonomy Stars, voice notes, action widgets) utilize rich pitch-black surfaces (`#0B0F17`) with vibrant emerald (`#10B981`) and amber accents.
- **Pill Geometry:** Buttons, status badges, segmented tab capsules, and search inputs are shaped as elegant pills (`rounded-full`).
- **Soft Bento Elevation:** Subtle multi-layer ambient shadows (`shadow-bento`, `shadow-soft`) giving tactile physical depth without harsh outlines.

---

## 2. Color Palette

### Primary & Accent
- **Radiant Emerald** (`#10B981` / hover `#059669`): Primary interactive actions, successful runs, high mastery indicators.
- **Dynamic Dark Island** (`#0B0F17`): High-contrast focus cards and primary action pills.
- **Amber Gold** (`#F59E0B`): Autonomy stars, gamification achievements, caution alerts.
- **Sky Blue** (`#0EA5E9`): Course module info, informative indicators.
- **Violet / AI** (`#8B5CF6`): AI Socratic tutor hints and pythonic reviews.

### Neutrals
- **Canvas:** `#F4F5F7` (Light) / `#090D16` (Dark)
- **Surface:** `#FFFFFF` (Light) / `#131926` (Dark)
- **Surface Raised:** `#F8F9FA` (Light) / `#1C2436` (Dark)
- **Borders:** `#E5E7EB` (Light) / `#263248` (Dark)
- **Foreground:** `#0F172A` (Light) / `#F8FAFC` (Dark)
- **Muted:** `#64748B` (Light) / `#94A3B8` (Dark)

---

## 3. Typography & Hierarchy

- **Font Family:** Apple SF Pro / Segoe UI modern system stack.
- **Headings:** Bold to extra-bold (`font-bold`, `tracking-tight`), crisp contrast against card surfaces.
- **Numbers & Counters:** Large, confident numbers (`text-2xl` / `text-3xl font-bold tracking-tight tabular-nums`).
- **Badges & Labels:** `text-xs font-semibold tracking-tight`.

---

## 4. Components & Geometry

### Cards (`<Card>` / Bento Widgets)
- **Border Radius:** `rounded-3xl` (24px) for main containers and class cards; `rounded-2xl` (18px) for list items.
- **Elevation:** `shadow-bento` (`0 4px 20px -2px rgba(0,0,0,0.04)`) with smooth hover lift `hover:shadow-bento-hover`.
- **Dark Island Card:** `keep-dark bg-slate-950 text-white rounded-3xl p-5 border border-slate-800/80 shadow-bento`.

### Buttons (`<Button>`)
- **Pill Shape:** `rounded-full font-semibold transition-all duration-200 active:scale-[0.98]`.
- **Primary:** `bg-emerald-500 hover:bg-emerald-600 text-white shadow-soft`.
- **Black Pill:** `bg-slate-950 hover:bg-black text-white dark:bg-white dark:text-slate-950 shadow-soft`.
- **Secondary:** `border border-border/80 bg-surface text-foreground hover:bg-surface-raised`.

### Badges (`<Badge>`)
- **Capsule Pill:** `rounded-full px-2.5 py-0.5 text-xs font-medium tracking-tight`.
- Clean translucent fills with matching hairline border rings.

### Segmented Controls (Tab Capsules)
- Capsule container: `p-1 bg-surface-raised rounded-full border border-border/80 inline-flex gap-1`.
- Active segment: Pure white pill with subtle drop shadow `bg-surface text-foreground shadow-sm rounded-full px-3.5 py-1.5 text-xs font-semibold`.
- Inactive segment: Quiet muted text with smooth hover.

### Inputs & Chat Fields (`<Input>`)
- Pill input: `rounded-full border border-border/80 bg-surface px-4 py-2.5 text-sm shadow-soft focus:border-primary focus:ring-2 focus:ring-primary/20`.
- Integrated circular action button: `size-8 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-soft`.

---

## 5. Quality Checklist & Verification

1. **Light / Dark Parity:** Light mode is clean, bright, and legible; Dark mode maintains identical contrast and visual weight.
2. **Accessible Contrast:** Text on badges, pills, and surfaces strictly adheres to WCAG AA contrast standards.
3. **No Destructive Overrides:** Zero blanket `!important` color wipes in `index.css`. Gradients, backdrop filters, and shadows remain active and controlled.
4. **All Tests & Builds Passing:** `npm run test:theme` (3/3 passed) and `npm run build` (zero errors).
