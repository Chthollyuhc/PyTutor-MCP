---
name: PyTutor-MCP
description: A clear, practical learning workspace for Python programming at NEU.
colors:
  primary-dark: "#066e44"
  primary-light: "#13633e"
  canvas-dark: "#020617"
  surface-dark: "#0f172a"
  canvas-light: "#f5f7f4"
  surface-light: "#ffffff"
  foreground-dark: "#f8fafc"
  foreground-light: "#1f2923"
  muted-dark: "#a7b4c7"
  muted-light: "#4c5b51"
  border-light: "#d3dcd5"
typography:
  body:
    fontFamily: "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 500
    lineHeight: 1.25
rounded:
  lg: "8px"
  xl: "10px"
  2xl: "12px"
  3xl: "16px"
components:
  button-primary:
    backgroundColor: "{colors.primary-light}"
    textColor: "#ffffff"
    rounded: "{rounded.lg}"
    height: "44px"
  card:
    backgroundColor: "{colors.surface-light}"
    rounded: "{rounded.xl}"
---

# Design System: PyTutor-MCP

## Overview

**Creative North Star: The Practical Learning Desk**

PyTutor-MCP should feel like a dependable course workspace: clear, practical, grounded, and focused on helping NEU students work through Python exercises. The interface preserves the PyTutor-MCP and NEU identity while making assignments, code, test results, and instructor information easy to scan. Light and dark themes share the same hierarchy and semantic color roles.

Prefer direct labels and useful status over decoration. The desired direction is quieter and less “AI-generated”: restrained surfaces, purposeful color, and minimal visual effects.

**Key Characteristics:**
- Learning-task-first hierarchy with readable labels and actionable controls.
- NEU green as the primary action color, supported by semantic status colors.
- Consistent light and dark themes, with preference following the device until manually changed.
- Flat, bordered surfaces rather than repeated decorative cards and glow effects.

## Colors

The palette pairs a dark slate workspace with a soft neutral light theme; green identifies primary actions and the NEU learning context.

### Primary
- **Forest Green** (`#066e44` dark / `#13633e` light): Main actions, focus, and branded emphasis. The light-theme value is darkened for contrast on white text.

### Neutral
- **Night Canvas** (`#020617`): Dark page background.
- **Night Surface** (`#0f172a`): Dark panels and controls.
- **Paper Canvas** (`#f5f7f4`): Light page background.
- **White Surface** (`#ffffff`): Light cards, menus, and panels.
- **Ink** (`#1f2923`): Light-theme primary text.
- **Slate White** (`#f8fafc`): Dark-theme primary text.
- **Quiet Green-Gray** (`#4c5b51` light / `#a7b4c7` dark): Secondary text and supporting labels.
- **Soft Divider** (`#d3dcd5`): Light-theme borders and dividers.

Success, warning, destructive, and informational colors are reserved for statuses and outcomes, not decoration.

## Typography

**Display Font:** System UI sans-serif stack  
**Body Font:** System UI sans-serif stack  
**Label/Mono Font:** Monaco's configured editor font for code; system UI for interface labels.

**Character:** Neutral and familiar, with clear differences in size and weight rather than a decorative display face.

### Hierarchy
- **Headline:** Use the page's established larger heading utilities for the current task or page title.
- **Title:** Medium-to-semibold system text for sections, classes, and exercise names.
- **Body** (400, 16px, 1.5): Instructions, explanations, and readable supporting content.
- **Label** (500, 15px, 1.25): Form labels, navigation, and compact controls. Light theme raises text-sm to 15px, text-xs to 13px, and legacy 9–11px utility text to 11–12px for readability.
- **Code:** Preserve monospace typography in the editor and code/result blocks.

## Layout

Use a task-oriented workspace: navigation frames the content, while the active assignment, editor, results, or class data receives the strongest area. Keep related controls close and separate major sections with space and simple borders. On narrow screens, retain the primary action and content; collapse secondary labels or move side navigation into a compact layout rather than allowing horizontal overflow. The document minimum width is 320px.

## Elevation & Depth

Depth is conveyed primarily with tonal surface changes and borders. Keep surfaces flat at rest; avoid ambient glow and heavy stacked shadows. Use overlays only to distinguish an active modal from the page behind it, and retain a clearly visible focus ring for keyboard interaction.

**The Flat-By-Default Rule.** Surfaces do not need a shadow to read as separate; use a surface tone and border first.

## Shapes

The shape language is compact and restrained: controls use modest corners (8px), cards and grouped panels use 10–12px, and larger enclosing regions may use 16px. Borders define boundaries; avoid wrapping every label or item in a pill.

## Components

### Buttons
- **Shape:** 8px corners.
- **Primary:** NEU green with white text; medium controls are at least 44px tall.
- **Hover / Focus:** Shift to the darker green hover token; provide a visible keyboard focus ring. Disabled and loading states remain legible and non-interactive.
- **Secondary / Ghost:** Neutral surface/border or quiet text treatment; do not compete with the primary action.

### Chips
- Use compact chips only for meaningful status or category; keep state colors semantic and avoid decorative tags.

### Cards / Containers
- **Corner Style:** 10–12px.
- **Background:** Theme surface token.
- **Shadow Strategy:** Flat by default; use borders and tonal contrast.
- **Border:** Semantic theme border.
- **Internal Padding:** Follow existing spacing utilities and maintain more separation between sections than within a control group.

### Inputs / Fields
- **Style:** Theme-aware canvas, semantic border, 6px input corners.
- **Focus:** Green border and subtle ring, plus the global visible focus outline for keyboard use.
- **Error / Disabled:** Use destructive color and explicit error copy; preserve readable contrast and disabled distinction.

### Navigation
- Keep role, class, and page context explicit. Active items use a clear state rather than decoration alone; on mobile, hide secondary text only when an accessible label remains.

### Theme Toggle
- Expose the current theme in the accessible name and pressed state. Persist a manual choice globally; without one, follow the device preference.

## Do's and Don'ts

### Do:
- **Do** use semantic theme tokens for new surfaces, text, borders, focus, and state colors.
- **Do** reserve green for primary actions and meaningful branded emphasis.
- **Do** keep labels, error messages, loading states, and empty states explicit.
- **Do** preserve the existing routes, role behavior, API calls, submission flow, and exam-mode restrictions when changing presentation.
- **Do** check both themes and narrow layouts whenever a page-level visual change is made.

### Don't:
- **Don't** add decorative gradients, glows, or large blurred effects to make a screen feel “AI.”
- **Don't** nest repeated cards or turn ordinary labels into badge/pill collections.
- **Don't** use color as the only indicator of status or active navigation.
- **Don't** change business behavior or backend contracts as part of a visual-only update.
